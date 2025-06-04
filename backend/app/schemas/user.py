"""Pydantic schemas for user-related data."""

from typing import Optional, List
from datetime import date
from pydantic import BaseModel, EmailStr, Field


class RegistrationRequest(BaseModel):
    """
    Schema for user registration request.
    """
    name: str = Field(..., example="John")
    surname: str = Field(..., example="Doe")
    birthday: date = Field(..., example="2000-01-01")
    gender: str = Field(..., example="male")
    mail: str = Field(..., example="johndoe")
    phone_num: Optional[str] = Field(None, example="+123456789")
    password: str = Field(..., example="StrongP@ssw0rd")


class LoginRequest(BaseModel):
    """
    Schema for user login request.
    """
    email: EmailStr = Field(..., example="johndoe@pmc-python.ru")
    password: str = Field(..., example="StrongP@ssw0rd")


class EditProfile(BaseModel):
    """
    Schema for profile update.
    """
    name: Optional[str] = None
    surname: Optional[str] = None
    birthday: Optional[date] = None
    gender: Optional[str] = None
    phone_num: Optional[str] = None
    password: Optional[str] = None


class UsersResponse(BaseModel):
    """
    Response schema for a user entry.
    """
    id: int
    name: str
    second_name: str
    birth_date: date
    gender: str
    email: EmailStr
    phone_num: Optional[str]
    avatar: Optional[str]

    class Config:
        orm_mode = True


class PaginatedUsersResponse(BaseModel):
    """
    Paginated list of users with total count.
    """
    total_users: int
    users: List[UsersResponse]
