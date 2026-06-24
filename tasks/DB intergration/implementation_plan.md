# Implementation Plan - Database and API Integration

This plan outlines the changes required to update the PostgreSQL schema to match `docs/scripts.txt` and integrate it with the API service to support the complete data pipeline: raw ingestion -> preprocessing -> model predictions -> dashboard retrieval.

## User Review Required

> [!IMPORTANT]
> The schema in `docs/scripts.txt` is missing a `hashed_password` column in the `users` table. To keep compatibility with the existing password hashing and token-based authentication in `src/auth.py`, we will add `hashed_password VARCHAR(255) NOT NULL` to the `users` table definition.

> [!WARNING]
> Updating the database schema will require database schema migration. Since the DB is not running, we will update the primary `Database/schema.sql` file and the `docker-compose.yml` to set up and seed the new tables.

## Open Questions

- None at the moment. We will implement fallback values for columns like `email` when creating test users to keep existing tests running.

## Proposed Changes

---

### Database Configuration & Schema

#### [MODIFY] [schema.sql](file:///c:/Users/vdchi/OneDrive/Documents/DATA%20SCIENCE/Sem5/Group%20Project/Prototyping%202/Database/schema.sql)
Replace the existing schema with the anticipated one from `docs/scripts.txt` (with `hashed_password` added to `users`):
- `users`: PK `user_id`, add `hashed_password`, `email`, `is_active`.
- `comments`: PK `comment_id`, text field renamed to `comment_text`, add `created_at`, `date_collected`, `collection_source`, `apify_dataset_id`, `apify_run_id`.
- `preprocessed_comments`: PK `comment_id`, FK `comment_id`, `cleaned_text`, `preprocessed_at` (remove emoji fields).
- `predictions`: PK `prediction_id`, FK `comment_id`, confidence and score fields, model metadata, `predicted_at`.
- `dev_annotations`: PK `comment_id` (replaces `annotations`).
- `activity_logs`: PK `log_id`, FK `user_id` (NOT NULL), `comment_id`, `action_type` constraint, `details` (TEXT), `action_timestamp`.

---

### DB CRUD Helpers (`src/db/*`)

#### [MODIFY] [users.py](file:///c:/Users/vdchi/OneDrive/Documents/DATA%20SCIENCE/Sem5/Group%20Project/Prototyping%202/src/db/users.py)
Update queries to use `user_id` instead of `id`. Add default `email` calculation so existing calls don't break.

#### [MODIFY] [comments.py](file:///c:/Users/vdchi/OneDrive/Documents/DATA%20SCIENCE/Sem5/Group%20Project/Prototyping%202/src/db/comments.py)
Update to match new schema: rename query references from `text` to `comment_text`, and add support for new columns (`created_at`, `apify_dataset_id`, `apify_run_id`).

#### [MODIFY] [preprocess.py](file:///c:/Users/vdchi/OneDrive/Documents/DATA%20SCIENCE/Sem5/Group%20Project/Prototyping%202/src/db/preprocess.py)
Update `insert_preprocessed` and `get_preprocessed` to remove emoji/token count columns.

#### [MODIFY] [predictions.py](file:///c:/Users/vdchi/OneDrive/Documents/DATA%20SCIENCE/Sem5/Group%20Project/Prototyping%202/src/db/predictions.py)
Ensure queries select and insert correct column names matching the new schema.

#### [MODIFY] [annotations.py](file:///c:/Users/vdchi/OneDrive/Documents/DATA%20SCIENCE/Sem5/Group%20Project/Prototyping%202/src/db/annotations.py)
Rewrite helper to work with `public.dev_annotations` table schema: columns `comment_id`, `topic_label`, `sentiment_label`, `confidence`, `include`, `notes`, `annotated_by`.

#### [MODIFY] [activity.py](file:///c:/Users/vdchi/OneDrive/Documents/DATA%20SCIENCE/Sem5/Group%20Project/Prototyping%202/src/db/activity.py)
- Map `user_id = None` to a default system user (e.g. `1` or query a special `system` user) since it's `NOT NULL` in the DB constraint.
- Store `details` JSON dictionary as a text string instead of JSONB.
- Check and validate the `action_type` values to ensure they match the CHECK constraint in PostgreSQL.

---

### API Service (`src/model_api.py`)

#### [MODIFY] [model_api.py](file:///c:/Users/vdchi/OneDrive/Documents/DATA%20SCIENCE/Sem5/Group%20Project/Prototyping%202/src/model_api.py)
- Update FastAPI endpoints and Pydantic schemas to align with the new schema naming conventions.
- Implement a unified `/predict-pipeline` endpoint that:
  1. Accepts raw comment payload.
  2. Saves raw comment to the raw `comments` table.
  3. Preprocesses raw comment to produce `cleaned_text` and saves it to `preprocessed_comments`.
  4. Feeds `cleaned_text` into the model and retrieves predictions.
  5. Saves the predictions to the `predictions` table referencing `comment_id`.
  6. Logs activity for `ingest`, `preprocess`, and `predict`.
- Add `GET /dashboard/predictions` endpoint to let a dashboard retrieve predictions joined with raw and cleaned comment text.

---

## Verification Plan

### Automated Tests
We will verify our updates by running the existing integration tests and modifying them as needed to conform to the new schema:
- `pytest tests/test_db_integration.py`

### Manual Verification
1. Start the PostgreSQL container via `docker-compose up -d`.
2. Inspect the created tables in Postgres to verify they match `docs/scripts.txt`.
3. Invoke the `/predict-pipeline` endpoint using `curl` or FastAPI's swagger UI.
4. Run `GET /dashboard/predictions` to verify the dashboard can access predictions.
