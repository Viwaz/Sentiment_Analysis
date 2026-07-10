"""Diagnostic plots for the final presentation: learning curves and
ROC / precision-recall curves for the winning baseline model.

These are generated as a *post-processing* step on top of
``train_and_score_models`` in ``train.py`` — they reuse the best
feature bundle and estimator that were already selected, so no
re-training of the whole model zoo is required.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless / no display backend needed
import matplotlib.pyplot as plt
import numpy as np
from sklearn.base import clone
from sklearn.metrics import auc, precision_recall_curve, roc_curve
from sklearn.model_selection import learning_curve
from sklearn.preprocessing import label_binarize


def _decision_scores(estimator, X) -> np.ndarray:
    """Return per-class scores for ROC/PR curves regardless of whether the
    estimator exposes predict_proba (LogReg, NB) or only decision_function
    (LinearSVC)."""
    if hasattr(estimator, "predict_proba"):
        return estimator.predict_proba(X)
    if hasattr(estimator, "decision_function"):
        scores = estimator.decision_function(X)
        # decision_function on a multiclass problem returns one column per
        # class already (ovr for LinearSVC); turn it into pseudo-probabilities
        # with a softmax so the ROC/PR math behaves the same way.
        scores = scores - scores.max(axis=1, keepdims=True)
        exp_scores = np.exp(scores)
        return exp_scores / exp_scores.sum(axis=1, keepdims=True)
    raise ValueError(
        f"{type(estimator).__name__} exposes neither predict_proba nor "
        "decision_function; cannot compute ROC/PR curves."
    )


def plot_learning_curve(
    estimator,
    X,
    y,
    title: str,
    output_path: Path,
    cv: int = 5,
    scoring: str = "f1_macro",
) -> dict:
    """Fit the estimator on increasing slices of the training data and plot
    train vs. cross-validated score. Returns the raw numbers too, in case
    they're wanted for a metrics json / appendix table."""
    train_sizes, train_scores, val_scores = learning_curve(
        clone(estimator),
        X,
        y,
        cv=cv,
        scoring=scoring,
        train_sizes=np.linspace(0.1, 1.0, 8),
        shuffle=True,
        random_state=42,
        n_jobs=-1,
    )

    train_mean, train_std = train_scores.mean(axis=1), train_scores.std(axis=1)
    val_mean, val_std = val_scores.mean(axis=1), val_scores.std(axis=1)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(train_sizes, train_mean, "o-", color="#2563eb", label="Training score")
    ax.fill_between(
        train_sizes, train_mean - train_std, train_mean + train_std, alpha=0.15, color="#2563eb"
    )
    ax.plot(train_sizes, val_mean, "o-", color="#dc2626", label=f"Cross-val score ({cv}-fold)")
    ax.fill_between(
        train_sizes, val_mean - val_std, val_mean + val_std, alpha=0.15, color="#dc2626"
    )
    ax.set_xlabel("Training examples")
    ax.set_ylabel(scoring.replace("_", " ").title())
    ax.set_title(title)
    ax.legend(loc="best")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)

    return {
        "train_sizes": train_sizes.tolist(),
        "train_score_mean": train_mean.tolist(),
        "train_score_std": train_std.tolist(),
        "val_score_mean": val_mean.tolist(),
        "val_score_std": val_std.tolist(),
        "scoring": scoring,
        "cv": cv,
    }


def generate_learning_curves_for_models(
    model_specs: dict,
    X,
    y,
    figures_dir: Path,
    cv: int = 5,
    scoring: str = "f1_macro",
) -> dict:
    """Plot a learning curve for every model in ``model_specs`` (trained on
    the same, winning feature bundle so the comparison is apples-to-apples),
    plus one combined comparison plot overlaying all of their cross-val
    curves. Saves one PNG per model + one comparison PNG."""
    per_model = {}
    fig_cmp, ax_cmp = plt.subplots(figsize=(8, 6))
    colors = plt.cm.tab10.colors

    for i, (model_name, estimator) in enumerate(model_specs.items()):
        curve_data = plot_learning_curve(
            estimator,
            X,
            y,
            title=f"Learning Curve — {model_name}",
            output_path=figures_dir / f"learning_curve_{model_name}.png",
            cv=cv,
            scoring=scoring,
        )
        per_model[model_name] = curve_data

        color = colors[i % len(colors)]
        ax_cmp.plot(
            curve_data["train_sizes"],
            curve_data["val_score_mean"],
            "o-",
            color=color,
            label=model_name,
        )
        val_mean = np.array(curve_data["val_score_mean"])
        val_std = np.array(curve_data["val_score_std"])
        ax_cmp.fill_between(
            curve_data["train_sizes"], val_mean - val_std, val_mean + val_std, alpha=0.1, color=color
        )

    ax_cmp.set_xlabel("Training examples")
    ax_cmp.set_ylabel(scoring.replace("_", " ").title())
    ax_cmp.set_title("Learning Curves — Model Comparison (cross-validated score)")
    ax_cmp.legend(loc="best", fontsize=9)
    ax_cmp.grid(alpha=0.3)
    fig_cmp.tight_layout()
    figures_dir.mkdir(parents=True, exist_ok=True)
    comparison_path = figures_dir / "learning_curves_comparison.png"
    fig_cmp.savefig(comparison_path, dpi=150)
    plt.close(fig_cmp)

    return {
        "per_model": per_model,
        "comparison_figure": str(comparison_path),
        "per_model_figures": {
            name: str(figures_dir / f"learning_curve_{name}.png") for name in model_specs
        },
    }


def plot_roc_curve(
    y_true,
    estimator,
    X,
    labels: list[str],
    output_path: Path,
    title: str = "ROC Curves (One-vs-Rest)",
) -> dict:
    """One-vs-rest ROC curve, one line per class plus a micro-average."""
    y_true_bin = label_binarize(y_true, classes=labels)
    y_score = _decision_scores(estimator, X)
    colors = ["#dc2626", "#65a30d", "#2563eb"]  # negative, neutral, positive

    fig, ax = plt.subplots(figsize=(6.5, 6))
    roc_summary = {}
    for i, label in enumerate(labels):
        fpr, tpr, _ = roc_curve(y_true_bin[:, i], y_score[:, i])
        roc_auc = auc(fpr, tpr)
        roc_summary[label] = roc_auc
        ax.plot(fpr, tpr, color=colors[i % len(colors)], label=f"{label} (AUC = {roc_auc:.3f})")

    fpr_micro, tpr_micro, _ = roc_curve(y_true_bin.ravel(), y_score.ravel())
    auc_micro = auc(fpr_micro, tpr_micro)
    roc_summary["micro_average"] = auc_micro
    ax.plot(
        fpr_micro, tpr_micro, color="black", linestyle="--", label=f"micro-average (AUC = {auc_micro:.3f})"
    )
    ax.plot([0, 1], [0, 1], color="gray", linestyle=":", linewidth=1)
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title(title)
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)

    return roc_summary


def plot_pr_curve(
    y_true,
    estimator,
    X,
    labels: list[str],
    output_path: Path,
    title: str = "Precision-Recall Curves (One-vs-Rest)",
) -> dict:
    """One-vs-rest precision-recall curve, one line per class plus a
    micro-average."""
    y_true_bin = label_binarize(y_true, classes=labels)
    y_score = _decision_scores(estimator, X)
    colors = ["#dc2626", "#65a30d", "#2563eb"]  # negative, neutral, positive

    fig, ax = plt.subplots(figsize=(6.5, 6))
    pr_summary = {}
    for i, label in enumerate(labels):
        precision, recall, _ = precision_recall_curve(y_true_bin[:, i], y_score[:, i])
        pr_auc = auc(recall, precision)
        pr_summary[label] = pr_auc
        ax.plot(recall, precision, color=colors[i % len(colors)], label=f"{label} (AUC = {pr_auc:.3f})")

    precision_micro, recall_micro, _ = precision_recall_curve(y_true_bin.ravel(), y_score.ravel())
    pr_auc_micro = auc(recall_micro, precision_micro)
    pr_summary["micro_average"] = pr_auc_micro
    ax.plot(
        recall_micro,
        precision_micro,
        color="black",
        linestyle="--",
        label=f"micro-average (AUC = {pr_auc_micro:.3f})",
    )
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.set_title(title)
    ax.legend(loc="lower left", fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)

    return pr_summary


def generate_model_evaluations(
    model_specs: dict,
    bundle,
    train_df,
    test_df,
    labels: list[str],
    figures_dir: Path,
) -> dict:
    """Fit every model in ``model_specs`` on the winning feature bundle and,
    for each one, save a confusion matrix and an ROC curve on the held-out
    test set. Returns per-model AUCs, accuracy/F1, and figure paths."""
    from .evaluate import compute_metrics, save_confusion_matrix

    per_model = {}
    for model_name, estimator_template in model_specs.items():
        estimator = clone(estimator_template)
        estimator.fit(bundle.X_train, train_df["label"])
        test_pred = estimator.predict(bundle.X_test)
        test_metrics = compute_metrics(test_df["label"], test_pred, labels)

        cm_path = figures_dir / f"confusion_matrix_{model_name}.png"
        save_confusion_matrix(
            test_df["label"],
            test_pred,
            labels,
            cm_path,
            f"Confusion Matrix — {model_name}",
        )

        roc_path = figures_dir / f"roc_curve_{model_name}.png"
        roc_auc = plot_roc_curve(
            test_df["label"],
            estimator,
            bundle.X_test,
            labels,
            roc_path,
            title=f"ROC Curves (One-vs-Rest) — {model_name}",
        )

        per_model[model_name] = {
            "test_metrics": test_metrics,
            "roc_auc": roc_auc,
            "confusion_matrix_figure": str(cm_path),
            "roc_curve_figure": str(roc_path),
        }

    return per_model


def generate_diagnostics(
    best_model,
    best_bundle,
    train_df,
    test_df,
    labels: list[str],
    figures_dir: Path,
    model_label: str,
    model_specs: dict | None = None,
) -> dict:
    """Run the diagnostic plots for the presentation and return a dict
    suitable for dropping straight into the metrics json.

    All models are trained on the same, winning feature bundle so every
    comparison (learning curves, ROC, confusion matrices) is apples-to-apples
    for that fixed feature pipeline. If ``model_specs`` is provided
    (name -> unfitted estimator):
      - a learning curve is produced for every model, plus one comparison figure
      - a confusion matrix and ROC curve is produced for every model
    A precision-recall curve is produced only for the overall best model,
    since PR is mainly useful for scrutinizing the model you'd actually ship.
    """
    if model_specs:
        learning_curve_data = generate_learning_curves_for_models(
            model_specs,
            best_bundle.X_train,
            train_df["label"],
            figures_dir=figures_dir,
        )
        per_model_evaluations = generate_model_evaluations(
            model_specs,
            best_bundle,
            train_df,
            test_df,
            labels,
            figures_dir=figures_dir,
        )
    else:
        learning_curve_data = plot_learning_curve(
            best_model,
            best_bundle.X_train,
            train_df["label"],
            title=f"Learning Curve — {model_label}",
            output_path=figures_dir / "learning_curve.png",
        )
        per_model_evaluations = {}

    pr_auc = plot_pr_curve(
        test_df["label"],
        best_model,
        best_bundle.X_test,
        labels,
        output_path=figures_dir / "pr_curves.png",
        title=f"Precision-Recall Curves (One-vs-Rest) — {model_label}",
    )

    if model_specs:
        figures = {
            "learning_curves_comparison": learning_curve_data["comparison_figure"],
            **{
                f"learning_curve_{name}": path
                for name, path in learning_curve_data["per_model_figures"].items()
            },
            **{
                f"confusion_matrix_{name}": data["confusion_matrix_figure"]
                for name, data in per_model_evaluations.items()
            },
            **{
                f"roc_curve_{name}": data["roc_curve_figure"]
                for name, data in per_model_evaluations.items()
            },
            "pr_curves": str(figures_dir / "pr_curves.png"),
        }
    else:
        figures = {
            "learning_curve": str(figures_dir / "learning_curve.png"),
            "pr_curves": str(figures_dir / "pr_curves.png"),
        }

    return {
        "learning_curve": learning_curve_data,
        "per_model_evaluations": per_model_evaluations,
        "pr_auc": pr_auc,
        "figures": figures,
    }
