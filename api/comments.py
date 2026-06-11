from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.db import get_db
from database.models import Comment, Pin
from database.shema import CommentInputShema, CommentOutShema
from api.auth import get_current_user

comment_router = APIRouter(prefix='/comments', tags=['Comments'])


@comment_router.get('/pin/{pin_id}/', response_model=list[CommentOutShema])
async def get_pin_comments(pin_id: int, db: Session = Depends(get_db)):
    comments = db.query(Comment).filter(Comment.pin_id == pin_id).order_by(Comment.created_at.desc()).all()
    return comments


@comment_router.post('/', response_model=CommentOutShema)
async def create_comment(data: CommentInputShema, user=Depends(get_current_user), db: Session = Depends(get_db)):
    pin = db.query(Pin).filter(Pin.id == data.pin_id).first()
    if not pin:
        raise HTTPException(status_code=404, detail='Пин табылган жок')
    comment = Comment(text=data.text, user_id=user.id, pin_id=data.pin_id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@comment_router.delete('/{comment_id}/')
async def delete_comment(comment_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail='Комментарий табылган жок')
    if comment.user_id != user.id:
        raise HTTPException(status_code=403, detail='Сиздин комментарий эмес')
    db.delete(comment)
    db.commit()
    return {'message': 'Комментарий очурулду'}
