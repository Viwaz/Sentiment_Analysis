# Database Integration Implementation Plan

## Goal
Integrate the PostgreSQL schema (stored in `DB/schema.sql`) into the sentiment‑analysis pipeline, add user management, activity logging, and update the existing ingestion/pre‑processing/prediction code to write to the new tables.

## User Review Required
[!IMPORTANT]
The plan includes breaking changes to the code base (new `db` module, added authentication, and modified pipeline flow). Please review and approve before any files are modified.

## Open Questions
- Which authentication method should be used (password hash with bcrypt, JWT, etc.)?
- Should the `dev_annotations` uploads be exposed via a separate API endpoint or reused existing upload logic?
- Do we need a Docker‑compose file for the PostgreSQL service, or is an external DB already provisioned?

## Proposed Changes
---
### 1. Directory Structure
- **`DB/`** – contains `schema.sql` (already created) and optional `docker-compose.yml`.
- **`src/db/`** – new Python module handling DB connections and CRUD helpers.
- **`src/config.py`** – add DB connection settings (host, port, dbname, user, password).
- **`src/pipeline.py`** – refactor to use `src.db` helpers for persisting comments, pre‑processed text, predictions, and logs.
- **`src/auth.py`** – new module for user registration, login, and role checking.

---
### 2. Database Helper (`src/db/*`)
| File | Responsibility |
|------|----------------|
| `connection.py` | Create a singleton `psycopg2` (or `asyncpg`) connection pool.
| `comments.py` | `insert_comment`, `fetch_comment`.
| `preprocess.py` | `insert_preprocessed`, `get_preprocessed`.
| `predictions.py` | `insert_prediction`, `fetch_predictions`.
| `annotations.py` | `insert_annotation` (dev only).
| `activity.py` | `log_action(user_id, action_type, comment_id=None, details=None)`.
| `users.py` | `create_user`, `authenticate_user`, `get_user_by_id`.

---
### 3. Pipeline Refactor
1. **Ingestion** – after scraping, call `db.comments.insert_comment` and then `db.activity.log_action` with `action_type='ingest'`.
2. **Pre‑processing** – store cleaned text via `db.preprocess.insert_preprocessed` and log `'preprocess'`.
3. **Prediction** – after model inference, store results with `db.predictions.insert_prediction` and log `'predict'`.
4. **Developer Annotation Upload** – endpoint calls `db.annotations.insert_annotation` and logs `'annotation_upload'`.

---
### 4. API / CLI Adjustments
- Extend `demo_pipeline.py` to accept a `--user-id` flag (or obtain from auth token) so actions can be attributed.
- Add a small FastAPI (or Flask) service exposing:
  * `/upload/url` – general user upload (creates comment, preprocesses, predicts).
  * `/upload/csv` – same as above for CSV files.
  * `/dev/annotations` – protected endpoint (role=developer) for bulk annotation CSV.
  * `/auth/register` & `/auth/login` – user management.

---
### 5. Migration & Testing
- **Step 1** – Run `psql -f DB/schema.sql` to create tables.
- **Step 2** – Write unit tests for each DB helper (using a test database).  
- **Step 3** – End‑to‑end test: run `demo_pipeline.py` with a small batch (e.g., 10 comments) and verify rows appear in `comments`, `preprocessed_comments`, `predictions`, and `activity_logs`.
- **Step 4** – Validate that PII columns (`author_name`, `raw_item`) are absent.
- **Step 5** – Deploy optional Docker‑compose for local dev:
```yaml
version: "3.8"
services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: sentiment_user
      POSTGRES_PASSWORD: secretpw
      POSTGRES_DB: sentiment_db
    ports:
      - "5432:5432"
    volumes:
      - db_data:/var/lib/postgresql/data
volumes:
  db_data:
```

---
## Verification Plan
### Automated Tests
- `pytest tests/test_db_helpers.py` – CRUD operations.
- `pytest tests/test_pipeline_integration.py` – runs a mini‑pipeline and asserts DB row counts.

### Manual Verification
- Use a DB client (psql or pgAdmin) to inspect tables after running the demo pipeline.
- Check that `activity_logs` correctly records the `user_id` and `action_type`.

---
## Timeline (estimated)
| Phase | Duration |
|-------|----------|
| Directory & config setup | 1 day |
| DB helper implementation | 2 days |
| Pipeline refactor & logging | 2 days |
| Auth module & API endpoints | 2 days |
| Migration, Docker, and testing | 1 day |
| Documentation & hand‑over | 1 day |

---
**End of Plan**
