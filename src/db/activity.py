"""
src/db/activity.py
Helper for inserting rows into the ``activity_logs`` table.

Schema expected:
    public.activity_logs(
        log_id          SERIAL PRIMARY KEY,
        user_id         INTEGER NOT NULL REFERENCES users(user_id) ON DELETE RESTRICT,
        comment_id      VARCHAR(100) REFERENCES comments(comment_id) ON DELETE SET NULL,
        action_type     VARCHAR(50) NOT NULL CHECK (action_type IN ('ingest', 'preprocess', 'predict', 'annotation_upload')),
        action_timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        details         TEXT
    )
"""
from __future__ import annotations

import json
from typing import Any, Mapping, Optional

from src.db.connection import get_connection


def _get_system_user_id() -> int:
    """Helper to get or create a default system user for unauthenticated logs."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT user_id FROM users WHERE username = 'system'")
            row = cur.fetchone()
            if row:
                return row[0]

            cur.execute("SELECT user_id FROM users LIMIT 1")
            row = cur.fetchone()
            if row:
                return row[0]

            cur.execute(
                """
                INSERT INTO users (username, hashed_password, email, role)
                VALUES ('system', 'disabled', 'system@example.com', 'admin')
                ON CONFLICT (username) DO NOTHING
                RETURNING user_id
                """
            )
            row = cur.fetchone()
            if row:
                return row[0]

            cur.execute("SELECT user_id FROM users WHERE username = 'system'")
            row = cur.fetchone()
            return row[0] if row else 1


def log_action(
    user_id: int | None,
    action_type: str,
    comment_id: str | None = None,
    details: Optional[Mapping[str, Any]] = None,
) -> int:
    """Insert a log entry and return the generated ``log_id``.

    * ``user_id`` – if ``None``, resolves to a default system user.
    * ``action_type`` – mapped to one of: ingest, preprocess, predict, annotation_upload.
    * ``comment_id`` – optional FK to the comment.
    * ``details`` – optional dictionary context stored as text.
    """
    if user_id is None:
        user_id = _get_system_user_id()

    # Map action_type to allowed constraint values
    allowed_types = {'ingest', 'preprocess', 'predict', 'annotation_upload'}
    norm_action = action_type.lower()
    if norm_action not in allowed_types:
        if "ingest" in norm_action:
            action_type = "ingest"
        elif "preprocess" in norm_action or "clean" in norm_action:
            action_type = "preprocess"
        elif "predict" in norm_action or "inference" in norm_action:
            action_type = "predict"
        elif "annot" in norm_action:
            action_type = "annotation_upload"
        else:
            action_type = "ingest"

    details_str = json.dumps(details) if details is not None else None

    sql = """
        INSERT INTO activity_logs (user_id, action_type, comment_id, details)
        VALUES (%s, %s, %s, %s)
        RETURNING log_id
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (user_id, action_type, comment_id, details_str))
            row = cur.fetchone()
    return row[0]
