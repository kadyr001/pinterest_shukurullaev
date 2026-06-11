from sqladmin import Admin, ModelView
from database.db import engine
from database.models import User, Board, Pin, Tag, Comment, Like, Follow, Save


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.username, User.email, User.full_name, User.is_active, User.created_at]
    column_searchable_list = [User.username, User.email]
    form_excluded_columns = [User.hashed_password, User.pins, User.boards, User.followers_rel, User.following_rel]


class BoardAdmin(ModelView, model=Board):
    column_list = [Board.id, Board.title, Board.user_id, Board.is_private, Board.created_at]
    column_searchable_list = [Board.title]


class PinAdmin(ModelView, model=Pin):
    column_list = [Pin.id, Pin.title, Pin.author_id, Pin.board_id, Pin.created_at]
    column_searchable_list = [Pin.title]


class TagAdmin(ModelView, model=Tag):
    column_list = [Tag.id, Tag.name]
    column_searchable_list = [Tag.name]


class CommentAdmin(ModelView, model=Comment):
    column_list = [Comment.id, Comment.text, Comment.user_id, Comment.pin_id, Comment.created_at]


class LikeAdmin(ModelView, model=Like):
    column_list = [Like.id, Like.user_id, Like.pin_id, Like.created_at]


class FollowAdmin(ModelView, model=Follow):
    column_list = [Follow.id, Follow.follower_id, Follow.followed_id, Follow.created_at]


class SaveAdmin(ModelView, model=Save):
    column_list = [Save.id, Save.user_id, Save.pin_id, Save.board_id, Save.created_at]


def setup_admin(app):
    admin = Admin(app, engine)
    admin.add_view(UserAdmin)
    admin.add_view(BoardAdmin)
    admin.add_view(PinAdmin)
    admin.add_view(TagAdmin)
    admin.add_view(CommentAdmin)
    admin.add_view(LikeAdmin)
    admin.add_view(FollowAdmin)
    admin.add_view(SaveAdmin)
    return admin
