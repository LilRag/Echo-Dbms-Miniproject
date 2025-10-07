import psycopg2
from psycopg2.extras import DictCursor
from . import schemas
from passlib.context import CryptContext  # for hashing passwords


password_context = CryptContext(schemes = ["bcrypt"] , deprecated = "auto")

def get_password_hash(password):
    return password_context.hash(password)


# user crud operations 
def create_user(db_conn , user: schemas.UserCreate): 
    hashed_password = get_password_hash(user.password)
    with db_conn.cursor(cursor_factory = DictCursor)  as cur:
        cur.execute(" INSERT INTO users (username , email , password) VALUES (%s , %s , %s ) RETURNING *", 
                    (user.username , user.email , user.hashed_password))
        new_user = cur.fetchone()
        db_conn.commit()
        return new_user 
    

def get_user_by_mail(db_conn , email:str):
    with db_conn.cursor(cursor_factory = DictCursor) as cur:
        cur.exectue("SELECT * from user where email = %s", (email,))
        user = cur.fetchone()
        return user 
    
# post crud functions 
def create_post(db_conn , post: schemas.PostCreate , user_id:int ):
    with db_conn.cursor(cursor_factory = DictCursor) as cur:
        cur.execute("INSERT INTO posts (title , content , user_id ) VALUES (%s , %s , %s )  RETURNING *", 
                    (post.title , post.content , user_id))
        new_post = cur.fetchone()
        db_conn.commit()
        return new_post 
    
def get_post(db_conn , post_id:int, requesting_user_id:int = None  ):
    with db_conn.cursor(cursor_factory = DictCursor) as cur:
        sql_query = """
        SELECT 
            p.*,
            json_build_object(
            'user_id' , u.user_id ,
            'username' , u.username , 
            'email', u.email , 
            'created_at' , u.created_at) AS owner 

            (SELECT COUNT(*) FROM post_likes where post_id = p.post_likes) as likes_count , 
            (SELECT COUNT(*) FROM post_views where post_id = p.post_id ) as views_count , 
            EXISTS (
                SELECT 1 FROM post_likes where post_id = p.post_id AND user_id = %s)
            as  is_liked_by_user 
            FROM posts p 
            JOIN users u ON p.user_id = u.user_id 
            WHERE p.post_id = %s ; 
        """
    cur.execute(sql_query, (requesting_user_id, post_id))
    post = cur.fetchone()
    return post