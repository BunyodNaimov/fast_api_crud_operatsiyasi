from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import UserCreate
import os
from fastapi_sqlalchemy import DBSessionMiddleware
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
app = FastAPI()

app.add_middleware(DBSessionMiddleware, db_url=os.environ["DATABASE_URL"])


