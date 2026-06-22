# Hosted Model Service Walkthrough

This document outlines the testing, verification, and hardening changes made to finalize the hosted model service.

## Hardening and Bug Fixes

During verification, we discovered that omitting the optional `text` or `id` fields in single/batch predictions resulted in a `Pydantic ValidationError` because the endpoint responses expected non-nullable strings/integers, whereas missing request values generated `None` or `NaN` inside the dataframe.

We resolved this by making the following improvements:
1. **[model_service.py](file:///c:/Users/vdchi/OneDrive/Documents/DATA%20SCIENCE/Sem5/Group%20Project/Prototyping%202/src/model_service.py)**: Hardened `_require_cleaned_text` to detect when `id` or `text` are present but contain `null`, `NaN`, or empty strings. They are now automatically populated with appropriate default fallbacks (e.g., matching the `cleaned_text` value or sequence indices).
2. **[model_api.py](file:///c:/Users/vdchi/OneDrive/Documents/DATA%20SCIENCE/Sem5/Group%20Project/Prototyping%202/src/model_api.py)**: Hardened the `_normalise_prediction_row` dictionary mapping to safely cast floats (e.g., pandas representation of integer IDs like `1.0`), strip whitespace, and default empty values to string types, satisfying the Pydantic type validator definitions.

## Endpoints Verified

All endpoints are fully operational. The API response schema matches the CSV file-based outputs.

### 1. healthcheck (`GET /health`)
- Returns `status: ok` and indicates the service is fully loaded and initialized.

### 2. model metadata (`GET /model-info`)
- Returns the current active model's metadata, labels, run ID, and family.

### 3. single prediction (`POST /predict`)
- Accepts a single comment and returns prediction confidence, labels, scores, and active model fields.

### 4. batch prediction (`POST /predict-batch`)
- Accepts a list of comments and handles scoring simultaneously using the loaded in-memory service.

---

## Verification Results

### AfriBERTa Small (Default Model)
Verified that uvicorn runs the service correctly. The test logs confirmed successful startup, weights loading, and correct responses:

```json
Testing GET /health...
Health response: {
  "status": "ok",
  "active_model_reference": "afriberta_small",
  "transformer_run_name": "afriberta_small",
  "model_loaded": true,
  "error": null
}

Testing POST /predict-batch...
Batch Prediction response: {
  "predictions": [
    {
      "id": "1",
      "text": "imihigo myiza cyane",
      "cleaned_text": "imihigo myiza cyane",
      "predicted_label": "positive",
      "predicted_confidence": 0.487705796957016,
      "score_negative": 0.25375139713287354,
      "score_neutral": 0.2585428059101105,
      "score_positive": 0.487705796957016,
      "model_name": "castorini/afriberta_small",
      "model_version": "afriberta_small",
      "model_family": "transformer",
      "predicted_at": "2026-06-16T08:27:08.581830+00:00"
    }
  ]
}
```

### Baseline Model (Fallback)
Verified by launching with `MODEL_REFERENCE=baseline`:

```json
Testing GET /model-info...
Model Info response: {
  "active_model_reference": "baseline",
  "model_name": "logistic_regression+char_tfidf",
  "model_version": "baseline",
  "model_family": "classical_ml",
  "labels": [
    "negative",
    "neutral",
    "positive"
  ]
}

Testing POST /predict-batch...
Batch Prediction response: {
  "predictions": [
    {
      "id": "1",
      "text": "imihigo myiza cyane",
      "cleaned_text": "imihigo myiza cyane",
      "predicted_label": "positive",
      "predicted_confidence": 0.3749856092964686,
      "score_negative": 0.32420882620857394,
      "score_neutral": 0.3008055644949574,
      "score_positive": 0.3749856092964686,
      "model_name": "logistic_regression+char_tfidf",
      "model_version": "baseline",
      "model_family": "classical_ml",
      "predicted_at": "2026-06-16T08:39:36.262743+00:00"
    }
  ]
}
```

## Model Loading Optimization
Verified from the Uvicorn log files that the active model is loaded **once at startup** during lifespan initialization, and subsequent inference requests reuse the in-memory estimator.
