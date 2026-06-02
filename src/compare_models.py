from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .data_utils import build_paths, ensure_project_dirs


def weighted_f1(metrics: dict) -> float | None:
    return (
        metrics.get("classification_report", {})
        .get("weighted avg", {})
        .get("f1-score")
    )


def metric_row(
    model_family: str,
    model_name: str,
    split: str,
    metrics: dict,
    source_file: str,
    feature_set: str | None = None,
) -> dict:
    return {
        "model_family": model_family,
        "model_name": model_name,
        "feature_set": feature_set or "",
        "split": split,
        "macro_f1": metrics.get("macro_f1"),
        "accuracy": metrics.get("accuracy"),
        "weighted_f1": weighted_f1(metrics),
        "source_file": source_file,
    }


def load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def collect_baseline_rows(results_dir: Path) -> list[dict]:
    path = results_dir / "baseline_metrics.json"
    payload = load_json(path)
    if not payload:
        return []

    rows = []
    for run in payload.get("all_runs", []):
        rows.append(
            metric_row(
                model_family="classical_ml",
                model_name=run["model_name"],
                feature_set=run["feature_set"],
                split="validation",
                metrics=run["validation_metrics"],
                source_file=path.name,
            )
        )

    best = payload.get("best_validation_run", {})
    if "test_metrics" in payload and best:
        rows.append(
            metric_row(
                model_family="classical_ml",
                model_name=f"best_baseline:{best.get('model_name', '')}",
                feature_set=best.get("feature_set", ""),
                split="test",
                metrics=payload["test_metrics"],
                source_file=path.name,
            )
        )
    return rows


def collect_transformer_rows(results_dir: Path) -> list[dict]:
    rows = []
    seen_model_names = set()
    excluded_names = {
        "baseline_metrics.json",
        "external_baseline_metrics.json",
    }
    for path in sorted(results_dir.glob("*_metrics.json")):
        if path.name in excluded_names or path.name.startswith("external_"):
            continue
        payload = load_json(path)
        if not payload or "test_metrics" not in payload:
            continue
        model_name = payload.get("model_name", path.stem.replace("_metrics", ""))
        if model_name in seen_model_names:
            continue
        seen_model_names.add(model_name)
        rows.append(
            metric_row(
                model_family="transformer",
                model_name=model_name,
                feature_set="subword_transformer",
                split="test",
                metrics=payload["test_metrics"],
                source_file=path.name,
            )
        )
    return rows


def collect_external_rows(results_dir: Path) -> list[dict]:
    rows = []
    for path in sorted(results_dir.glob("external_*_metrics.json")):
        payload = load_json(path)
        if not payload or "metrics" not in payload:
            continue
        name = path.stem.removeprefix("external_").removesuffix("_metrics")
        family = "classical_ml" if name == "baseline" else "transformer"
        rows.append(
            metric_row(
                model_family=family,
                model_name=name,
                feature_set="",
                split="external_test",
                metrics=payload["metrics"],
                source_file=path.name,
            )
        )
    return rows


def build_model_comparison(root: Path | None = None) -> pd.DataFrame:
    paths = build_paths(root)
    ensure_project_dirs(paths)
    rows = []
    rows.extend(collect_baseline_rows(paths.results_dir))
    rows.extend(collect_transformer_rows(paths.results_dir))
    rows.extend(collect_external_rows(paths.results_dir))
    comparison = pd.DataFrame(rows)
    if not comparison.empty:
        comparison = comparison.sort_values(
            by=["split", "macro_f1"],
            ascending=[True, False],
            na_position="last",
        )
    comparison.to_csv(paths.results_dir / "model_comparison.csv", index=False)
    return comparison


def main() -> None:
    comparison = build_model_comparison()
    if comparison.empty:
        print("No model metrics found to compare.")
        return
    print("Model comparison saved to reports/results/model_comparison.csv")
    print(comparison.to_string(index=False))


if __name__ == "__main__":
    main()
