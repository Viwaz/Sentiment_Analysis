# Recent changes: Apify collection & preprocessing

**Date:** 2026-06-22

**What changed:** implemented enrichment of Apify-collected Facebook comments so the collected data matches the processed dataset schema used for training.

**Files added / modified:**

- `src/collect_apify.py` — updated to call preprocessing utilities after normalising items; writes both the raw collected CSV and a preprocessed CSV (`data/collected/apify_facebook_comments_preprocessed.csv`) that includes `cleaned_text`, `tokens`, `token_count_cleaned`, `emoji_aliases`, `emoji_count` and placeholder processed-style columns (`topic_label`, `sentiment_label`, `label`, `include`, `text_length_chars`, `token_count_whitespace`, `is_short_comment`, `is_duplicate_text`, etc.). Labels are left empty (NaN) because Apify collection is unlabeled.

- `src/compare_collected_vs_processed.py` — added a small utility script to compare collected vs processed CSVs (schema, cleaned_text presence, label distribution); writes a JSON report at `reports/results/compare_apify_vs_processed.json`.

- `tasks/local_test_enrich_apify.py` — small helper used locally to test enrichment of existing collected CSV files.

**Why:** Make the Apify-collected workflow compatible with downstream training and evaluation code so you can transfer between file-based and API-based data sources without changing model input logic.

**Notes / prerequisites:**

- The enrichment/preprocessing uses `src/preprocess.py` which depends on the `emoji` package. Install requirements via `pip install -r requirements.txt` or `pip install emoji apify-client` before running collection/enrichment.
- The preprocessed Apify file intentionally leaves label fields empty; you can later match `cleaned_text` to existing labeled rows to transfer labels when appropriate.

**Next steps suggested:**

1. Optionally run `src/compare_collected_vs_processed.py` to regenerate the comparison report after collecting new data.
2. Add a CLI flag `--preprocess` to `src/collect_apify.py` if you want preprocessing to be optional at collection time.
3. (Optional) Implement a fuzzy-match label transfer that attaches `label` from processed data when `cleaned_text` matches collected rows.
