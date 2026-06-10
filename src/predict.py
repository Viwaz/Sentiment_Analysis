from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy.special import softmax

from .data_utils import build_paths, ensure_project_dirs
from .evaluate_external import transform_with_saved_vectorizer
from .preprocess import clean_text

LABELS = ["negative", "neutral", "positive"]
LABEL_TO_ID = {label: idx for idx, label in enumerate(LABELS)}
ID_TO_LABEL = {idx: label for label, idx in LABEL_TO_ID.items()}

REFERENCE_MODELS = {
    "baseline": {
        "family": "classical_ml",
        "model_dir": ("baseline", "best_baseline_model.joblib"),
        "vectorizer_dir": ("baseline", "best_baseline_vectorizer.joblib"),
        "artifact_type": "joblib",
    },
    "afriberta_small": {
        "family": "transformer",
        "model_dir": ("transformer", "afriberta_small", "best_model"),
        "tokenizer_dir": ("transformer", "afriberta_small", "best_tokenizer"),
        "artifact_type": "transformer",
    },
}
def _ensure_text_column(df: pd.DataFrame) -> pd.DataFrame:
    text_candidates = ["text", "comment_text", "Comment"]
    text_col = next((col for col in text_candidates if col in df.columns), None)
    if text_col is None:
        raise ValueError(f"Input CSV must contain one of these text columns: {', '.join(text_candidates)}")
    if text_col != "text":
        df = df.rename(columns={text_col: "text"})
    if "id" not in df.columns:
        df = df.copy()
        df["id"] = range(1, len(df) + 1)
    return df


def load_input_csv(input_path: Path) -> pd.DataFrame:
    if not input_path.exists():
        raise FileNotFoundError(f"Input CSV not found: {input_path}")
    df = pd.read_csv(input_path)
    df = _ensure_text_column(df)
    df = df[df["text"].notna() & df["text"].astype(str).str.strip().ne("")].copy()
    if df.empty:
        raise ValueError("Input CSV does not contain any usable text rows.")
    return df


def _probabilities_from_estimator(model, X) -> np.ndarray:
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(X)
        if probs.shape[1] != len(LABELS):
            probs = np.asarray(probs)
        return probs
    if hasattr(model, "decision_function"):
        decisions = model.decision_function(X)
        decisions = np.asarray(decisions)
        if decisions.ndim == 1:
            decisions = np.column_stack([-decisions, decisions])
        return softmax(decisions, axis=1)
    raise AttributeError("Model does not expose predict_proba or decision_function.")


def predict_baseline(paths, input_df: pd.DataFrame) -> pd.DataFrame:
    model = joblib.load(paths.models_dir / "baseline" / "best_baseline_model.joblib")
    vectorizer = joblib.load(paths.models_dir / "baseline" / "best_baseline_vectorizer.joblib")
    input_df = input_df.copy()
    input_df["cleaned_text"] = input_df["text"].apply(clean_text)
    X = transform_with_saved_vectorizer(vectorizer, input_df["cleaned_text"])
    probabilities = _probabilities_from_estimator(model, X)
    predicted_ids = np.argmax(probabilities, axis=1)
    output = input_df.copy()
    output["predicted_label"] = [ID_TO_LABEL[int(idx)] for idx in predicted_ids]
    output["predicted_confidence"] = probabilities.max(axis=1)
    for idx, label in enumerate(LABELS):
        output[f"score_{label}"] = probabilities[:, idx]
    return output


def predict_transformer(paths, input_df: pd.DataFrame, run_name: str = "afriberta_small") -> pd.DataFrame:
    from datasets import Dataset
    from transformers import (
        AutoModelForSequenceClassification,
        AutoTokenizer,
        DataCollatorWithPadding,
        Trainer,
        TrainingArguments,
    )

    run_root = paths.models_dir / "transformer" / run_name
    model_dir = run_root / "best_model"
    tokenizer_dir = run_root / "best_tokenizer"
    if not model_dir.exists():
        raise FileNotFoundError(f"Transformer model not found at {model_dir}")

    tokenizer_source = tokenizer_dir if tokenizer_dir.exists() else model_dir
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_source)
    model = AutoModelForSequenceClassification.from_pretrained(model_dir)

    frame = input_df.copy()
    frame["cleaned_text"] = frame["text"].apply(clean_text)
    dataset = pd.DataFrame({"cleaned_text": frame["cleaned_text"]})

    ds = Dataset.from_pandas(dataset, preserve_index=False)

    def tokenize_batch(batch):
        return tokenizer(batch["cleaned_text"], truncation=True, max_length=128)

    tokenized = ds.map(tokenize_batch, batched=True)
    keep_columns = {"input_ids", "attention_mask"}
    if "token_type_ids" in tokenized.column_names:
        keep_columns.add("token_type_ids")
    tokenized = tokenized.remove_columns([col for col in tokenized.column_names if col not in keep_columns])

    trainer = Trainer(
        model=model,
        args=TrainingArguments(
            output_dir=str(run_root / "batch_inference_tmp"),
            per_device_eval_batch_size=8,
            report_to="none",
        ),
        data_collator=DataCollatorWithPadding(tokenizer=tokenizer),
    )
    predictions = trainer.predict(tokenized)
    probabilities = softmax(np.asarray(predictions.predictions), axis=1)
    predicted_ids = np.argmax(probabilities, axis=1)

    output = frame.copy()
    output["predicted_label"] = [ID_TO_LABEL[int(idx)] for idx in predicted_ids]
    output["predicted_confidence"] = probabilities.max(axis=1)
    for idx, label in enumerate(LABELS):
        output[f"score_{label}"] = probabilities[:, idx]
    return output


def run_batch_prediction(
    input_path: str | Path,
    output_path: str | Path,
    reference_model: str = "baseline",
    run_name: str = "afriberta_small",
    root: Path | None = None,
) -> pd.DataFrame:
    paths = build_paths(root)
    ensure_project_dirs(paths)

    input_path = Path(input_path)
    output_path = Path(output_path)
    df = load_input_csv(input_path)

    if reference_model == "baseline":
        output_df = predict_baseline(paths, df)
    else:
        output_df = predict_transformer(paths, df, run_name=run_name)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_df.to_csv(output_path, index=False, encoding="utf-8")
    return output_df


def main() -> None:
    parser = argparse.ArgumentParser(description="Batch sentiment inference for saved models.")
    parser.add_argument("--input_path", required=True, help="CSV file containing new comments.")
    parser.add_argument(
        "--output_path",
        default="reports/results/batch_predictions.csv",
        help="Where to write prediction results.",
    )
    parser.add_argument(
        "--reference_model",
        choices=sorted(REFERENCE_MODELS),
        default="baseline",
        help="Which saved reference model to use.",
    )
    parser.add_argument(
        "--run_name",
        default="afriberta_small",
        help="Transformer run folder name when reference_model is not baseline.",
    )
    args = parser.parse_args()

    predictions = run_batch_prediction(
        input_path=args.input_path,
        output_path=args.output_path,
        reference_model=args.reference_model,
        run_name=args.run_name,
    )
    print(f"Wrote {len(predictions)} predictions to {args.output_path}")


if __name__ == "__main__":
    main()
