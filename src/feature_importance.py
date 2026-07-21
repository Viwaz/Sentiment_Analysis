from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .data_utils import build_paths, ensure_project_dirs


DEFAULT_TOP_N = 15


def _load_baseline_metadata(model_dir: Path) -> dict:
    metadata_path = model_dir / "model_metadata.json"
    if not metadata_path.exists():
        return {}
    return json.loads(metadata_path.read_text(encoding="utf-8"))


def _feature_names(vectorizer: object) -> np.ndarray:
    if isinstance(vectorizer, dict):
        names = []
        for prefix, inner_vectorizer in vectorizer.items():
            inner_names = inner_vectorizer.get_feature_names_out()
            names.extend([f"{prefix}:{name}" for name in inner_names])
        return np.array(names, dtype=object)
    return np.array(vectorizer.get_feature_names_out(), dtype=object)


def _display_feature(feature: object) -> str:
    return str(feature).replace(" ", "<space>")


def extract_linear_feature_importance(
    model: object,
    vectorizer: object,
    labels: list[str],
    top_n: int = DEFAULT_TOP_N,
) -> pd.DataFrame:
    if not hasattr(model, "coef_"):
        raise TypeError(
            "The saved baseline model does not expose coef_. "
            "Feature-importance extraction currently supports linear models such as LogisticRegression and LinearSVC."
        )

    feature_names = _feature_names(vectorizer)
    coefficients = np.asarray(model.coef_)
    model_classes = [str(label) for label in getattr(model, "classes_", labels)]

    if coefficients.ndim == 1:
        coefficients = coefficients.reshape(1, -1)

    if len(model_classes) != coefficients.shape[0]:
        model_classes = labels[: coefficients.shape[0]]

    rows = []
    for class_index, class_label in enumerate(model_classes):
        class_weights = coefficients[class_index]
        top_indices = np.argsort(class_weights)[-top_n:][::-1]
        for rank, feature_index in enumerate(top_indices, start=1):
            rows.append(
                {
                    "class_label": class_label,
                    "rank": rank,
                    "feature": str(feature_names[feature_index]),
                    "feature_display": _display_feature(feature_names[feature_index]),
                    "weight": float(class_weights[feature_index]),
                    "absolute_weight": float(abs(class_weights[feature_index])),
                }
            )
    return pd.DataFrame(rows)


def save_feature_importance_plot(importance_df: pd.DataFrame, output_path: Path, title: str) -> None:
    classes = importance_df["class_label"].drop_duplicates().tolist()
    fig, axes = plt.subplots(len(classes), 1, figsize=(11, 4 * len(classes)))
    if len(classes) == 1:
        axes = [axes]

    palette = {
        "negative": "#b23a48",
        "neutral": "#6c757d",
        "positive": "#2a9d8f",
    }

    for axis, class_label in zip(axes, classes):
        class_df = importance_df[importance_df["class_label"] == class_label].sort_values("weight")
        axis.barh(
            class_df["feature_display"],
            class_df["weight"],
            color=palette.get(class_label, "#3a6ea5"),
        )
        axis.set_title(f"Top features for {class_label}")
        axis.set_xlabel("Model coefficient weight")
        axis.grid(axis="x", alpha=0.25)

    fig.suptitle(title, fontsize=15, y=0.995)
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def generate_feature_importance(root: Path | None = None, top_n: int = DEFAULT_TOP_N) -> dict[str, str]:
    paths = build_paths(root)
    ensure_project_dirs(paths)

    model_dir = paths.models_dir / "baseline"
    metadata = _load_baseline_metadata(model_dir)
    labels = metadata.get("label_mapping") or ["negative", "neutral", "positive"]

    model_path = model_dir / "best_baseline_model.joblib"
    vectorizer_path = model_dir / "best_baseline_vectorizer.joblib"
    if not model_path.exists() or not vectorizer_path.exists():
        raise FileNotFoundError(
            "Baseline artifacts were not found. Run `python -m src.train_baseline` before generating feature importance."
        )

    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)
    importance_df = extract_linear_feature_importance(model, vectorizer, labels, top_n=top_n)

    csv_path = paths.results_dir / "baseline_feature_importance.csv"
    figure_path = paths.figures_dir / "baseline_feature_importance.png"
    importance_df.to_csv(csv_path, index=False, encoding="utf-8")

    best_run = metadata.get("best_validation_run", {})
    model_name = best_run.get("model_name", type(model).__name__)
    feature_set = best_run.get("feature_set", "saved TF-IDF features")
    title = f"Baseline Feature Importance ({model_name} + {feature_set})"
    save_feature_importance_plot(importance_df, figure_path, title)

    return {
        "csv_path": str(csv_path),
        "figure_path": str(figure_path),
        "model_name": str(model_name),
        "feature_set": str(feature_set),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate baseline feature-importance outputs.")
    parser.add_argument("--top-n", type=int, default=DEFAULT_TOP_N, help="Number of top features to show per class.")
    args = parser.parse_args()

    result = generate_feature_importance(top_n=args.top_n)
    print("Feature importance generated.")
    print(f"Model: {result['model_name']} + {result['feature_set']}")
    print(f"CSV: {result['csv_path']}")
    print(f"Figure: {result['figure_path']}")


if __name__ == "__main__":
    main()
