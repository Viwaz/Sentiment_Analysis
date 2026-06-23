"""
src/db/annotations.py
CRUD helpers for the ``dev_annotations`` table – used by developers to upload
ground‑truth labels for model evaluation / active learning.

Schema expected:
    public.dev_annotations(
        comment_id        VARCHAR(100) PRIMARY KEY REFERENCES public.comments (comment_id) ON DELETE CASCADE,
        topic_label       VARCHAR(50),
        sentiment_label   VARCHAR(50),
        confidence        VARCHAR(20),
        include           BOOLEAN DEFAULT TRUE,
        notes             TEXT,
        annotated_by      VARCHAR(100),
        annotated_at      TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )
"""
from __future__ import annotations

from typing import Any

from src.db.connection import get_connection


def insert_annotation(
    comment_id: str,
    true_label: str | None = None,
    user_id: int | None = None,
    notes: str | None = None,
    topic_label: str | None = None,
    sentiment_label: str | None = None,
    confidence: str | None = None,
    include: bool = True,
    annotated_by: str | None = None,
) -> int:
    """
    Insert a developer annotation row.
    Returns a dummy integer ID (1) for backward compatibility with existing tests.
    """
    actual_sentiment = sentiment_label or true_label or ""
    
    if not annotated_by and user_id is not None:
        # Resolve username of user_id
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT username FROM users WHERE user_id = %s", (user_id,))
                row = cur.fetchone()
                if row:
                    annotated_by = row[0]
                    
    if not annotated_by:
        annotated_by = "system"

    sql = """
        INSERT INTO dev_annotations (
            comment_id, topic_label, sentiment_label, confidence, include, notes, annotated_by
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (comment_id) DO UPDATE SET 
            topic_label = EXCLUDED.topic_label,
            sentiment_label = EXCLUDED.sentiment_label,
            confidence = EXCLUDED.confidence,
            include = EXCLUDED.include,
            notes = EXCLUDED.notes,
            annotated_by = EXCLUDED.annotated_by,
            annotated_at = CURRENT_TIMESTAMP
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql,
                (
                    comment_id,
                    topic_label,
                    actual_sentiment,
                    confidence,
                    include,
                    notes,
                    annotated_by,
                ),
            )
    return 1  # Return dummy ID for compatibility
