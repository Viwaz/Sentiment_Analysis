from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)


def compute_metrics(y_true, y_pred, labels: list[str]) -> dict:
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true,
        y_pred,
        labels=labels,
        zero_division=0,
    )
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "macro_f1": f1_score(y_true, y_pred, average="macro"),
        "per_class": {
            label: {
                "precision": float(p),
                "recall": float(r),
                "f1": float(f),
                "support": int(s),
            }
            for label, p, r, f, s in zip(labels, precision, recall, f1, support)
        },
        "classification_report": classification_report(
            y_true, y_pred, labels=labels, zero_division=0, output_dict=True
        ),
    }


def save_metrics(metrics: dict, output_path: Path) -> None:
    output_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")


def save_confusion_matrix(y_true, y_pred, labels: list[str], output_path: Path, title: str) -> None:
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    cm_df = pd.DataFrame(cm, index=labels, columns=labels)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm_df, annot=True, fmt="d", cmap="Blues")
    plt.title(title)
    plt.ylabel("True label")
    plt.xlabel("Predicted label")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
