"""FastAPI dependency functions for authentication and user context."""

from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import SessionLocal
from app.crud import user as crud_user
from app.db.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_db() -> Session:
    """
    Dependency to provide a DB session per request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)]
) -> User:
    """
    Dependency to get the current authenticated user.
    """
    payload = decode_access_token(token)
    email = payload.get("sub")
    if email is None:
        raise HTTPException(status_code=401, detail="Missing 'sub' in token")

    user = crud_user.get_user_by_email(db, email)
    if user is None or crud_user.is_token_revoked(db, user.token):
        raise HTTPException(status_code=401, detail="Invalid or revoked credentials")

    return user
