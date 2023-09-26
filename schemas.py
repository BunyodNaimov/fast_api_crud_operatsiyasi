from fastapi import FastAPI
from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str


class UserUpdate(BaseModel):
    username: str
    password: str
    is_active: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserInDB(UserCreate):
    hashed_password: str


class TokenData(BaseModel):
    username: str | None = None
