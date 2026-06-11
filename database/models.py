from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, Boolean, Integer, DateTime, func, ForeignKey, Table, Column
from typing import Optional, List
from datetime import datetime
from .db import Base


pin_tags = Table(
    'pin_tags', Base.metadata,
    Column('pin_id', Integer, ForeignKey('pins.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
)


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    avatar: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    pins = relationship('Pin', back_populates='author', foreign_keys='Pin.author_id')
    boards = relationship('Board', back_populates='user')
    followers_rel = relationship('Follow', back_populates='followed', foreign_keys='Follow.followed_id')
    following_rel = relationship('Follow', back_populates='follower', foreign_keys='Follow.follower_id')


class Board(Base):
    __tablename__ = 'boards'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cover_image: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    is_private: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user = relationship('User', back_populates='boards')
    pins = relationship('Pin', back_populates='board')


class Pin(Base):
    __tablename__ = 'pins'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    link_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    author_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    board_id: Mapped[Optional[int]] = mapped_column(ForeignKey('boards.id', ondelete='SET NULL'), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    author = relationship('User', back_populates='pins', foreign_keys=[author_id])
    board = relationship('Board', back_populates='pins')
    comments = relationship('Comment', back_populates='pin', cascade='all, delete-orphan')
    likes = relationship('Like', back_populates='pin', cascade='all, delete-orphan')
    tags = relationship('Tag', secondary=pin_tags, back_populates='pins')


class Tag(Base):
    __tablename__ = 'tags'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    pins = relationship('Pin', secondary=pin_tags, back_populates='tags')


class Comment(Base):
    __tablename__ = 'comments'

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    pin_id: Mapped[int] = mapped_column(ForeignKey('pins.id', ondelete='CASCADE'))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user = relationship('User')
    pin = relationship('Pin', back_populates='comments')


class Like(Base):
    __tablename__ = 'likes'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    pin_id: Mapped[int] = mapped_column(ForeignKey('pins.id', ondelete='CASCADE'))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user = relationship('User')
    pin = relationship('Pin', back_populates='likes')


class Follow(Base):
    __tablename__ = 'follows'

    id: Mapped[int] = mapped_column(primary_key=True)
    follower_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    followed_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    follower = relationship('User', back_populates='following_rel', foreign_keys=[follower_id])
    followed = relationship('User', back_populates='followers_rel', foreign_keys=[followed_id])


class Save(Base):
    __tablename__ = 'saves'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    pin_id: Mapped[int] = mapped_column(ForeignKey('pins.id', ondelete='CASCADE'))
    board_id: Mapped[Optional[int]] = mapped_column(ForeignKey('boards.id', ondelete='SET NULL'), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
