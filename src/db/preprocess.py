"""
src/db/preprocess.py
CRUD helpers for the ``preprocessed_comments`` table.

Schema expected:
    preprocessed_comments(
        comment_id      VARCHAR(100) PRIMARY KEY REFERENCES comments(comment_id) ON DELETE CASCADE,
        cleaned_text    TEXT NOT NULL,
        preprocessed_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )
"""
from __future__ import annotations

from typing import Any

from src.db.connection import get_connection


def insert_preprocessed(
    comment_id: str,
    cleaned_text: str,
    emoji_aliases: str | None = None,
    emoji_count: int | None = None,
    token_count: int | None = None,
) -> str:
    """
    Insert a preprocessed record linked to a parent comment.

    Args:
        comment_id:    FK to ``comments.comment_id``.
        cleaned_text:  The normalised text produced by ``src.preprocess.clean_text``.
        emoji_aliases: Ignored (kept for backward compatibility).
        emoji_count:   Ignored (kept for backward compatibility).
        token_count:   Ignored (kept for backward compatibility).

    Returns:
        The ``comment_id`` of the inserted row.
    """
    sql = """
        INSERT INTO preprocessed_comments (comment_id, cleaned_text)
        VALUES (%s, %s)
        ON CONFLICT (comment_id) DO UPDATE SET cleaned_text = EXCLUDED.cleaned_text, preprocessed_at = CURRENT_TIMESTAMP
        RETURNING comment_id
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (comment_id, cleaned_text))
            row = cur.fetchone()
    return row[0]


def get_preprocessed(comment_id: str) -> dict[str, Any] | None:
    """
    Fetch the preprocessed record for a given comment.

    Returns:
        Dict with preprocessing columns, or ``None`` if no record exists.
    """
    sql = """
        SELECT comment_id, cleaned_text, preprocessed_at
        FROM preprocessed_comments
        WHERE comment_id = %s
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (comment_id,))
            row = cur.fetchone()

    if row is None:
        return None
    return {
        "id": 1,  # dummy integer id for backward compatibility
        "comment_id": row[0],
        "cleaned_text": row[1],
        "preprocessed_at": row[2],
        "emoji_aliases": None,  # compat
        "emoji_count": None,  # compat
        "token_count": None,  # compat
    }
