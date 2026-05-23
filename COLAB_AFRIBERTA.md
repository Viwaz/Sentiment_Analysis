# AfriBERTa Training on Google Colab

This guide runs the transformer stage on Google Colab so the model download and training do not depend on the local Windows environment.

## 1. Prepare the Project Folder

Before uploading to Colab, make sure the repository contains the current processed split files:

```text
data/processed/train.csv
data/processed/val.csv
data/processed/test.csv
data/processed/metadata.json
src/
requirements.txt
```

The raw files are not required if preprocessing has already been run locally. If the team wants Colab to rerun preprocessing too, upload `data/raw/` as well.

Do not upload large local transformer checkpoints.

## 2. Open Colab With GPU

In Colab:

1. Open `Runtime`.
2. Select `Change runtime type`.
3. Set `Hardware accelerator` to `GPU`.
4. Save.

Check the GPU:

```python
!nvidia-smi
```

## 3. Upload or Mount the Project

Recommended option: zip the project folder locally, upload it to Colab, and unzip it.

```python
from google.colab import files
uploaded = files.upload()
```

Then unzip the uploaded archive:

```python
!unzip -q "project.zip" -d /content/project
%cd /content/project
```

If the zip extracts into a nested folder, change into the folder that contains `src/`, `data/`, and `requirements.txt`.

## 4. Install Dependencies

```python
!pip install -r requirements.txt
```

If Colab reports dependency conflicts, restart the runtime and run the install command again before training.

## 5. Optional Hugging Face Login

AfriBERTa is public, so login is usually not required. If downloads are slow or rate-limited, use a Hugging Face token:

```python
from huggingface_hub import login
login()
```

Paste the token when prompted.

## 6. Run AfriBERTa Small

AfriBERTa small is the recommended first Colab run because it is lighter and gives a clear comparison point.

```python
!python -m src.train_transformer --model_name castorini/afriberta_small --run_name afriberta_small
```

Expected outputs:

```text
reports/results/afriberta_small_metrics.json
reports/results/afriberta_small_predictions.csv
reports/figures/afriberta_small_confusion_matrix.png
models/transformer/afriberta_small/
```

## 7. Optional AfriBERTa Base Run

Only run base after small completes successfully.

```python
!python -m src.train_transformer --model_name castorini/afriberta_base --run_name afriberta_base
```

Expected outputs:

```text
reports/results/afriberta_base_metrics.json
reports/results/afriberta_base_predictions.csv
reports/figures/afriberta_base_confusion_matrix.png
models/transformer/afriberta_base/
```

## 8. Download Results Back to Local Machine

Download only the reports first. The model folder may be large.

```python
!zip -r afriberta_reports.zip reports/results reports/figures
from google.colab import files
files.download("afriberta_reports.zip")
```

If the team also needs the trained model:

```python
!zip -r afriberta_small_model.zip models/transformer/afriberta_small
from google.colab import files
files.download("afriberta_small_model.zip")
```

## 9. Compare Against Baseline

Use macro F1 as the main comparison metric.

Compare:

- `reports/results/baseline_metrics.json`
- `reports/results/afriberta_small_metrics.json`
- `reports/results/afriberta_base_metrics.json`, if base is also run

The transformer should not automatically replace the baseline. It should only be considered better if it improves macro F1 and gives better per-class behavior, especially for `neutral` and `positive`.
