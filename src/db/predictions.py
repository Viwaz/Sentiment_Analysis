"""
src/db/predictions.py
CRUD helpers for the ``predictions`` table.

Schema expected:
    public.predictions(
        prediction_id        SERIAL PRIMARY KEY,
        comment_id           VARCHAR(100) NOT NULL REFERENCES comments(comment_id) ON DELETE CASCADE,
        predicted_label      VARCHAR(50) NOT NULL,
        predicted_confidence NUMERIC(10,8) NOT NULL,
        score_negative       NUMERIC(10,8) NOT NULL,
        score_neutral        NUMERIC(10,8) NOT NULL,
        score_positive       NUMERIC(10,8) NOT NULL,
        model_name           VARCHAR(100) NOT NULL,
        model_version        VARCHAR(50) NOT NULL,
        model_family         VARCHAR(50) NOT NULL,
        predicted_at         TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    )
"""
from __future__ import annotations

from typing import Any, List

from src.db.connection import get_connection


def insert_prediction(
    comment_id: str,
    predicted_label: str,
    predicted_confidence: float,
    score_negative: float,
    score_neutral: float,
    score_positive: float,
    model_name: str,
    model_version: str,
    model_family: str,
) -> int:
    """Insert a single prediction row and return the generated ``prediction_id``."""
    sql = """
        INSERT INTO predictions (
            comment_id,
            predicted_label,
            predicted_confidence,
            score_negative,
            score_neutral,
            score_positive,
            model_name,
            model_version,
            model_family
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING prediction_id
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                sql,
                (
                    comment_id,
                    predicted_label,
                    predicted_confidence,
                    score_negative,
                    score_neutral,
                    score_positive,
                    model_name,
                    model_version,
                    model_family,
                ),
            )
            row = cur.fetchone()
    return row[0]


def fetch_predictions(comment_id: str) -> List[dict[str, Any]]:
    """Return all predictions for a given comment_id ordered by ``predicted_at`` descending."""
    sql = """
        SELECT
            prediction_id,
            comment_id,
            predicted_label,
            predicted_confidence,
            score_negative,
            score_neutral,
            score_positive,
            model_name,
            model_version,
            model_family,
            predicted_at
        FROM predictions
        WHERE comment_id = %s
        ORDER BY predicted_at DESC;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (comment_id,))
            rows = cur.fetchall()

    result = []
    for row in rows:
        result.append(
            {
                "id": row[0],  # for backward compatibility
                "prediction_id": row[0],
                "comment_id": row[1],
                "predicted_label": row[2],
                "predicted_confidence": float(row[3]) if row[3] is not None else 0.0,
                "score_negative": float(row[4]) if row[4] is not None else 0.0,
                "score_neutral": float(row[5]) if row[5] is not None else 0.0,
                "score_positive": float(row[6]) if row[6] is not None else 0.0,
                "model_name": row[7],
                "model_version": row[8],
                "model_family": row[9],
                "predicted_at": row[10],
            }
        )
    return result


def fetch_predictions_with_comments() -> List[dict[str, Any]]:
    """Return all predictions joined with comment text and cleaned text ordered by ``predicted_at`` descending."""
    sql = """
        SELECT
            p.prediction_id,
            p.comment_id,
            c.comment_text,
            pc.cleaned_text,
            p.predicted_label,
            p.predicted_confidence,
            p.score_negative,
            p.score_neutral,
            p.score_positive,
            p.model_name,
            p.model_version,
            p.model_family,
            p.predicted_at
        FROM predictions p
        JOIN comments c ON p.comment_id = c.comment_id
        LEFT JOIN preprocessed_comments pc ON p.comment_id = pc.comment_id
        ORDER BY p.predicted_at DESC;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()

    result = []
    for row in rows:
        result.append(
            {
                "prediction_id": row[0],
                "id": row[0],  # backward compatibility
                "comment_id": row[1],
                "comment_text": row[2],
                "text": row[2],  # backward compatibility
                "cleaned_text": row[3] or "",
                "predicted_label": row[4],
                "predicted_confidence": float(row[5]) if row[5] is not None else 0.0,
                "score_negative": float(row[6]) if row[6] is not None else 0.0,
                "score_neutral": float(row[7]) if row[7] is not None else 0.0,
                "score_positive": float(row[8]) if row[8] is not None else 0.0,
                "model_name": row[9],
                "model_version": row[10],
                "model_family": row[11],
                "predicted_at": str(row[12]),
            }
        )
    return result
