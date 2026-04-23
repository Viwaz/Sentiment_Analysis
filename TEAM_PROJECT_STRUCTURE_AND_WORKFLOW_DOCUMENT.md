# Project Structure and Workflow Overview for the Sentiment Classifier

## Purpose of This Document

This document explains how the current sentiment-classification project is structured, how data and models move through the pipeline, why the workflow is organized this way, and which points the team should review together. The goal is to make sure everyone understands the same project structure before we continue changing preprocessing, modeling, or evaluation decisions.

This is not a code manual. It is a team alignment document. It is meant to help us discuss whether the current structure is clear, whether the workflow is valid, and what the next technical priorities should be.

## Project Objective and Current State

The project goal is to build a sentiment classifier for Facebook comments in a low-resource, code-switched language setting. The workflow currently supports classical machine-learning baselines, transformer-based modeling, and external evaluation on a separate dataset.

At this point, the following work has already been completed:

- Training annotation files were imported into the project and preprocessed.
- A separate external test dataset was kept outside the training pipeline.
- Baseline models were trained on the main processed dataset.
- A multilingual transformer was trained on the same fixed train, validation, and test split.
- Internal and external evaluation outputs were saved in the repository.

The main result so far is that the TF-IDF baseline currently performs better than the transformer on the internal test set, and external performance is weaker than internal performance. This suggests that the current bottleneck is not only model choice. Data quality, class balance, and robustness to domain shift are still major issues.

## Repository Structure Overview

### `data/raw/`

This folder contains the original training annotation files. These are the raw CSV files collected from the team’s annotation process.

This folder is kept separate because raw data should remain untouched. If preprocessing changes later, we should always be able to rebuild the pipeline from the original annotation files without guessing which earlier edits were applied.

### `data/external_test/`

This folder contains the separate dataset used only for external evaluation.

It exists to protect the integrity of testing. The external dataset must not be mixed into training or model selection. Keeping it separate allows us to check whether the model generalizes beyond the original training distribution.

### `data/interim/`

This folder contains intermediate outputs created during preprocessing, such as merged annotation files, audit tables, and cleaned comment text.

This separation is useful because preprocessing is a high-risk stage. By saving intermediate outputs, we can inspect how labels were normalized, how rows were filtered, and whether cleaning changed the text in ways we did or did not intend.

Current examples in this folder include:

- `merged_comments.csv`
- `label_audit.csv`
- `cleaned_comments.csv`

### `data/processed/`

This folder contains final model-ready files. These are the datasets used directly by the training scripts after preprocessing has been completed.

This separation prevents training code from redoing data logic in different ways. Once preprocessing is finalized, all models should be trained from the same processed files.

Current examples in this folder include:

- `train.csv`
- `val.csv`
- `test.csv`
- `metadata.json`

### `src/`

This folder contains the reusable implementation of the pipeline. It is the main code layer of the project.

This separation exists because notebooks are useful for inspection and experimentation, but the actual workflow should remain reproducible through normal Python modules. Reusable code belongs here, not scattered across notebooks.

### `notebooks/`

This folder contains analysis and reporting notebooks. These are meant for human inspection, explanation, and exploratory review of pipeline outputs.

This separation makes the workflow easier to understand. Team members can inspect each stage in notebook form without relying on notebooks as the only implementation layer.

### `models/`

This folder contains saved model artifacts and supporting files.

It is separate because trained models are outputs of the workflow, not source code. This keeps experiment artifacts distinct from the implementation itself.

The current structure includes:

- `models/baseline/`
- `models/transformer/`

### `reports/results/`

This folder contains numerical outputs and evaluation artifacts in file form, such as metrics summaries and prediction tables.

It exists to make experimental results easy to compare, review, and report without digging through logs or rerunning notebooks.

### `reports/figures/`

This folder contains plots and exported visual outputs, including confusion matrices.

This separation is useful for report writing, presentation preparation, and side-by-side comparison of model behavior.

### `README.md` and `requirements.txt`

`README.md` explains how the project is organized and how to run the main pipeline stages. `requirements.txt` lists the Python dependencies needed to run the code.

These files are the entry point for anyone joining the project or running it on another machine.

## Workflow Explanation

The project follows a staged workflow so that each step has a clear input, output, and purpose.

### Stage 1: Place raw annotation files in `data/raw/`

Input:

- Original annotation CSV files from the team

Output:

- A stable raw-data source for the preprocessing pipeline

Reason:

- This gives us one defined source of truth for training data.

Risk prevented:

- accidental editing of source data
- confusion about which file version was used

### Stage 2: Preprocessing

Input:

- Raw training annotation files in `data/raw/`

Output:

- merged comments
- label audit file
- cleaned comments
- processed train, validation, and test files

Reason:

- Preprocessing prepares the data for training in a consistent and reviewable way.

What happens here:

- files are loaded and merged
- labels are normalized
- rows marked for exclusion are filtered out
- duplicates are removed
- text is lightly cleaned while preserving sentiment cues

Risk prevented:

- inconsistent label use
- noisy or excluded rows leaking into training
- duplicated comments inflating performance
- cleaning differences across experiments

### Stage 3: Processed data split

Input:

- cleaned data from preprocessing

Output:

- `train.csv`
- `val.csv`
- `test.csv`

Reason:

- This creates a fixed basis for fair model comparison.

Risk prevented:

- evaluation leakage
- models being compared on different data splits

### Stage 4: Baseline model training

Input:

- processed training and validation files

Output:

- trained baseline model
- saved vectorizer
- metrics JSON
- prediction file
- confusion matrix figure

Reason:

- Baselines establish the minimum standard that more complex models must beat.

Risk prevented:

- assuming a transformer is automatically better
- overcomplicating the pipeline before understanding simple feature-based behavior

### Stage 5: Transformer training

Input:

- the same processed train, validation, and test files used by the baseline

Output:

- trained transformer checkpoint
- tokenizer files
- metrics JSON
- prediction file
- confusion matrix figure

Reason:

- This allows a fair comparison between transfer learning and the classical baseline.

Risk prevented:

- unfair comparison caused by different training data
- claiming model improvement without controlled evaluation

### Stage 6: External evaluation

Input:

- external dataset in `data/external_test/`
- saved trained model artifacts

Output:

- external evaluation metrics
- external predictions
- external confusion matrix

Reason:

- This tests how well the model generalizes to related but different data.

Risk prevented:

- overestimating performance by relying only on internal held-out data

### Stage 7: Store results in `reports/`

Input:

- outputs from baseline, transformer, and external evaluation stages

Output:

- metrics files
- prediction files
- figures

Reason:

- This keeps results reviewable and makes the project easier to discuss and report on.

Risk prevented:

- losing track of experimental outputs
- mixing result files with implementation code

## File and Script Responsibilities

### `data_utils.py`

This module contains shared dataset utilities such as path handling, raw file discovery, file loading, and label normalization.

Its role is to centralize dataset rules so they do not get duplicated differently across scripts and notebooks.

### `preprocess.py`

This module performs the preprocessing pipeline. It handles cleaning, filtering, deduplication, splitting, and metadata export.

Its role is to turn raw annotations into a consistent, model-ready dataset.

### `features.py`

This module creates feature representations for the baseline models, including TF-IDF feature sets.

Its role is to keep feature engineering separate from model training logic.

### `train_baseline.py`

This module trains and compares the baseline models.

Its role is to provide the reference point for model performance using simpler ML methods.

### `train_transformer.py`

This module fine-tunes the multilingual transformer.

Its role is to test whether pretrained multilingual modeling improves over the classical baseline under the same data split.

### `evaluate.py`

This module provides the shared evaluation logic, including metrics and confusion matrices.

Its role is to ensure that different model families are scored in a consistent way.

### `evaluate_external.py`

This module evaluates a trained model on the external dataset.

Its role is to measure generalization without contaminating training or validation.

## Notebook Responsibilities

The notebooks are the human-facing layer of the workflow. They are meant for inspection, communication, and reporting. The actual reusable pipeline lives in `src/`.

### `01_data_audit.ipynb`

Used to inspect raw data quality, class balance, duplicates, and general annotation patterns before modeling.

### `02_preprocessing.ipynb`

Used to inspect the effects of preprocessing and confirm that cleaned and split data look correct.

### `03_baseline_models.ipynb`

Used to review baseline model training and compare baseline feature/model combinations.

### `04_transformer_training.ipynb`

Used to review transformer training and the resulting evaluation outputs.

### `05_error_analysis.ipynb`

Used to inspect misclassifications and understand where the models are failing.

### `06_external_evaluation.ipynb`

Used to inspect how a trained model transfers to the external dataset.

## Why This Workflow Is Standard

This is a standard applied ML workflow because it separates key responsibilities that are often mixed together in weaker projects.

The workflow separates:

- raw data from derived data
- preprocessing from modeling
- reusable code from exploratory notebooks
- internal train, validation, and test data from external evaluation data
- trained models and output artifacts from source code

The exact folder names may vary between teams, but the design principles are standard. The structure supports traceability, reproducibility, fair comparison, and easier collaboration.

This matters because the project is not only about fitting a model. It is also about being able to explain which data was used, how it was cleaned, how models were compared, and whether the results are trustworthy.

## Current Findings and Implications

The current experiments already show several important things.

First, class imbalance is a major issue. Positive comments dominate the training data and the model outputs. That means accuracy alone is not enough to judge success. Macro F1 is more informative for this project.

Second, the positive class is much easier for the models than the negative and neutral classes. Negative and neutral are still weak across both the baseline and transformer runs.

Third, external evaluation performs worse than internal evaluation. This indicates domain shift or weaker generalization when the model is applied to different but related data.

Fourth, the TF-IDF baseline currently performs better than the transformer on the internal test set. This means the current project bottleneck is not only the choice of model architecture. Data quality, class balance, annotation consistency, and robustness remain central issues.

This should be treated as a status snapshot, not a final conclusion. The current evidence suggests that future gains may come more from data improvements and targeted preprocessing review than from simply switching to a more complex model.

## Current Performance Snapshot

The main results so far are:

- Internal baseline test macro F1: `0.3562`
- Internal transformer test macro F1: `0.2994`
- External baseline macro F1: `0.2641`

In practical terms, the baseline is currently the better internal model, while external generalization remains weak. This is useful for the team because it gives us a concrete basis for deciding whether the next effort should focus on data, labeling consistency, or modeling changes.

## Points for Team Review

The following questions are the main discussion points for the team:

1. Is the current file structure clear enough for everyone to use without confusion?
2. Do we agree on keeping the external dataset fully separate from training and model selection?
3. Do we agree that baseline models should remain the benchmark before making stronger claims about transformers?
4. Should the next round of work focus more on annotation quality, class balance, or model design?
5. Are there preprocessing rules that the team believes should be revised before the next experiment?
6. Do we want to keep the workflow notebook-first for communication, while treating `src/` as the actual reproducible implementation?

The purpose of these questions is to make sure the team is aligned before additional experiments are run. If the structure and workflow are agreed now, later model comparisons will be easier to trust and explain.
