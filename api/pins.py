from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from database.db import get_db
from database.models import Pin, Tag, Like, Save, Comment, Board
from database.shema import PinInputShema, PinOutShema
from api.auth import get_current_user

pin_router = APIRouter(prefix='/pins', tags=['Pins'])


@pin_router.get('/', response_model=list[PinOutShema])
async def get_pins(db: Session = Depends(get_db)):
    pins = db.query(Pin).order_by(Pin.created_at.desc()).all()
    result = []
    for pin in pins:
        pin_data = PinOutShema.model_validate(pin)
        pin_data.likes_count = db.query(func.count(Like.id)).filter(Like.pin_id == pin.id).scalar() or 0
        pin_data.comments_count = db.query(func.count(Comment.id)).filter(Comment.pin_id == pin.id).scalar() or 0
        pin_data.saves_count = db.query(func.count(Save.id)).filter(Save.pin_id == pin.id).scalar() or 0
        result.append(pin_data)
    return result


@pin_router.get('/{pin_id}/', response_model=PinOutShema)
async def get_pin(pin_id: int, db: Session = Depends(get_db)):
    pin = db.query(Pin).filter(Pin.id == pin_id).first()
    if not pin:
        raise HTTPException(status_code=404, detail='Пин табылган жок')
    pin_data = PinOutShema.model_validate(pin)
    pin_data.likes_count = db.query(func.count(Like.id)).filter(Like.pin_id == pin.id).scalar() or 0
    pin_data.comments_count = db.query(func.count(Comment.id)).filter(Comment.pin_id == pin.id).scalar() or 0
    pin_data.saves_count = db.query(func.count(Save.id)).filter(Save.pin_id == pin.id).scalar() or 0
    return pin_data


@pin_router.post('/', response_model=PinOutShema)
async def create_pin(data: PinInputShema, user=Depends(get_current_user), db: Session = Depends(get_db)):
    if data.board_id:
        board = db.query(Board).filter(Board.id == data.board_id).first()
        if not board:
            raise HTTPException(status_code=404, detail='Доска табылган жок')

    pin = Pin(
        title=data.title,
        description=data.description,
        image_url=data.image_url,
        link_url=data.link_url,
        author_id=user.id,
        board_id=data.board_id,
    )
    db.add(pin)
    db.flush()

    if data.tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(data.tag_ids)).all()
        pin.tags = tags

    db.commit()
    db.refresh(pin)
    pin_data = PinOutShema.model_validate(pin)
    pin_data.likes_count = 0
    pin_data.comments_count = 0
    pin_data.saves_count = 0
    return pin_data


@pin_router.put('/{pin_id}/', response_model=PinOutShema)
async def update_pin(pin_id: int, data: PinInputShema, user=Depends(get_current_user), db: Session = Depends(get_db)):
    pin = db.query(Pin).filter(Pin.id == pin_id).first()
    if not pin:
        raise HTTPException(status_code=404, detail='Пин табылган жок')
    if pin.author_id != user.id:
        raise HTTPException(status_code=403, detail='Сиздин пининиз эмес')

    for key, value in data.model_dump(exclude={'tag_ids'}).items():
        setattr(pin, key, value)

    if data.tag_ids is not None:
        tags = db.query(Tag).filter(Tag.id.in_(data.tag_ids)).all()
        pin.tags = tags

    db.commit()
    db.refresh(pin)
    return await get_pin(pin_id, db)


@pin_router.delete('/{pin_id}/')
async def delete_pin(pin_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    pin = db.query(Pin).filter(Pin.id == pin_id).first()
    if not pin:
        raise HTTPException(status_code=404, detail='Пин табылган жок')
    if pin.author_id != user.id:
        raise HTTPException(status_code=403, detail='Сиздин пининиз эмес')
    db.delete(pin)
    db.commit()
    return {'message': 'Пин очурулду'}


@pin_router.post('/{pin_id}/like/')
async def like_pin(pin_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    pin = db.query(Pin).filter(Pin.id == pin_id).first()
    if not pin:
        raise HTTPException(status_code=404, detail='Пин табылган жок')
    existing = db.query(Like).filter(Like.user_id == user.id, Like.pin_id == pin_id).first()
    if existing:
        db.delete(existing)
        db.commit()
        return {'message': 'Лайк алынды', 'liked': False}
    db.add(Like(user_id=user.id, pin_id=pin_id))
    db.commit()
    return {'message': 'Лайк койду', 'liked': True}


@pin_router.post('/{pin_id}/save/')
async def save_pin(pin_id: int, board_id: int = None, user=Depends(get_current_user), db: Session = Depends(get_db)):
    pin = db.query(Pin).filter(Pin.id == pin_id).first()
    if not pin:
        raise HTTPException(status_code=404, detail='Пин табылган жок')
    existing = db.query(Save).filter(Save.user_id == user.id, Save.pin_id == pin_id).first()
    if existing:
        db.delete(existing)
        db.commit()
        return {'message': 'Сохранение алынды', 'saved': False}
    db.add(Save(user_id=user.id, pin_id=pin_id, board_id=board_id))
    db.commit()
    return {'message': 'Сохранено', 'saved': True}


