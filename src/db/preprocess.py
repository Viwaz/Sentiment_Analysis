"""
src/db/preprocess.py
CRUD helpers for the ``preprocessed_comments`` table.

Schema expected:
    preprocessed_comments(
        preprocessed_id  SERIAL PRIMARY KEY,
        comment_id       VARCHAR(100) NOT NULL UNIQUE REFERENCES comments(comment_id) ON DELETE CASCADE,
        cleaned_text     TEXT NOT NULL,
        metadata         JSONB,
        preprocessed_at  TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )
"""
from __future__ import annotations

from typing import Any
import json

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
    # Build metadata dictionary from optional parameters
    metadata: dict[str, Any] = {}
    if emoji_aliases is not None:
        metadata["emoji_aliases"] = emoji_aliases
    if emoji_count is not None:
        metadata["emoji_count"] = int(emoji_count)
    if token_count is not None:
        metadata["token_count"] = int(token_count)

    metadata_json = json.dumps(metadata) if metadata else None

    sql = """
        INSERT INTO preprocessed_comments (comment_id, cleaned_text, metadata)
        VALUES (%s, %s, %s)
        ON CONFLICT (comment_id) DO UPDATE SET
            cleaned_text = EXCLUDED.cleaned_text,
            metadata = EXCLUDED.metadata,
            preprocessed_at = CURRENT_TIMESTAMP
        RETURNING preprocessed_id
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (comment_id, cleaned_text, metadata_json))
            row = cur.fetchone()
    return row[0]


def get_preprocessed(comment_id: str) -> dict[str, Any] | None:
    """
    Fetch the preprocessed record for a given comment.

    Returns:
        Dict with preprocessing columns, or ``None`` if no record exists.
    """
    sql = """
        SELECT preprocessed_id, comment_id, cleaned_text, metadata, preprocessed_at
        FROM preprocessed_comments
        WHERE comment_id = %s
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (comment_id,))
            row = cur.fetchone()

    if row is None:
        return None

    preprocessed_id, cid, cleaned_text, metadata_json, preprocessed_at = row

    metadata: dict[str, Any] = {}
    if metadata_json is not None:
        try:
            # metadata_json may be a string or already a dict depending on the adapter
            metadata = json.loads(metadata_json) if isinstance(metadata_json, str) else metadata_json
        except Exception:
            metadata = {}

    return {
        "id": int(preprocessed_id),
        "comment_id": cid,
        "cleaned_text": cleaned_text,
        "preprocessed_at": preprocessed_at,
        "emoji_aliases": metadata.get("emoji_aliases"),
        "emoji_count": metadata.get("emoji_count"),
        "token_count": metadata.get("token_count"),
    }
