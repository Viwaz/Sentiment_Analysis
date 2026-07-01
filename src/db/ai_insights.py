"""
src/db/ai_insights.py
CRUD helpers for the ``ai_insights`` table.

Schema (from Database/migrations/004_ai_insights.sql):
    ai_insights (
        insight_id      SERIAL PRIMARY KEY,
        session_id      INTEGER REFERENCES scrape_sessions(session_id) ON DELETE CASCADE,
        summary         TEXT         NOT NULL DEFAULT '',
        key_issues      JSONB        NOT NULL DEFAULT '[]',
        recommendations JSONB        NOT NULL DEFAULT '[]',
        model_used      VARCHAR(100) NOT NULL DEFAULT '',
        generated_at    TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT ai_insights_session_unique UNIQUE (session_id)
    )
"""
from __future__ import annotations

import json
from typing import Any

from src.db.connection import get_connection


# ---------------------------------------------------------------------------
# Read helpers
# ---------------------------------------------------------------------------

def get_cached_insight(session_id: int) -> dict[str, Any] | None:
    """Return the cached AI insight for *session_id*, or ``None`` if absent."""
    sql = """
        SELECT insight_id, session_id, summary, key_issues, recommendations,
               model_used, generated_at
        FROM   ai_insights
        WHERE  session_id = %s
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (session_id,))
            row = cur.fetchone()

    if row is None:
        return None

    return {
        "insight_id":      row[0],
        "session_id":      row[1],
        "summary":         row[2],
        "key_issues":      row[3] if isinstance(row[3], list) else json.loads(row[3] or "[]"),
        "recommendations": row[4] if isinstance(row[4], list) else json.loads(row[4] or "[]"),
        "model_used":      row[5],
        "generated_at":    str(row[6]),
    }


def fetch_session_for_insights(session_id: int) -> dict[str, Any]:
    """
    Build the structured payload the LLM service needs.

    Returns a dict with:
        session_id, session_name, source_url,
        total_comments, sentiment_distribution (pos/neg/neu counts + pct),
        comments: list[{text, predicted_label, predicted_confidence}]
    """
    # ── session meta ───────────────────────────────────────────────────────
    meta_sql = """
        SELECT session_id, session_name, source_url,
               pos_count, neg_count, neu_count, comment_count
        FROM   scrape_sessions
        WHERE  session_id = %s
    """
    # ── comments + predictions ─────────────────────────────────────────────
    comments_sql = """
        SELECT c.comment_text,
               p.predicted_label,
               p.predicted_confidence
        FROM   comments c
        LEFT JOIN predictions p ON c.comment_id = p.comment_id
        WHERE  c.session_id = %s
          AND  p.predicted_label IS NOT NULL
        ORDER  BY c.date_collected
        LIMIT  200
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(meta_sql, (session_id,))
            meta = cur.fetchone()
            cur.execute(comments_sql, (session_id,))
            comment_rows = cur.fetchall()

    if meta is None:
        raise ValueError(f"Session {session_id} not found.")

    _, session_name, source_url, pos_count, neg_count, neu_count, total = meta
    pos_count   = pos_count or 0
    neg_count   = neg_count or 0
    neu_count   = neu_count or 0
    total       = total or (pos_count + neg_count + neu_count) or 1  # guard /0

    def pct(n: int) -> float:
        return round(n / total * 100, 1)

    comments = [
        {
            "text":                  row[0],
            "predicted_label":       row[1],
            "predicted_confidence":  float(row[2]) if row[2] is not None else 0.0,
        }
        for row in comment_rows
    ]

    return {
        "session_id":   session_id,
        "session_name": session_name,
        "source_url":   source_url,
        "total_comments": total,
        "sentiment_distribution": {
            "positive": {"count": pos_count, "pct": pct(pos_count)},
            "negative": {"count": neg_count, "pct": pct(neg_count)},
            "neutral":  {"count": neu_count, "pct": pct(neu_count)},
        },
        "comments": comments,
    }


# ---------------------------------------------------------------------------
# Write helpers
# ---------------------------------------------------------------------------

def upsert_insight(
    session_id: int,
    summary: str,
    key_issues: list[str],
    recommendations: list[str],
    model_used: str,
) -> dict[str, Any]:
    """
    Insert or overwrite the cached AI insight for *session_id*.

    Returns the saved record dict.
    """
    sql = """
        INSERT INTO ai_insights (session_id, summary, key_issues, recommendations, model_used)
        VALUES (%s, %s, %s::jsonb, %s::jsonb, %s)
        ON CONFLICT (session_id) DO UPDATE
            SET summary         = EXCLUDED.summary,
                key_issues      = EXCLUDED.key_issues,
                recommendations = EXCLUDED.recommendations,
                model_used      = EXCLUDED.model_used,
                generated_at    = CURRENT_TIMESTAMP
        RETURNING insight_id, session_id, summary, key_issues, recommendations,
                  model_used, generated_at
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql,
                (
                    session_id,
                    summary,
                    json.dumps(key_issues),
                    json.dumps(recommendations),
                    model_used,
                ),
            )
            row = cur.fetchone()

    return {
        "insight_id":      row[0],
        "session_id":      row[1],
        "summary":         row[2],
        "key_issues":      row[3] if isinstance(row[3], list) else json.loads(row[3] or "[]"),
        "recommendations": row[4] if isinstance(row[4], list) else json.loads(row[4] or "[]"),
        "model_used":      row[5],
        "generated_at":    str(row[6]),
    }
