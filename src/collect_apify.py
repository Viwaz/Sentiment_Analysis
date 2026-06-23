from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Iterable
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

import pandas as pd
from .preprocess import add_clean_text_features
import numpy as np

from .data_utils import build_paths, ensure_project_dirs

DEFAULT_ACTOR_ID = "apify/facebook-comments-scraper"
DEFAULT_TOKEN_FILE = Path("secret/token.txt")
DEFAULT_URL_FILE = Path("secret/url.txt")
TEXT_FIELDS = ("text", "comment", "commentText", "message", "body")
ID_FIELDS = ("id", "commentId", "comment_id")
# AUTHOR_FIELDS = ("authorName", "author", "profileName", "userName")
CREATED_FIELDS = ("createdAt", "created_at", "date", "timestamp")


def get_apify_token(token: str | None = None, token_file: str | Path | None = None) -> str:
    if token_file and not token:
        token_path = Path(token_file)
        if not token_path.exists():
            raise FileNotFoundError(f"Apify token file does not exist: {token_path}")
        token = token_path.read_text(encoding="utf-8").strip()
    token = token or os.getenv("APIFY_API_TOKEN")
    if not token:
        raise RuntimeError("Set APIFY_API_TOKEN, pass --token, or pass --token-file before collecting data from Apify.")
    return token


def _first_present(item: dict, fields: Iterable[str]) -> object | None:
    for field in fields:
        value = item.get(field)
        if value not in (None, ""):
            return value
    return None


def _normalise_start_urls(urls: list[str]) -> list[dict]:
    return [{"url": url} for url in urls]


def read_urls_from_file(url_file: str | Path = DEFAULT_URL_FILE) -> list[str]:
    """Read one or more Facebook URLs from a local text file."""
    path = Path(url_file)
    if not path.exists():
        raise FileNotFoundError(f"URL file does not exist: {path}")

    urls: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        urls.extend(part.strip() for part in stripped.split(",") if part.strip())
    return urls


def _db_value(value: object) -> object | None:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    return value


def _db_text(value: object, default: str = "") -> str:
    cleaned = _db_value(value)
    return default if cleaned is None else str(cleaned)


def _comment_id_from_row(row: pd.Series, index: int) -> str:
    explicit_id = _db_value(row.get("comment_id"))
    if explicit_id is not None:
        return str(explicit_id)

    source_id = _db_value(row.get("id"))
    dataset_id = _db_text(row.get("apify_dataset_id"), "dataset")
    run_id = _db_text(row.get("apify_run_id"), "run")
    suffix = str(source_id) if source_id is not None else str(index + 1)
    return f"apify_{dataset_id}_{run_id}_{suffix}"


def run_facebook_comments_actor(
    urls: list[str],
    limit: int,
    token: str | None = None,
    token_file: str | Path | None = None,
    actor_id: str = DEFAULT_ACTOR_ID,
) -> tuple[str, str]:
    from apify_client import ApifyClient

    client = ApifyClient(get_apify_token(token, token_file=token_file))
    run_input = {
        "startUrls": _normalise_start_urls(urls),
        "resultsLimit": limit,
    }
    run = client.actor(actor_id).call(run_input=run_input)
    if isinstance(run, dict):
        return run["defaultDatasetId"], run["id"]
    return run.default_dataset_id, run.id


def fetch_apify_dataset_items(
    dataset_id: str,
    token: str | None = None,
    token_file: str | Path | None = None,
) -> list[dict]:
    from apify_client import ApifyClient

    client = ApifyClient(get_apify_token(token, token_file=token_file))
    return list(client.dataset(dataset_id).iterate_items())


def run_facebook_comments_sync(
    urls: list[str],
    limit: int,
    token: str | None = None,
    token_file: str | Path | None = None,
    actor_id: str = DEFAULT_ACTOR_ID,
    timeout_seconds: int = 300,
) -> list[dict]:
    actor_api_id = actor_id.replace("/", "~")
    actor_path = quote(actor_api_id, safe="")
    query = urlencode({"format": "json", "clean": "true", "limit": limit})
    endpoint = f"https://api.apify.com/v2/actors/{actor_path}/run-sync-get-dataset-items?{query}"
    payload = json.dumps(
        {
            "startUrls": _normalise_start_urls(urls),
            "resultsLimit": limit,
        }
    ).encode("utf-8")
    request = Request(
        endpoint,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {get_apify_token(token, token_file=token_file)}",
            "Content-Type": "application/json",
        },
    )
    with urlopen(request, timeout=timeout_seconds) as response:
        return json.loads(response.read().decode("utf-8"))


def normalise_apify_items(items: list[dict], source_urls: list[str]) -> pd.DataFrame:
    rows = []
    default_source_url = source_urls[0] if source_urls else ""
    for index, item in enumerate(items, start=1):
        text = _first_present(item, TEXT_FIELDS)
        if text in (None, ""):
            continue
        rows.append(
            {
                "id": _first_present(item, ID_FIELDS) or index,
                "text": str(text),
                "source_url": item.get("url") or item.get("postUrl") or default_source_url,
                "comment_id": _first_present(item, ID_FIELDS),
                "created_at": _first_present(item, CREATED_FIELDS),
                "collection_source": "apify/facebook-comments-scraper",
            }
        )
    if not rows:
        raise ValueError("Apify returned no records with a usable comment text field.")
    return pd.DataFrame(rows)


def collect_facebook_comments(
    urls: list[str] | None = None,
    limit: int = 50,
    output_path: str | Path | None = None,
    mode: str = "actor",
    token: str | None = None,
    token_file: str | Path | None = None,
    actor_id: str = DEFAULT_ACTOR_ID,
    dataset_id: str | None = None,
    root: Path | None = None,
) -> pd.DataFrame:
    paths = build_paths(root)
    ensure_project_dirs(paths)
    output_path = Path(output_path) if output_path else paths.collected_dir / "apify_facebook_comments.csv"
    source_urls = urls or []

    if dataset_id:
        items = fetch_apify_dataset_items(dataset_id, token=token, token_file=token_file)
        run_id = ""
    elif mode == "sync":
        if not source_urls:
            raise ValueError("At least one --url is required when running the Apify actor.")
        items = run_facebook_comments_sync(source_urls, limit, token=token, token_file=token_file, actor_id=actor_id)
        dataset_id = ""
        run_id = ""
    else:
        if not source_urls:
            raise ValueError("At least one --url is required when running the Apify actor.")
        dataset_id, run_id = run_facebook_comments_actor(source_urls, limit, token=token, token_file=token_file, actor_id=actor_id)
        items = fetch_apify_dataset_items(dataset_id, token=token, token_file=token_file)

    df = normalise_apify_items(items, source_urls)
    df["apify_dataset_id"] = dataset_id
    df["apify_run_id"] = run_id
    # Save raw collected CSV
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8")

    # Enrich collected data to match processed schema (no labels filled)
    enriched = add_clean_text_features(df)

    # Add or fill processed-style columns with sensible defaults/placeholders
    enriched["topic_label"] = np.nan
    enriched["sentiment_label"] = np.nan
    enriched["confidence"] = np.nan
    enriched["include"] = "yes"
    enriched["notes"] = ""
    enriched["source_file"] = "apify/facebook-comments-scraper"
    enriched["sentiment_label_normalized"] = np.nan
    enriched["include_normalized"] = "yes"
    enriched["text_missing"] = enriched["text"].isna() | enriched["text"].astype(str).str.strip().eq("")
    enriched["text_length_chars"] = enriched["cleaned_text"].astype(str).str.len().fillna(0).astype(int)
    enriched["token_count_whitespace"] = enriched["text"].astype(str).apply(lambda t: len(str(t).split())).fillna(0).astype(int)
    enriched["is_short_comment"] = enriched["token_count_cleaned"].fillna(0).astype(int) < 3
    enriched["is_duplicate_text"] = False
    enriched["exclude_reason"] = np.nan
    enriched["label"] = np.nan

    # Ensure output path for preprocessed file
    preproc_path = output_path.parent / "apify_facebook_comments_preprocessed.csv"
    enriched.to_csv(preproc_path, index=False, encoding="utf-8")
    return enriched


def persist_collected_comments_to_db(
    collected: pd.DataFrame,
    user_id: int | None = None,
) -> dict[str, int]:
    """Persist collected Apify rows to raw and preprocessed DB tables."""
    from src.db.activity import log_action
    from src.db.comments import insert_comment
    from src.db.preprocess import insert_preprocessed

    comments_written = 0
    preprocessed_written = 0

    for index, row in collected.reset_index(drop=True).iterrows():
        comment_id = _comment_id_from_row(row, index)
        text = _db_text(row.get("text"))
        cleaned_text = _db_text(row.get("cleaned_text"))

        if not text:
            continue

        insert_comment(
            comment_id=comment_id,
            comment_text=text,
            source_url=_db_text(row.get("source_url")),
            collection_source=_db_text(row.get("collection_source"), DEFAULT_ACTOR_ID),
            created_at=_db_value(row.get("created_at")),
            apify_dataset_id=_db_text(row.get("apify_dataset_id")) or None,
            apify_run_id=_db_text(row.get("apify_run_id")) or None,
        )
        log_action(
            user_id=user_id,
            action_type="ingest",
            comment_id=comment_id,
            details={"source": "collect_apify"},
        )
        comments_written += 1

        if cleaned_text:
            insert_preprocessed(
                comment_id=comment_id,
                cleaned_text=cleaned_text,
                emoji_aliases=_db_text(row.get("emoji_aliases")) or None,
                emoji_count=_db_value(row.get("emoji_count")),
                token_count=_db_value(row.get("token_count_cleaned")),
            )
            log_action(
                user_id=user_id,
                action_type="preprocess",
                comment_id=comment_id,
                details={"source": "collect_apify"},
            )
            preprocessed_written += 1

    return {
        "comments_written": comments_written,
        "preprocessed_written": preprocessed_written,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect Facebook comments from Apify for prediction.")
    parser.add_argument("--url", action="append", default=[], help="Facebook post URL. Pass multiple times for multiple posts.")
    parser.add_argument("--url-file", default=str(DEFAULT_URL_FILE), help="Text file containing Facebook post URLs.")
    parser.add_argument("--dataset-id", default=None, help="Fetch an existing Apify dataset without rerunning the actor.")
    parser.add_argument("--limit", type=int, default=50, help="Maximum comments to request from the actor.")
    parser.add_argument("--output", default=None, help="CSV path for collected comments.")
    parser.add_argument("--mode", choices=["actor", "sync"], default="actor", help="Actor mode fetches dataset after run; sync returns items directly.")
    parser.add_argument("--actor-id", default=DEFAULT_ACTOR_ID, help="Apify actor ID.")
    parser.add_argument("--token", default=None, help="Apify token. Prefer APIFY_API_TOKEN instead of this argument.")
    parser.add_argument("--token-file", default=str(DEFAULT_TOKEN_FILE), help="Path to a local file containing the Apify token.")
    parser.add_argument("--persist-db", action="store_true", help="Persist collected raw and preprocessed comments to PostgreSQL.")
    parser.add_argument("--user-id", type=int, default=None, help="Optional user_id for DB activity logs.")
    parser.add_argument("--predict-output", default=None, help="Optional CSV path for immediate prediction output.")
    parser.add_argument("--reference-model", default="afriberta_small", help="Reference model to use when --predict-output is set.")
    parser.add_argument("--run-name", default="afriberta_small", help="Transformer run name for prediction.")
    args = parser.parse_args()

    urls = args.url
    if not urls and not args.dataset_id:
        urls = read_urls_from_file(args.url_file)

    if not args.dataset_id and not urls:
        parser.error("Pass --url, provide --url-file, or pass --dataset-id.")

    output_path = Path(args.output) if args.output else None
    collected = collect_facebook_comments(
        urls=urls,
        limit=args.limit,
        output_path=output_path,
        mode=args.mode,
        token=args.token,
        token_file=args.token_file,
        actor_id=args.actor_id,
        dataset_id=args.dataset_id,
    )
    final_output_path = output_path or build_paths().collected_dir / "apify_facebook_comments.csv"
    print(f"Wrote {len(collected)} collected comments to {final_output_path}")

    if args.persist_db:
        result = persist_collected_comments_to_db(collected, user_id=args.user_id)
        print(
            "Persisted collected comments to DB: "
            f"{result['comments_written']} raw, {result['preprocessed_written']} preprocessed"
        )

    if args.predict_output:
        from .predict import run_batch_prediction

        predictions = run_batch_prediction(
            input_path=final_output_path,
            output_path=args.predict_output,
            reference_model=args.reference_model,
            run_name=args.run_name,
        )
        print(f"Wrote {len(predictions)} predictions to {args.predict_output}")


if __name__ == "__main__":
    main()
