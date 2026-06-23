"""
src/auth.py
JWT-based authentication utilities and FastAPI dependency functions.

Dependencies added to requirements.txt:
    python-jose[cryptography]>=3.3
    bcrypt>=4.0
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from .config import JWT_ALGORITHM, JWT_EXPIRE_MINUTES, JWT_SECRET_KEY

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------
_bearer_scheme = HTTPBearer()


def _password_bytes(plain_password: str) -> bytes:
    """bcrypt accepts at most 72 bytes; truncate explicitly for backend compatibility."""
    return plain_password.encode("utf-8")[:72]


def hash_password(plain_password: str) -> str:
    """Return a bcrypt hash of the plaintext password."""
    return bcrypt.hashpw(_password_bytes(plain_password), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True if *plain_password* matches *hashed_password*."""
    try:
        return bcrypt.checkpw(_password_bytes(plain_password), hashed_password.encode("utf-8"))
    except ValueError:
        return False


# ---------------------------------------------------------------------------
# JWT creation & decoding
# ---------------------------------------------------------------------------

def create_access_token(data: dict[str, Any]) -> str:
    """
    Create a signed JWT containing *data* plus an 'exp' claim.

    Args:
        data: Payload dict.  Must include at least ``user_id`` and ``role``.

    Returns:
        Encoded JWT string.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and validate *token*.

    Raises:
        HTTPException 401: If the token is invalid, expired, or tampered.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        raise credentials_exception


# ---------------------------------------------------------------------------
# FastAPI dependency functions
# ---------------------------------------------------------------------------

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> dict[str, Any]:
    """
    FastAPI dependency — extracts and validates the Bearer JWT from the
    Authorization header.

    Returns:
        The decoded JWT payload dict (contains ``user_id``, ``role``, etc.).
    """
    return decode_token(credentials.credentials)


def require_developer(
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, Any]:
    """
    FastAPI dependency — asserts that the authenticated user has
    ``role == "developer"``.  Raises 403 otherwise.
    """
    if current_user.get("role") != "developer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Developer role required.",
        )
    return current_user
