from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from .data_utils import (
    build_label_audit,
    build_paths,
    discover_raw_files,
    ensure_project_dirs,
    merge_annotation_files,
    normalize_include,
    normalize_label,
    save_json,
)

RANDOM_SEED = 42
URL_PATTERN = re.compile(r"(https?://\S+|www\.\S+)")
MENTION_PATTERN = re.compile(r"(?<!\w)@\w+")
NUMBER_PATTERN = re.compile(r"\b\d+\b")
WHITESPACE_PATTERN = re.compile(r"\s+")
PUNCT_SPACING_PATTERN = re.compile(r"([,;:\(\)\[\]\{\}\"'])")


def normalize_unicode(text: str) -> str:
    return unicodedata.normalize("NFKC", text)


def clean_text(text: object) -> str:
    if pd.isna(text):
        return ""
    value = normalize_unicode(str(text)).lower().strip()
    value = URL_PATTERN.sub(" <url> ", value)
    value = MENTION_PATTERN.sub(" <user> ", value)
    value = NUMBER_PATTERN.sub(" <num> ", value)
    value = PUNCT_SPACING_PATTERN.sub(r" \1 ", value)
    value = WHITESPACE_PATTERN.sub(" ", value).strip()
    return value


def tokenize_text(text: str) -> list[str]:
    return text.split()


def prepare_clean_dataframe(audit_df: pd.DataFrame) -> pd.DataFrame:
    filtered = audit_df.copy()
    filtered = filtered[filtered["include_normalized"] == "yes"]
    filtered = filtered[~filtered["text_missing"]]
    filtered = filtered[filtered["sentiment_label_normalized"].notna()]
    filtered = filtered[~filtered["is_duplicate_text"]]
    filtered = filtered.copy()
    filtered["label"] = filtered["sentiment_label_normalized"]
    filtered["cleaned_text"] = filtered["text"].apply(clean_text)
    filtered["tokens"] = filtered["cleaned_text"].apply(tokenize_text)
    filtered["token_count_cleaned"] = filtered["tokens"].apply(len)
    return filtered


def split_dataset(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train_df, temp_df = train_test_split(
        df,
        test_size=0.30,
        random_state=RANDOM_SEED,
        stratify=df["label"],
    )
    val_df, test_df = train_test_split(
        temp_df,
        test_size=0.50,
        random_state=RANDOM_SEED,
        stratify=temp_df["label"],
    )
    return train_df, val_df, test_df


def build_metadata(
    merged_df: pd.DataFrame,
    audit_df: pd.DataFrame,
    cleaned_df: pd.DataFrame,
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
) -> dict:
    return {
        "random_seed": RANDOM_SEED,
        "raw_rows": int(len(merged_df)),
        "rows_after_filtering": int(len(cleaned_df)),
        "excluded_rows": int(len(merged_df) - len(cleaned_df)),
        "duplicate_rows_dropped": int(audit_df["is_duplicate_text"].sum()),
        "invalid_label_rows": int(audit_df["sentiment_label_normalized"].isna().sum()),
        "missing_text_rows": int(audit_df["text_missing"].sum()),
        "split_sizes": {
            "train": int(len(train_df)),
            "val": int(len(val_df)),
            "test": int(len(test_df)),
        },
        "label_distribution": cleaned_df["label"].value_counts().to_dict(),
        "raw_files": sorted(merged_df["source_file"].unique().tolist()),
        "split_indices": {
            "train": train_df.index.tolist(),
            "val": val_df.index.tolist(),
            "test": test_df.index.tolist(),
        },
    }


def run_preprocessing(root: Path | None = None) -> dict:
    paths = build_paths(root)
    ensure_project_dirs(paths)

    raw_files = discover_raw_files(paths.raw_dir)
    merged_df = merge_annotation_files(raw_files)
    audit_df = build_label_audit(merged_df)
    cleaned_df = prepare_clean_dataframe(audit_df)
    train_df, val_df, test_df = split_dataset(cleaned_df)

    merged_df.to_csv(paths.interim_dir / "merged_comments.csv", index=False)
    audit_df.to_csv(paths.interim_dir / "label_audit.csv", index=False)
    cleaned_df.to_csv(paths.interim_dir / "cleaned_comments.csv", index=False)
    train_df.to_csv(paths.processed_dir / "train.csv", index=False)
    val_df.to_csv(paths.processed_dir / "val.csv", index=False)
    test_df.to_csv(paths.processed_dir / "test.csv", index=False)

    metadata = build_metadata(merged_df, audit_df, cleaned_df, train_df, val_df, test_df)
    save_json(metadata, paths.processed_dir / "metadata.json")
    return metadata


def main() -> None:
    metadata = run_preprocessing()
    print("Preprocessing complete.")
    print(f"Rows after filtering: {metadata['rows_after_filtering']}")
    print(f"Train/val/test: {metadata['split_sizes']}")


if __name__ == "__main__":
    main()
