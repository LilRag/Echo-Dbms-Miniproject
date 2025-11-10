# app/database.py
import mysql.connector 
from mysql.connector import errorcode
from fastapi import FastAPI, Depends, HTTPException, status
from typing import List
import crud
import schemas  # Make sure schemas.py has CommentCreate and LikeRequest
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
    "http://localhost:5501",  # Add this too in case
    "http://127.0.0.1:5501",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # This should allow all methods including OPTIONS
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
    try:
        db_user = crud.get_user_by_email(cursor, email=user.email)
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        new_user = crud.create_user(cursor=cursor, user=user)
        
        if not new_user:
            raise HTTPException(status_code=500, detail="Failed to create user")
        
        return new_user
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in create_new_user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login", tags=["Users"])
def login_user(login_data: schemas.UserLogin, cursor=Depends(get_db)):
    """
    Logs in a user by verifying their email and password.
    """
    # 1. Get user by email
    user = crud.get_user_by_email(cursor, email=login_data.email)
    
    # 2. Check if user exists and password is correct
    if not user or not crud.verify_password(login_data.password, user['hashed_password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
        
    # 3. Success! Remove password hash before returning user data
    del user['hashed_password']
    return user


# --- Collection and Bookmark Endpoints ---
# (MODIFIED: Now uses `cursor=Depends(get_db)` and passes cursor to crud)
@app.post("/collections/", response_model=schemas.Collection, status_code=status.HTTP_201_CREATED, tags=["Collections & Bookmarks"])
def create_new_collection(collection: schemas.CollectionCreate, cursor=Depends(get_db)):
    """
    Creates a new collection for a user using sp_create_collection.
    """
    try:
        cursor.callproc('sp_create_collection', [collection.user_id, collection.name])
        for result in cursor.stored_results():
            new_collection = result.fetchone()
        
        if not new_collection:
            raise HTTPException(status_code=500, detail="Failed to create collection")
            
        return new_collection
    except mysql.connector.Error as err:
        if err.errno == 1062: # Duplicate entry
            raise HTTPException(status_code=400, detail="Collection with this name already exists")
        raise HTTPException(status_code=500, detail=str(err))
    

@app.post("/bookmarks/", response_model=schemas.Bookmark, status_code=status.HTTP_201_CREATED, tags=["Collections & Bookmarks"])
def create_new_bookmark(bookmark: schemas.BookmarkCreate, cursor=Depends(get_db)):
    """
    Bookmarks a post into a collection using sp_add_bookmark.
    """
    try:
        cursor.callproc('sp_add_bookmark', [bookmark.user_id, bookmark.post_id, bookmark.collection_id])
        for result in cursor.stored_results():
            new_bookmark = result.fetchone()
        
        if not new_bookmark:
            # This can happen if the post or collection doesn't exist (foreign key constraint)
            raise HTTPException(status_code=404, detail="Post or Collection not found")
        
        return new_bookmark
    except mysql.connector.Error as err:
        if err.errno == 1062: # Duplicate entry
             return {"detail": "Post already bookmarked in this collection"}
        raise HTTPException(status_code=500, detail=str(err))

@app.get("/users/{user_id}/collections", tags=["Collections & Bookmarks"])
def get_user_collections(user_id: int, cursor=Depends(get_db)):
    """
    Gets all collections for a specific user.
    """
    try:
        cursor.callproc('sp_get_user_collections', [user_id])
        collections = []
        for result in cursor.stored_results():
            collections = result.fetchall()
        return collections
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/posts/{post_id}/bookmark-status", tags=["Collections & Bookmarks"])
def get_bookmark_status(post_id: int, user_id: int, cursor=Depends(get_db)):
    """
    Checks which collections a post is bookmarked in for a user.
    """
    try:
        cursor.callproc('sp_check_bookmark_status', [user_id, post_id])
        status = []
        for result in cursor.stored_results():
            status = result.fetchall()
        # Return a simple list of IDs, e.g., [1, 5]
        return [item['collection_id'] for item in status]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/bookmarks/", status_code=status.HTTP_200_OK, tags=["Collections & Bookmarks"])
def remove_bookmark(
    user_id: int,
    post_id: int,
    collection_id: int,
    cursor=Depends(get_db)
):
    """
    Removes a bookmark from a collection.
    """
    try:
        cursor.callproc('sp_remove_bookmark', [user_id, post_id, collection_id])
        for result in cursor.stored_results():
            status = result.fetchone()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/collections/{collection_id}/posts", tags=["Collections & Bookmarks"])
def get_posts_in_collection(
    collection_id: int,
    user_id: int, # We need this to ensure the user owns the collection
    cursor=Depends(get_db)
):
    """
    Gets all posts saved in a specific collection.
    """
    try:
        cursor.callproc('sp_get_posts_in_collection', [user_id, collection_id])
        posts = []
        for result in cursor.stored_results():
            posts = result.fetchall()
        return posts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# --- Stored Procedure Endpoints (Unchanged, but now work with new get_db) ---

# === THIS IS THE ONLY /posts/ ENDPOINT NOW ===

@app.post("/posts/", tags=["Posts"], status_code=status.HTTP_201_CREATED)
def create_new_post(post: schemas.PostCreate, cursor = Depends(get_db)):
    """
    Creates a new post and links any provided categories.
    Corresponds to `sp_create_post` procedure.
    """
    try:
        # Pass the new categories string to the procedure
        cursor.callproc('sp_create_post', [
            post.user_id, 
            post.title, 
            post.content, 
            post.categories # This can be None or a string
        ])
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

@app.get("/users/{user_id}", response_model=schemas.UserProfile, tags=["Users"])
def get_user_profile(user_id: int, cursor=Depends(get_db)):
    """
    Fetches detailed profile information for a single user,
    including their post, follower, and following counts.
    """
    try:
        cursor.callproc('sp_get_user_profile', [user_id])
        for result in cursor.stored_results():
            profile = result.fetchone() # Use fetchone() since we expect 1 user
        
        if not profile:
            raise HTTPException(status_code=404, detail="User not found")
        
        return profile
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# --- ADD THIS ENDPOINT (e.g., after the one above) ---
@app.get("/users/{user_id}/posts", tags=["Users"])
def get_posts_by_user(user_id: int, limit: int = 20, offset: int = 0, cursor=Depends(get_db)):
    """
    Fetches all posts created by a specific user.
    """
    try:
        cursor.callproc('sp_get_user_posts', [user_id, limit, offset])
        for result in cursor.stored_results():
            posts = result.fetchall()
        
        return posts
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    


@app.get("/users/{user_id}/is-following", tags=["Users"])
def check_follow_status(user_id: int, follower_id: int, cursor=Depends(get_db)):
    """
    Checks if the 'follower_id' is following the 'user_id'.
    """
    try:
        cursor.callproc('sp_check_follow', [follower_id, user_id])
        for result in cursor.stored_results():
            status = result.fetchone() # e.g., {'is_following': 1}
        return status
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/users/{user_id}/follow", tags=["Users"])
def toggle_follow_user(user_id: int, follow_request: schemas.FollowRequest, cursor=Depends(get_db)):
    """
    Toggles the follow state between the requesting user and the user_id.
    'user_id' is the person being followed.
    'follow_request.user_id' is the person doing the following.
    """
    try:
        follower_id = follow_request.user_id
        followed_id = user_id

        if follower_id == followed_id:
            raise HTTPException(status_code=400, detail="Cannot follow yourself")

        cursor.callproc('sp_toggle_follow', [follower_id, followed_id])
        for result in cursor.stored_results():
            new_state = result.fetchone() # e.g., {'is_following': 1, 'new_follower_count': 1}
        
        return new_state
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    

@app.get("/users/{user_id}/is-following", tags=["Users"])
def check_follow_status(user_id: int, follower_id: int, cursor=Depends(get_db)):
    """
    Checks if the 'follower_id' is following the 'user_id'.
    """
    status = None  # <-- FIX: Initialize status here
    try:
        cursor.callproc('sp_check_follow', [follower_id, user_id])
        for result in cursor.stored_results():
            status = result.fetchone() # e.g., {'is_following': 1}
        
        if status is None:
            # This should ideally not happen, but it's good to check
            raise HTTPException(status_code=500, detail="Could not retrieve follow status")

        return status
    except Exception as e:
        print(f"Error in check_follow_status: {e}") # More detailed logging
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/users/{user_id}/follow", tags=["Users"])
def toggle_follow_user(user_id: int, follow_request: schemas.FollowRequest, cursor=Depends(get_db)):
    """
    Toggles the follow state between the requesting user and the user_id.
    'user_id' is the person being followed.
    'follow_request.user_id' is the person doing the following.
    """
    try:
        follower_id = follow_request.user_id
        followed_id = user_id

        if follower_id == followed_id:
            raise HTTPException(status_code=400, detail="Cannot follow yourself")

        cursor.callproc('sp_toggle_follow', [follower_id, followed_id])
        for result in cursor.stored_results():
            new_state = result.fetchone() # e.g., {'is_following': 1, 'new_follower_count': 1}
        
        return new_state
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# In app/main.py

@app.get("/feed", tags=["Posts"])
def get_home_feed(user_id: int, limit: int = 20, offset: int = 0, cursor=Depends(get_db)):
    """
    Gets the curated home feed for a specific user.
    Only shows posts from people they follow.
    """
    try:
        cursor.callproc('sp_get_home_feed', [user_id, limit, offset])
        for result in cursor.stored_results():
            posts = result.fetchall()
        return posts
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@app.get("/search", response_model=schemas.SearchResults, tags=["Search"])
def search_all(q: str, cursor=Depends(get_db)):
    """
    Performs a site-wide search for posts, users, and tags.
    """
    if not q:
        return {"posts": [], "users": [], "tags": []}

    try:
        # 1. Search Posts
        cursor.callproc('sp_search_posts', [q])
        posts = []
        for result in cursor.stored_results():
            posts = result.fetchall()
        
        # 2. Search Users
        cursor.callproc('sp_search_users', [q])
        users = []
        for result in cursor.stored_results():
            users = result.fetchall()
            
        # 3. Search Tags
        cursor.callproc('sp_search_tags', [q])
        tags = []
        for result in cursor.stored_results():
            tags = result.fetchall()
            
        return {"posts": posts, "users": users, "tags": tags}
        
    except Exception as e:
        print(f"Error in search_all: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    

class DeleteRequest(BaseModel):
    user_id: int   

@app.delete("/posts/{post_id}", status_code=status.HTTP_200_OK, tags=["Posts"])
def delete_post(post_id: int, delete_request: DeleteRequest, cursor=Depends(get_db)):
    """
    Deletes a post, but only if the user_id matches the post's author.
    """
    try:
        cursor.callproc('sp_delete_post', [post_id, delete_request.user_id])
        for result in cursor.stored_results():
            status = result.fetchone()
        
        if status['deleted_rows'] == 0:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Post not found or user not authorized to delete"
            )
            
        return {"status": "Post deleted successfully"}
        
    except Exception as e:
        print(f"Error in delete_post: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
@app.get("/users/{user_id}/notifications/unread-count", response_model=schemas.UnreadCount, tags=["Notifications"])
def get_unread_count(user_id: int, cursor=Depends(get_db)):
    """
    Gets the count of unread notifications for a user.
    """
    try:
        cursor.callproc('sp_get_unread_notification_count', [user_id])
        for result in cursor.stored_results():
            count = result.fetchone()
        return count
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/users/{user_id}/notifications", response_model=List[schemas.Notification], tags=["Notifications"])
def get_notifications(user_id: int, cursor=Depends(get_db)):
    """
    Gets the 50 most recent notifications for a user.
    """
    try:
        cursor.callproc('sp_get_user_notifications', [user_id])
        notifications = []
        for result in cursor.stored_results():
            notifications = result.fetchall()
        return notifications
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/users/{user_id}/notifications/mark-read", tags=["Notifications"])
def mark_notifications_read(user_id: int, cursor=Depends(get_db)):
    """
    Marks all unread notifications for a user as read.
    """
    try:
        cursor.callproc('sp_mark_notifications_as_read', [user_id])
        for result in cursor.stored_results():
            status = result.fetchone()
        return status
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")