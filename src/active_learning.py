from __future__ import annotations

import argparse
import logging
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from .data_utils import build_paths, ensure_project_dirs
from .evaluate_external import transform_with_saved_vectorizer
from .preprocess import clean_text

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def compute_entropy(probs: np.ndarray) -> np.ndarray:
    """Compute Shannon entropy for class probabilities.
    
    H = - sum(p * log2(p))
    """
    # Avoid log2(0) by clipping
    probs = np.clip(probs, 1e-15, 1.0)
    entropy = -np.sum(probs * np.log2(probs), axis=1)
    return entropy


def compute_margin(probs: np.ndarray) -> np.ndarray:
    """Compute uncertainty using margin sampling.
    
    Uncertainty = 1 - (p_first - p_second)
    where p_first and p_second are the two highest predicted probabilities.
    """
    sorted_probs = np.sort(probs, axis=1)
    p_first = sorted_probs[:, -1]
    p_second = sorted_probs[:, -2]
    return 1.0 - (p_first - p_second)


def compute_least_confidence(probs: np.ndarray) -> np.ndarray:
    """Compute uncertainty using least confidence sampling.
    
    Uncertainty = 1 - p_first
    where p_first is the maximum class probability.
    """
    p_first = np.max(probs, axis=1)
    return 1.0 - p_first


def run_active_learning(
    unlabeled_path: str | Path,
    output_path: str | Path,
    n_samples: int = 200,
    strategy: str = "entropy",
    root: Path | None = None,
) -> pd.DataFrame:
    paths = build_paths(root)
    ensure_project_dirs(paths)

    unlabeled_path = Path(unlabeled_path)
    output_path = Path(output_path)

    if not unlabeled_path.exists():
        raise FileNotFoundError(f"Unlabeled CSV file not found at: {unlabeled_path}")

    # 1. Load trained baseline models
    model_path = paths.models_dir / "baseline" / "best_baseline_model.joblib"
    vectorizer_path = paths.models_dir / "baseline" / "best_baseline_vectorizer.joblib"

    if not model_path.exists() or not vectorizer_path.exists():
        raise FileNotFoundError(
            f"Trained baseline model or vectorizer not found under '{paths.models_dir / 'baseline'}'. "
            "Please run 'python -m src.train_baseline' first."
        )

    logger.info("Loading baseline model and vectorizer...")
    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)

    # 2. Load unlabeled dataset
    logger.info(f"Loading unlabeled data from {unlabeled_path}...")
    df = pd.read_csv(unlabeled_path)

    # Ensure required columns
    text_col = None
    for col in ["text", "comment_text", "Comment"]:
        if col in df.columns:
            text_col = col
            break

    if not text_col:
        raise ValueError(f"Could not find a text column in {unlabeled_path}. Existing columns: {list(df.columns)}")

    # Standardize column name
    if text_col != "text":
        df = df.rename(columns={text_col: "text"})

    # Ensure id column exists
    if "id" not in df.columns:
        if "comment_id" in df.columns:
            df = df.rename(columns={"comment_id": "id"})
        else:
            logger.info("Generating 'id' column for unlabeled comments...")
            df["id"] = range(10000, 10000 + len(df))

    # Drop rows with missing text
    df = df[df["text"].notna() & df["text"].astype(str).str.strip().ne("")].copy()
    if len(df) == 0:
        raise ValueError("The unlabeled dataset does not contain any valid text records.")

    # 3. Clean and transform text
    logger.info("Cleaning text and extracting features...")
    df["cleaned_text"] = df["text"].apply(clean_text)
    X = transform_with_saved_vectorizer(vectorizer, df["cleaned_text"])

    # 4. Compute uncertainty scores
    logger.info(f"Computing uncertainty using strategy: {strategy}...")
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(X)
        if strategy == "entropy":
            scores = compute_entropy(probs)
        elif strategy == "margin":
            scores = compute_margin(probs)
        elif strategy == "lc":
            scores = compute_least_confidence(probs)
        else:
            raise ValueError(f"Unknown active learning strategy: {strategy}")
    elif hasattr(model, "decision_function"):
        logger.warning(
            "Model does not support predict_proba. Falling back to decision_function distance."
        )
        decisions = model.decision_function(X)
        # For SVM, decision values closer to 0 indicate higher uncertainty
        # If binary: decisions is 1D shape (n_samples,). If multiclass: shape (n_samples, n_classes).
        if len(decisions.shape) == 1 or decisions.shape[1] == 1:
            scores = -np.abs(decisions)  # Higher is closer to 0
        else:
            # For multiclass, sort and find margin of top 2 decision scores
            sorted_decisions = np.sort(decisions, axis=1)
            margin = sorted_decisions[:, -1] - sorted_decisions[:, -2]
            scores = -margin  # Higher uncertainty means smaller margin
    else:
        raise AttributeError("Model has neither predict_proba nor decision_function.")

    df["uncertainty_score"] = scores

    # 5. Filter out already annotated text if possible to avoid duplicates
    # Let's see if we can find existing annotated text from data/interim/cleaned_comments.csv
    cleaned_path = paths.interim_dir / "cleaned_comments.csv"
    if cleaned_path.exists():
        logger.info("Comparing with existing annotations to prevent duplicates...")
        annotated_df = pd.read_csv(cleaned_path)
        if "cleaned_text" in annotated_df.columns:
            annotated_texts = set(annotated_df["cleaned_text"].tolist())
            before_len = len(df)
            df = df[~df["cleaned_text"].isin(annotated_texts)].copy()
            logger.info(f"Dropped {before_len - len(df)} comments that are already annotated.")

    # 6. Sort and select top candidates
    df_sorted = df.sort_values(by="uncertainty_score", ascending=False)
    candidates = df_sorted.head(n_samples).copy()

    # 7. Format output in expected annotation format
    candidates["sentiment_label"] = ""
    candidates["include"] = ""
    if "notes" not in candidates.columns:
        candidates["notes"] = ""
    
    # Store uncertainty score inside notes for traceablity
    candidates["notes"] = candidates.apply(
        lambda r: f"[AL {strategy}: {r['uncertainty_score']:.4f}] {r['notes']}".strip(), axis=1
    )

    # Reorder columns to match standard schema
    output_cols = ["id", "text", "sentiment_label", "include", "notes"]
    # Preserve other metadata columns if they exist
    for col in candidates.columns:
        if col not in output_cols and col not in ["cleaned_text", "uncertainty_score"]:
            output_cols.append(col)

    export_df = candidates[output_cols]

    # Save to output path
    output_path.parent.mkdir(parents=True, exist_ok=True)
    export_df.to_csv(output_path, index=False, encoding="utf-8")
    logger.info(f"Successfully exported {len(export_df)} uncertainty-selected comments to: {output_path}")

    return candidates


def main() -> None:
    parser = argparse.ArgumentParser(description="Active learning pipeline for sentiment annotation candidates.")
    parser.add_argument(
        "--unlabeled_path",
        type=str,
        required=True,
        help="Path to CSV containing unlabeled comments.",
    )
    parser.add_argument(
        "--output_path",
        type=str,
        default="data/raw/Facebook_Comment_Annotation - ActiveBatch1.csv",
        help="Path to save the candidates for annotation.",
    )
    parser.add_argument(
        "--n_samples",
        type=int,
        default=200,
        help="Number of candidates to select.",
    )
    parser.add_argument(
        "--strategy",
        type=str,
        choices=["entropy", "margin", "lc"],
        default="entropy",
        help="Uncertainty strategy (entropy, margin, or least confidence).",
    )

    args = parser.parse_args()
    
    try:
        run_active_learning(
            unlabeled_path=args.unlabeled_path,
            output_path=args.output_path,
            n_samples=args.n_samples,
            strategy=args.strategy,
        )
    except Exception as e:
        logger.error(f"Active learning execution failed: {e}", exc_info=True)
        exit(1)


if __name__ == "__main__":
    main()
