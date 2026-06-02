# AfriBERTa Training on Google Colab

This guide explains how to run the transformer stage on Google Colab so training can use remote compute instead of the local Windows environment.

## 1. Prepare The Project

Before using Colab, make sure the project contains:

```text
data/processed/train.csv
data/processed/val.csv
data/processed/test.csv
data/processed/metadata.json
src/
requirements.txt
```

If preprocessing must be rerun in Colab, also upload `data/raw/`. If preprocessing was already run locally, the processed files are enough for transformer training.

Do not upload local transformer checkpoints unless the team specifically needs them. They are large and should not be committed to Git.

## 2. Enable GPU In Colab

In Colab:

1. Open `Runtime`.
2. Select `Change runtime type`.
3. Set `Hardware accelerator` to `GPU`.
4. Save.

Check the GPU:

```python
!nvidia-smi
```

## 3. Upload Or Clone The Project

Recommended for a private or authentication-protected repository: upload a zip file of the project, then unzip it.

```python
from google.colab import files
uploaded = files.upload()
```

```python
!unzip -q "project.zip" -d /content/project
%cd /content/project
```

If the zip extracts into a nested folder, change into the folder that contains `src/`, `data/`, and `requirements.txt`.

If cloning from GitHub, use a properly scoped token and never paste the token into shared notebooks, screenshots, or chat logs.

## 4. Install Dependencies

```python
!pip install -r requirements.txt
```

If Colab reports dependency conflicts, restart the runtime and rerun the install step before training.

## 5. Run AfriBERTa Small

AfriBERTa Small is the preferred transformer run for this project because it is lighter than larger multilingual transformers and is more practical for low-resource experimentation.

```python
!python -m src.train_transformer --model_name castorini/afriberta_small --run_name afriberta_small
```

Expected outputs:

```text
reports/results/afriberta_small_metrics.json
reports/results/afriberta_small_predictions.csv
reports/figures/afriberta_small_confusion_matrix.png
reports/figures/afriberta_small_learning_curves.png
models/transformer/afriberta_small/
```

## 6. Evaluate External Data

After training finishes, run external evaluation if the trained model is available in the Colab environment:

```python
!python -m src.evaluate_external --model_type transformer --model_name castorini/afriberta_small --run_name afriberta_small
```

Expected outputs:

```text
reports/results/external_afriberta_small_metrics.json
reports/results/external_afriberta_small_predictions.csv
reports/figures/external_afriberta_small_confusion_matrix.png
```

## 7. Rebuild The Comparison Table

```python
!python -m src.compare_models
```

This writes:

```text
reports/results/model_comparison.csv
```

Use macro F1 as the primary comparison metric.

## 8. Download Results

Download reports first. Avoid downloading model folders unless they are explicitly needed.

```python
!zip -r afriberta_reports.zip reports/results reports/figures
from google.colab import files
files.download("afriberta_reports.zip")
```

If the team needs the model artifacts:

```python
!zip -r afriberta_small_model.zip models/transformer/afriberta_small
from google.colab import files
files.download("afriberta_small_model.zip")
```

## 9. Important Notes

- Keep processed splits identical across local and Colab runs.
- Do not train on `data/external_test/`.
- Do not commit large transformer checkpoints to Git.
- If a GitHub token has been exposed, revoke it and create a new one.
- If results change after rerunning training, update the README, team workflow document, and model comparison chart.
