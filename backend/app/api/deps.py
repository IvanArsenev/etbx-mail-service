"""FastAPI dependency functions for authentication and user context."""

from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.security import decode_access_token
from app.db.models import User, DisabledTokens
from app.db.session import SessionLocal
from app.core.config import API_KEY

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_user_by_email(email: str) -> User | None:
    """
    Retrieve a user by email from the database.

    Args:
        email (str): Email address to search.

    Returns:
        Optional[User]: User instance or None.
    """
    db = SessionLocal()
    try:
        return db.query(User).filter(User.mail == email).first()
    finally:
        db.close()


def is_token_revoked(token: str) -> bool:
    """
    Check if a token has been marked as revoked.

    Args:
        token (str): JWT token.

    Returns:
        bool: True if the token is revoked, False otherwise.
    """
    db = SessionLocal()
    try:
        return db.query(DisabledTokens).filter(DisabledTokens.token == token).first() is not None
    finally:
        db.close()


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)]
) -> User:
    """
    FastAPI dependency that returns the currently authenticated user.

    Args:
        token (str): JWT token from Authorization header.

    Raises:
        HTTPException: If credentials are invalid or token is revoked.

    Returns:
        User: The authenticated user object.
    """
    payload = decode_access_token(token)
    email = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing 'sub' in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_user_by_email(email)
    if user is None or is_token_revoked(user.token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
