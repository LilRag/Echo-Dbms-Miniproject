from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List 

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email:str
    password:str
    
class User(UserBase):
    user_id: int
    created_at: datetime
    class Config:
        from_attributes = True

class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(BaseModel):
    title: str
    content: str
    user_id: int # In a real app, you'd get this from the auth token
    categories: Optional[str] = None

    
class Post(PostBase):
    post_id: int
    created_at: datetime
    user_id: int
    owner: User
    likes_count: int = 0
    views_count: int = 0
    is_liked_by_user: bool = False
    class Config:
        from_attributes = True

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    # Corrected: A user only needs to send the content of the comment.
    # The server will add the user_id, post_id, etc.
    pass

class Comment(CommentBase):
    comment_id: int
    created_at: datetime
    user_id: int
    post_id: int
    parent_id: Optional[int] = None
    owner: User
    class Config:
        from_attributes = True

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    # Corrected: The field name should be 'category_id' and the type 'int'.
    category_id: int
    class Config:
        from_attributes = True

class CollectionBase(BaseModel):
    name: str

class CollectionCreate(CollectionBase):
    # Corrected: A user only sends the name for the new collection.
    name: str
    user_id: int

class Collection(CollectionBase):
    collection_id: int # Corrected: 'collectiion_id' typo
    user_id: int
    created_at: datetime
    class Config:
        from_attributes = True

class BookmarkCreate(BaseModel):
    post_id: int
    # Corrected: The field should be 'collection_id' and the type 'int'.
    collection_id: int
    user_id: int

class Bookmark(BookmarkCreate):
    user_id: int
    created_at: datetime
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

class PostViews(BaseModel):
    post_id :int 
    user_id : Optional[int] = None # for anonymous
    view_id : int 
    viwed_at:  datetime 

    class Config:
        from_attributes = True 



class LikeRequest(BaseModel):
    user_id: int

class CommentCreate(BaseModel):
    user_id: int
    content: str

class UserProfile(BaseModel):
    user_id: int
    username: str
    email: str
    created_at: datetime
    post_count: int
    follower_count: int
    following_count: int

class FollowRequest(BaseModel):
    user_id: int

class FollowRequest(BaseModel):
    user_id: int


class PostSearchResult(BaseModel):
    post_id: int
    title: str
    content: str
    created_at: datetime
    user_id: int
    likes_count: int
    views_count: int
    comments_count: int
    username: str

class UserSearchResult(BaseModel):
    user_id: int
    username: str
    email: str
    created_at: datetime

class TagSearchResult(BaseModel):
    category_id: int
    name: str
    post_count: int

class SearchResults(BaseModel):
    posts: List[PostSearchResult]
    users: List[UserSearchResult]
    tags: List[TagSearchResult]


