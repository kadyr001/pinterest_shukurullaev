from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from database.db import get_db
from database.models import Pin, Like, Comment, Save, Tag
from database.shema import PinOutShema, CommentInputShema, CommentOutShema

feed_router = APIRouter(prefix='/feed', tags=['Feed'])


@feed_router.get('/', response_model=list[PinOutShema])
async def get_feed(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    pins = db.query(Pin).order_by(Pin.created_at.desc()).offset(skip).limit(limit).all()
    result = []
    for pin in pins:
        pin_data = PinOutShema.model_validate(pin)
        pin_data.likes_count = db.query(func.count(Like.id)).filter(Like.pin_id == pin.id).scalar() or 0
        pin_data.comments_count = db.query(func.count(Comment.id)).filter(Comment.pin_id == pin.id).scalar() or 0
        pin_data.saves_count = db.query(func.count(Save.id)).filter(Save.pin_id == pin.id).scalar() or 0
        result.append(pin_data)
    return result


@feed_router.get('/search/', response_model=list[PinOutShema])
async def search_pins(q: str = Query(min_length=1), db: Session = Depends(get_db)):
    pins = db.query(Pin).filter(Pin.title.ilike(f'%{q}%')).order_by(Pin.created_at.desc()).all()
    result = []
    for pin in pins:
        pin_data = PinOutShema.model_validate(pin)
        pin_data.likes_count = db.query(func.count(Like.id)).filter(Like.pin_id == pin.id).scalar() or 0
        pin_data.comments_count = db.query(func.count(Comment.id)).filter(Comment.pin_id == pin.id).scalar() or 0
        pin_data.saves_count = db.query(func.count(Save.id)).filter(Save.pin_id == pin.id).scalar() or 0
        result.append(pin_data)
    return result


@feed_router.get('/tags/{tag_name}/', response_model=list[PinOutShema])
async def get_pins_by_tag(tag_name: str, db: Session = Depends(get_db)):
    tag = db.query(Tag).filter(Tag.name == tag_name).first()
    if not tag:
        raise HTTPException(status_code=404, detail='Тег табылган жок')
    pins = tag.pins
    result = []
    for pin in pins:
        pin_data = PinOutShema.model_validate(pin)
        pin_data.likes_count = db.query(func.count(Like.id)).filter(Like.pin_id == pin.id).scalar() or 0
        pin_data.comments_count = db.query(func.count(Comment.id)).filter(Comment.pin_id == pin.id).scalar() or 0
        pin_data.saves_count = db.query(func.count(Save.id)).filter(Save.pin_id == pin.id).scalar() or 0
        result.append(pin_data)
    return result


@feed_router.get('/trending/', response_model=list[PinOutShema])
async def get_trending_pins(limit: int = 20, db: Session = Depends(get_db)):
    pins = db.query(
        Pin,
        func.count(Like.id).label('likes_count')
    ).outerjoin(Like).group_by(Pin.id).order_by(desc('likes_count')).limit(limit).all()
    result = []
    for pin, _ in pins:
        pin_data = PinOutShema.model_validate(pin)
        pin_data.likes_count = db.query(func.count(Like.id)).filter(Like.pin_id == pin.id).scalar() or 0
        pin_data.comments_count = db.query(func.count(Comment.id)).filter(Comment.pin_id == pin.id).scalar() or 0
        pin_data.saves_count = db.query(func.count(Save.id)).filter(Save.pin_id == pin.id).scalar() or 0
        result.append(pin_data)
    return result


