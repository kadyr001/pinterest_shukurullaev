from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class UserRegisterShema(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserLoginShema(BaseModel):
    email: EmailStr
    password: str


class UserOutShema(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None
    website: Optional[str] = None
    created_at: datetime

    model_config = {'from_attributes': True}


class UserUpdateShema(BaseModel):
    full_name: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None
    website: Optional[str] = None


class BoardInputShema(BaseModel):
    title: str
    description: Optional[str] = None
    cover_image: Optional[str] = None
    is_private: bool = False


class BoardOutShema(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    cover_image: Optional[str] = None
    user_id: int
    is_private: bool
    created_at: datetime
    pin_count: int = 0

    model_config = {'from_attributes': True}


class PinInputShema(BaseModel):
    title: str
    description: Optional[str] = None
    image_url: str
    link_url: Optional[str] = None
    board_id: Optional[int] = None
    tag_ids: List[int] = []


class PinOutShema(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    image_url: str
    link_url: Optional[str] = None
    author_id: int
    board_id: Optional[int] = None
    created_at: datetime
    likes_count: int = 0
    comments_count: int = 0
    saves_count: int = 0

    model_config = {'from_attributes': True}


class TagOutShema(BaseModel):
    id: int
    name: str

    model_config = {'from_attributes': True}


class CommentInputShema(BaseModel):
    text: str
    pin_id: int


class CommentOutShema(BaseModel):
    id: int
    text: str
    user_id: int
    pin_id: int
    created_at: datetime

    model_config = {'from_attributes': True}


class FeedOutShema(BaseModel):
    pins: List[PinOutShema] = []
