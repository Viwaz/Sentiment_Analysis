# Verification and Testing Checklist

- `[x]` Run syntax and import checks for model api and service modules
- `[x]` Verify batch predictions via the CLI adapter
- `[x]` Start uvicorn server locally and verify endpoints:
  - `[x]` Verify `GET /health` with default settings (`afriberta_small`)
  - `[x]` Verify `GET /model-info` metadata
  - `[x]` Verify `POST /predict` returns correct response
  - `[x]` Verify `POST /predict-batch` behaves identically
- `[x]` Verify model loading behavior (loaded once at startup)
- `[x]` Verify service with baseline fallback (`MODEL_REFERENCE=baseline`)
