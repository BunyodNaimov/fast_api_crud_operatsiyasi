from sqlalchemy import MetaData, Column, Integer, String, Table, Boolean

from database import Base

metadata = MetaData()


class User(Base):
    __tablename__ = "users"
    metadata = metadata
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
