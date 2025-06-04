"""Security utilities for password encryption and JWT token management."""

import jwt
from cryptography.fernet import Fernet
from fastapi import HTTPException, status
from typing import Any, Dict

from app.core.config import SECRET_KEY, ALGORITHM, FORNET_KEY

cipher_suite = Fernet(FORNET_KEY)


def encrypt_password(password: str) -> str:
    """
    Encrypt a plaintext password using Fernet symmetric encryption.

    Args:
        password (str): Plaintext password to encrypt.

    Returns:
        str: Encrypted password as a base64-encoded string.
    """
    return cipher_suite.encrypt(password.encode()).decode()


def decrypt_password(encrypted_password: str) -> str:
    """
    Decrypt an encrypted password string using Fernet.

    Args:
        encrypted_password (str): Base64-encoded encrypted password.

    Returns:
        str: Decrypted plaintext password.
    """
    return cipher_suite.decrypt(encrypted_password.encode()).decode()


def create_access_token(data: Dict[str, Any]) -> str:
    """
    Generate a JWT access token with provided payload.

    Args:
        data (Dict[str, Any]): Data to encode into the token.

    Returns:
        str: Encoded JWT token string.
    """
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decode a JWT token and validate it.

    Args:
        token (str): JWT token string.

    Raises:
        HTTPException: If the token is invalid or cannot be decoded.

    Returns:
        Dict[str, Any]: Decoded payload.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
