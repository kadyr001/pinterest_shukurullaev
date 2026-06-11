from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.db import get_db
from database.models import Board, Pin, User
from database.shema import BoardInputShema, BoardOutShema
from api.auth import get_current_user

board_router = APIRouter(prefix='/boards', tags=['Boards'])


@board_router.get('/', response_model=list[BoardOutShema])
async def get_boards(db: Session = Depends(get_db)):
    boards = db.query(Board).filter(Board.is_private == False).order_by(Board.created_at.desc()).all()
    result = []
    for b in boards:
        data = BoardOutShema.model_validate(b)
        data.pin_count = db.query(Pin).filter(Pin.board_id == b.id).count()
        result.append(data)
    return result


@board_router.get('/{board_id}/', response_model=BoardOutShema)
async def get_board(board_id: int, db: Session = Depends(get_db)):
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail='Доска табылган жок')
    data = BoardOutShema.model_validate(board)
    data.pin_count = db.query(Pin).filter(Pin.board_id == board.id).count()
    return data


@board_router.post('/', response_model=BoardOutShema)
async def create_board(data: BoardInputShema, user=Depends(get_current_user), db: Session = Depends(get_db)):
    board = Board(
        title=data.title,
        description=data.description,
        cover_image=data.cover_image,
        user_id=user.id,
        is_private=data.is_private,
    )
    db.add(board)
    db.commit()
    db.refresh(board)
    result = BoardOutShema.model_validate(board)
    result.pin_count = 0
    return result


@board_router.put('/{board_id}/', response_model=BoardOutShema)
async def update_board(board_id: int, data: BoardInputShema, user=Depends(get_current_user), db: Session = Depends(get_db)):
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail='Доска табылган жок')
    if board.user_id != user.id:
        raise HTTPException(status_code=403, detail='Сиздин досканыз эмес')
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(board, key, value)
    db.commit()
    db.refresh(board)
    return await get_board(board_id, db)


@board_router.delete('/{board_id}/')
async def delete_board(board_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail='Доска табылган жок')
    if board.user_id != user.id:
        raise HTTPException(status_code=403, detail='Сиздин досканыз эмес')
    db.delete(board)
    db.commit()
    return {'message': 'Доска очурулду'}


@board_router.get('/{board_id}/pins/')
async def get_board_pins(board_id: int, db: Session = Depends(get_db)):
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail='Доска табылган жок')
    pins = db.query(Pin).filter(Pin.board_id == board_id).order_by(Pin.created_at.desc()).all()
    return pins


@board_router.get('/user/{user_id}/')
async def get_user_boards(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='Колдонуучу табылган жок')
    boards = db.query(Board).filter(Board.user_id == user_id, Board.is_private == False).all()
    result = []
    for b in boards:
        data = BoardOutShema.model_validate(b)
        data.pin_count = db.query(Pin).filter(Pin.board_id == b.id).count()
        result.append(data)
    return result
