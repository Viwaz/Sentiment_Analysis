# Low-Resource Facebook Sentiment Classifier

This project implements a notebook-first workflow for preprocessing and training a sentiment classifier on heavily code-switched Facebook comments in a low-resource language setting.

## Project Layout

```text
project/
├─ data/
│  ├─ raw/
│  ├─ interim/
│  └─ processed/
├─ notebooks/
│  ├─ 01_data_audit.ipynb
│  ├─ 02_preprocessing.ipynb
│  ├─ 03_baseline_models.ipynb
│  ├─ 04_transformer_training.ipynb
│  └─ 05_error_analysis.ipynb
├─ src/
│  ├─ __init__.py
│  ├─ data_utils.py
│  ├─ preprocess.py
│  ├─ features.py
│  ├─ evaluate.py
│  ├─ train_baseline.py
│  └─ train_transformer.py
├─ models/
│  ├─ baseline/
│  └─ transformer/
├─ reports/
│  ├─ figures/
│  └─ results/
├─ requirements.txt
└─ README.md
```

## Expected Raw Data Format

Place all annotation CSV files inside `data/raw/`. Each file should contain at least:

- `id`
- `text`
- `sentiment_label`
- `include`

Additional columns such as `topic_label`, `confidence`, or `notes` are preserved automatically.

## Recommended Workflow

1. Copy all annotator CSV files into `data/raw/`.
2. Run preprocessing:

```powershell
python -m src.preprocess
```

3. Train baseline models:

```powershell
python -m src.train_baseline
```

4. Train the multilingual transformer:

```powershell
python -m src.train_transformer
```

5. Open the notebooks in `notebooks/` for audit, experiments, and reporting.

## What The Pipeline Does

- Loads each raw CSV exactly once and adds `source_file` for traceability.
- Normalizes labels to `positive`, `negative`, and `neutral`.
- Filters out rows where `include` is not `Yes`.
- Audits missing labels, missing text, excluded rows, duplicates, and short comments.
- Applies light text normalization while preserving sentiment cues such as emojis, `!`, and `?`.
- Exports:
  - `data/interim/merged_comments.csv`
  - `data/interim/label_audit.csv`
  - `data/interim/cleaned_comments.csv`
  - `data/processed/train.csv`
  - `data/processed/val.csv`
  - `data/processed/test.csv`
  - `data/processed/metadata.json`
- Trains TF-IDF baseline models and stores metrics in `reports/results/`.

## Notes For Low-Resource, Code-Switched Text

- Do not use generic English stopword removal by default.
- Do not stem or lemmatize unless you have language-specific tools.
- Preserve emojis, expressive punctuation, hashtags, and negations.
- Prefer character n-grams and subword-aware models over manually curated full vocabularies.

## Optional Lexicon Support

Use `data/raw/custom_lexicon_template.csv` as a starter for local slang, intensifiers, negations, and spelling variants. The current code does not force lexicon-based normalization, but the file is included so the team can expand it during error analysis.
