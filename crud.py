from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from auth import authenticate_user, create_access_token
from config import ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from passlib.hash import bcrypt_sha256
from starlette import status
from starlette.exceptions import HTTPException

from database import get_db, engine
from models import User
from schemas import UserCreate, Token, UserInDB

app = FastAPI()
session = Session(bind=engine)


@app.post('/user/register', response_model=UserCreate)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
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

