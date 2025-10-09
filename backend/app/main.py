from fastapi import FastAPI, Depends, HTTPException, status
from typing import List
from . import crud, schemas
from .database import get_db_connection
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(
    title="Echo Blogging API (MySQL Edition)",
    description="API for the Echo blogging platform, now with MySQL.",
    version="1.1.0"
)

origins = [
    # "null" is the origin for local HTML files opened in the browser.
    "null",
    # You might also add your frontend's future deployed URL here.
    "http://localhost",
    "http://127.0.0.1",
    "http://localhost:5500", 
    "http://127.0.0.1:5500", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)



# Dependency for DB connection
def get_db():
    conn = get_db_connection()
    if conn is None:
        raise HTTPException(status_code=503, detail="Could not connect to the database.")
    try:
        yield conn
    finally:
        if conn and conn.is_connected():
            conn.close()

# --- User Endpoints ---
@app.post("/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED, tags=["Users"])
def create_new_user(user: schemas.UserCreate, db_conn=Depends(get_db)):
    db_user = crud.get_user_by_email(db_conn, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db_conn=db_conn, user=user)

# --- Post Endpoints ---
@app.get("/posts/", response_model=List[schemas.Post], tags=["Posts"])
def read_posts(skip: int = 0, limit: int = 10, db_conn=Depends(get_db)):
    posts_from_db = crud.get_posts(db_conn, skip=skip, limit=limit)
    formatted_posts = []
    for post in posts_from_db:
        owner_data = {
            "user_id": post["user_id"],
            "username": post["username"],
            "email": post["user_email"],
            "created_at": post["user_created_at"]
        }
        post_obj = schemas.Post(
            post_id=post["post_id"],
            title=post["title"],
            content=post["content"],
            created_at=post["created_at"],
            user_id=post["user_id"],
            owner=owner_data,
            likes_count=post["likes_count"],
            views_count=post["views_count"],
            comments_count=post.get("comments_count", 0),
            is_liked_by_user=False
        )
        formatted_posts.append(post_obj)
    return formatted_posts

# --- Like, Follow, and Comment endpoints would go here ---
# (Keeping them omitted for brevity as they are unchanged)


# --- Collection and Bookmark Endpoints ---

@app.post("/collections/", response_model=schemas.Collection, status_code=status.HTTP_201_CREATED, tags=["Collections & Bookmarks"])
def create_new_collection(collection: schemas.CollectionCreate, db_conn=Depends(get_db)):
    """
    Creates a new collection for the current user.
    """
    current_user_id = 1 # Placeholder for auth
    new_collection = crud.create_collection(db_conn, collection=collection, user_id=current_user_id)
    if not new_collection:
        raise HTTPException(status_code=400, detail="Collection with this name already exists for the user.")
    return new_collection

@app.post("/bookmarks/", response_model=schemas.Bookmark, status_code=status.HTTP_201_CREATED, tags=["Collections & Bookmarks"])
def create_new_bookmark(bookmark: schemas.BookmarkCreate, db_conn=Depends(get_db)):
    """
    Bookmarks a post into one of the user's collections.
    """
    current_user_id = 1 # Placeholder for auth
    new_bookmark = crud.create_bookmark(db_conn, bookmark=bookmark, user_id=current_user_id)
    if new_bookmark is None:
        raise HTTPException(
            status_code=403,
            detail="Collection does not exist or does not belong to this user."
        )
    return new_bookmark

