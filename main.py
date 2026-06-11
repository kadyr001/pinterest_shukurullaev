from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

from database.db import engine, Base
from api.auth import auth_router
from api.pins import pin_router
from api.boards import board_router
from api.users import user_router
from api.feed import feed_router
from api.comments import comment_router
from api.upload import upload_router
from admin.admin import setup_admin

app = FastAPI(
    title='Pinterest KLON',
    description='Pinterest',
    version='1.0.0',
)


@app.on_event('startup')
async def create_tables():
    Base.metadata.create_all(bind=engine)


media_dir = os.path.join(os.path.dirname(__file__), 'media')
os.makedirs(media_dir, exist_ok=True)
app.mount('/media', StaticFiles(directory=media_dir), name='media')

app.include_router(auth_router)
app.include_router(pin_router)
app.include_router(board_router)
app.include_router(user_router)
app.include_router(feed_router)
app.include_router(comment_router)
app.include_router(upload_router)

setup_admin(app)


@app.get('/')
async def root():
    return {'message': 'Pinterest KLON'}
