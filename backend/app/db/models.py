"""SQLAlchemy models for the application."""

from sqlalchemy import Column, String, Integer, Date, Boolean
from sqlalchemy.orm import relationship

from app.db.session import Base


class User(Base):
    """
    Represents a user in the system.

    Attributes:
        id (int): Primary key.
        name (str): First name of the user.
        surname (str): Last name of the user.
        birthday (date): Date of birth.
        gender (str): Gender identity.
        mail (str): Email address (used as login).
        phone_num (str): Optional phone number.
        password (str): Encrypted user password.
        avatar (str): Optional path to user's avatar image.
        token (str): JWT token issued to the user.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    birthday = Column(Date, nullable=False)
    gender = Column(String, nullable=False)
    mail = Column(String, unique=True, index=True, nullable=False)
    phone_num = Column(String, nullable=True)
    password = Column(String, nullable=False)
    avatar = Column(String, nullable=True)
    token = Column(String, nullable=False)


class DisabledTokens(Base):
    """
    Represents a disabled (revoked) token, used for logout or invalidation.

    Attributes:
        id (int): Primary key.
        token (str): The JWT token that has been invalidated.
    """
    __tablename__ = "disabled_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, nullable=False, unique=True)
