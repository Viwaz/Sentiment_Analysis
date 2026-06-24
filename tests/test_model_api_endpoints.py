from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from fastapi.testclient import TestClient

from src import model_api


@dataclass
class DummyModelInfo:
    reference_name: str
    model_family: str
    model_name: str = "dummy_sentiment_model"
    model_version: str = "test"
    metadata: dict | None = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {"source": "test"}


class DummyModelService:
    def __init__(self, reference_name: str, model_family: str):
        self.info = DummyModelInfo(reference_name=reference_name, model_family=model_family)

    def _prediction(self, record: dict) -> dict:
        return {
            **record,
            "predicted_label": "positive",
            "predicted_confidence": 0.88,
            "score_negative": 0.02,
            "score_neutral": 0.10,
            "score_positive": 0.88,
            "model_name": self.info.model_name,
            "model_version": self.info.model_version,
            "model_family": self.info.model_family,
            "predicted_at": "2026-06-23T00:00:00+00:00",
        }

    def predict_one(self, record):
        return self._prediction(dict(record))

    def predict_batch(self, records: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame([self._prediction(row) for row in records.to_dict(orient="records")])


def _configure_dummy_model(monkeypatch, reference_name: str, model_family: str) -> None:
    monkeypatch.setattr(model_api, "MODEL_REFERENCE", reference_name)
    monkeypatch.setattr(model_api, "TRANSFORMER_RUN_NAME", "afriberta_small")
    monkeypatch.setattr(model_api, "_model_service", DummyModelService(reference_name, model_family))
    monkeypatch.setattr(model_api, "_model_load_error", None)


def test_transformer_model_api_endpoints(monkeypatch):
    _configure_dummy_model(monkeypatch, reference_name="afriberta_small", model_family="transformer")
    client = TestClient(model_api.app)

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    assert health.json()["model_loaded"] is True
    assert health.json()["active_model_reference"] == "afriberta_small"

    info = client.get("/model-info")
    assert info.status_code == 200
    assert info.json()["active_model_reference"] == "afriberta_small"
    assert info.json()["model_family"] == "transformer"
    assert info.json()["labels"] == ["negative", "neutral", "positive"]

    prediction = client.post(
        "/predict",
        json={"id": "1", "text": "optional original text", "cleaned_text": "imihigo myiza cyane"},
    )
    assert prediction.status_code == 200
    pred_data = prediction.json()
    assert pred_data["predicted_label"] in ["negative", "neutral", "positive"]
    assert pred_data["model_family"] == "transformer"
    assert {"score_negative", "score_neutral", "score_positive"} <= pred_data.keys()


def test_baseline_model_api_batch_endpoint(monkeypatch):
    _configure_dummy_model(monkeypatch, reference_name="baseline", model_family="classical_ml")
    client = TestClient(model_api.app)

    info = client.get("/model-info")
    assert info.status_code == 200
    assert info.json()["active_model_reference"] == "baseline"
    assert info.json()["model_family"] == "classical_ml"

    response = client.post(
        "/predict-batch",
        json={
            "records": [
                {"id": "1", "cleaned_text": "imihigo myiza cyane"},
                {"id": "2", "cleaned_text": "turaje murakoze"},
            ]
        },
    )

    assert response.status_code == 200
    predictions = response.json()["predictions"]
    assert len(predictions) == 2
    assert predictions[0]["id"] == "1"
    assert predictions[1]["id"] == "2"
    assert {row["model_family"] for row in predictions} == {"classical_ml"}
