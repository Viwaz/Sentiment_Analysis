from __future__ import annotations

import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# DB helpers
from src.db.comments import insert_comment, fetch_comment, fetch_comments_missing_preprocessing
from src.db.preprocess import insert_preprocessed, fetch_preprocessed_missing_predictions
from src.db.predictions import insert_prediction, fetch_predictions_with_comments
from src.db.activity import log_action

# Processing
from src.preprocess import clean_text

# Model service (kept for predict endpoints)
try:
    from .model_service import LABELS, SentimentModelService, load_model
except ImportError:
    LABELS = []
    SentimentModelService = None  # type: ignore
    load_model = None  # type: ignore

DEFAULT_MODEL_REFERENCE = "afriberta_small"
DEFAULT_TRANSFORMER_RUN_NAME = "afriberta_small"

MODEL_REFERENCE = os.getenv("MODEL_REFERENCE", DEFAULT_MODEL_REFERENCE)
TRANSFORMER_RUN_NAME = os.getenv("TRANSFORMER_RUN_NAME", DEFAULT_TRANSFORMER_RUN_NAME)

_model_service: SentimentModelService | None = None
_model_load_error: str | None = None


class CommentCreate(BaseModel):
    comment_id: str
    comment_text: str | None = None
    text: str | None = None  # backward compatibility
    source_url: str | None = None
    collection_source: str | None = None
    created_at: str | None = None
    apify_dataset_id: str | None = None
    apify_run_id: str | None = None


class CommentRead(BaseModel):
    comment_id: str
    comment_text: str
    text: str  # backward compatibility
    source_url: str
    created_at: datetime | str | None = None
    date_collected: datetime | str
    ingested_at: datetime | str  # backward compatibility
    collection_source: str
    apify_dataset_id: str | None = None
    apify_run_id: str | None = None


class PipelineRequest(BaseModel):
    comment_id: str
    comment_text: str | None = None
    text: str | None = None  # backward compatibility
    source_url: str | None = None
    collection_source: str | None = None
    created_at: str | None = None
    apify_dataset_id: str | None = None
    apify_run_id: str | None = None
    user_id: int | None = None


class PipelineResponse(BaseModel):
    comment_id: str
    comment_text: str
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


class PreprocessDbBatchRequest(BaseModel):
    limit: int = Field(default=100, ge=1, le=1000)
    user_id: int | None = None
    overwrite: bool = False


class PreprocessDbBatchResponse(BaseModel):
    processed_count: int
    comment_ids: list[str]


class PredictDbBatchRequest(BaseModel):
    limit: int = Field(default=100, ge=1, le=1000)
    user_id: int | None = None


class DashboardPrediction(BaseModel):
    prediction_id: int
    comment_id: str
    comment_text: str
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


class PredictDbBatchResponse(BaseModel):
    prediction_count: int
    predictions: list[PredictionResponse]


class PredictResponseSingle(BaseModel):
    predicted_label: str
    predicted_confidence: float
    score_negative: float
    score_neutral: float
    score_positive: float
    model_name: str
    model_version: str
    model_family: str
    predicted_at: str


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


@app.post("/comments", response_model=CommentRead)
def create_comment(comment: CommentCreate) -> CommentRead:
    """Insert a comment into the DB and return the stored record."""
    if not (comment.comment_text or comment.text):
        raise HTTPException(status_code=422, detail="comment_text or text field is required")

    inserted_id = insert_comment(
        comment_id=comment.comment_id,
        comment_text=comment.comment_text,
        text=comment.text,
        source_url=comment.source_url,
        collection_source=comment.collection_source,
        created_at=comment.created_at,
        apify_dataset_id=comment.apify_dataset_id,
        apify_run_id=comment.apify_run_id,
    )
    # fetch the full row to return
    row = fetch_comment(inserted_id)
    return CommentRead(**row)


@app.get("/comments/{comment_id}", response_model=CommentRead)
def read_comment(comment_id: str) -> CommentRead:
    """Retrieve a comment by its comment_id."""
    row = fetch_comment(comment_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return CommentRead(**row)


@app.post("/predict-pipeline", response_model=PipelineResponse)
def predict_pipeline(req: PipelineRequest) -> PipelineResponse:
    """
    Unified endpoint to ingest raw comment, preprocess it, generate predictions,
    store everything in the database, log activities, and return predictions.
    """
    actual_text = req.comment_text or req.text
    if not actual_text:
        raise HTTPException(status_code=422, detail="comment_text or text field is required")

    # 1. Ingest comment
    insert_comment(
        comment_id=req.comment_id,
        comment_text=actual_text,
        source_url=req.source_url,
        collection_source=req.collection_source,
        created_at=req.created_at,
        apify_dataset_id=req.apify_dataset_id,
        apify_run_id=req.apify_run_id,
    )
    log_action(user_id=req.user_id, action_type="ingest", comment_id=req.comment_id)

    # 2. Preprocess text
    cleaned = clean_text(actual_text)
    insert_preprocessed(comment_id=req.comment_id, cleaned_text=cleaned)
    log_action(user_id=req.user_id, action_type="preprocess", comment_id=req.comment_id)

    # 3. Predict sentiment
    service = _get_service()
    pred_dict = service.predict_one({
        "cleaned_text": cleaned,
        "id": req.comment_id,
        "text": actual_text,
    })

    # 4. Save prediction
    prediction_id = insert_prediction(
        comment_id=req.comment_id,
        predicted_label=pred_dict["predicted_label"],
        predicted_confidence=float(pred_dict["predicted_confidence"]),
        score_negative=float(pred_dict["score_negative"]),
        score_neutral=float(pred_dict["score_neutral"]),
        score_positive=float(pred_dict["score_positive"]),
        model_name=pred_dict["model_name"],
        model_version=pred_dict["model_version"],
        model_family=pred_dict["model_family"],
    )
    log_action(
        user_id=req.user_id,
        action_type="predict",
        comment_id=req.comment_id,
        details={"prediction_id": prediction_id, "model_name": pred_dict["model_name"]},
    )

    return PipelineResponse(
        comment_id=req.comment_id,
        comment_text=actual_text,
        cleaned_text=cleaned,
        predicted_label=pred_dict["predicted_label"],
        predicted_confidence=float(pred_dict["predicted_confidence"]),
        score_negative=float(pred_dict["score_negative"]),
        score_neutral=float(pred_dict["score_neutral"]),
        score_positive=float(pred_dict["score_positive"]),
        model_name=pred_dict["model_name"],
        model_version=pred_dict["model_version"],
        model_family=pred_dict["model_family"],
        predicted_at=str(pred_dict["predicted_at"]),
    )


@app.post("/preprocess-db-batch", response_model=PreprocessDbBatchResponse)
def preprocess_db_batch(req: PreprocessDbBatchRequest) -> PreprocessDbBatchResponse:
    """Preprocess raw DB comments into preprocessed_comments."""
    rows = fetch_comments_missing_preprocessing(limit=req.limit, overwrite=req.overwrite)
    processed_ids: list[str] = []
    for row in rows:
        comment_id = str(row["comment_id"])
        cleaned = clean_text(row["comment_text"])
        if not cleaned:
            continue

        insert_preprocessed(comment_id=comment_id, cleaned_text=cleaned)
        log_action(
            user_id=req.user_id,
            action_type="preprocess",
            comment_id=comment_id,
            details={"source": "preprocess_db_batch"},
        )
        processed_ids.append(comment_id)

    return PreprocessDbBatchResponse(processed_count=len(processed_ids), comment_ids=processed_ids)


@app.post("/predict-db-batch", response_model=PredictDbBatchResponse)
def predict_db_batch(req: PredictDbBatchRequest) -> PredictDbBatchResponse:
    """Predict sentiment for existing DB preprocessed rows and store predictions."""
    service = _get_service()
    rows = fetch_preprocessed_missing_predictions(
        model_name=service.info.model_name,
        model_version=service.info.model_version,
        model_family=service.info.model_family,
        limit=req.limit,
    )
    if not rows:
        return PredictDbBatchResponse(prediction_count=0, predictions=[])

    frame = pd.DataFrame(
        [
            {
                "id": row["comment_id"],
                "text": row["comment_text"],
                "cleaned_text": row["cleaned_text"],
            }
            for row in rows
        ]
    )
    pred_frame = service.predict_batch(frame)
    predictions: list[PredictionResponse] = []

    for pred in pred_frame.to_dict(orient="records"):
        comment_id = str(pred["id"])
        prediction_id = insert_prediction(
            comment_id=comment_id,
            predicted_label=str(pred["predicted_label"]),
            predicted_confidence=float(pred["predicted_confidence"]),
            score_negative=float(pred["score_negative"]),
            score_neutral=float(pred["score_neutral"]),
            score_positive=float(pred["score_positive"]),
            model_name=str(pred["model_name"]),
            model_version=str(pred["model_version"]),
            model_family=str(pred["model_family"]),
        )
        log_action(
            user_id=req.user_id,
            action_type="predict",
            comment_id=comment_id,
            details={"source": "predict_db_batch", "prediction_id": prediction_id},
        )
        predictions.append(PredictionResponse(**_normalise_prediction_row(pred)))

    return PredictDbBatchResponse(prediction_count=len(predictions), predictions=predictions)


@app.get("/dashboard/predictions", response_model=list[DashboardPrediction])
def get_dashboard_predictions() -> list[DashboardPrediction]:
    """Retrieve all predictions with comment text and preprocessed text for dashboard access."""
    rows = fetch_predictions_with_comments()
    return [DashboardPrediction(**row) for row in rows]


@app.post("/predict", response_model=PredictResponseSingle)
def predict_single(record: PredictionRecord) -> PredictResponseSingle:
    """Predict sentiment of a single preprocessed comment record."""
    service = _get_service()
    row = _record_to_dict(record)
    pred = service.predict_one(row)
    return PredictResponseSingle(
        predicted_label=pred["predicted_label"],
        predicted_confidence=pred["predicted_confidence"],
        score_negative=pred["score_negative"],
        score_neutral=pred["score_neutral"],
        score_positive=pred["score_positive"],
        model_name=pred["model_name"],
        model_version=pred["model_version"],
        model_family=pred["model_family"],
        predicted_at=str(pred["predicted_at"]),
    )


@app.post("/predict-batch", response_model=BatchPredictionResponse)
def predict_batch_endpoint(request: BatchPredictionRequest) -> BatchPredictionResponse:
    """Predict sentiment of a batch of preprocessed comment records."""
    service = _get_service()
    frame = _records_to_frame(request.records)
    pred_frame = service.predict_batch(frame)
    responses = _prediction_frame_to_responses(pred_frame)
    return BatchPredictionResponse(predictions=responses)

