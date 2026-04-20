from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd

from .data_utils import build_paths, discover_raw_files, ensure_project_dirs, load_annotation_file
from .evaluate import compute_metrics, save_confusion_matrix, save_metrics
from .preprocess import prepare_external_test_dataframe

LABELS = ["negative", "neutral", "positive"]


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


def main() -> None:
    summary = evaluate_external_baseline()
    print("External baseline evaluation complete.")
    print(f"Rows evaluated: {summary['dataset_rows']}")
    print(f"Macro F1: {summary['metrics']['macro_f1']:.4f}")


if __name__ == "__main__":
    main()
