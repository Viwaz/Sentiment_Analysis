"""
src/db/users.py
CRUD helpers for the ``users`` table.

Schema expected (from Database/schema.sql):
    users(user_id SERIAL PK, username VARCHAR(100) UNIQUE, hashed_password VARCHAR(255), email VARCHAR(255) UNIQUE, role VARCHAR(50), created_at TIMESTAMP, is_active BOOLEAN)
"""
from __future__ import annotations

from typing import Any

from src.auth import hash_password, verify_password
from src.db.connection import get_connection


def create_user(username: str, password: str, role: str = "general", email: str | None = None) -> dict[str, Any]:
    """
    Register a new user.

    Args:
        username: Unique username string.
        password: Plain-text password (will be hashed before storage).
        role: ``"general"`` (default), ``"developer"``, or ``"admin"``.
        email: User email string. If not provided, will default to username@example.com.

    Returns:
        Dict with ``user_id``, ``username``, ``role``, and ``email``.

    Raises:
        psycopg2.errors.UniqueViolation: If *username* or *email* already exists.
    """
    if role == "user":
        role = "general"
    if not email:
        email = f"{username}@example.com"

    pw_hash = hash_password(password)
    sql = """
        INSERT INTO users (username, hashed_password, role, email)
        VALUES (%s, %s, %s, %s)
        RETURNING user_id, username, role, email
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (username, pw_hash, role, email))
            row = cur.fetchone()
    return {"user_id": row[0], "username": row[1], "role": row[2], "email": row[3]}


def authenticate_user(username: str, password: str) -> dict[str, Any] | None:
    """
    Verify credentials and return the user record, or ``None`` on failure.

    Args:
        username: The username to look up.
        password: Plain-text password to verify.

    Returns:
        Dict with ``user_id``, ``username``, ``role`` on success; ``None`` otherwise.
    """
    sql = "SELECT user_id, username, hashed_password, role FROM users WHERE username = %s"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (username,))
            row = cur.fetchone()

    if row is None:
        return None
    user_id, uname, pw_hash, role = row
    if not verify_password(password, pw_hash):
        return None
    return {"user_id": user_id, "username": uname, "role": role}


def get_user_by_id(user_id: int) -> dict[str, Any] | None:
    """
    Fetch a user record by primary key.

    Returns:
        Dict with ``user_id``, ``username``, ``role``, or ``None`` if not found.
    """
    sql = "SELECT user_id, username, role FROM users WHERE user_id = %s"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (user_id,))
            row = cur.fetchone()

    if row is None:
        return None
    return {"user_id": row[0], "username": row[1], "role": row[2]}
