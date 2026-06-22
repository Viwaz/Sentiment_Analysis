from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

import joblib
import numpy as np
import pandas as pd
from scipy.sparse import hstack
from scipy.special import softmax

from .data_utils import DatasetPaths, build_paths

LABELS = ["negative", "neutral", "positive"]
LABEL_TO_ID = {label: idx for idx, label in enumerate(LABELS)}
SCORE_COLUMNS = [f"score_{label}" for label in LABELS]

REFERENCE_MODELS = {
    "baseline": {
        "family": "classical_ml",
        "model_path": ("baseline", "best_baseline_model.joblib"),
        "vectorizer_path": ("baseline", "best_baseline_vectorizer.joblib"),
        "metadata_path": ("baseline", "model_metadata.json"),
    },
    "afriberta_small": {
        "family": "transformer",
        "run_name": "afriberta_small",
        "model_path": ("transformer", "afriberta_small", "best_model"),
        "tokenizer_path": ("transformer", "afriberta_small", "best_tokenizer"),
        "metadata_path": ("transformer", "afriberta_small", "model_metadata.json"),
    },
}


@dataclass
class ModelServiceInfo:
    reference_name: str
    model_family: str
    model_name: str
    model_version: str
    metadata: dict


def _load_metadata(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _metadata_model_name(reference_name: str, metadata: dict) -> str:
    if metadata.get("model_name"):
        return str(metadata["model_name"])
    best_run = metadata.get("best_validation_run", {})
    model_name = best_run.get("model_name")
    feature_set = best_run.get("feature_set")
    if model_name and feature_set:
        return f"{model_name}+{feature_set}"
    return reference_name


def _metadata_version(reference_name: str, metadata: dict) -> str:
    return str(metadata.get("run_id") or metadata.get("reference_name") or reference_name)


def _require_cleaned_text(records: pd.DataFrame) -> pd.DataFrame:
    if "cleaned_text" not in records.columns:
        raise ValueError("Model service input must include a 'cleaned_text' column.")
    frame = records.copy()
    frame = frame[frame["cleaned_text"].notna() & frame["cleaned_text"].astype(str).str.strip().ne("")]
    if frame.empty:
        raise ValueError("Model service input does not contain any usable cleaned_text rows.")
    
    if "id" not in frame.columns:
        frame["id"] = range(1, len(frame) + 1)
    else:
        # If id column is present, fill any null/NaN values
        null_ids = frame["id"].isna() | frame["id"].isnull()
        if null_ids.any():
            fallback_ids = list(range(1, len(frame) + 1))
            # Align fallbacks with original index
            frame.loc[null_ids, "id"] = [fallback_ids[i] for i, val in enumerate(null_ids) if val]

    if "text" not in frame.columns:
        frame["text"] = frame["cleaned_text"]
    else:
        # If text column is present, fill null/NaN or empty values with cleaned_text
        frame["text"] = frame["text"].fillna(frame["cleaned_text"])
        empty_text = frame["text"].astype(str).str.strip() == ""
        frame.loc[empty_text, "text"] = frame["cleaned_text"]
        
    return frame


def _align_probabilities(probabilities: np.ndarray, classes: list[object] | np.ndarray | None) -> np.ndarray:
    probabilities = np.asarray(probabilities)
    if classes is None:
        if probabilities.shape[1] != len(LABELS):
            raise ValueError("Cannot align model probabilities without class labels.")
        return probabilities

    aligned = np.zeros((probabilities.shape[0], len(LABELS)), dtype=float)
    for source_idx, label in enumerate(classes):
        label_key = str(label)
        if label_key in LABEL_TO_ID:
            aligned[:, LABEL_TO_ID[label_key]] = probabilities[:, source_idx]
    return aligned


def _probabilities_from_estimator(model, features) -> np.ndarray:
    classes = getattr(model, "classes_", None)
    if hasattr(model, "predict_proba"):
        return _align_probabilities(model.predict_proba(features), classes)
    if hasattr(model, "decision_function"):
        decisions = np.asarray(model.decision_function(features))
        if decisions.ndim == 1:
            decisions = np.column_stack([-decisions, decisions])
        return _align_probabilities(softmax(decisions, axis=1), classes)
    raise AttributeError("Model does not expose predict_proba or decision_function.")


def transform_with_saved_vectorizer(vectorizer, texts: pd.Series):
    if isinstance(vectorizer, dict):
        return hstack(
            [
                vectorizer["word"].transform(texts),
                vectorizer["char"].transform(texts),
            ]
        ).tocsr()
    return vectorizer.transform(texts)


def _build_prediction_frame(
    records: pd.DataFrame,
    probabilities: np.ndarray,
    info: ModelServiceInfo,
) -> pd.DataFrame:
    predicted_ids = np.argmax(probabilities, axis=1)
    prediction_time = datetime.now(timezone.utc).isoformat()

    output = records.copy()
    output["predicted_label"] = [LABELS[int(idx)] for idx in predicted_ids]
    output["predicted_confidence"] = probabilities.max(axis=1)
    for idx, label in enumerate(LABELS):
        output[f"score_{label}"] = probabilities[:, idx]
    output["model_name"] = info.model_name
    output["model_version"] = info.model_version
    output["model_family"] = info.model_family
    output["predicted_at"] = prediction_time
    return output


class SentimentModelService:
    def __init__(self, info: ModelServiceInfo):
        self.info = info

    def predict_batch(self, records: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError

    def predict_one(self, record: Mapping[str, object]) -> dict:
        result = self.predict_batch(pd.DataFrame([dict(record)]))
        return result.iloc[0].to_dict()


class BaselineModelService(SentimentModelService):
    def __init__(self, paths: DatasetPaths, reference_name: str, config: dict):
        metadata_path = paths.models_dir.joinpath(*config["metadata_path"])
        metadata = _load_metadata(metadata_path)
        info = ModelServiceInfo(
            reference_name=reference_name,
            model_family="classical_ml",
            model_name=_metadata_model_name(reference_name, metadata),
            model_version=_metadata_version(reference_name, metadata),
            metadata=metadata,
        )
        super().__init__(info)
        self.model = joblib.load(paths.models_dir.joinpath(*config["model_path"]))
        self.vectorizer = joblib.load(paths.models_dir.joinpath(*config["vectorizer_path"]))

    def predict_batch(self, records: pd.DataFrame) -> pd.DataFrame:
        frame = _require_cleaned_text(records)
        features = transform_with_saved_vectorizer(self.vectorizer, frame["cleaned_text"])
        probabilities = _probabilities_from_estimator(self.model, features)
        return _build_prediction_frame(frame, probabilities, self.info)


class TransformerModelService(SentimentModelService):
    def __init__(self, paths: DatasetPaths, reference_name: str, config: dict, run_name: str | None = None):
        run_name = run_name or config["run_name"]
        model_dir = paths.models_dir / "transformer" / run_name / "best_model"
        tokenizer_dir = paths.models_dir / "transformer" / run_name / "best_tokenizer"
        metadata_path = paths.models_dir / "transformer" / run_name / "model_metadata.json"
        if not model_dir.exists():
            raise FileNotFoundError(f"Transformer model not found at {model_dir}")

        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        metadata = _load_metadata(metadata_path)
        info = ModelServiceInfo(
            reference_name=reference_name,
            model_family="transformer",
            model_name=_metadata_model_name(reference_name, metadata),
            model_version=_metadata_version(run_name, metadata),
            metadata=metadata,
        )
        super().__init__(info)
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_dir if tokenizer_dir.exists() else model_dir)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_dir)

    def predict_batch(self, records: pd.DataFrame) -> pd.DataFrame:
        import torch

        frame = _require_cleaned_text(records)
        encoded = self.tokenizer(
            frame["cleaned_text"].astype(str).tolist(),
            truncation=True,
            padding=True,
            max_length=128,
            return_tensors="pt",
        )
        self.model.eval()
        with torch.no_grad():
            logits = self.model(**encoded).logits.detach().cpu().numpy()
        probabilities = softmax(logits, axis=1)
        return _build_prediction_frame(frame, probabilities, self.info)


def load_model(
    reference_name: str = "baseline",
    root: Path | None = None,
    run_name: str | None = None,
) -> SentimentModelService:
    if reference_name not in REFERENCE_MODELS:
        available = ", ".join(sorted(REFERENCE_MODELS))
        raise ValueError(f"Unknown reference model '{reference_name}'. Available: {available}")

    paths = build_paths(root)
    config = REFERENCE_MODELS[reference_name]
    if config["family"] == "classical_ml":
        return BaselineModelService(paths, reference_name, config)
    return TransformerModelService(paths, reference_name, config, run_name=run_name)
