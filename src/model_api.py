from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import Any

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .model_service import LABELS, SentimentModelService, load_model

DEFAULT_MODEL_REFERENCE = "afriberta_small"
DEFAULT_TRANSFORMER_RUN_NAME = "afriberta_small"

MODEL_REFERENCE = os.getenv("MODEL_REFERENCE", DEFAULT_MODEL_REFERENCE)
TRANSFORMER_RUN_NAME = os.getenv("TRANSFORMER_RUN_NAME", DEFAULT_TRANSFORMER_RUN_NAME)

_model_service: SentimentModelService | None = None
_model_load_error: str | None = None


class PredictionRecord(BaseModel):
    id: str | int | None = None
    text: str | None = None
    cleaned_text: str = Field(..., min_length=1)


class BatchPredictionRequest(BaseModel):
    records: list[PredictionRecord] = Field(..., min_length=1)


class PredictionResponse(BaseModel):
    id: str | int
    text: str
    cleaned_text: str
    predicted_label: str
    predicted_confidence: float
    score_negative: float
    score_neutral: float
    score_positive: float
    model_name: str
    model_version: str
    model_family: str
    predicted_at: str


class BatchPredictionResponse(BaseModel):
    predictions: list[PredictionResponse]


class HealthResponse(BaseModel):
    status: str
    active_model_reference: str
    transformer_run_name: str
    model_loaded: bool
    error: str | None = None


class ModelInfoResponse(BaseModel):
    active_model_reference: str
    model_name: str
    model_version: str
    model_family: str
    labels: list[str]
    metadata: dict[str, Any]


def _record_to_dict(record: PredictionRecord) -> dict:
    if hasattr(record, "model_dump"):
        return record.model_dump()
    return record.dict()


def _records_to_frame(records: list[PredictionRecord]) -> pd.DataFrame:
    return pd.DataFrame([_record_to_dict(record) for record in records])


def _normalise_prediction_row(row: dict) -> dict:
    id_val = row.get("id")
    if pd.isna(id_val) or id_val is None:
        id_val = ""
    elif isinstance(id_val, float) and id_val.is_integer():
        id_val = int(id_val)

    text_val = row.get("text")
    if pd.isna(text_val) or text_val is None:
        text_val = row.get("cleaned_text")

    return {
        "id": id_val,
        "text": str(text_val),
        "cleaned_text": str(row.get("cleaned_text")),
        "predicted_label": str(row.get("predicted_label")),
        "predicted_confidence": float(row.get("predicted_confidence")),
        "score_negative": float(row.get("score_negative")),
        "score_neutral": float(row.get("score_neutral")),
        "score_positive": float(row.get("score_positive")),
        "model_name": str(row.get("model_name")),
        "model_version": str(row.get("model_version")),
        "model_family": str(row.get("model_family")),
        "predicted_at": str(row.get("predicted_at")),
    }


def _prediction_frame_to_responses(frame: pd.DataFrame) -> list[PredictionResponse]:
    rows = [_normalise_prediction_row(row) for row in frame.to_dict(orient="records")]
    return [PredictionResponse(**row) for row in rows]


def _load_service() -> None:
    global _model_service, _model_load_error
    try:
        _model_service = load_model(
            reference_name=MODEL_REFERENCE,
            run_name=TRANSFORMER_RUN_NAME,
        )
        _model_load_error = None
    except Exception as exc:
        _model_service = None
        _model_load_error = str(exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    _load_service()
    yield


app = FastAPI(
    title="Sentiment Model Service",
    version="1.0.0",
    description="Hosted inference API for the sentiment classification model.",
    lifespan=lifespan,
)


def _get_service() -> SentimentModelService:
    if _model_service is None:
        detail = "Model service is not loaded."
        if _model_load_error:
            detail = f"{detail} Last error: {_model_load_error}"
        raise HTTPException(status_code=503, detail=detail)
    return _model_service


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    model_loaded = _model_service is not None
    return HealthResponse(
        status="ok" if model_loaded else "degraded",
        active_model_reference=MODEL_REFERENCE,
        transformer_run_name=TRANSFORMER_RUN_NAME,
        model_loaded=model_loaded,
        error=_model_load_error,
    )


@app.get("/model-info", response_model=ModelInfoResponse)
def model_info() -> ModelInfoResponse:
    service = _get_service()
    return ModelInfoResponse(
        active_model_reference=service.info.reference_name,
        model_name=service.info.model_name,
        model_version=service.info.model_version,
        model_family=service.info.model_family,
        labels=LABELS,
        metadata=service.info.metadata,
    )


@app.post("/predict", response_model=PredictionResponse)
def predict(record: PredictionRecord) -> PredictionResponse:
    service = _get_service()
    frame = service.predict_batch(_records_to_frame([record]))
    return _prediction_frame_to_responses(frame)[0]


@app.post("/predict-batch", response_model=BatchPredictionResponse)
def predict_batch(payload: BatchPredictionRequest) -> BatchPredictionResponse:
    service = _get_service()
    frame = service.predict_batch(_records_to_frame(payload.records))
    return BatchPredictionResponse(predictions=_prediction_frame_to_responses(frame))
