import sys
import os
import traceback
from pathlib import Path
import pandas as pd

# Add the project root to python path to resolve local src imports
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.collect_apify import collect_facebook_comments
from src.preprocess import clean_text
from src.model_service import load_model

def run_demo():
    print("=" * 60)
    print("STARTING FACEBOOK COMMENT PIPELINE DEMO")
    print("=" * 60)

    # Paths
    collected_dir = project_root / "data" / "collected"
    collected_csv = collected_dir / "apify_facebook_comments.csv"
    preprocessed_csv = collected_dir / "apify_facebook_comments_preprocessed.csv"
    predictions_csv = project_root / "reports" / "results" / "demo_predictions.csv"
    token_file = project_root / "secrets" / "apify_token.txt"
    url_file = project_root / "secrets" / "url.txt"

    # Step 0: Verification of credentials and URL
    print("\n[Step 0] Verifying Setup and Secrets...")
    if not token_file.exists():
        print(f"Error: Token file not found at {token_file}")
        return
    if not url_file.exists():
        print(f"Error: URL file not found at {url_file}")
        return

    try:
        token = token_file.read_text().strip()
        url = url_file.read_text().strip()
        print(f"  Token found (prefix: {token[:12]}...)")
        print(f"  Target URL: {url}")
    except Exception as e:
        print(f"Error reading secrets: {e}")
        traceback.print_exc()
        return

    # Step 1: Scraping and Retrieval
    print("\n[Step 1] Scraping Comments from Apify...")
    print("  Running Apify actor 'apify/facebook-comments-scraper' in sync mode (limit: 100)...")
    try:
        # We will use mode='sync' to run synchronously and limit to 100 comments
        collected_df = collect_facebook_comments(
            urls=[url],
            limit=100,
            output_path=collected_csv,
            mode="sync",
            token_file=token_file,
            root=project_root
        )
        print("  Scraping and enrichment completed successfully!")
        print(f"  Enriched/Preprocessed Data saved to: {preprocessed_csv}")
        print(f"  Scraped DataFrame shape: {collected_df.shape}")
        print("  Columns returned:", list(collected_df.columns))
        print("  Sample comments collected:")
        for idx, row in collected_df.head(3).iterrows():
            print(f"    - ID {row.get('id')}: {str(row.get('text'))[:60]}...")
    except Exception as e:
        print(f"❌ Error during Scraping stage: {e}")
        traceback.print_exc()
        return

    # Step 2: Verification of Preprocessed Data
    print("\n[Step 2] Verifying Preprocessed Data...")
    try:
        if not preprocessed_csv.exists():
            raise FileNotFoundError(f"Preprocessed CSV not found: {preprocessed_csv}")

        df = pd.read_csv(preprocessed_csv)
        print(f"  Loaded {len(df)} rows from {preprocessed_csv}")
        print(f"  Preprocessed DataFrame shape: {df.shape}")
        print("  Columns in preprocessed data:", list(df.columns))
        print("  Preprocessed Sample:")
        for idx, row in df.head(3).iterrows():
            print(f"    - Original: {str(row['text'])[:50]}...")
            print(f"      Cleaned:  {str(row['cleaned_text'])[:50]}...")
    except Exception as e:
        print(f"❌ Error during Preprocessing verification stage: {e}")
        traceback.print_exc()
        return

    # Step 3: Baseline Model Prediction
    print("\n[Step 3] Running Predictions using Baseline Model...")
    try:
        if not preprocessed_csv.exists():
            raise FileNotFoundError(f"Preprocessed CSV not found: {preprocessed_csv}")

        df_preprocessed = pd.read_csv(preprocessed_csv)

        # Load baseline model service
        print("  Loading baseline model service...")
        model_service = load_model("baseline", root=project_root)
        print(f"  Loaded model family: {model_service.info.model_family}")
        print(f"  Model name: {model_service.info.model_name}")
        print(f"  Model version: {model_service.info.model_version}")

        # Run batch prediction
        print("  Predicting sentiment...")
        predictions_df = model_service.predict_batch(df_preprocessed)
        
        # Save predictions
        predictions_csv.parent.mkdir(parents=True, exist_ok=True)
        predictions_df.to_csv(predictions_csv, index=False, encoding="utf-8")
        print("  Predictions completed successfully!")
        print(f"  Predictions saved to: {predictions_csv}")
        print("\n  Prediction results sample:")
        for idx, row in predictions_df.head(3).iterrows():
            print(f"    - Cleaned: {str(row['cleaned_text'])[:50]}...")
            print(f"      Label:   {row['predicted_label']} (confidence: {row['predicted_confidence']:.4f})")
        
        print("\n  Predicted Label Distribution:")
        print(predictions_df["predicted_label"].value_counts())
    except Exception as e:
        print(f"❌ Error during Prediction stage: {e}")
        traceback.print_exc()
        return

    print("\n" + "=" * 60)
    print("DEMO RUN FINISHED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_demo()
