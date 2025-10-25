# app/database.py
import mysql.connector 
from mysql.connector import errorcode
from fastapi import FastAPI, Depends, HTTPException, status
from typing import List
from . import crud, schemas  # Make sure schemas.py has CommentCreate and LikeRequest
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel # Keep this import for the Pydantic models in schemas.py

# --- Database Connection Config ---
DB_USER = "root"
DB_PASSWORD ="anurag10"
DB_HOST = "localhost"
DB_NAME ="ECHO"

def get_db_connection():
    """Establishes a new database connection."""
    try:
        conn = mysql.connector.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            database=DB_NAME
        )
        return conn
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        return None

# --- FastAPI App Setup ---
app = FastAPI(
    title="Echo Blogging API (MySQL Edition)",
    description="API for the Echo blogging platform, now with MySQL.",
    version="1.1.0"
)

origins = [
    "null",
    "http://localhost",
    "http://127.0.0.1",
    "http://localhost:5500", 
    "http://127.0.0.1:5500", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

# --- NEW: Corrected Database Dependency ---
def get_db():
    """
    Dependency that provides a DB cursor and handles commit/close.
    """
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=503, detail="Could not connect to the database.")
    
    # Use dictionary=True so all fetches return dicts
    cursor = conn.cursor(dictionary=True)
    try:
        yield cursor
        # If no exceptions, commit any changes made
        # This is CRUCIAL for likes, comments, and views
        conn.commit()
    except Exception as e:
        # If any exception occurs, roll back
        conn.rollback()
        # Re-raise the exception so FastAPI can handle it
        print(f"Error in get_db: {e}")
        raise e
    finally:
        # Always close the cursor and connection
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

# --- User Endpoints ---
# (MODIFIED: Now uses `cursor=Depends(get_db)` and passes cursor to crud)
@app.post("/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED, tags=["Users"])
def create_new_user(user: schemas.UserCreate, cursor=Depends(get_db)):
    db_user = crud.get_user_by_email(cursor, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(cursor=cursor, user=user)

# --- Collection and Bookmark Endpoints ---
# (MODIFIED: Now uses `cursor=Depends(get_db)` and passes cursor to crud)
@app.post("/collections/", response_model=schemas.Collection, status_code=status.HTTP_201_CREATED, tags=["Collections & Bookmarks"])
def create_new_collection(collection: schemas.CollectionCreate, cursor=Depends(get_db)):
    current_user_id = 1 # Placeholder for auth
    new_collection = crud.create_collection(cursor, collection=collection, user_id=current_user_id)
    if not new_collection:
        raise HTTPException(status_code=400, detail="Collection with this name already exists for the user.")
    return new_collection

@app.post("/bookmarks/", response_model=schemas.Bookmark, status_code=status.HTTP_201_CREATED, tags=["Collections & Bookmarks"])
def create_new_bookmark(bookmark: schemas.BookmarkCreate, cursor=Depends(get_db)):
    current_user_id = 1 # Placeholder for auth
    new_bookmark = crud.create_bookmark(cursor, bookmark=bookmark, user_id=current_user_id)
    if new_bookmark is None:
        raise HTTPException(
            status_code=403,
            detail="Collection does not exist or does not belong to this user."
        )
    return new_bookmark

# --- Stored Procedure Endpoints (Unchanged, but now work with new get_db) ---

# === THIS IS THE ONLY /posts/ ENDPOINT NOW ===

@app.post("/posts/", tags=["Posts"], status_code=status.HTTP_201_CREATED)
def create_new_post(post: schemas.PostCreate, cursor = Depends(get_db)):
    """
    Creates a new post.
    Corresponds to `sp_create_post` procedure.
    """
    try:
        cursor.callproc('sp_create_post', [post.user_id, post.title, post.content])
        for result in cursor.stored_results():
            new_post = result.fetchall()
        
        if not new_post:
            raise HTTPException(status_code=500, detail="Failed to create post")
            
        # The procedure returns a list, so return the first item
        return new_post[0]
    except Exception as e:
        print(f"Error: {e}")
        # Handle duplicate titles or other DB errors
        raise HTTPException(status_code=400, detail=str(e))
    
    
@app.get("/posts/", tags=["Posts"])
def get_posts(limit: int = 20, offset: int = 0, cursor = Depends(get_db)):
    """
    Fetches all posts. Corresponds to `get_all_posts` procedure.
    """
    cursor.callproc('get_all_posts', [limit, offset])
    for result in cursor.stored_results():
        posts = result.fetchall()
    return posts

@app.get("/posts/{post_id}", tags=["Posts"])
def get_post_details(post_id: int, user_id: int, cursor = Depends(get_db)):
    """
    Fetches details for a single post.
    Corresponds to `get_post_details` procedure.
    """
    try:
        cursor.callproc('get_post_details', [post_id, user_id])
        for result in cursor.stored_results():
            post = result.fetchall()
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        return post
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/posts/{post_id}/comments", tags=["Posts"])
def get_post_comments(post_id: int, cursor = Depends(get_db)):
    """
    Fetches all comments for a post.
    Corresponds to `sp_get_post_comments` procedure.
    """
    cursor.callproc('sp_get_post_comments', [post_id])
    for result in cursor.stored_results():
        comments = result.fetchall()
    return comments

@app.post("/posts/{post_id}/like", tags=["Posts"])
def toggle_post_like(post_id: int, like_request: schemas.LikeRequest, cursor = Depends(get_db)):
    """
    Toggles a like on a post.
    Corresponds to `sp_toggle_like` procedure.
    """
    cursor.callproc('sp_toggle_like', [like_request.user_id, post_id])
    for result in cursor.stored_results():
        like_status = result.fetchall()
    return like_status

@app.post("/posts/{post_id}/comments", tags=["Posts"])
def create_comment(post_id: int, comment: schemas.CommentCreate, cursor = Depends(get_db)):
    """
    Creates a new comment on a post.
    Corresponds to `sp_create_comment` procedure.
    """
    cursor.callproc('sp_create_comment', [comment.user_id, post_id, comment.content])
    for result in cursor.stored_results():
        new_comment = result.fetchall()
    
    # Commit is handled by the get_db dependency
    return new_comment