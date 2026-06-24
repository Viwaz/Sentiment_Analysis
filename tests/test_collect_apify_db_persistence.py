from __future__ import annotations

import pandas as pd

from src import collect_apify


def test_persist_collected_comments_to_db_writes_raw_cleaned_and_logs(monkeypatch):
    calls = []
    collected = pd.DataFrame(
        [
            {
                "id": "fallback-id",
                "comment_id": "comment-1",
                "text": "Great service!",
                "cleaned_text": "great service!",
                "source_url": "https://facebook.com/post/1",
                "collection_source": "apify/facebook-comments-scraper",
                "created_at": "2026-06-23T10:00:00Z",
                "apify_dataset_id": "dataset-1",
                "apify_run_id": "run-1",
                "emoji_aliases": "",
                "emoji_count": 0,
                "token_count_cleaned": 2,
            }
        ]
    )

    monkeypatch.setattr(
        "src.db.comments.insert_comment",
        lambda **kwargs: calls.append(("insert_comment", kwargs)) or kwargs["comment_id"],
    )
    monkeypatch.setattr(
        "src.db.preprocess.insert_preprocessed",
        lambda **kwargs: calls.append(("insert_preprocessed", kwargs)) or 1,
    )
    monkeypatch.setattr(
        "src.db.activity.log_action",
        lambda **kwargs: calls.append(("log_action", kwargs)) or 1,
    )

    result = collect_apify.persist_collected_comments_to_db(collected, user_id=7)

    assert result == {"comments_written": 1, "preprocessed_written": 1}
    assert [name for name, _ in calls] == [
        "insert_comment",
        "log_action",
        "insert_preprocessed",
        "log_action",
    ]
    assert calls[0][1]["comment_id"] == "comment-1"
    assert calls[0][1]["comment_text"] == "Great service!"
    assert calls[0][1]["apify_dataset_id"] == "dataset-1"
    assert calls[2][1]["cleaned_text"] == "great service!"
    assert [payload["action_type"] for name, payload in calls if name == "log_action"] == [
        "ingest",
        "preprocess",
    ]


def test_read_urls_from_file_supports_lines_and_commas(tmp_path):
    url_file = tmp_path / "url.txt"
    url_file.write_text(
        "# ignored\n"
        "https://facebook.com/post/1\n"
        "https://facebook.com/post/2, https://facebook.com/post/3\n",
        encoding="utf-8",
    )

    assert collect_apify.read_urls_from_file(url_file) == [
        "https://facebook.com/post/1",
        "https://facebook.com/post/2",
        "https://facebook.com/post/3",
    ]
