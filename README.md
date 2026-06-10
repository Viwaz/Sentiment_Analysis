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
|   |-- compare_models.py
|   |-- data_utils.py
|   |-- evaluate.py
|   |-- evaluate_external.py
|   |-- features.py
|   |-- predict.py
|   |-- preprocess.py
|   |-- train_baseline.py
|   `-- train_transformer.py
|-- requirements.txt
`-- README.md
```

## Folder Responsibilities

- `data/raw/`: original annotation CSV files. These files are the source of truth for training data.
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
