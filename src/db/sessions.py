"""CRUD helpers for the ``scrape_sessions`` table.

Schema expected (from Database/migrations/002_sessions_and_post_text.sql)::

    scrape_sessions (
        session_id    SERIAL PRIMARY KEY,
        user_id       INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
        session_name  VARCHAR(255) NOT NULL,
        source_url    VARCHAR(500) NOT NULL,
        comment_count INTEGER NOT NULL DEFAULT 0,
        model_used    VARCHAR(100),
        pos_count     INTEGER DEFAULT 0,
        neg_count     INTEGER DEFAULT 0,
        neu_count     INTEGER DEFAULT 0,
        created_at    TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )
"""

from __future__ import annotations

from typing import Any

from src.db.connection import get_connection


def create_session(
    user_id: int,
    session_name: str,
    source_url: str,
    comment_count: int = 0,
    model_used: str | None = None,
    pos_count: int = 0,
    neg_count: int = 0,
    neu_count: int = 0,
) -> dict[str, Any]:
    """Insert a new scrape session and return its full record."""
    sql = """
        INSERT INTO scrape_sessions
            (user_id, session_name, source_url, comment_count, model_used, pos_count, neg_count, neu_count)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING session_id, user_id, session_name, source_url, comment_count, model_used, pos_count, neg_count, neu_count, created_at
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql,
                (user_id, session_name, source_url, comment_count, model_used, pos_count, neg_count, neu_count),
            )
            row = cur.fetchone()
    return {
        "session_id": row[0],
        "user_id": row[1],
        "session_name": row[2],
        "source_url": row[3],
        "comment_count": row[4],
        "model_used": row[5],
        "pos_count": row[6],
        "neg_count": row[7],
        "neu_count": row[8],
        "created_at": row[9],
    }


def update_session(
    session_id: int,
    comment_count: int | None = None,
    model_used: str | None = None,
    pos_count: int | None = None,
    neg_count: int | None = None,
    neu_count: int | None = None,
    session_name: str | None = None,
) -> None:
    """Update mutable fields of a scrape session. Only non-``None`` fields are applied."""
    fields = []
    values = []
    if comment_count is not None:
        fields.append("comment_count = %s")
        values.append(comment_count)
    if model_used is not None:
        fields.append("model_used = %s")
        values.append(model_used)
    if pos_count is not None:
        fields.append("pos_count = %s")
        values.append(pos_count)
    if neg_count is not None:
        fields.append("neg_count = %s")
        values.append(neg_count)
    if neu_count is not None:
        fields.append("neu_count = %s")
        values.append(neu_count)
    if session_name is not None:
        fields.append("session_name = %s")
        values.append(session_name)
    if not fields:
        return
    values.append(session_id)
    sql = f"UPDATE scrape_sessions SET {', '.join(fields)} WHERE session_id = %s"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, values)


def rename_session(session_id: int, new_name: str) -> None:
    """Update the display name of an existing session."""
    sql = "UPDATE scrape_sessions SET session_name = %s WHERE session_id = %s"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (new_name, session_id))


def get_user_sessions(user_id: int) -> list[dict[str, Any]]:
    """Return all sessions belonging to a user, most recent first."""
    sql = """
        SELECT session_id, user_id, session_name, source_url, comment_count,
               model_used, pos_count, neg_count, neu_count, created_at
        FROM scrape_sessions
        WHERE user_id = %s
        ORDER BY created_at DESC
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (user_id,))
            rows = cur.fetchall()
    return [
        {
            "session_id": row[0],
            "user_id": row[1],
            "session_name": row[2],
            "source_url": row[3],
            "comment_count": row[4],
            "model_used": row[5],
            "pos_count": row[6],
            "neg_count": row[7],
            "neu_count": row[8],
            "created_at": row[9],
        }
        for row in rows
    ]


def get_session(session_id: int) -> dict[str, Any] | None:
    """Fetch a single session by its primary key."""
    sql = """
        SELECT session_id, user_id, session_name, source_url, comment_count,
               model_used, pos_count, neg_count, neu_count, created_at
        FROM scrape_sessions
        WHERE session_id = %s
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (session_id,))
            row = cur.fetchone()
    if row is None:
        return None
    return {
        "session_id": row[0],
        "user_id": row[1],
        "session_name": row[2],
        "source_url": row[3],
        "comment_count": row[4],
        "model_used": row[5],
        "pos_count": row[6],
        "neg_count": row[7],
        "neu_count": row[8],
        "created_at": row[9],
    }


def fetch_session_results(session_id: int) -> list[dict[str, Any]]:
    """Fetch the comment + prediction rows for a given session.

    Returns a list of dicts with keys ``text``, ``source_url``, ``cleaned_text``,
    ``predicted_sentiment``, ``predicted_confidence``, ``score_negative``,
    ``score_neutral``, ``score_positive``, and ``comment_id``.
    """
    sql = """
        SELECT
            c.comment_text,
            c.source_url,
            pc.cleaned_text,
            p.predicted_label,
            p.predicted_confidence,
            p.score_negative,
            p.score_neutral,
            p.score_positive,
            c.comment_id
        FROM comments c
        LEFT JOIN preprocessed_comments pc ON c.comment_id = pc.comment_id
        LEFT JOIN predictions p ON c.comment_id = p.comment_id
        WHERE c.session_id = %s
        ORDER BY c.date_collected
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (session_id,))
            rows = cur.fetchall()
    return [
        {
            "text": row[0],
            "source_url": row[1],
            "cleaned_text": row[2] or row[0],
            "predicted_sentiment": row[3] or "neutral",
            "predicted_confidence": float(row[4]) if row[4] is not None else 0.0,
            "score_negative": float(row[5]) if row[5] is not None else 0.0,
            "score_neutral": float(row[6]) if row[6] is not None else 0.0,
            "score_positive": float(row[7]) if row[7] is not None else 0.0,
            "comment_id": row[8],
        }
        for row in rows
    ]
