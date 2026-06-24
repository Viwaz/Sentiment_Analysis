"""
src/db/comments.py
CRUD helpers for the ``comments`` table.

Schema expected:
    public.comments (
        comment_id          VARCHAR(100) PRIMARY KEY,
        comment_text        TEXT NOT NULL,
        source_url          VARCHAR(500) NOT NULL,
        created_at          TIMESTAMP,
        date_collected      TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        collection_source   VARCHAR(100) NOT NULL,
        apify_dataset_id    VARCHAR(100),
        apify_run_id        VARCHAR(100)
    )
"""
from __future__ import annotations

from typing import Any

from src.db.connection import get_connection


def insert_comment(
    comment_id: str,
    comment_text: str | None = None,
    text: str | None = None,
    source_url: str | None = None,
    collection_source: str | None = None,
    created_at: Any = None,
    apify_dataset_id: str | None = None,
    apify_run_id: str | None = None,
) -> str:
    """
    Insert a raw comment into the ``comments`` table.

    Uses ``ON CONFLICT DO NOTHING`` so re-ingesting the same comment_id is safe.

    Returns:
        The ``comment_id`` that was inserted (or already existed).
    """
    actual_text = comment_text or text or ""
    actual_source_url = source_url or ""
    actual_collection_source = collection_source or "api"

    sql = """
        INSERT INTO comments (
            comment_id, comment_text, source_url, created_at, collection_source, apify_dataset_id, apify_run_id
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (comment_id) DO NOTHING
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql,
                (
                    comment_id,
                    actual_text,
                    actual_source_url,
                    created_at,
                    actual_collection_source,
                    apify_dataset_id,
                    apify_run_id,
                ),
            )
    return comment_id


def fetch_comment(comment_id: str) -> dict[str, Any] | None:
    """
    Fetch a single comment row by its external identifier.

    Returns:
        Dict with all comment columns, or ``None`` if not found.
    """
    sql = """
        SELECT comment_id, comment_text, source_url, created_at, date_collected, collection_source, apify_dataset_id, apify_run_id
        FROM comments
        WHERE comment_id = %s
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (comment_id,))
            row = cur.fetchone()

    if row is None:
        return None
    return {
        "comment_id": row[0],
        "comment_text": row[1],
        "text": row[1],  # alias for backward compatibility
        "source_url": row[2],
        "created_at": row[3],
        "date_collected": row[4],
        "ingested_at": row[4],  # alias for backward compatibility
        "collection_source": row[5],
        "apify_dataset_id": row[6],
        "apify_run_id": row[7],
    }
