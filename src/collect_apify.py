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
    return run["defaultDatasetId"], run["id"]


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


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect Facebook comments from Apify for prediction.")
    parser.add_argument("--url", action="append", default=[], help="Facebook post URL. Pass multiple times for multiple posts.")
    parser.add_argument("--dataset-id", default=None, help="Fetch an existing Apify dataset without rerunning the actor.")
    parser.add_argument("--limit", type=int, default=50, help="Maximum comments to request from the actor.")
    parser.add_argument("--output", default=None, help="CSV path for collected comments.")
    parser.add_argument("--mode", choices=["actor", "sync"], default="actor", help="Actor mode fetches dataset after run; sync returns items directly.")
    parser.add_argument("--actor-id", default=DEFAULT_ACTOR_ID, help="Apify actor ID.")
    parser.add_argument("--token", default=None, help="Apify token. Prefer APIFY_API_TOKEN instead of this argument.")
    parser.add_argument("--token-file", default=None, help="Path to a local file containing the Apify token.")
    parser.add_argument("--predict-output", default=None, help="Optional CSV path for immediate prediction output.")
    parser.add_argument("--reference-model", default="afriberta_small", help="Reference model to use when --predict-output is set.")
    parser.add_argument("--run-name", default="afriberta_small", help="Transformer run name for prediction.")
    args = parser.parse_args()

    if not args.dataset_id and not args.url:
        parser.error("Pass --url to run the Apify actor or --dataset-id to fetch an existing dataset.")

    output_path = Path(args.output) if args.output else None
    collected = collect_facebook_comments(
        urls=args.url,
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
