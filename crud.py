from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, APIKeyHeader, HTTPBearer
from sqlalchemy import exists

from auth import authenticate_user, create_access_token
from config import ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from passlib.hash import bcrypt_sha256
from starlette import status
from starlette.exceptions import HTTPException

from database import get_db, engine
from models import User
from schemas import UserCreate, Token, UserInDB, UserUpdate
from utils import get_current_user

app = FastAPI()
session = Session(bind=engine)

api_key_header = APIKeyHeader(name='Authorization')
security = HTTPBearer()


@app.get('/')
def main(authorization: str = Depends(security)):
    return authorization.credentials


@app.post('/user/register', response_model=UserCreate)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_username = db.query(User).filter_by(username=user.username).first()
    if db_username is not None or db_username:
        raise HTTPException(status_code=400, detail="User with the username already exists")
    db_user = User(username=user.username, password=bcrypt_sha256.hash(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post('/users/login/', response_model=Token)
def login_for_access_token(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter_by(username=user.username).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not bcrypt_sha256.verify(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=60)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.put("/user/update", response_model=UserUpdate)
def update_user(user_update: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_user = db.query(User).filter_by(id=current_user.id).first()
    print(db_user)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update user data
    db_user.username = user_update.username
    if user_update.password:
        db_user.password = bcrypt_sha256.hash(user_update.password)

    db.commit()
    db.refresh(db_user)
    return db_user
