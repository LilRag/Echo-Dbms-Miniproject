from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List 

class UserBase(BaseModel):
    # fields that are common to all user related models 
    username:str
    email:str 

class UserCreate(UserBase):
    # fields required to create a user 
    password : str

class User(UserBase):
    user_id:int 
    created_at:datetime

    class Config:
        # read date even if its not a dict 
        from_attributes = True 

class PostBase(BaseModel):
    title:str
    content:str

class PostCreate(PostBase):
    pass 

class Post(PostBase):
    post_id:int 
    created_at:datetime 
    user_id:int 

    owner:User 
    likes_count: int = 0
    views_count: int = 0
    
    is_liked_by_user: bool = False

    
    class Config:
        from_attributes = True

class CommentBase(BaseModel):
    content:str

class CommentCreate(CommentBase):
    comment_id : int
    created_at: datetime 
    user_id : int 
    post_id : int 
    parent_id : Optional[int] = None 
    owner : User 

    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    category:id

    class Config:
        from_attributes = True  


class Follow(BaseModel):
    follower_id:int
    followed_id:int 
    created_at : datetime

    class Config:
        from_attributes = True 

class PostLike(BaseModel):
    user_id :int 
    post_id : int 

    class Config:
        from_attributes = True 

class CollectionBase(BaseModel):
    name: str

class CollectionCreate(CollectionBase):
    user_id:int 
    collectiion_id:int 
    created_at: datetime 

    class Config:
        from_attributes = True 

class BookmarkCreate(BaseModel):
    post_id : int 
    collection: id 

class Bookmark(BookmarkCreate):
    user_id : int 
    created_at: datetime 

    class Config:
        from_attributes = True 


class PostViews(BaseModel):
    post_id :int 
    user_id : Optional[int] = None # for anonymous
    view_id : int 
    viwed_at:  datetime 

    class Config:
        from_attributes = True 





