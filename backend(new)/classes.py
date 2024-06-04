from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, Field, ValidationError
from typing import Optional
import re

from config import *

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    surname = Column(String(50))
    birthday = Column(String(10))
    gender = Column(String(1))
    mail = Column(String(50))
    phone_num = Column(String(15))
    password = Column(String(250))
    token = Column(String(250))

class DisabledTokens(Base):
    __tablename__ = "disabledTokens"
    token = Column(String(150), primary_key=True)

# Определение схемы запроса регистрации
class RegistrationRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    surname: str = Field(..., min_length=2, max_length=50)
    birthday: str = Field(..., pattern=r'^\d{2}-\d{2}-\d{4}$')
    gender: str = Field(..., min_length=1, max_length=1)
    mail: str = Field(..., min_length=5, max_length=50)
    phone_num: Optional[str] = Field(None, min_length=0, max_length=15)
    password: str = Field(..., min_length=6, max_length=50)

class LoginRequest(BaseModel):
    email: str
    password: str

# Создание таблиц
Base.metadata.create_all(bind=create_engine(DATABASE_URL))