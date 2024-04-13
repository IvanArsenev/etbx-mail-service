from pydantic import BaseModel, Field, ValidationError
from typing import Optional


class RegistrationRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    surname: str = Field(..., min_length=2, max_length=50)
    birthday: str = Field(..., pattern=r'^\d{2}-\d{2}-\d{4}$')
    gender: str = Field(..., min_length=1, max_length=1)
    mail: str = Field(..., min_length=5, max_length=50)
    phone_num: Optional[str] = Field(None, min_length=0, max_length=15)
    password: str = Field(..., min_length=6, max_length=50)


class LoginRequest(BaseModel):
    mail: str = Field(..., min_length=5, max_length=100)
    password: str = Field(..., min_length=6, max_length=50)


class EditProfile(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    surname: Optional[str] = Field(None, min_length=2, max_length=50)
    birthday: Optional[str] = Field(None, pattern=r'^\d{2}-\d{2}-\d{4}$')
    gender: Optional[str] = Field(None, min_length=1, max_length=1)
    mail: Optional[str] = Field(None, min_length=5, max_length=50)
    phone_num: Optional[str] = Field(None, min_length=0, max_length=15)
    password: Optional[str] = Field(None, min_length=6, max_length=50)


class MailModel(BaseModel):
    theme: Optional[str] = Field(None, min_length=3, max_length=50)
    body: str = Field(..., min_length=5, max_length=5000)
    reciever: str = Field(..., min_length=5, max_length=50)