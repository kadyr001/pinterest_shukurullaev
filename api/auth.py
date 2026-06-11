from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database.db import get_db
from database.models import User
from database.shema import UserRegisterShema, UserLoginShema, UserOutShema, UserUpdateShema
from passlib.context import CryptContext
from datetime import timedelta, datetime
from jose import jwt
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_LIFETIME, REFRESH_TOKEN_LIFETIME

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_shema = OAuth2PasswordBearer(tokenUrl="/auth/login/")

auth_router = APIRouter(prefix='/auth', tags=['Auth'])


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_LIFETIME)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_LIFETIME)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_shema), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get('sub')
        if user_id is None:
            raise HTTPException(status_code=401, detail='Токен туура эмес')
    except:
        raise HTTPException(status_code=401, detail='Токен туура эмес')
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail='Колдонуучу табылган жок')
    return user


@auth_router.post('/register/', response_model=dict)
async def register(data: UserRegisterShema, db: Session = Depends(get_db)):
    user_db = db.query(User).filter((User.username == data.username) | (User.email == data.email)).first()
    if user_db:
        raise HTTPException(status_code=400, detail='Мындай username же email бар экен')

    user = User(
        username=data.username,
        email=data.email,
        hashed_password=get_password_hash(data.password),
        full_name=data.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {'message': 'Сиз регистрация болдунуз', 'user_id': user.id}


@auth_router.post('/login/', response_model=dict)
async def login(data: UserLoginShema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail='Сиз жазган маалымат туура эмес')

    access_token = create_access_token({'sub': user.id})
    refresh_token = create_refresh_token({'sub': user.id})
    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'Bearer', 'user_id': user.id}


@auth_router.get('/me/', response_model=UserOutShema)
async def get_me(user: User = Depends(get_current_user)):
    return user


@auth_router.put('/me/', response_model=UserOutShema)
async def update_me(data: UserUpdateShema, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user
