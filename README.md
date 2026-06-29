# Low-Resource Facebook Sentiment Classifier

A longitudinal sentiment analysis system for code-switched Facebook comments in low-resource language settings. The platform combines a pretrained **AfriBERTa Small** transformer model with a multi-user **Streamlit dashboard**, a **FastAPI model service**, and a **PostgreSQL** persistence layer for tracking public sentiment shifts over time.

---

## Architecture Overview

```
+-------------------------------------------------------------+
|                    Streamlit Dashboard                      |
|  * Login / Registration (bcrypt auth)                       |
|  * Apify Facebook scraper integration                       |
|  * Session history sidebar with context menus              |
|  * Longitudinal time-series sentiment charts                |
+----------------------+--------------------------------------+
                       | HTTP
+----------------------v--------------------------------------+
|               FastAPI Model Service (src/model_api.py)      |
|  * AfriBERTa Small / Logistic Regression baseline           |
|  * /predict, /predict-batch, /predict-pipeline endpoints    |
|  * PostgreSQL-backed comment & prediction storage           |
+----------------------+--------------------------------------+
                       | psycopg2
+----------------------v--------------------------------------+
|              PostgreSQL  (two schema namespaces)            |
|  public.*    -> developer pipeline tables (comments, etc.) |
|  dashboard.* -> app tables (users, sessions, comments)      |
+-------------------------------------------------------------+
```

---

## Current Model Performance

| Model | Feature/Input | Test Macro F1 | Test Accuracy | Weighted F1 |
|---|---|---:|---:|---:|
| Logistic Regression | Character TF-IDF | `0.5463` | `0.6140` | `0.6124` |
| AfriBERTa Small | Subword transformer | `0.4901` | `0.5368` | `0.5481` |
| XLM-RoBERTa Base | Subword transformer | `0.2994` | `0.5439` | `0.5748` |
| External baseline | Separate external dataset | `0.3572` | `0.3783` | `0.4254` |

> The strongest saved test result is the Logistic Regression baseline with character TF-IDF. AfriBERTa Small is used as the default dashboard model because it tests cross-lingual transfer on African-language text.

---

## Dataset Statistics

- Raw rows loaded: `2393`
- Rows after filtering: `1813`
- Train / Validation / Test: `1269 / 272 / 272`
- Label distribution: `negative=1019`, `positive=410`, `neutral=384`
- Rows containing emojis: `467`

---

## Project Layout

```
project/
+-- data/
|   +-- collected/          # Apify-scraped comments (CSV)
|   +-- raw/                # Human-annotated source CSVs
|   +-- external_test/      # Held-out evaluation datasets
|   +-- interim/            # Merged, cleaned intermediate files
|   +-- processed/          # Final train/val/test splits
+-- Database/
|   +-- schema.sql          # Public schema DDL for model API tables
|   +-- migrations/         # Incremental schema migrations
+-- docs/
|   +-- COLAB_AFRIBERTA.md
|   +-- GROUP_4_DS_SRS_V7.pdf
|   +-- TEAM_PROJECT_STRUCTURE_AND_WORKFLOW_DOCUMENT.md
+-- models/
|   +-- baseline/           # Saved LogReg + TF-IDF pipeline
|   +-- transformer/        # AfriBERTa Small fine-tuned checkpoint
+-- notebooks/              # Audit, experiment, and reporting notebooks
+-- reports/
|   +-- figures/            # Confusion matrices, learning curves, charts
|   +-- results/            # Metrics JSON/CSV and prediction tables
+-- src/
|   +-- auth.py             # JWT authentication helpers
|   +-- collect_apify.py    # Apify Facebook scraper integration
|   +-- compare_models.py   # Cross-model comparison table builder
|   +-- config.py           # Environment config (DB, model paths)
|   +-- data_utils.py       # Dataset loaders and split helpers
|   +-- database.py         # Dashboard PostgreSQL layer (dashboard.*)
|   +-- db/                 # Connection pool / connection factory
|   +-- evaluate.py         # Internal test-set evaluator
|   +-- evaluate_external.py# External dataset evaluator
|   +-- features.py         # TF-IDF feature construction
|   +-- model_api.py        # FastAPI model service
|   +-- model_service.py    # Model loading and prediction contract
|   +-- predict.py          # Batch CSV inference entry point
|   +-- preprocess.py       # Full preprocessing pipeline
|   +-- train_baseline.py   # Baseline model training
|   +-- train_transformer.py# Transformer fine-tuning (AfriBERTa)
+-- tests/
|   +-- test_api_db_pipeline_contract.py
|   +-- test_collect_apify_db_persistence.py
|   +-- test_db_integration.py
|   +-- test_model_api_endpoints.py
|   +-- test_new_database.py
|   +-- test_preprocess_enrichment.py
+-- streamlit_app.py        # Multi-user Streamlit dashboard
+-- Dockerfile
+-- docker-compose.yml
+-- requirements.txt
```

---

## Database Schema

The project uses **two isolated PostgreSQL schema namespaces** to prevent table conflicts between the developer ML pipeline and the live dashboard.

### `public.*` — Model API Pipeline Tables
Managed by `Database/schema.sql` and the FastAPI service. Includes `comments`, `preprocessed_comments`, `predictions`, and `activity_logs`.

### `dashboard.*` — Streamlit App Tables
Initialized automatically by `src/database.py -> init_db()` on dashboard startup.

| Table | Key Columns |
|---|---|
| `dashboard.users` | `user_id`, `username`, `password` (bcrypt), `role`, `is_active` |
| `dashboard.sessions` | `session_id`, `user_id` (FK), `url`, `timestamp`, `custom_title` |
| `dashboard.comments` | `comment_id`, `session_id` (FK cascade), `text`, `sentiment`, `created_time` |

> **Important**: Never modify `public.*` tables from dashboard code. All dashboard CRUD targets `dashboard.*` only.

---

## Streamlit Dashboard Features

### Authentication
- Login and registration tabs with bcrypt password hashing.
- SHA-256 fallback for legacy password compatibility.
- Session state persists across page reruns via `st.session_state`.

### Session Management Sidebar
- **History Sessions list**: all past scraping sessions for the logged-in user, labelled using `COALESCE(custom_title, timestamp)`.
- **Context menu (gear popover)** per session:
  - **Original Post** — hyperlink to the scraped Facebook source.
  - **Rename** — conditional state-driven text input (hidden until clicked, revealed by toggle flag `show_rename_{session_id}`).
  - **Share** — sets `st.query_params["session_id"]` for shareable URL routing.
  - **Delete** — cascading deletion of session and all associated comments.
- Shareable URL support: opening `?session_id=N` automatically loads that session.

### Analysis Dashboard
- Scrape Facebook comments live via Apify with configurable post URL and comment limit.
- Batch sentiment scoring (Negative / Neutral / Positive) using the model API.
- Results persisted into `dashboard.sessions` and `dashboard.comments` using `psycopg2.extras.execute_values` for high-throughput batch inserts.
- Historical view loads stored results from PostgreSQL without re-scoring.

### Visualisations
- Pie chart of sentiment distribution.
- Grouped bar chart comparing sentiment counts.
- Time-series line chart of hourly sentiment trends.
- Word cloud of most frequent comment terms.
- Top-5 positive and negative comment highlights.

---

## Setup and Installation

### Prerequisites
- Python 3.10+
- PostgreSQL 14+
- Docker (optional, for containerised Postgres)

### Install Dependencies

```powershell
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file or set the following:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sentiment_db
DB_USER=postgres
DB_PASSWORD=your_password
APIFY_API_TOKEN=your_apify_token
MODEL_REFERENCE=afriberta_small
```

### Start PostgreSQL

```powershell
docker compose up -d db
```

The container applies `Database/schema.sql` on first start. For existing volumes with an older schema, run migrations under `Database/migrations/` or recreate the volume.

---

## Running the Dashboard

```powershell
streamlit run streamlit_app.py
```

On startup the dashboard will:
1. Connect to PostgreSQL and call `init_db()` to create the `dashboard` schema and tables if they do not exist.
2. Present a Login / Register gate before loading any content.
3. Load the authenticated user's session history into the sidebar.

---

## Running the Model API

```powershell
uvicorn src.model_api:app --host 0.0.0.0 --port 8000
```

Loads the selected model once at startup. Prediction requests must supply `cleaned_text` because preprocessing is owned by a separate module.

### API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness check |
| `GET` | `/model-info` | Active model metadata |
| `POST` | `/predict` | Single comment prediction |
| `POST` | `/predict-batch` | Batch prediction |
| `POST` | `/predict-pipeline` | Raw comment -> preprocess -> predict -> DB |
| `POST` | `/comments` | Insert a raw comment |
| `GET` | `/comments/{comment_id}` | Fetch stored comment |
| `GET` | `/dashboard/predictions` | Predictions joined with comment text |

---

## ML Pipeline Workflow

### Preprocessing

```powershell
python -m src.preprocess
```

Outputs: `data/interim/merged_comments.csv`, `data/interim/cleaned_comments.csv`, `data/processed/train.csv`, `val.csv`, `test.csv`, `data/processed/metadata.json`.

### Train Baseline

```powershell
python -m src.train_baseline
```

Compares Logistic Regression, Linear SVM, Multinomial NB, and Complement NB across word, character, and combined TF-IDF feature sets.

### Fine-tune AfriBERTa Small

```powershell
python -m src.train_transformer --model_name castorini/afriberta_small --run_name afriberta_small
```

For GPU training on Google Colab, see `docs/COLAB_AFRIBERTA.md`.

### Evaluate on External Dataset

```powershell
python -m src.evaluate_external
python -m src.evaluate_external --model_type transformer --model_name castorini/afriberta_small --run_name afriberta_small
```

### Rebuild Model Comparison Table

```powershell
python -m src.compare_models
```

### Batch Inference from CSV

```powershell
python -m src.predict --input_path path/to/comments.csv --output_path reports/results/predictions.csv --reference_model baseline
```

### Scrape Facebook via Apify

```powershell
python -m src.collect_apify --token-file secrets/apify_token.txt --url "https://www.facebook.com/..." --limit 50 --output data/collected/apify_comments.csv --predict-output reports/results/apify_predictions.csv --reference-model afriberta_small
```

To fetch an already-collected Apify dataset:

```powershell
python -m src.collect_apify --token-file secrets/apify_token.txt --dataset-id "YOUR_DATASET_ID" --output data/collected/apify_existing.csv --predict-output reports/results/apify_predictions.csv --reference-model afriberta_small
```

---

## Testing

All tests target the `dashboard.*` schema and the API contract; they do **not** modify `public.*` tables.

```powershell
$env:PYTHONPATH="."; pytest
```

**Current status: 41 / 41 tests passing.**

| Test File | Coverage Area |
|---|---|
| `test_new_database.py` | bcrypt auth, session save, title rename, cascade delete |
| `test_db_integration.py` | Full CRUD across `dashboard.*` tables |
| `test_api_db_pipeline_contract.py` | FastAPI <-> PostgreSQL contract |
| `test_collect_apify_db_persistence.py` | Apify scraper -> DB persistence |
| `test_model_api_endpoints.py` | Model API endpoint responses |
| `test_preprocess_enrichment.py` | Preprocessor text normalization |

---

## Reporting Outputs

| File | Description |
|---|---|
| `reports/results/model_comparison.csv` | Cross-model performance table |
| `reports/results/baseline_metrics.json` | Logistic Regression test metrics |
| `reports/results/afriberta_small_metrics.json` | AfriBERTa Small test metrics |
| `reports/results/external_baseline_metrics.json` | External evaluation metrics |
| `reports/figures/model_comparison_macro_f1.png` | Bar chart of macro F1 scores |
| `reports/figures/baseline_confusion_matrix.png` | Baseline confusion matrix |
| `reports/figures/afriberta_small_confusion_matrix.png` | Transformer confusion matrix |
| `reports/figures/afriberta_small_learning_curves.png` | Training loss / eval curves |

---

## Notes for Low-Resource Code-Switched Text

- Avoid generic English stopword removal — it strips meaningful local-language tokens.
- Avoid English stemming or lemmatization for local-language text.
- Preserve negations, hashtags, emojis, and expressive punctuation.
- Prefer character n-grams and multilingual/subword transformer models over a fixed vocabulary.
- Treat external evaluation as a generalization check only, never as a training split.

---

## Documentation

| File | Purpose |
|---|---|
| `docs/TEAM_PROJECT_STRUCTURE_AND_WORKFLOW_DOCUMENT.md` | Team alignment and workflow guide |
| `docs/COLAB_AFRIBERTA.md` | Remote GPU training on Google Colab |
| `docs/GROUP_4_DS_SRS_V7.pdf` | Software Requirements Specification |
