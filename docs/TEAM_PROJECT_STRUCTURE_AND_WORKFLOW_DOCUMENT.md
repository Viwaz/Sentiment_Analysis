# Project Structure and Workflow Overview for the Sentiment Classifier

## Purpose

This document gives the team a shared view of the current project structure, workflow, and model status. It is intended for discussion and presentation preparation, not as a line-by-line code manual.

## Project Objective

The project goal is to classify Facebook comments into `negative`, `neutral`, and `positive` sentiment in a low-resource, code-switched language setting. The current prototype supports preprocessing, audit, baseline training, transformer training, external evaluation, active learning, and result reporting.

## Current Status Snapshot

The current processed dataset contains `1813` usable rows after filtering and deduplication. The fixed split is `1269` training rows, `272` validation rows, and `272` internal test rows.

The current saved internal test results show that the strongest model is the Logistic Regression baseline using character TF-IDF. AfriBERTa Small remains an important transformer comparison, but it has not surpassed the latest baseline result.

| Model | Input representation | Test macro F1 | Test accuracy | Main interpretation |
|---|---|---:|---:|---|
| Logistic Regression | Character TF-IDF | `0.5463` | `0.6140` | Current strongest saved internal result |
| AfriBERTa Small | Subword transformer | `0.4901` | `0.5368` | Useful multilingual transfer-learning comparison |
| XLM-RoBERTa Base | Subword transformer | `0.2994` | `0.5439` | Weaker on the earlier saved transformer run |
| External baseline | Separate external dataset | `0.3572` | `0.3783` | Shows generalization remains difficult |

These values are a status snapshot. They should not be presented as final deployment performance because the data is still small, code-switched, and imbalanced. The XLM-RoBERTa result is retained as historical evidence, but it should be rerun on the current processed split before strict comparison.

## Repository Structure

```text
project/
|-- data/
|   |-- raw/
|   |-- external_test/
|   |-- interim/
|   `-- processed/
|-- docs/
|-- models/
|-- notebooks/
|-- reports/
|   |-- figures/
|   `-- results/
|-- src/
|-- requirements.txt
`-- README.md
```

## What Each Folder Does

`data/raw/` contains original annotation CSV files. It is kept separate so preprocessing can always be rerun from the original data source.

`data/external_test/` contains a separate evaluation dataset. It must not be mixed into training or model selection because it measures generalization.

`data/interim/` contains intermediate preprocessing outputs such as merged data, audit reports, and cleaned text. This allows the team to inspect how rows and labels were handled.

`data/processed/` contains the final model-ready train, validation, and test splits. All models should use these same splits for fair comparison.

`src/` contains reusable pipeline code. This is the reproducible implementation layer.

`notebooks/` contains exploratory and reporting notebooks. Notebooks are useful for inspection, charts, and discussion, but the reusable logic should remain in `src/`.

`models/` contains saved model artifacts. Large transformer checkpoints should stay out of Git and should be regenerated or stored externally when needed.

`reports/results/` contains metric files, prediction CSVs, and comparison tables.

`reports/figures/` contains visual outputs such as confusion matrices, learning curves, and model comparison charts.

`docs/` contains team-facing and submission-facing documentation, including this workflow memo and Colab guidance.

## End-to-End Workflow

1. Raw CSV annotation files are placed in `data/raw/`.
2. Preprocessing merges the files, normalizes labels, filters excluded rows, removes duplicates, cleans text lightly, and exports audit files.
3. The cleaned data is split into fixed train, validation, and internal test sets.
4. Classical baseline models are trained first using TF-IDF features.
5. Transformer models such as AfriBERTa Small are trained on the same fixed splits.
6. External evaluation is run separately using `data/external_test/`.
7. Batch inference can be run on new CSV input using `python -m src.predict`.
8. Model loading and scoring are isolated in `src/model_service.py`, so the baseline or transformer can be swapped without changing preprocessing, storage, or dashboard code.
9. The hosted model API is exposed through `src/model_api.py` using FastAPI. It accepts cleaned text, loads the selected model once at startup, and returns prediction responses for storage or dashboard modules.
10. Metrics, predictions, confusion matrices, learning curves, and comparison tables are saved under `reports/`.

## Why This Workflow Is Standard

The structure is standard for applied machine-learning projects because it separates raw data from generated data, source code from notebooks, model artifacts from reports, and internal testing from external testing. This makes the pipeline easier to audit, rerun, and explain.

The exact folder names can differ across teams, but the principles are standard: preserve raw data, make preprocessing inspectable, compare models on fixed splits, and keep final results in a reporting layer.

## Current Interpretation

The current results suggest that model choice alone is not the only challenge. Character-level TF-IDF remains strong because it handles spelling variation, short comments, and code-switching reasonably well with limited data. AfriBERTa Small is still valuable because it tests whether an African-language pretrained transformer can learn richer context, but it needs enough clean and balanced data to show its advantage.

External evaluation is weaker than internal evaluation. That means the model may be learning patterns specific to the main annotation set and may not generalize well to comments collected under different conditions.

## Points For Team Review

- Is the current folder structure clear enough for everyone to use?
- Do we agree that `data/external_test/` should remain completely separate from training?
- Should Logistic Regression with character TF-IDF be treated as the current benchmark?
- Should the next improvement focus on annotation quality, class balance, external evaluation, or transformer tuning?
- Are the current emoji preprocessing rules acceptable for the next run?
- Which result files should be used in the final DDD/PPT discussion?
