from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from fastapi.testclient import TestClient

from src import model_api


@dataclass
class DummyModelInfo:
    model_name: str = "dummy_model"
    model_version: str = "test"
    model_family: str = "test_double"


class DummyModelService:
    def __init__(self):
        self.info = DummyModelInfo()

    def predict_one(self, record):
        return {
            "predicted_label": "positive",
            "predicted_confidence": 0.87,
            "score_negative": 0.03,
            "score_neutral": 0.10,
            "score_positive": 0.87,
            "model_name": self.info.model_name,
            "model_version": self.info.model_version,
            "model_family": self.info.model_family,
            "predicted_at": "2026-06-23T00:00:00+00:00",
        }

    def predict_batch(self, records: pd.DataFrame) -> pd.DataFrame:
        frame = records.copy()
        frame["predicted_label"] = "positive"
        frame["predicted_confidence"] = 0.87
        frame["score_negative"] = 0.03
        frame["score_neutral"] = 0.10
        frame["score_positive"] = 0.87
        frame["model_name"] = self.info.model_name
        frame["model_version"] = self.info.model_version
        frame["model_family"] = self.info.model_family
        frame["predicted_at"] = "2026-06-23T00:00:00+00:00"
        return frame


def test_predict_pipeline_persists_each_pipeline_stage(monkeypatch):
    calls = []

    monkeypatch.setattr(model_api, "_model_service", DummyModelService())
    monkeypatch.setattr(model_api, "_model_load_error", None)
    monkeypatch.setattr(
        model_api,
        "insert_comment",
        lambda **kwargs: calls.append(("insert_comment", kwargs)) or kwargs["comment_id"],
    )
    monkeypatch.setattr(
        model_api,
        "insert_preprocessed",
        lambda **kwargs: calls.append(("insert_preprocessed", kwargs)) or 101,
    )
    monkeypatch.setattr(
        model_api,
        "insert_prediction",
        lambda **kwargs: calls.append(("insert_prediction", kwargs)) or 202,
    )
    monkeypatch.setattr(
        model_api,
        "log_action",
        lambda **kwargs: calls.append(("log_action", kwargs)) or len(calls),
    )

    client = TestClient(model_api.app)
    response = client.post(
        "/predict-pipeline",
        json={
            "comment_id": "api_db_001",
            "text": "Great service!",
            "source_url": "https://facebook.com/post/1",
            "collection_source": "test",
            "user_id": 7,
        },
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["comment_id"] == "api_db_001"
    assert data["comment_text"] == "Great service!"
    assert data["cleaned_text"] == "great service!"
    assert data["predicted_label"] == "positive"

    call_names = [name for name, _ in calls]
    assert call_names == [
        "insert_comment",
        "log_action",
        "insert_preprocessed",
        "log_action",
        "insert_prediction",
        "log_action",
    ]

    assert calls[0][1]["comment_id"] == "api_db_001"
    assert calls[0][1]["comment_text"] == "Great service!"
    assert calls[2][1]["comment_id"] == "api_db_001"
    assert calls[2][1]["cleaned_text"] == "great service!"
    assert calls[4][1]["comment_id"] == "api_db_001"
    assert calls[4][1]["predicted_label"] == "positive"
    assert [payload["action_type"] for name, payload in calls if name == "log_action"] == [
        "ingest",
        "preprocess",
        "predict",
    ]


def test_dashboard_predictions_returns_joined_rows(monkeypatch):
    monkeypatch.setattr(
        model_api,
        "fetch_predictions_with_comments",
        lambda: [
            {
                "prediction_id": 202,
                "comment_id": "api_db_001",
                "comment_text": "Great service!",
                "cleaned_text": "great service !",
                "predicted_label": "positive",
                "predicted_confidence": 0.87,
                "score_negative": 0.03,
                "score_neutral": 0.10,
                "score_positive": 0.87,
                "model_name": "dummy_model",
                "model_version": "test",
                "model_family": "test_double",
                "predicted_at": "2026-06-23T00:00:00+00:00",
            }
        ],
    )

    client = TestClient(model_api.app)
    response = client.get("/dashboard/predictions")

    assert response.status_code == 200, response.text
    assert response.json()[0]["comment_id"] == "api_db_001"
    assert response.json()[0]["cleaned_text"] == "great service !"


def test_preprocess_db_batch_reads_raw_comments_and_writes_cleaned_rows(monkeypatch):
    calls = []

    monkeypatch.setattr(
        model_api,
        "fetch_comments_missing_preprocessing",
        lambda **kwargs: calls.append(("fetch_comments_missing_preprocessing", kwargs))
        or [{"comment_id": "comment-1", "comment_text": "Great service!"}],
    )
    monkeypatch.setattr(
        model_api,
        "insert_preprocessed",
        lambda **kwargs: calls.append(("insert_preprocessed", kwargs)) or 1,
    )
    monkeypatch.setattr(
        model_api,
        "log_action",
        lambda **kwargs: calls.append(("log_action", kwargs)) or 1,
    )

    client = TestClient(model_api.app)
    response = client.post("/preprocess-db-batch", json={"limit": 10, "user_id": 7})

    assert response.status_code == 200, response.text
    assert response.json() == {"processed_count": 1, "comment_ids": ["comment-1"]}
    assert calls[0] == ("fetch_comments_missing_preprocessing", {"limit": 10, "overwrite": False})
    assert calls[1][0] == "insert_preprocessed"
    assert calls[1][1]["comment_id"] == "comment-1"
    assert calls[1][1]["cleaned_text"] == "great service!"
    assert calls[2][0] == "log_action"
    assert calls[2][1]["action_type"] == "preprocess"


def test_predict_db_batch_reads_cleaned_text_from_db_and_writes_predictions(monkeypatch):
    calls = []
    service = DummyModelService()
    captured_model_input = {}
    original_predict_batch = service.predict_batch

    def predict_batch(records: pd.DataFrame) -> pd.DataFrame:
        captured_model_input["records"] = records.to_dict(orient="records")
        return original_predict_batch(records)

    service.predict_batch = predict_batch  # type: ignore[method-assign]
    monkeypatch.setattr(model_api, "_model_service", service)
    monkeypatch.setattr(model_api, "_model_load_error", None)
    monkeypatch.setattr(
        model_api,
        "fetch_preprocessed_missing_predictions",
        lambda **kwargs: calls.append(("fetch_preprocessed_missing_predictions", kwargs))
        or [
            {
                "comment_id": "comment-1",
                "comment_text": "RAW TEXT SHOULD ONLY BE METADATA",
                "cleaned_text": "cleaned model input",
            }
        ],
    )
    monkeypatch.setattr(
        model_api,
        "insert_prediction",
        lambda **kwargs: calls.append(("insert_prediction", kwargs)) or 301,
    )
    monkeypatch.setattr(
        model_api,
        "log_action",
        lambda **kwargs: calls.append(("log_action", kwargs)) or 1,
    )

    client = TestClient(model_api.app)
    response = client.post("/predict-db-batch", json={"limit": 10, "user_id": 7})

    assert response.status_code == 200, response.text
    assert response.json()["prediction_count"] == 1
    assert captured_model_input["records"] == [
        {
            "id": "comment-1",
            "text": "RAW TEXT SHOULD ONLY BE METADATA",
            "cleaned_text": "cleaned model input",
        }
    ]
    assert calls[0] == (
        "fetch_preprocessed_missing_predictions",
        {
            "model_name": "dummy_model",
            "model_version": "test",
            "model_family": "test_double",
            "limit": 10,
        },
    )
    assert calls[1][0] == "insert_prediction"
    assert calls[1][1]["comment_id"] == "comment-1"
    assert calls[1][1]["predicted_label"] == "positive"
    assert calls[2][0] == "log_action"
    assert calls[2][1]["action_type"] == "predict"
