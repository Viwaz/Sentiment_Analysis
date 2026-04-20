from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd

EXPECTED_COLUMNS = {"id", "text", "sentiment_label", "include"}
CANONICAL_LABELS = {
    "positive": "positive",
    "pos": "positive",
    "negative": "negative",
    "neg": "negative",
    "neutral": "neutral",
    "neu": "neutral",
}


@dataclass(frozen=True)
class DatasetPaths:
    root: Path
    raw_dir: Path
    external_test_dir: Path
    interim_dir: Path
    processed_dir: Path
    models_dir: Path
    reports_dir: Path
    figures_dir: Path
    results_dir: Path


def build_paths(root: Path | None = None) -> DatasetPaths:
    root = root or Path(__file__).resolve().parents[1]
    return DatasetPaths(
        root=root,
        raw_dir=root / "data" / "raw",
        external_test_dir=root / "data" / "external_test",
        interim_dir=root / "data" / "interim",
        processed_dir=root / "data" / "processed",
        models_dir=root / "models",
        reports_dir=root / "reports",
        figures_dir=root / "reports" / "figures",
        results_dir=root / "reports" / "results",
    )


def ensure_project_dirs(paths: DatasetPaths) -> None:
    for directory in (
        paths.raw_dir,
        paths.external_test_dir,
        paths.interim_dir,
        paths.processed_dir,
        paths.models_dir / "baseline",
        paths.models_dir / "transformer",
        paths.figures_dir,
        paths.results_dir,
        paths.root / "notebooks",
        paths.root / "src",
    ):
        directory.mkdir(parents=True, exist_ok=True)


def discover_raw_files(raw_dir: Path) -> list[Path]:
    files = sorted(raw_dir.glob("*.csv"))
    return [file for file in files if file.name != "custom_lexicon_template.csv"]


def load_annotation_file(file_path: Path) -> pd.DataFrame:
    df = pd.read_csv(file_path)
    if "id" not in df.columns and "Unnamed: 0" in df.columns:
        df = df.rename(columns={"Unnamed: 0": "id"})
    missing = EXPECTED_COLUMNS - set(df.columns)
    if missing:
        missing_cols = ", ".join(sorted(missing))
        raise ValueError(f"{file_path.name} is missing required columns: {missing_cols}")
    df = df.copy()
    df["source_file"] = file_path.name
    return df


def merge_annotation_files(file_paths: Iterable[Path]) -> pd.DataFrame:
    frames = [load_annotation_file(path) for path in file_paths]
    if not frames:
        raise FileNotFoundError("No annotation CSV files were found in data/raw/")
    return pd.concat(frames, ignore_index=True)


def normalize_label(value: object) -> str | None:
    if pd.isna(value):
        return None
    normalized = str(value).strip().lower()
    if normalized == "nuetral":
        normalized = "neutral"
    return CANONICAL_LABELS.get(normalized)


def normalize_include(value: object) -> str:
    if pd.isna(value):
        return "no"
    normalized = str(value).strip().lower()
    return "yes" if normalized in {"yes", "y", "true", "1"} else "no"


def build_label_audit(df: pd.DataFrame, min_comment_tokens: int = 2) -> pd.DataFrame:
    audit = df.copy()
    audit["sentiment_label_normalized"] = audit["sentiment_label"].apply(normalize_label)
    audit["include_normalized"] = audit["include"].apply(normalize_include)
    audit["text_missing"] = audit["text"].isna() | audit["text"].astype(str).str.strip().eq("")
    audit["text_length_chars"] = audit["text"].fillna("").astype(str).str.len()
    audit["token_count_whitespace"] = (
        audit["text"].fillna("").astype(str).str.split().apply(len)
    )
    audit["is_short_comment"] = audit["token_count_whitespace"] < min_comment_tokens
    audit["is_duplicate_text"] = audit["text"].fillna("").astype(str).duplicated(keep="first")
    audit["exclude_reason"] = ""
    audit.loc[audit["include_normalized"] != "yes", "exclude_reason"] = "include_not_yes"
    audit.loc[audit["text_missing"], "exclude_reason"] = "missing_text"
    audit.loc[audit["sentiment_label_normalized"].isna(), "exclude_reason"] = "invalid_label"
    audit.loc[audit["is_duplicate_text"], "exclude_reason"] = "duplicate_text"
    return audit


def save_json(payload: dict, output_path: Path) -> None:
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
