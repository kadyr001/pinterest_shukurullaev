from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
import os
from uuid import uuid4
from database.models import User
from api.auth import get_current_user

upload_router = APIRouter(prefix='/upload', tags=['Upload'])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media')
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_TYPES = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}


@upload_router.post('/')
async def upload_file(file: UploadFile = File(...), user: User = Depends(get_current_user)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail='Формат туура эмес. jpg, png, gif, webp гана')

    ext = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
    filename = f'{uuid4().hex}.{ext}'
    filepath = os.path.join(UPLOAD_DIR, filename)

    content = await file.read()
    with open(filepath, 'wb') as f:
        f.write(content)

    return {'filename': filename, 'url': f'/media/{filename}'}
