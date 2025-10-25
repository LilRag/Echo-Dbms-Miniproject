from . import schemas
from passlib.context import CryptContext

# Hashing setup remains the same
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    """Hashes a plain-text password."""

    # Encode the string to bytes to check its byte length
    password_bytes = password.encode('utf-8')

    # Truncate the byte string to 72 bytes if it's too long
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]

    # Hash the (potentially truncated) byte string
    return pwd_context.hash(password_bytes)
# --- User CRUD Functions ---
# (MODIFIED: Accepts cursor, no 'with' block, no 'commit')
def create_user(cursor, user: schemas.UserCreate):
    """Creates a new user in the MySQL database."""
    hashed_password = get_password_hash(user.password)
    
    cursor.execute(
        "INSERT INTO users (username, email, hashed_password) VALUES (%s, %s, %s);",
        (user.username, user.email, hashed_password)
    )
    new_user_id = cursor.lastrowid
    # Commit is handled by the dependency
    cursor.execute("SELECT * FROM users WHERE user_id = %s;", (new_user_id,))
    new_user = cursor.fetchone()
    return new_user

# (MODIFIED: Accepts cursor, no 'with' block)
def get_user_by_email(cursor, email: str):
    """Retrieves a user by their email address."""
    cursor.execute("SELECT * FROM users WHERE email = %s;", (email,))
    user = cursor.fetchone()
    return user

# (MODIFIED: Accepts cursor, no 'with' block)
def get_user_by_id(cursor, user_id: int):
    """Retrieves a user by their ID."""
    cursor.execute("SELECT * FROM users WHERE user_id = %s;", (user_id,))
    user = cursor.fetchone()
    return user

# --- Post CRUD Functions ---
# (MODIFIED: Accepts cursor, no 'with' block, no 'commit')
def create_post(cursor, post: schemas.PostCreate, user_id: int):
    """Creates a new post."""
    cursor.execute(
        "INSERT INTO posts (title, content, user_id) VALUES (%s, %s, %s);",
        (post.title, post.content, user_id)
    )
    new_post_id = cursor.lastrowid
    # Commit is handled by the dependency
    cursor.execute("SELECT * FROM posts WHERE post_id = %s;", (new_post_id,))
    new_post = cursor.fetchone()
    return new_post

# (MODIFIED: Accepts cursor, no 'with' block)
def get_posts(cursor, skip: int = 0, limit: int = 10):
    """
    Retrieves a list of posts with owner details using a standard JOIN.
    NOTE: This function is no longer called by any endpoint.
    The `/posts/` endpoint now calls the `get_all_posts` procedure.
    """
    sql_query = """
        SELECT
            p.post_id, p.title, p.content, p.created_at, p.user_id,
            u.username, u.email as user_email, u.created_at as user_created_at,
            (SELECT COUNT(*) FROM post_likes pl WHERE pl.post_id = p.post_id) as likes_count,
            (SELECT COUNT(*) FROM post_views pv WHERE pv.post_id = p.post_id) as views_count
        FROM posts p
        JOIN users u ON p.user_id = u.user_id
        ORDER BY p.created_at DESC
        LIMIT %s OFFSET %s;
    """
    cursor.execute(sql_query, (limit, skip))
    posts = cursor.fetchall()
    return posts

# --- Comment CRUD Functions ---
# (MODIFIED: Accepts cursor, no 'with' block, no 'commit')
def create_comment(cursor, comment: schemas.CommentCreate, post_id: int, user_id: int):
    """Creates a new comment on a post."""
    cursor.execute(
        "INSERT INTO comments (content, post_id, user_id) VALUES (%s, %s, %s);",
        (comment.content, post_id, user_id)
    )
    new_comment_id = cursor.lastrowid
    # Commit is handled by the dependency
    cursor.execute("SELECT * FROM comments WHERE comment_id = %s;", (new_comment_id,))
    return cursor.fetchone()

# --- Post Like CRUD Functions ---
# (MODIFIED: Accepts cursor, no 'with' block, no 'commit')
def create_post_like(cursor, post_id: int, user_id: int):
    """Likes a post for a user. Ignores duplicates."""
    cursor.execute(
        "INSERT IGNORE INTO post_likes (post_id, user_id) VALUES (%s, %s);",
        (post_id, user_id)
    )
    # Commit is handled by the dependency
    return {"status": "ok"}

# (MODIFIED: Accepts cursor, no 'with' block, no 'commit')
def delete_post_like(cursor, post_id: int, user_id: int):
    """Unlikes a post for a user."""
    cursor.execute(
        "DELETE FROM post_likes WHERE post_id = %s AND user_id = %s;",
        (post_id, user_id)
    )
    # Commit is handled by the dependency
    return {"status": "ok"}

# --- Follow CRUD Functions ---
# (MODIFIED: Accepts cursor, no 'with' block, no 'commit')
def create_follow(cursor, follower_id: int, followed_id: int):
    """Creates a follow relationship."""
    cursor.execute(
        "INSERT IGNORE INTO follows (follower_id, followed_id) VALUES (%s, %s);",
        (follower_id, followed_id)
    )
    # Commit is handled by the dependency
    return {"status": "ok"}

# (MODIFIED: Accepts cursor, no 'with' block, no 'commit')
def delete_follow(cursor, follower_id: int, followed_id: int):
    """Deletes a follow relationship."""
    cursor.execute(
        "DELETE FROM follows WHERE follower_id = %s AND followed_id = %s;",
        (follower_id, followed_id)
    )
    # Commit is handled by the dependency
    return {"status": "ok"}

# (MODIFIED: Accepts cursor, no 'with' block, no 'commit')
def create_collection(cursor, collection: schemas.CollectionCreate, user_id: int):
    """Creates a new collection for a user."""
    cursor.execute(
        "INSERT IGNORE INTO collections (name, user_id) VALUES (%s, %s);",
        (collection.name, user_id)
    )
    new_collection_id = cursor.lastrowid
    # Commit is handled by the dependency
    cursor.execute("SELECT * FROM collections WHERE collection_id = %s;", (new_collection_id,))
    return cursor.fetchone()

# (MODIFIED: Accepts cursor, no 'with' block, no 'commit')
def create_bookmark(cursor, bookmark: schemas.BookmarkCreate, user_id: int):
    """Creates a bookmark, linking a user, post, and collection."""
    cursor.execute(
        "SELECT user_id FROM collections WHERE collection_id = %s;",
        (bookmark.collection_id,)
    )
    collection_owner = cursor.fetchone()
    if not collection_owner or collection_owner['user_id'] != user_id:
        return None 

    cursor.execute(
        "INSERT IGNORE INTO bookmarks (user_id, post_id, collection_id) VALUES (%s, %s, %s);",
        (user_id, bookmark.post_id, bookmark.collection_id)
    )
    # Commit is handled by the dependency
    return {"status": "ok", "user_id": user_id, "post_id": bookmark.post_id, "collection_id": bookmark.collection_id}