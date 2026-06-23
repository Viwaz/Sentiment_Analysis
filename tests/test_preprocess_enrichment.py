from __future__ import annotations

import pandas as pd

from src.preprocess import add_clean_text_features


def test_add_clean_text_features_enriches_collected_comments():
    df = pd.DataFrame(
        [
            {
                "id": "comment-1",
                "text": "Great work! 😊",
                "source_url": "https://facebook.com/post/1",
            }
        ]
    )

    enriched = add_clean_text_features(df)

    assert "cleaned_text" in enriched.columns
    assert "emoji_aliases" in enriched.columns
    assert "emoji_count" in enriched.columns
    assert "token_count_cleaned" in enriched.columns
    assert enriched.loc[0, "emoji_count"] == 1
    assert "emoji_" in enriched.loc[0, "cleaned_text"]
