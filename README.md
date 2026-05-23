# Low-Resource Facebook Sentiment Classifier

This Prototype implements a notebook-first workflow for preprocessing and training a sentiment classifier on heavily code-switched Facebook comments in a low-resource language setting.

## Project Layout

```text
project/
├─ data/
│  ├─ raw/
│  ├─ external_test/
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

Place all training annotation CSV files inside `data/raw/`. Each file should contain at least:

- `id`
- `text`
- `sentiment_label`
- `include`

Additional columns such as `topic_label`, `confidence`, or `notes` are preserved automatically.

Place any separate evaluation-only dataset inside `data/external_test/`. It should use the same sentiment labels, or labels that can be mapped cleanly to `positive`, `negative`, and `neutral`.

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

4. Train the multilingual transformer. The default is now AfriBERTa small, which is more practical on a CPU-only laptop:

```powershell
python -m src.train_transformer
```

To run a specific transformer variant, pass the Hugging Face model name and a short run name:

```powershell
python -m src.train_transformer --model_name castorini/afriberta_base --run_name afriberta_base
```

Transformer outputs are written with model-specific names, for example `reports/results/castorini_afriberta_small_metrics.json` and `models/transformer/castorini_afriberta_small/`.

If Hugging Face downloads appear to hang, check that `HTTP_PROXY`, `HTTPS_PROXY`, and `ALL_PROXY` are not set to `http://127.0.0.1:9`. The training script clears that known broken proxy value automatically, but slow unauthenticated downloads can still take time.

For GPU training on Google Colab, follow `COLAB_AFRIBERTA.md`.

5. Evaluate the trained baseline on an external dataset if available:

```powershell
python -m src.evaluate_external
```

6. Open the notebooks in `notebooks/` for audit, experiments, and reporting.

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
- Supports separate external evaluation without mixing that dataset into training.

## External Test Set Workflow

Use a second dataset as an external test set only when:

- it is not used in training or model selection
- it follows the same sentiment task
- its labels can be normalized to `positive`, `negative`, and `neutral`

Recommended flow:

1. Train and validate on the main dataset in `data/raw/`.
2. Keep the second dataset in `data/external_test/`.
3. Run:

```powershell
python -m src.evaluate_external
```

This produces:

- `reports/results/external_baseline_metrics.json`
- `reports/results/external_baseline_predictions.csv`
- `reports/figures/external_baseline_confusion_matrix.png`

This lets the team compare internal held-out performance against external generalization performance.

## Active Learning Workflow

To accelerate data annotation and address the dataset size limitation, use the active learning script to select the most uncertain comments from an unlabeled pool:

1. Place a CSV file containing scraped, unlabeled Facebook comments (containing a `text` or `comment_text` column) in your workspace.
2. Run the active learning query script:

```powershell
python -m src.active_learning --unlabeled_path data/scratch/mock_unlabeled.csv --output_path "data/raw/Facebook_Comment_Annotation - ActiveBatch1.csv" --n_samples 200 --strategy entropy
```

Available CLI arguments:
* `--unlabeled_path`: Path to the CSV containing unlabeled comments (required).
* `--output_path`: Path to save the query batch (default: `data/raw/Facebook_Comment_Annotation - ActiveBatch1.csv`).
* `--n_samples`: Number of uncertain comments to select (default: `200`).
* `--strategy`: Uncertainty metric to use (`entropy`, `margin`, or `lc` for Least Confidence).

3. Open the output CSV file in Excel/Google Sheets, fill in the blank `sentiment_label` and `include` columns, and save it back into `data/raw/`.
4. Re-run preprocessing and retraining to incorporate the new annotations into the next model version:
   ```powershell
   python -m src.preprocess
   python -m src.train_baseline
   ```

To run active learning interactively and visualize candidate uncertainty distributions, open `notebooks/07_active_learning.ipynb`.

## Notes For Low-Resource, Code-Switched Text

- Do not use generic English stopword removal by default.
- Do not stem or lemmatize unless you have language-specific tools.
- Preserve emojis, expressive punctuation, hashtags, and negations.
- Prefer character n-grams and subword-aware models over manually curated full vocabularies.

## Optional Lexicon Support

Use `data/raw/custom_lexicon_template.csv` as a starter for local slang, intensifiers, negations, and spelling variants. The current code does not force lexicon-based normalization, but the file is included so the team can expand it during error analysis.
