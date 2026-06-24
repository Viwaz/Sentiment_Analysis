"""
tests/test_db_integration.py
End-to-end integration tests for the DB layer and comment API endpoints.

These tests require a running PostgreSQL database with the schema applied.
Configure credentials in the `.env` file at the project root (see `.env` template).

Run with:
    pytest tests/test_db_integration.py -v

The tests use FastAPI's TestClient so no live uvicorn server is needed.
They connect to a real DB, so they will insert (and clean up) test rows.
"""
from __future__ import annotations

import uuid
import os
import pytest

# Load .env BEFORE importing the app so DB env vars are set in time
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from fastapi.testclient import TestClient
from src.model_api import app

client = TestClient(app, raise_server_exceptions=True)

# Unique prefix so tests never clash with real data
TEST_PREFIX = "pytest_"


# ===========================================================================
# Helpers
# ===========================================================================

@pytest.fixture
def test_comment_id() -> str:
    """Generate a unique comment_id for each test run."""
    return f"{TEST_PREFIX}{uuid.uuid4().hex[:12]}"


@pytest.fixture
def inserted_comment(test_comment_id: str) -> str:
    """Insert a comment via the API and return its comment_id."""
    payload = {
        "comment_id": test_comment_id,
        "text": "Fixture comment for testing",
        "source_url": "https://facebook.com/post/fixture",
        "collection_source": "test_suite",
    }
    client.post("/comments", json=payload)
    return test_comment_id


@pytest.fixture
def test_user() -> dict:
    """Create a unique test user directly via the DB helper and return info."""
    from src.db.users import create_user
    username = f"{TEST_PREFIX}user_{uuid.uuid4().hex[:8]}"
    return create_user(username=username, password="test_pass_123", role="developer")


# ===========================================================================
# POST /comments
# ===========================================================================

class TestCreateComment:
    def test_insert_returns_comment_id(self, test_comment_id: str):
        payload = {
            "comment_id": test_comment_id,
            "text": "Good development",
            "source_url": "https://facebook.com/post/1",
            "collection_source": "test_suite",
        }
        response = client.post("/comments", json=payload)
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["comment_id"] == test_comment_id
        assert data["text"] == "Good development"

    def test_insert_with_minimal_fields(self, test_comment_id: str):
        """Only required fields — source_url and collection_source are optional."""
        payload = {"comment_id": test_comment_id, "text": "Nzeru"}
        response = client.post("/comments", json=payload)
        assert response.status_code == 200, response.text
        assert response.json()["comment_id"] == test_comment_id

    def test_idempotent_insert(self, test_comment_id: str):
        """Inserting the same comment_id twice must not raise an error (ON CONFLICT DO NOTHING)."""
        payload = {"comment_id": test_comment_id, "text": "First insert"}
        client.post("/comments", json=payload)
        response = client.post("/comments", json=payload)
        assert response.status_code == 200, response.text

    def test_missing_comment_id_returns_422(self):
        payload = {"text": "no id provided"}
        response = client.post("/comments", json=payload)
        assert response.status_code == 422

    def test_missing_text_returns_422(self):
        payload = {"comment_id": "test_no_text"}
        response = client.post("/comments", json=payload)
        assert response.status_code == 422


# ===========================================================================
# GET /comments/{comment_id}
# ===========================================================================

class TestReadComment:
    def test_fetch_existing_comment(self, test_comment_id: str):
        """Insert a comment then retrieve it and verify all fields round-trip."""
        payload = {
            "comment_id": test_comment_id,
            "text": "Congratulations Bwana",
            "source_url": "https://facebook.com/post/2",
            "collection_source": "test_suite",
        }
        client.post("/comments", json=payload)

        response = client.get(f"/comments/{test_comment_id}")
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["comment_id"] == test_comment_id
        assert data["text"] == "Congratulations Bwana"
        assert data["source_url"] == "https://facebook.com/post/2"
        assert data["collection_source"] == "test_suite"

    def test_fetch_nonexistent_comment_returns_404(self):
        response = client.get("/comments/this_id_does_not_exist_xyz123")
        assert response.status_code == 404

    def test_fetched_comment_has_ingested_at(self, test_comment_id: str):
        """Verify the DB auto-fills ingested_at."""
        client.post("/comments", json={"comment_id": test_comment_id, "text": "Test"})
        data = client.get(f"/comments/{test_comment_id}").json()
        assert "ingested_at" in data
        assert data["ingested_at"] is not None


# ===========================================================================
# Direct DB: predictions
# ===========================================================================

class TestPredictions:
    def test_insert_and_fetch_prediction(self, inserted_comment: str):
        """Insert a prediction linked to a comment and fetch it back."""
        from src.db.predictions import insert_prediction, fetch_predictions

        pred_id = insert_prediction(
            comment_id=inserted_comment,
            predicted_label="positive",
            predicted_confidence=0.92,
            score_negative=0.03,
            score_neutral=0.05,
            score_positive=0.92,
            model_name="afriberta_small",
            model_version="1.0",
            model_family="transformer",
        )
        assert isinstance(pred_id, int)
        assert pred_id > 0

        rows = fetch_predictions(inserted_comment)
        assert len(rows) >= 1
        latest = rows[0]
        assert latest["comment_id"] == inserted_comment
        assert latest["predicted_label"] == "positive"
        assert latest["predicted_confidence"] == pytest.approx(0.92, abs=0.001)
        assert latest["model_name"] == "afriberta_small"

    def test_multiple_predictions_per_comment(self, inserted_comment: str):
        """The same comment can have multiple predictions (different models)."""
        from src.db.predictions import insert_prediction, fetch_predictions

        insert_prediction(
            comment_id=inserted_comment,
            predicted_label="positive",
            predicted_confidence=0.9,
            score_negative=0.05, score_neutral=0.05, score_positive=0.9,
            model_name="baseline", model_version="1.0", model_family="sklearn",
        )
        insert_prediction(
            comment_id=inserted_comment,
            predicted_label="neutral",
            predicted_confidence=0.6,
            score_negative=0.1, score_neutral=0.6, score_positive=0.3,
            model_name="afriberta_small", model_version="2.0", model_family="transformer",
        )

        rows = fetch_predictions(inserted_comment)
        assert len(rows) >= 2
        labels = {r["predicted_label"] for r in rows}
        assert "positive" in labels
        assert "neutral" in labels

    def test_fetch_returns_empty_for_unknown_comment(self):
        from src.db.predictions import fetch_predictions
        rows = fetch_predictions("nonexistent_comment_xyz")
        assert rows == []


# ===========================================================================
# Direct DB: preprocessed_comments
# ===========================================================================

class TestPreprocessed:
    def test_insert_and_get_preprocessed(self, inserted_comment: str):
        """Insert a preprocessed record and fetch it back."""
        from src.db.preprocess import insert_preprocessed, get_preprocessed

        pp_id = insert_preprocessed(
            comment_id=inserted_comment,
            cleaned_text="fixture comment testing",
            emoji_aliases=":thumbs_up:",
            emoji_count=1,
            token_count=3,
        )
        assert isinstance(pp_id, int)
        assert pp_id > 0

        record = get_preprocessed(inserted_comment)
        assert record is not None
        assert record["comment_id"] == inserted_comment
        assert record["cleaned_text"] == "fixture comment testing"
        assert record["emoji_aliases"] == ":thumbs_up:"
        assert record["emoji_count"] == 1
        assert record["token_count"] == 3

    def test_get_preprocessed_returns_none_for_unknown(self):
        from src.db.preprocess import get_preprocessed
        assert get_preprocessed("nonexistent_comment_xyz") is None

    def test_preprocessed_with_minimal_fields(self, inserted_comment: str):
        """Only comment_id and cleaned_text are required; rest are nullable."""
        from src.db.preprocess import insert_preprocessed, get_preprocessed

        pp_id = insert_preprocessed(
            comment_id=inserted_comment,
            cleaned_text="minimal test",
        )
        assert pp_id > 0

        record = get_preprocessed(inserted_comment)
        assert record is not None
        assert record["emoji_aliases"] is None
        assert record["emoji_count"] is None


# ===========================================================================
# Direct DB: users
# ===========================================================================

class TestUsers:
    def test_create_and_authenticate_user(self):
        """Create a user and verify authentication works."""
        from src.db.users import create_user, authenticate_user

        username = f"{TEST_PREFIX}auth_{uuid.uuid4().hex[:8]}"
        user = create_user(username=username, password="my_secret_pw")
        assert user["username"] == username
        assert user["role"] == "general"
        assert "user_id" in user

        authed = authenticate_user(username=username, password="my_secret_pw")
        assert authed is not None
        assert authed["user_id"] == user["user_id"]
        assert authed["username"] == username

    def test_authenticate_wrong_password_returns_none(self):
        from src.db.users import create_user, authenticate_user

        username = f"{TEST_PREFIX}badpw_{uuid.uuid4().hex[:8]}"
        create_user(username=username, password="correct_password")

        result = authenticate_user(username=username, password="wrong_password")
        assert result is None

    def test_authenticate_nonexistent_user_returns_none(self):
        from src.db.users import authenticate_user
        result = authenticate_user(username="no_such_user_xyz_999", password="any")
        assert result is None

    def test_get_user_by_id(self):
        from src.db.users import create_user, get_user_by_id

        username = f"{TEST_PREFIX}byid_{uuid.uuid4().hex[:8]}"
        user = create_user(username=username, password="pw123", role="developer")

        found = get_user_by_id(user["user_id"])
        assert found is not None
        assert found["username"] == username
        assert found["role"] == "developer"

    def test_get_user_by_id_nonexistent(self):
        from src.db.users import get_user_by_id
        assert get_user_by_id(999999) is None

    def test_duplicate_username_raises(self):
        from src.db.users import create_user
        import psycopg2

        username = f"{TEST_PREFIX}dup_{uuid.uuid4().hex[:8]}"
        create_user(username=username, password="pw1")
        with pytest.raises(psycopg2.errors.UniqueViolation):
            create_user(username=username, password="pw2")


# ===========================================================================
# Direct DB: annotations
# ===========================================================================

class TestAnnotations:
    def test_insert_annotation(self, inserted_comment: str, test_user: dict):
        """Insert an annotation linked to a comment and user."""
        from src.db.annotations import insert_annotation

        ann_id = insert_annotation(
            comment_id=inserted_comment,
            true_label="positive",
            user_id=test_user["user_id"],
            notes="Clearly positive sentiment",
        )
        assert isinstance(ann_id, int)
        assert ann_id > 0

    def test_insert_annotation_without_notes(self, inserted_comment: str, test_user: dict):
        """Notes are optional."""
        from src.db.annotations import insert_annotation

        ann_id = insert_annotation(
            comment_id=inserted_comment,
            true_label="negative",
            user_id=test_user["user_id"],
        )
        assert ann_id > 0


# ===========================================================================
# Direct DB: activity_logs
# ===========================================================================

class TestActivityLogs:
    def test_log_action_basic(self, test_user: dict):
        """Log an action and verify it returns a valid id."""
        from src.db.activity import log_action

        log_id = log_action(
            user_id=test_user["user_id"],
            action_type="test_action",
        )
        assert isinstance(log_id, int)
        assert log_id > 0

    def test_log_action_with_comment_and_details(self, inserted_comment: str, test_user: dict):
        """Log an action with optional comment_id and JSON details."""
        from src.db.activity import log_action

        log_id = log_action(
            user_id=test_user["user_id"],
            action_type="predict",
            comment_id=inserted_comment,
            details={"model": "afriberta_small", "confidence": 0.95},
        )
        assert log_id > 0

    def test_log_action_no_user(self):
        """System actions may have user_id=None."""
        from src.db.activity import log_action

        log_id = log_action(
            user_id=None,
            action_type="system_ingest",
        )
        assert log_id > 0


# ===========================================================================
# End-to-end pipeline flow
# ===========================================================================

class TestEndToEndPipeline:
    """Simulate the full ingest → preprocess → predict → annotate → log flow."""

    def test_full_pipeline(self):
        from src.db.comments import insert_comment, fetch_comment
        from src.db.preprocess import insert_preprocessed, get_preprocessed
        from src.db.predictions import insert_prediction, fetch_predictions
        from src.db.annotations import insert_annotation
        from src.db.activity import log_action
        from src.db.users import create_user

        cid = f"{TEST_PREFIX}e2e_{uuid.uuid4().hex[:12]}"

        # 1. Create a developer user
        username = f"{TEST_PREFIX}dev_{uuid.uuid4().hex[:8]}"
        user = create_user(username=username, password="dev_pass", role="developer")

        # 2. Ingest a comment
        insert_comment(
            comment_id=cid,
            text="Zikomo kwambiri! 🙏",
            source_url="https://facebook.com/post/e2e",
            collection_source="apify",
        )
        log_action(user_id=user["user_id"], action_type="ingest", comment_id=cid)

        comment = fetch_comment(cid)
        assert comment is not None
        assert comment["text"] == "Zikomo kwambiri! 🙏"
        assert comment["collection_source"] == "apify"

        # 3. Preprocess
        insert_preprocessed(
            comment_id=cid,
            cleaned_text="zikomo kwambiri :folded_hands:",
            emoji_aliases=":folded_hands:",
            emoji_count=1,
            token_count=3,
        )
        log_action(user_id=user["user_id"], action_type="preprocess", comment_id=cid)

        pp = get_preprocessed(cid)
        assert pp is not None
        assert pp["cleaned_text"] == "zikomo kwambiri :folded_hands:"

        # 4. Predict
        pred_id = insert_prediction(
            comment_id=cid,
            predicted_label="positive",
            predicted_confidence=0.95,
            score_negative=0.02,
            score_neutral=0.03,
            score_positive=0.95,
            model_name="afriberta_small",
            model_version="1.0",
            model_family="transformer",
        )
        log_action(
            user_id=user["user_id"],
            action_type="predict",
            comment_id=cid,
            details={"prediction_id": pred_id, "model": "afriberta_small"},
        )

        preds = fetch_predictions(cid)
        assert len(preds) >= 1
        assert preds[0]["predicted_label"] == "positive"

        # 5. Developer annotation
        ann_id = insert_annotation(
            comment_id=cid,
            true_label="positive",
            user_id=user["user_id"],
            notes="Confirmed positive — gratitude expression",
        )
        log_action(
            user_id=user["user_id"],
            action_type="annotation_upload",
            comment_id=cid,
            details={"annotation_id": ann_id},
        )
        assert ann_id > 0
