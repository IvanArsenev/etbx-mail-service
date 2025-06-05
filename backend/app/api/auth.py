"""Authentication routes: register, login, logout."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import requests
import imaplib

from app.schemas.user import RegistrationRequest, LoginRequest
from app.db.models import User, DisabledTokens
from app.crud import user as crud_user
from app.core.security import encrypt_password, decrypt_password, create_access_token
from app.api.deps import get_current_user, is_token_revoked, get_db
from app.core.config import API_KEY

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
def register_user(request: RegistrationRequest, db: Session = Depends(get_db)) -> dict:
    """
    Register a new user by validating and storing their data locally and remotely.

    Args:
        request (RegistrationRequest): Registration form data.
        db: session of connecting database.

    Raises:
        HTTPException: If user already exists or remote registration fails.

    Returns:
        dict: JWT token.
    """
    email_full = f"{request.mail}@pmc-python.ru"

    if crud_user.get_user_by_email(db, email_full):
        db.close()
        raise HTTPException(status_code=400, detail="User already registered.")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.get(f"https://pmc-python.ru/api/v1/user/{email_full}", headers=headers)
    if response.status_code == 200:
        db.close()
        raise HTTPException(status_code=400, detail="User already exists in external system.")

    encrypted_password = encrypt_password(request.password)
    token = create_access_token({"sub": email_full})

    new_user = User(
        name=request.name,
        surname=request.surname,
        birthday=request.birthday,
        gender=request.gender,
        mail=email_full,
        phone_num=request.phone_num,
        password=encrypted_password,
        token=token
    )

    external_data = {
        "email": email_full,
        "raw_password": request.password,
        "displayed_name": f"{request.name} {request.surname}"
    }

    response = requests.post("https://pmc-python.ru/api/v1/user", json=external_data, headers=headers)
    if response.status_code not in (200, 201):
        db.close()
        raise HTTPException(status_code=502, detail=f"External registration failed: {response.text}")

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()

    return {"token": new_user.token}


@router.post("/login")
def login_user(request: LoginRequest, db: Session = Depends(get_db)) -> dict:
    """
    Log in a user and return a JWT token.

    Args:
        request (LoginRequest): Login form data.
        db: session of connecting database.

    Raises:
        HTTPException: On invalid credentials.

    Returns:
        dict: JWT token.
    """
    domain = request.email.split("@")[-1]

    if domain == "pmc-python.ru":
        user = crud_user.get_user_by_email(db, request.email)
        if user is None or decrypt_password(user.password) != request.password:
            db.close()
            raise HTTPException(status_code=401, detail="Invalid email or password.")

        if crud_user.is_token_revoked(db, user.token):
            db.query(DisabledTokens).filter(DisabledTokens.token == user.token).delete()
            db.commit()

        db.close()
        return {"token": user.token}

    try:
        mail = imaplib.IMAP4_SSL("imap.mail.ru", 993)
        mail.login(request.email, request.password)
        mail.logout()
    except imaplib.IMAP4.error:
        return {"message": "Login failed. Invalid credentials."}

    user = crud_user.get_user_by_email(db, request.email)
    if user:
        db.close()
        return {"token": user.token}

    encrypted_password = encrypt_password(request.password)
    token = create_access_token({"sub": request.email})

    user = User(
        name="Imported",
        surname="User",
        birthday="2000-01-01",
        gender="unknown",
        mail=request.email,
        password=encrypted_password,
        token=token
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()

    return {"token": user.token}


@router.post("/logout")
def logout_user(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict:
    """
    Logout the current user by revoking their token.

    Args:
        current_user (User): Current authenticated user.
        db: session of connecting database.

    Returns:
        dict: Success message.
    """
    if crud_user.is_token_revoked(db, current_user.token):
        return {"message": "Already logged out."}
    crud_user.revoke_token(db, current_user.token)
    return {"message": "Successfully logged out."}
