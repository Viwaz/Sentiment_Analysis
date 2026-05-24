from __future__ import annotations

import argparse
import re
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from .data_utils import build_paths, discover_raw_files, ensure_project_dirs, load_annotation_file
from .evaluate import compute_metrics, save_confusion_matrix, save_metrics
from .preprocess import prepare_external_test_dataframe

LABELS = ["negative", "neutral", "positive"]
ID_TO_LABEL = {idx: label for idx, label in enumerate(LABELS)}
LABEL_TO_ID = {label: idx for idx, label in enumerate(LABELS)}


def safe_run_name(model_name: str, run_name: str | None = None) -> str:
    raw_name = run_name or model_name
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", raw_name).strip("_").lower()
    return safe_name or "transformer"


def load_external_dataset(root: Path | None = None) -> pd.DataFrame:
    paths = build_paths(root)
    external_files = discover_raw_files(paths.external_test_dir)
    if not external_files:
        raise FileNotFoundError(
            "No external test CSV files were found in data/external_test/. "
            "Place the second dataset there before running evaluation."
        )
    frames = [load_annotation_file(path) for path in external_files]
    merged = pd.concat(frames, ignore_index=True)
    return prepare_external_test_dataframe(merged)


def transform_with_saved_vectorizer(vectorizer, texts: pd.Series):
    if isinstance(vectorizer, dict):
        word_vectorizer = vectorizer["word"]
        char_vectorizer = vectorizer["char"]
        from scipy.sparse import hstack

        return hstack(
            [
                word_vectorizer.transform(texts),
                char_vectorizer.transform(texts),
            ]
        ).tocsr()
    return vectorizer.transform(texts)


def evaluate_external_baseline(root: Path | None = None) -> dict:
    paths = build_paths(root)
    ensure_project_dirs(paths)

    external_df = load_external_dataset(root)
    model = joblib.load(paths.models_dir / "baseline" / "best_baseline_model.joblib")
    vectorizer = joblib.load(paths.models_dir / "baseline" / "best_baseline_vectorizer.joblib")
    X_external = transform_with_saved_vectorizer(vectorizer, external_df["cleaned_text"])
    predictions = model.predict(X_external)

    metrics = compute_metrics(external_df["label"], predictions, LABELS)
    summary = {
        "dataset_rows": int(len(external_df)),
        "label_distribution": external_df["label"].value_counts().to_dict(),
        "metrics": metrics,
        "source_files": sorted(external_df["source_file"].unique().tolist()),
    }

    save_metrics(summary, paths.results_dir / "external_baseline_metrics.json")
    save_confusion_matrix(
        external_df["label"],
        predictions,
        LABELS,
        paths.figures_dir / "external_baseline_confusion_matrix.png",
        "External Baseline Confusion Matrix",
    )
    pd.DataFrame(
        {
            "text": external_df["text"],
            "cleaned_text": external_df["cleaned_text"],
            "true_label": external_df["label"],
            "predicted_label": predictions,
            "source_file": external_df["source_file"],
        }
    ).to_csv(paths.results_dir / "external_baseline_predictions.csv", index=False)
    return summary


def evaluate_external_transformer(
    root: Path | None = None,
    model_name: str = "castorini/afriberta_small",
    run_name: str | None = None,
) -> dict:
    from datasets import Dataset
    from transformers import AutoModelForSequenceClassification, AutoTokenizer, DataCollatorWithPadding, Trainer, TrainingArguments

    paths = build_paths(root)
    ensure_project_dirs(paths)
    run_id = safe_run_name(model_name, run_name)

    external_df = load_external_dataset(root)
    model_root = paths.models_dir / "transformer" / run_id
    model_dir = model_root / "best_model"
    tokenizer_dir = model_root / "best_tokenizer"
    if not model_dir.exists():
        raise FileNotFoundError(
            f"Transformer model not found at {model_dir}. "
            "Run transformer training first, or download the trained model folder from Colab."
        )

    tokenizer_source = tokenizer_dir if tokenizer_dir.exists() else model_dir
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_source)
    model = AutoModelForSequenceClassification.from_pretrained(model_dir)

    dataset = Dataset.from_pandas(external_df[["cleaned_text"]], preserve_index=False)

    def tokenize_batch(batch):
        return tokenizer(batch["cleaned_text"], truncation=True, max_length=128)

    tokenized = dataset.map(tokenize_batch, batched=True)
    keep_columns = {"input_ids", "attention_mask"}
    if "token_type_ids" in tokenized.column_names:
        keep_columns.add("token_type_ids")
    remove_columns = [col for col in tokenized.column_names if col not in keep_columns]
    tokenized = tokenized.remove_columns(remove_columns)

    trainer = Trainer(
        model=model,
        args=TrainingArguments(
            output_dir=str(paths.models_dir / "transformer" / run_id / "external_eval_tmp"),
            report_to="none",
            per_device_eval_batch_size=8,
        ),
        data_collator=DataCollatorWithPadding(tokenizer=tokenizer),
    )
    predictions = trainer.predict(tokenized)
    pred_ids = np.argmax(predictions.predictions, axis=1)
    id_to_label = {
        int(key): value
        for key, value in getattr(model.config, "id2label", ID_TO_LABEL).items()
    }
    predicted_labels = [
        id_to_label.get(int(pred_id), ID_TO_LABEL[int(pred_id)])
        for pred_id in pred_ids
    ]

    metrics = compute_metrics(external_df["label"], predicted_labels, LABELS)
    summary = {
        "model_name": model_name,
        "run_id": run_id,
        "dataset_rows": int(len(external_df)),
        "label_distribution": external_df["label"].value_counts().to_dict(),
        "metrics": metrics,
        "source_files": sorted(external_df["source_file"].unique().tolist()),
    }

    save_metrics(summary, paths.results_dir / f"external_{run_id}_metrics.json")
    save_confusion_matrix(
        external_df["label"],
        predicted_labels,
        LABELS,
        paths.figures_dir / f"external_{run_id}_confusion_matrix.png",
        f"External {run_id} Confusion Matrix",
    )
    pd.DataFrame(
        {
            "text": external_df["text"],
            "cleaned_text": external_df["cleaned_text"],
            "true_label": external_df["label"],
            "predicted_label": predicted_labels,
            "source_file": external_df["source_file"],
        }
    ).to_csv(paths.results_dir / f"external_{run_id}_predictions.csv", index=False)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a saved model on data/external_test/.")
    parser.add_argument(
        "--model_type",
        choices=["baseline", "transformer"],
        default=None,
        help="Model type to evaluate. If omitted, transformer is inferred when --model_name or --run_name is provided.",
    )
    parser.add_argument(
        "--model_name",
        default=None,
        help="Hugging Face model ID used by the transformer run.",
    )
    parser.add_argument(
        "--run_name",
        default=None,
        help="Saved transformer run folder name under models/transformer/.",
    )
    args = parser.parse_args()

    model_type = args.model_type
    if model_type is None:
        model_type = "transformer" if args.model_name or args.run_name else "baseline"

    if model_type == "transformer":
        summary = evaluate_external_transformer(
            model_name=args.model_name or "castorini/afriberta_small",
            run_name=args.run_name,
        )
        print(f"External transformer evaluation complete: {summary['run_id']}")
        metrics = summary["metrics"]
    else:
        summary = evaluate_external_baseline()
        print("External baseline evaluation complete.")
        metrics = summary["metrics"]

    print(f"Rows evaluated: {summary['dataset_rows']}")
    print(f"Macro F1: {metrics['macro_f1']:.4f}")


if __name__ == "__main__":
    main()
