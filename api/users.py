from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from database.db import get_db
from database.models import User, Follow, Pin, Like, Save, Comment
from database.shema import UserOutShema, PinOutShema
from api.auth import get_current_user

user_router = APIRouter(prefix='/users', tags=['Users'])


@user_router.get('/{user_id}/', response_model=UserOutShema)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='Колдонуучу табылган жок')
    return user


@user_router.get('/{user_id}/pins/', response_model=list[PinOutShema])
async def get_user_pins(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='Колдонуучу табылган жок')
    pins = db.query(Pin).filter(Pin.author_id == user_id).order_by(Pin.created_at.desc()).all()
    result = []
    for pin in pins:
        pin_data = PinOutShema.model_validate(pin)
        pin_data.likes_count = db.query(func.count(Like.id)).filter(Like.pin_id == pin.id).scalar() or 0
        pin_data.comments_count = db.query(func.count(Comment.id)).filter(Comment.pin_id == pin.id).scalar() or 0
        pin_data.saves_count = db.query(func.count(Save.id)).filter(Save.pin_id == pin.id).scalar() or 0
        result.append(pin_data)
    return result


@user_router.get('/{user_id}/saves/', response_model=list[PinOutShema])
async def get_user_saves(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='Колдонуучу табылган жок')
    saved_pins = db.query(Pin).join(Save, Save.pin_id == Pin.id).filter(Save.user_id == user_id).all()
    result = []
    for pin in saved_pins:
        pin_data = PinOutShema.model_validate(pin)
        pin_data.likes_count = db.query(func.count(Like.id)).filter(Like.pin_id == pin.id).scalar() or 0
        pin_data.comments_count = db.query(func.count(Comment.id)).filter(Comment.pin_id == pin.id).scalar() or 0
        pin_data.saves_count = db.query(func.count(Save.id)).filter(Save.pin_id == pin.id).scalar() or 0
        result.append(pin_data)
    return result


@user_router.post('/{user_id}/follow/')
async def follow_user(user_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    if user_id == user.id:
        raise HTTPException(status_code=400, detail='Озуноз эре албайсын')
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail='Колдонуучу табылган жок')
    existing = db.query(Follow).filter(Follow.follower_id == user.id, Follow.followed_id == user_id).first()
    if existing:
        db.delete(existing)
        db.commit()
        return {'message': 'Подписка алынды', 'following': False}
    db.add(Follow(follower_id=user.id, followed_id=user_id))
    db.commit()
    return {'message': 'Подписка кошулду', 'following': True}


@user_router.get('/{user_id}/followers/')
async def get_followers(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='Колдонуучу табылган жок')
    followers = db.query(Follow).filter(Follow.followed_id == user_id).all()
    result = []
    for f in followers:
        follower_user = db.query(User).filter(User.id == f.follower_id).first()
        if follower_user:
            result.append(UserOutShema.model_validate(follower_user))
    return result


@user_router.get('/{user_id}/following/')
async def get_following(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='Колдонуучу табылган жок')
    following = db.query(Follow).filter(Follow.follower_id == user_id).all()
    result = []
    for f in following:
        followed_user = db.query(User).filter(User.id == f.followed_id).first()
        if followed_user:
            result.append(UserOutShema.model_validate(followed_user))
    return result

