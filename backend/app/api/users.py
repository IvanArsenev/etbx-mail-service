"""User profile and listing endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.db.models import User
from app.db.session import SessionLocal
from app.schemas.user import UsersResponse, PaginatedUsersResponse
from app.crud import user as crud_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UsersResponse)
def read_current_user(current_user: User = Depends(get_current_user)) -> UsersResponse:
    """
    Get the currently authenticated user's profile.

    Args:
        current_user (User): Current authenticated user.

    Returns:
        UsersResponse: User profile information.
    """
    return UsersResponse(
        id=current_user.id,
        name=current_user.name,
        second_name=current_user.surname,
        birth_date=current_user.birthday,
        gender=current_user.gender,
        email=current_user.mail,
        phone_num=current_user.phone_num,
        avatar=current_user.avatar
    )


@router.get("/{user_id}", response_model=UsersResponse)
def read_user_by_id(user_id: int, db: Session = Depends(get_db)) -> UsersResponse:
    """
    Get a user by their unique ID.

    Args:
        user_id (int): The user's ID.
        db: session of connecting database.

    Raises:
        HTTPException: If user is not found.

    Returns:
        UsersResponse: The user's profile.
    """
    user = crud_user.get_user_by_id(db, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    return UsersResponse(
        id=user.id,
        name=user.name,
        second_name=user.surname,
        birth_date=user.birthday,
        gender=user.gender,
        email=user.mail,
        phone_num=user.phone_num,
        avatar=user.avatar
    )


@router.get("/", response_model=PaginatedUsersResponse)
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    db: Session = Depends(get_db)
) -> PaginatedUsersResponse:
    """
    Get a paginated list of users.

    Args:
        page (int): Page number (default 1).
        page_size (int): Users per page (default 10).
        db: session of connecting database.

    Returns:
        PaginatedUsersResponse: Total count and list of users.
    """
    total = crud_user.count_users(db)
    total_users = crud_user.list_users(db, skip=(page - 1) * page_size, limit=page_size)
    return PaginatedUsersResponse(
        total_users=total_users,
        users=[
            UsersResponse(
                id=user.id,
                name=user.name,
                second_name=user.surname,
                birth_date=user.birthday,
                gender=user.gender,
                email=user.mail,
                phone_num=user.phone_num,
                avatar=user.avatar
            )
            for user in total
        ]
    )
