from __future__ import annotations

import hashlib
import re
import secrets
from typing import Any

import bcrypt
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

from src.config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER
from src.db.connection import get_connection


def get_db_connection() -> psycopg2.extensions.connection:
    """Get a direct PostgreSQL connection."""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def init_db() -> None:
    """Create the three main tables in a dedicated dashboard schema namespace."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE SCHEMA IF NOT EXISTS dashboard;")
            
            # ── users ──
            cur.execute("""
                CREATE TABLE IF NOT EXISTS dashboard.users (
                    user_id          SERIAL PRIMARY KEY,
                    username         VARCHAR(255) NOT NULL UNIQUE,
                    password         VARCHAR(255) NOT NULL,
                    email            VARCHAR(255),
                    role             VARCHAR(50)  DEFAULT 'general',
                    created_at       TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    is_active        BOOLEAN DEFAULT TRUE
                );
            """)

            # ── sessions ──
            cur.execute("""
                CREATE TABLE IF NOT EXISTS dashboard.sessions (
                    session_id    SERIAL PRIMARY KEY,
                    user_id       INTEGER NOT NULL REFERENCES dashboard.users(user_id) ON DELETE CASCADE,
                    url           TEXT NOT NULL,
                    timestamp     TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    custom_title  VARCHAR(255)
                );
            """)

            # Idempotent migration to add custom_title column to dashboard.sessions if it doesn't exist
            cur.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_schema = 'dashboard'
                          AND table_name = 'sessions'
                          AND column_name = 'custom_title'
                    ) THEN
                        ALTER TABLE dashboard.sessions ADD COLUMN custom_title VARCHAR(255);
                    END IF;
                END $$;
            """)

            # ── comments ──
            cur.execute("""
                CREATE TABLE IF NOT EXISTS dashboard.comments (
                    comment_id       SERIAL PRIMARY KEY,
                    session_id       INTEGER NOT NULL REFERENCES dashboard.sessions(session_id) ON DELETE CASCADE,
                    comment_text     TEXT NOT NULL,
                    sentiment_label  VARCHAR(50),
                    model_confidence NUMERIC(10,8),
                    created_time     TIMESTAMP WITHOUT TIME ZONE
                );
            """)

            # Idempotent migration: add model_confidence to existing installs
            cur.execute("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_schema = 'dashboard'
                          AND table_name = 'comments'
                          AND column_name = 'model_confidence'
                    ) THEN
                        ALTER TABLE dashboard.comments ADD COLUMN model_confidence NUMERIC(10,8);
                    END IF;
                END $$;
            """)


# ── Password helpers ─────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    if "$" in hashed and len(hashed.split("$")) == 2:
        parts = hashed.split("$")
        salt, h = parts
        return hashlib.sha256((salt + password).encode()).hexdigest() == h
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


# ── User helpers ─────────────────────────────────────────────────────────────

def _user_row_to_dict(row: tuple) -> dict[str, Any]:
    return {
        "user_id": row[0],
        "username": row[1],
        "password": row[2],
        "email": row[3],
        "role": row[4],
        "created_at": row[5],
        "is_active": row[6],
    }


def create_user(email: str, password: str, username: str | None = None) -> dict[str, Any]:
    email = (email or "").strip().lower()
    if not email or not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        raise ValueError("Please enter a valid email address.")
    username = (username or email).strip().lower()
    hashed = hash_password(password)
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(
                    "INSERT INTO dashboard.users (username, password, email, role) "
                    "VALUES (%s, %s, %s, %s) RETURNING user_id, username, password, email, role, created_at, is_active",
                    (username, hashed, email, "general"),
                )
                row = cur.fetchone()
                return _user_row_to_dict(row)
            except psycopg2.errors.UniqueViolation:
                raise ValueError("An account with this email already exists.")


def authenticate_user(identifier: str, password: str) -> dict[str, Any] | None:
    identifier = (identifier or "").strip().lower()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT user_id, username, password, email, role, created_at, is_active "
                "FROM dashboard.users WHERE LOWER(username) = %s OR LOWER(email) = %s",
                (identifier, identifier),
            )
            row = cur.fetchone()
    if row is None:
        return None
    user = _user_row_to_dict(row)
    stored = user.get("password") or ""
    if verify_password(password, stored):
        return {
            "user_id": user["user_id"],
            "username": user["username"],
            "role": user.get("role", "general"),
        }
    return None


def get_user_by_username(username: str) -> dict[str, Any] | None:
    username = (username or "").strip().lower()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT user_id, username, password, email, role, created_at, is_active "
                "FROM dashboard.users WHERE LOWER(username) = %s OR LOWER(email) = %s",
                (username, username),
            )
            row = cur.fetchone()
    if row is None:
        return None
    user = _user_row_to_dict(row)
    return {
        "user_id": user["user_id"],
        "username": user["username"],
        "role": user.get("role", "general"),
    }


def create_or_get_google_user(email: str) -> dict[str, Any]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Check if user exists by username (email)
            cur.execute(
                "SELECT user_id, username, password, email, role, created_at, is_active "
                "FROM dashboard.users WHERE username = %s",
                (email,)
            )
            row = cur.fetchone()
            if row is not None:
                user = _user_row_to_dict(row)
                return {
                    "user_id": user["user_id"],
                    "username": user["username"],
                    "role": user.get("role", "general"),
                }
            
            # If not, create a new one
            cur.execute(
                "INSERT INTO dashboard.users (username, password, email, role) "
                "VALUES (%s, 'google_oauth', %s, 'general') RETURNING user_id",
                (email, email)
            )
            new_user_id = cur.fetchone()[0]
            return {
                "user_id": new_user_id,
                "username": email,
                "role": "general"
            }



# ── Session helpers ──────────────────────────────────────────────────────────

def _session_row_to_dict(row: tuple) -> dict[str, Any]:
    return {
        "session_id": row[0],
        "user_id": row[1],
        "url": row[2],
        "timestamp": row[3].isoformat() if row[3] else None,
        "custom_title": row[4] if len(row) > 4 else None,
        "display_title": row[5] if len(row) > 5 else (row[4] if len(row) > 4 else None),
    }


def create_session(user_id: int, url: str) -> dict[str, Any]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO dashboard.sessions (user_id, url) VALUES (%s, %s) "
                "RETURNING session_id, user_id, url, timestamp, custom_title",
                (user_id, url),
            )
            row = cur.fetchone()
    return _session_row_to_dict(row)


def get_session(session_id: int) -> dict[str, Any] | None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT session_id, user_id, url, timestamp, custom_title, "
                "COALESCE(custom_title, TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI')) AS display_title "
                "FROM dashboard.sessions WHERE session_id = %s",
                (session_id,),
            )
            row = cur.fetchone()
    if row is None:
        return None
    return _session_row_to_dict(row)


def get_user_sessions(user_id: int) -> list[dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT session_id, user_id, url, timestamp, custom_title, "
                "COALESCE(custom_title, TO_CHAR(timestamp, 'YYYY-MM-DD HH24:MI')) AS display_title "
                "FROM dashboard.sessions WHERE user_id = %s ORDER BY timestamp DESC",
                (user_id,),
            )
            rows = cur.fetchall()
    return [_session_row_to_dict(r) for r in rows]


def update_session_title(session_id: int, new_title: str | None) -> None:
    """Update the custom_title of a session."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE dashboard.sessions SET custom_title = %s WHERE session_id = %s",
                (new_title, session_id),
            )


def delete_session(session_id: int) -> None:
    """Delete a session record. Foreign key CASCADE constraints will drop comment rows."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM dashboard.sessions WHERE session_id = %s",
                (session_id,),
            )


# ── Comment helpers ──────────────────────────────────────────────────────────

def _comment_row_to_dict(row: tuple) -> dict[str, Any]:
    return {
        "comment_id": row[0],
        "session_id": row[1],
        "comment_text": row[2],
        "sentiment_label": row[3],
        "model_confidence": float(row[4]) if row[4] is not None else None,
        "created_time": row[5].isoformat() if row[5] else None,
    }


def add_comment(
    session_id: int,
    comment_text: str,
    sentiment_label: str | None = None,
    model_confidence: float | None = None,
    created_time: str | None = None,
) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO dashboard.comments (session_id, comment_text, sentiment_label, model_confidence, created_time) "
                "VALUES (%s, %s, %s, %s, %s)",
                (session_id, comment_text, sentiment_label, model_confidence, created_time),
            )


def get_session_comments(session_id: int) -> list[dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT comment_id, session_id, comment_text, sentiment_label, model_confidence, created_time "
                "FROM dashboard.comments WHERE session_id = %s ORDER BY created_time NULLS LAST",
                (session_id,),
            )
            rows = cur.fetchall()
    return [_comment_row_to_dict(r) for r in rows]


# ── Save analysis helper ─────────────────────────────────────────────────────

def parse_datetime(val: Any) -> Any:
    if pd.isna(val):
        return None
    try:
        dt = pd.to_datetime(val)
        if pd.isna(dt):
            return None
        return dt.to_pydatetime()
    except Exception:
        return None


def save_analysis(user_id: int, url: str, df: pd.DataFrame) -> dict[str, Any]:
    """Persist a completed analysis (session + comments) to PostgreSQL using fast batch insertions.

    Expects *df* to contain at least the columns ``text`` (or ``commentText``)
    and ``predicted_sentiment`` (or ``predicted_label``).
    The optional ``created_at`` / ``createdAt`` / ``created_time`` column
    holds the original Facebook timestamp.
    The optional ``model_confidence`` column holds the per-row confidence score.
    """
    session = create_session(user_id, url)

    text_col = next(
        (c for c in ("text", "commentText", "comment_text") if c in df.columns), None
    )
    sentiment_col = next(
        (c for c in ("predicted_sentiment", "predicted_label", "sentiment_label") if c in df.columns), None
    )
    time_col = next(
        (c for c in ("created_at", "createdAt", "created_time", "timestamp") if c in df.columns), None
    )
    confidence_col = "model_confidence" if "model_confidence" in df.columns else None

    if text_col is None:
        raise ValueError("DataFrame must contain a text/comment column.")

    data_tuples = []
    for _, row in df.iterrows():
        text = row.get(text_col)
        if not text or (isinstance(text, float) and pd.isna(text)):
            continue
        sentiment = str(row.get(sentiment_col, "")) if sentiment_col and pd.notna(row.get(sentiment_col)) else ""
        raw_time = row.get(time_col) if time_col else None
        created = parse_datetime(raw_time)
        confidence = float(row[confidence_col]) if confidence_col and pd.notna(row.get(confidence_col)) else None
        data_tuples.append((session["session_id"], str(text), sentiment or None, confidence, created))

    if data_tuples:
        with get_connection() as conn:
            with conn.cursor() as cur:
                execute_values(
                    cur,
                    "INSERT INTO dashboard.comments (session_id, comment_text, sentiment_label, model_confidence, created_time) "
                    "VALUES %s",
                    data_tuples
                )

    return session
