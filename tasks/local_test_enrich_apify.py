import pandas as pd
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.preprocess import add_clean_text_features

collected = Path("data/collected/apify_facebook_comments_preprocessed.csv")
if not collected.exists():
    collected = Path("data/collected/apify_facebook_comments.csv")

df = pd.read_csv(collected)
enriched = add_clean_text_features(df)
enriched.to_csv(Path("data/collected/apify_facebook_comments_preprocessed_test.csv"), index=False, encoding="utf-8")
print(f"Wrote enriched test file with {len(enriched)} rows")
