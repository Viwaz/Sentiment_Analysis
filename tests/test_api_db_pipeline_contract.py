from __future__ import annotations

from fastapi.testclient import TestClient

from src import model_api


class DummyModelService:
    def predict_one(self, record):
        return {
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
