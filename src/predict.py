from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .data_utils import build_paths, ensure_project_dirs
from .model_service import REFERENCE_MODELS, load_model
from .preprocess import clean_text


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


def prepare_prediction_input(df: pd.DataFrame) -> pd.DataFrame:
    prepared = df.copy()
    prepared["cleaned_text"] = prepared["text"].apply(clean_text)
    return prepared


def run_batch_prediction(
    input_path: str | Path,
    output_path: str | Path,
    reference_model: str = "baseline",
    run_name: str = "afriberta_small",
    root: Path | None = None,
) -> pd.DataFrame:
    paths = build_paths(root)
    ensure_project_dirs(paths)

    input_df = load_input_csv(Path(input_path))
    prediction_input = prepare_prediction_input(input_df)
    service = load_model(reference_model, root=root, run_name=run_name)
    output_df = service.predict_batch(prediction_input)

    output_path = Path(output_path)
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
