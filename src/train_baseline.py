from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.base import clone
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from .data_utils import build_paths, ensure_project_dirs
from .evaluate import compute_metrics, save_confusion_matrix, save_metrics
from .features import build_feature_sets

LABELS = ["negative", "neutral", "positive"]


def load_splits(root: Path | None = None) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    paths = build_paths(root)
    train_df = pd.read_csv(paths.processed_dir / "train.csv")
    val_df = pd.read_csv(paths.processed_dir / "val.csv")
    test_df = pd.read_csv(paths.processed_dir / "test.csv")
    return train_df, val_df, test_df


def train_and_score_models(root: Path | None = None) -> dict:
    paths = build_paths(root)
    ensure_project_dirs(paths)
    train_df, val_df, test_df = load_splits(root)

    feature_sets = build_feature_sets(
        train_df["cleaned_text"],
        val_df["cleaned_text"],
        test_df["cleaned_text"],
    )

    model_specs = {
        "logistic_regression": LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            solver="lbfgs",
        ),
        "linear_svm": LinearSVC(class_weight="balanced"),
    }

    all_results = []
    best_bundle = None
    best_model = None
    best_result = None

    for bundle in feature_sets:
        for model_name, estimator_template in model_specs.items():
            estimator = clone(estimator_template)
            estimator.fit(bundle.X_train, train_df["label"])
            val_pred = estimator.predict(bundle.X_val)
            val_metrics = compute_metrics(val_df["label"], val_pred, LABELS)

            result = {
                "feature_set": bundle.name,
                "model_name": model_name,
                "validation_metrics": val_metrics,
            }
            all_results.append(result)

            if best_result is None or val_metrics["macro_f1"] > best_result["validation_metrics"]["macro_f1"]:
                best_result = result
                best_bundle = bundle
                best_model = estimator

    test_pred = best_model.predict(best_bundle.X_test)
    test_metrics = compute_metrics(test_df["label"], test_pred, LABELS)
    summary = {
        "best_validation_run": best_result,
        "test_metrics": test_metrics,
        "all_runs": all_results,
    }

    model_dir = paths.models_dir / "baseline"
    result_dir = paths.results_dir
    figure_dir = paths.figures_dir
    model_dir.mkdir(parents=True, exist_ok=True)

    joblib.dump(best_model, model_dir / "best_baseline_model.joblib")
    joblib.dump(best_bundle.vectorizer, model_dir / "best_baseline_vectorizer.joblib")
    save_metrics(summary, result_dir / "baseline_metrics.json")
    save_confusion_matrix(
        test_df["label"],
        test_pred,
        LABELS,
        figure_dir / "baseline_confusion_matrix.png",
        "Baseline Model Confusion Matrix",
    )
    (result_dir / "baseline_predictions.csv").write_text(
        pd.DataFrame(
            {
                "text": test_df["text"],
                "cleaned_text": test_df["cleaned_text"],
                "true_label": test_df["label"],
                "predicted_label": test_pred,
            }
        ).to_csv(index=False),
        encoding="utf-8",
    )
    return summary


def main() -> None:
    summary = train_and_score_models()
    best = summary["best_validation_run"]
    print("Baseline training complete.")
    print(
        f"Best run: {best['model_name']} + {best['feature_set']} "
        f"(macro_f1={best['validation_metrics']['macro_f1']:.4f})"
    )


if __name__ == "__main__":
    main()
