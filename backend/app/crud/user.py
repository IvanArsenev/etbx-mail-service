"""CRUD operations for the User model."""

from sqlalchemy.orm import Session
from app.db.models import User, DisabledTokens


def get_user_by_email(db: Session, email: str) -> User | None:
    """
    Retrieve a user by their email.

    Args:
        db (Session): SQLAlchemy session.
        email (str): Email to search for.

    Returns:
        Optional[User]: Matching user or None.
    """
    return db.query(User).filter(User.mail == email).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """
    Retrieve a user by their ID.

    Args:
        db (Session): SQLAlchemy session.
        user_id (int): User ID.

    Returns:
        Optional[User]: Matching user or None.
    """
    return db.query(User).filter(User.id == user_id).first()


def list_users(db: Session, skip: int = 0, limit: int = 10) -> list[User]:
    """
    Return a list of users with pagination.

    Args:
        db (Session): SQLAlchemy session.
        skip (int): Number of users to skip.
        limit (int): Number of users to return.

    Returns:
        List[User]: Paginated list of users.
    """
    return db.query(User).offset(skip).limit(limit).all()


def count_users(db: Session) -> int:
    """
    Count total number of users.

    Args:
        db (Session): SQLAlchemy session.

    Returns:
        int: Total user count.
    """
    return db.query(User).count()


def is_token_revoked(db: Session, token: str) -> bool:
    """
    Check whether a given token is revoked.

    Args:
        db (Session): SQLAlchemy session.
        token (str): JWT token.

    Returns:
        bool: True if revoked, False otherwise.
    """
    return db.query(DisabledTokens).filter(DisabledTokens.token == token).first() is not None


def revoke_token(db: Session, token: str) -> None:
    """
    Mark a token as revoked.

    Args:
        db (Session): SQLAlchemy session.
        token (str): JWT token to revoke.
    """
    db.add(DisabledTokens(token=token))
    db.commit()
