# Low-Resource Facebook Sentiment Classifier

This project builds and evaluates sentiment classifiers for code-switched Facebook comments in a low-resource language setting. The current prototype supports data preprocessing, baseline model training, transformer fine-tuning, external evaluation, active learning, and result reporting.

## Current Status

The latest processed dataset contains:

- Raw rows loaded: `2393`
- Rows after filtering: `1813`
- Train/validation/test split: `1269 / 272 / 272`
- Label distribution: `negative=1019`, `positive=410`, `neutral=384`
- Rows containing emojis: `467`

Latest internal test results from the current saved metric files:

| Model | Feature/input | Test macro F1 | Test accuracy | Weighted F1 |
|---|---|---:|---:|---:|
| Logistic Regression | Character TF-IDF | `0.5463` | `0.6140` | `0.6124` |
| AfriBERTa Small | Subword transformer | `0.4901` | `0.5368` | `0.5481` |
| XLM-RoBERTa Base | Subword transformer | `0.2994` | `0.5439` | `0.5748` |
| External baseline evaluation | Separate external dataset | `0.3572` | `0.3783` | `0.4254` |

The current strongest saved internal test result is the Logistic Regression baseline with character TF-IDF. AfriBERTa Small remains important because it tests transfer learning on an African-language model, but the current evidence does not justify replacing the baseline automatically.

The XLM-RoBERTa metric file is an older saved transformer run. It is useful historical evidence that the team tried a multilingual transformer, but it should be rerun on the current processed split before being treated as a strict apples-to-apples comparison.

## Project Layout

```text
project/
|-- data/
|   |-- collected/
|   |-- raw/
|   |-- external_test/
|   |-- interim/
|   `-- processed/
|-- docs/
|   |-- COLAB_AFRIBERTA.md
|   |-- GROUP_4_DS_SRS_V7.pdf
|   `-- TEAM_PROJECT_STRUCTURE_AND_WORKFLOW_DOCUMENT.md
|-- models/
|   |-- baseline/
|   `-- transformer/
|-- notebooks/
|   |-- 01_data_audit.ipynb
|   |-- 02_preprocessing.ipynb
|   |-- 03_baseline_models.ipynb
|   |-- 04_transformer_training.ipynb
|   |-- 05_error_analysis.ipynb
|   |-- 06_external_evaluation.ipynb
|   `-- 07_active_learning.ipynb
|-- reports/
|   |-- figures/
|   `-- results/
|-- src/
|   |-- active_learning.py
|   |-- collect_apify.py
|   |-- compare_models.py
|   |-- data_utils.py
|   |-- evaluate.py
|   |-- evaluate_external.py
|   |-- features.py
|   |-- model_service.py
|   |-- predict.py
|   |-- preprocess.py
|   |-- train_baseline.py
|   `-- train_transformer.py
|-- requirements.txt
`-- README.md
```

## Folder Responsibilities

- `data/raw/`: original annotation CSV files. These files are the source of truth for training data.
- `data/collected/`: unlabeled comments collected from external sources such as Apify for prediction or annotation.
- `data/external_test/`: separate evaluation-only CSV files. These are not used in training or model selection.
- `data/interim/`: merged, audited, and cleaned intermediate files for inspection.
- `data/processed/`: final train, validation, and test splits used by all models.
- `src/`: reusable Python implementation of preprocessing, training, evaluation, comparison, and active learning.
- `notebooks/`: human-facing audit, experiment, and reporting notebooks.
- `models/`: saved model artifacts. Large transformer checkpoints should not be committed to Git.
- `reports/results/`: metrics JSON/CSV files and prediction tables.
- `reports/figures/`: confusion matrices, learning curves, and model comparison charts.
- `docs/`: team-facing, Colab, SRS, and presentation-support documentation.

## Expected Raw Data Format

Place training annotation CSV files inside `data/raw/`. Each file should contain at least:

- `id`
- `text`
- `sentiment_label`
- `include`

Additional columns such as `topic_label`, `confidence`, `notes`, or `source_file` are preserved when possible.

Place any separate evaluation-only dataset inside `data/external_test/`. It should use labels that can be normalized to:

- `negative`
- `neutral`
- `positive`

## Recommended Workflow

Run preprocessing:

```powershell
python -m src.preprocess
```

Train baseline models:

```powershell
python -m src.train_baseline
```

This compares Logistic Regression, Linear SVM, Multinomial Naive Bayes, and Complement Naive Bayes across word, character, and combined TF-IDF feature sets.

Train AfriBERTa Small:

```powershell
python -m src.train_transformer --model_name castorini/afriberta_small --run_name afriberta_small
```

Evaluate the baseline on the external test dataset:

```powershell
python -m src.evaluate_external
```

Evaluate a trained transformer on the external test dataset:

```powershell
python -m src.evaluate_external --model_type transformer --model_name castorini/afriberta_small --run_name afriberta_small
```

Rebuild the model comparison table:

```powershell
python -m src.compare_models
```

Run batch inference on a CSV of new comments:

```powershell
python -m src.predict --input_path path/to/new_comments.csv --output_path reports/results/batch_predictions.csv --reference_model baseline
```

Use `--reference_model afriberta_small` to score the same CSV with the transformer reference run.

The model loading and prediction contract lives in `src/model_service.py`. The CSV command in `src/predict.py` is only the file adapter: it reads comments, applies preprocessing, calls the selected model service, and writes prediction results. This keeps the model module replaceable without changing preprocessing, database writing, or dashboard code later.

Run the hosted model service locally:

```powershell
uvicorn src.model_api:app --host 0.0.0.0 --port 8000
```

The hosted API loads the selected model once at startup. By default it loads `afriberta_small`; use `MODEL_REFERENCE=baseline` to run the lighter baseline service. Prediction requests must provide `cleaned_text`, because preprocessing is intentionally owned by a separate module.

Hosted endpoints:

- `GET /health`
- `GET /model-info`
- `POST /comments`
- `GET /comments/{comment_id}`
- `POST /predict`
- `POST /predict-batch`
- `POST /predict-pipeline`
- `GET /dashboard/predictions`

The database-backed API flow is:

```text
POST /predict-pipeline
  raw comment -> comments
  cleaned text -> preprocessed_comments
  model output -> predictions
  audit events -> activity_logs

GET /dashboard/predictions
  predictions joined with raw comment text and cleaned text
```

Run Postgres locally before using the DB-backed endpoints:

```powershell
docker compose up -d db
```

The container applies `Database/schema.sql` on first initialization. If an existing `db_data` volume was created from an older schema, apply the SQL migration under `Database/migrations/` or recreate the local development volume after backing up any data you need.

Collect Facebook comments through Apify and feed them into the prediction pipeline:

```powershell
python -m src.collect_apify --token-file secrets/apify_token.txt --url "https://www.facebook.com/..." --limit 50 --output data/collected/apify_facebook_comments.csv --predict-output reports/results/apify_predictions.csv --reference-model afriberta_small
```

If the Apify actor has already run and you have the dataset ID, fetch that dataset directly without scraping again:

```powershell
python -m src.collect_apify --token-file secrets/apify_token.txt --dataset-id "YOUR_DATASET_ID" --output data/collected/apify_existing_dataset.csv --predict-output reports/results/apify_predictions.csv --reference-model afriberta_small
```

The default collection mode runs the Apify actor, fetches the actor dataset, normalizes comments into a `text` column, and then optionally calls the existing prediction pipeline. Put the Apify token in `secrets/apify_token.txt` or set `APIFY_API_TOKEN`; never commit the token. Use `--dataset-id` when the data already exists in Apify storage. Use `--mode sync` only for small demo runs where the Apify synchronous endpoint can finish before timing out.

For GPU-based Colab training, use `docs/COLAB_AFRIBERTA.md`.

## Preprocessing Behavior

The preprocessing pipeline:

- loads each raw CSV and records `source_file`
- normalizes labels to `negative`, `neutral`, and `positive`
- filters rows where `include` is not approved
- audits missing labels, missing text, excluded rows, duplicates, and very short comments
- applies light text normalization
- preserves sentiment-bearing punctuation such as `!` and `?`
- preserves emojis and appends readable emoji alias tokens to `cleaned_text`
- exports fixed train/validation/test splits and metadata

Generated preprocessing outputs:

- `data/interim/merged_comments.csv`
- `data/interim/label_audit.csv`
- `data/interim/cleaned_comments.csv`
- `data/processed/train.csv`
- `data/processed/val.csv`
- `data/processed/test.csv`
- `data/processed/metadata.json`

## Reporting Outputs

The most useful files for presentation and review are:

- `reports/results/model_comparison.csv`
- `reports/results/model_comparison_ppt_table.csv`
- `reports/results/baseline_metrics.json`
- `reports/results/afriberta_small_metrics.json`
- `reports/results/external_baseline_metrics.json`
- `models/baseline/model_metadata.json`
- `models/transformer/afriberta_small/model_metadata.json`
- `reports/figures/model_comparison_macro_f1.png`
- `reports/figures/baseline_confusion_matrix.png`
- `reports/figures/afriberta_small_confusion_matrix.png`
- `reports/figures/afriberta_small_learning_curves.png`

## Notes For Low-Resource, Code-Switched Text

- Avoid generic English stopword removal unless the team has evidence it helps.
- Avoid English stemming or lemmatization for local-language text.
- Preserve negations, hashtags, emojis, and expressive punctuation.
- Prefer character n-grams and multilingual/subword transformer models over a manually fixed vocabulary.
- Treat external evaluation as a generalization check, not as another training split.

## Documentation

Team and submission-facing documentation is kept in `docs/`.

Use:

- `docs/TEAM_PROJECT_STRUCTURE_AND_WORKFLOW_DOCUMENT.md` for team alignment.
- `docs/COLAB_AFRIBERTA.md` for remote GPU training.
- `docs/GROUP_4_DS_SRS_V7.pdf` for the current SRS PDF copy.

The original SRS PDF may still exist at the repository root on some machines if Windows or OneDrive blocks moving the file. The preferred documentation location is `docs/`.
