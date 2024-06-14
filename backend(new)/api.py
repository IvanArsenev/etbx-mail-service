import uvicorn, jwt
from fastapi import Depends, status, FastAPI, HTTPException, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from typing import Optional, List
import re
import requests
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import *
from classes import *
from passlib.context import CryptContext
from datetime import datetime

# Инициализация приложения и базы данных
app = FastAPI()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Создание движка и сессии для работы с базой данных
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Функция для получения текущего пользователя по токену
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = get_user_by_email(email=email)
    if user is None:
        raise credentials_exception
    return user

# Функция для получения пользователя по email
def get_user_by_email(email):
    return SessionLocal().query(User).filter(User.mail == email).first()

@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    date_obj = datetime.strptime(current_user.birthday, "%d-%m-%Y")
    formatted_date_str = date_obj.strftime("%d.%m.%Y")
    user = {
        "id": current_user.id,
        "Имя": current_user.name,
        "Фамилия": current_user.surname,
        "Дата рождения": formatted_date_str,
        "Пол": current_user.gender,
        "Логин": current_user.mail,
        "Аватар": current_user.avatar,
        "token": current_user.token
    }
    return user

@app.get("/users", response_model=PaginatedUsersResponse)
async def get_users(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1)):
    db = SessionLocal()
    total_users = db.query(User).count()
    users = db.query(User).offset((page - 1) * page_size).limit(page_size).all()

    formatted_users = []
    for user in users:
        date_obj = datetime.strptime(user.birthday, "%d-%m-%Y")
        formatted_date_str = date_obj.strftime("%d.%m.%Y")
        formatted_users.append(UsersResponse(
            id=user.id,
            Имя=user.name,
            Фамилия=user.surname,
            Дата_рождения=formatted_date_str,
            Пол=user.gender,
            Логин=user.mail,
            Номер_телефона=user.phone_num if user.phone_num else "Отсутствует",
            Аватар=user.avatar
        ))

    return {
        "total_users": total_users,
        "users": formatted_users
    }

@app.post("/register")
async def register_user(registration_request: RegistrationRequest):
    db = SessionLocal()
    
    new_user = User(
        name=registration_request.name,
        surname=registration_request.surname,
        birthday=registration_request.birthday,
        gender=registration_request.gender,
        mail=f'{registration_request.mail}'+'@pmc-python.ru',
        phone_num=registration_request.phone_num,
        password=get_password_hash(registration_request.password),
        token=create_access_token(data={"sub": registration_request.mail})
    )
    
    external_api_data = {
        "email": str(registration_request.mail)+'@pmc-python.ru',
        "raw_password": registration_request.password,
        "displayed_name": f"{registration_request.name} {registration_request.surname}"
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.post("https://pmc-python.ru/api/v1/user", json=external_api_data, headers=headers)

    if response.status_code != 201 and response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Registration failed on external server.")
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}

@app.post("/login")
async def login_for_access_token(form_data: LoginRequest):
    user = get_user_by_email(form_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильный логин или пароль!",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"Token": user.token}




uvicorn.run(app, host=run_host, port=run_port)