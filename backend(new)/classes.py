from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, Field
from typing import Optional, List

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
    avatar = Column(String(50))

class DisabledTokens(Base):
    __tablename__ = "disabledTokens"
    token = Column(String(150), primary_key=True)

class UnhashedPasswords(Base):
    __tablename__ = "pwds"
    id = Column(Integer, primary_key=True, index=True)
    password = Column(String(100))

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

class UsersResponse(BaseModel):
    id: int
    Имя: str
    Фамилия: str
    Дата_рождения: str
    Пол: str
    Логин: str
    Номер_телефона: Optional[str]
    Аватар: Optional[str]

class PaginatedUsersResponse(BaseModel):
    total_users: int
    users: List[UsersResponse]

class EditProfile(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    surname: Optional[str] = Field(None, min_length=2, max_length=50)
    birthday: Optional[str] = Field(None, pattern=r'^\d{2}-\d{2}-\d{4}$')
    gender: Optional[str] = Field(None, min_length=1, max_length=1)
    mail: Optional[str] = Field(None, min_length=5, max_length=50)
    phone_num: Optional[str] = Field(None, min_length=0, max_length=15)
    password: Optional[str] = Field(None, min_length=6, max_length=50)

Base.metadata.create_all(bind=create_engine(DATABASE_URL))