from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

BROKEN_PROXY_VALUE = "http://127.0.0.1:9"
for proxy_var in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY"):
    if os.environ.get(proxy_var) == BROKEN_PROXY_VALUE:
        os.environ.pop(proxy_var)

os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")

import numpy as np
import pandas as pd
from datasets import Dataset, DatasetDict
from sklearn.utils.class_weight import compute_class_weight
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    DataCollatorWithPadding,
    EarlyStoppingCallback,
    Trainer,
    TrainingArguments,
)

from .data_utils import build_paths, ensure_project_dirs
from .evaluate import compute_metrics, save_confusion_matrix, save_metrics

DEFAULT_MODEL_NAME = "castorini/afriberta_small"
LABELS = ["negative", "neutral", "positive"]
LABEL_TO_ID = {label: idx for idx, label in enumerate(LABELS)}
ID_TO_LABEL = {idx: label for label, idx in LABEL_TO_ID.items()}


class WeightedTrainer(Trainer):
    def __init__(self, class_weights=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_weights = class_weights

    def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None):
        import torch

        labels = inputs.get("labels")
        outputs = model(**inputs)
        logits = outputs.get("logits")
        loss_fct = torch.nn.CrossEntropyLoss(weight=self.class_weights.to(logits.device))
        loss = loss_fct(logits.view(-1, model.config.num_labels), labels.view(-1))
        return (loss, outputs) if return_outputs else loss


def load_processed_splits(root: Path | None = None) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    paths = build_paths(root)
    return (
        pd.read_csv(paths.processed_dir / "train.csv"),
        pd.read_csv(paths.processed_dir / "val.csv"),
        pd.read_csv(paths.processed_dir / "test.csv"),
    )


def safe_run_name(model_name: str, run_name: str | None = None) -> str:
    raw_name = run_name or model_name
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", raw_name).strip("_").lower()
    return safe_name or "transformer"


def encode_frame(frame: pd.DataFrame) -> pd.DataFrame:
    encoded = frame.copy()
    encoded["labels"] = encoded["label"].map(LABEL_TO_ID)
    return encoded


def build_dataset_dict(train_df: pd.DataFrame, val_df: pd.DataFrame, test_df: pd.DataFrame) -> DatasetDict:
    return DatasetDict(
        {
            "train": Dataset.from_pandas(encode_frame(train_df), preserve_index=False),
            "validation": Dataset.from_pandas(encode_frame(val_df), preserve_index=False),
            "test": Dataset.from_pandas(encode_frame(test_df), preserve_index=False),
        }
    )


def tokenize_dataset(dataset: DatasetDict, tokenizer):
    def tokenize_batch(batch):
        return tokenizer(batch["cleaned_text"], truncation=True, max_length=128)

    tokenized = dataset.map(tokenize_batch, batched=True)
    keep_columns = {"input_ids", "attention_mask", "labels"}
    if "token_type_ids" in tokenized["train"].column_names:
        keep_columns.add("token_type_ids")

    cleaned_splits = {}
    for split_name, split_dataset in tokenized.items():
        remove_columns = [col for col in split_dataset.column_names if col not in keep_columns]
        cleaned_splits[split_name] = split_dataset.remove_columns(remove_columns)
    return DatasetDict(cleaned_splits)


def metric_fn(eval_prediction):
    logits, labels = eval_prediction
    preds = np.argmax(logits, axis=1)
    y_true = [ID_TO_LABEL[int(label)] for label in labels]
    y_pred = [ID_TO_LABEL[int(pred)] for pred in preds]
    metrics = compute_metrics(y_true, y_pred, LABELS)
    return {"accuracy": metrics["accuracy"], "macro_f1": metrics["macro_f1"]}


def train_transformer(
    root: Path | None = None,
    model_name: str = DEFAULT_MODEL_NAME,
    run_name: str | None = None,
) -> dict:
    paths = build_paths(root)
    ensure_project_dirs(paths)
    run_id = safe_run_name(model_name, run_name)
    train_df, val_df, test_df = load_processed_splits(root)

    dataset = build_dataset_dict(train_df, val_df, test_df)
    print(f"Loading tokenizer: {model_name}", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenizer_max_length = getattr(tokenizer, "model_max_length", None)
    if not isinstance(tokenizer_max_length, int) or tokenizer_max_length > 512:
        tokenizer.model_max_length = 512
    print("Tokenizing processed splits.", flush=True)
    tokenized = tokenize_dataset(dataset, tokenizer)

    print(f"Loading model weights: {model_name}", flush=True)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=len(LABELS),
        id2label=ID_TO_LABEL,
        label2id=LABEL_TO_ID,
    )

    print("Computing class weights.", flush=True)
    import torch

    class_weights = compute_class_weight(
        class_weight="balanced",
        classes=np.array(sorted(train_df["label"].map(LABEL_TO_ID).unique())),
        y=train_df["label"].map(LABEL_TO_ID),
    )
    class_weights_tensor = torch.tensor(class_weights, dtype=torch.float)

    print(f"Starting training run: {run_id}", flush=True)
    output_dir = paths.models_dir / "transformer" / run_id
    args = TrainingArguments(
        output_dir=str(output_dir),
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        num_train_epochs=5,
        weight_decay=0.01,
        load_best_model_at_end=True,
        metric_for_best_model="macro_f1",
        greater_is_better=True,
        logging_dir=str(paths.results_dir / f"{run_id}_logs"),
        save_total_limit=2,
        report_to="none",
        seed=42,
    )

    trainer = WeightedTrainer(
        class_weights=class_weights_tensor,
        model=model,
        args=args,
        train_dataset=tokenized["train"],
        eval_dataset=tokenized["validation"],
        data_collator=DataCollatorWithPadding(tokenizer=tokenizer),
        compute_metrics=metric_fn,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=2)],
    )

    trainer.train()
    predictions = trainer.predict(tokenized["test"])
    test_preds = np.argmax(predictions.predictions, axis=1)
    y_true = test_df["label"].tolist()
    y_pred = [ID_TO_LABEL[int(pred)] for pred in test_preds]
    test_metrics = compute_metrics(y_true, y_pred, LABELS)

    tokenizer.save_pretrained(output_dir / "best_tokenizer")
    trainer.save_model(output_dir / "best_model")

    summary = {
        "model_name": model_name,
        "run_id": run_id,
        "test_metrics": test_metrics,
        "trainer_metrics": predictions.metrics,
    }
    save_metrics(summary, paths.results_dir / f"{run_id}_metrics.json")
    save_confusion_matrix(
        y_true,
        y_pred,
        LABELS,
        paths.figures_dir / f"{run_id}_confusion_matrix.png",
        f"{run_id} Confusion Matrix",
    )
    (paths.results_dir / f"{run_id}_predictions.csv").write_text(
        pd.DataFrame(
            {
                "text": test_df["text"],
                "cleaned_text": test_df["cleaned_text"],
                "true_label": y_true,
                "predicted_label": y_pred,
            }
        ).to_csv(index=False),
        encoding="utf-8",
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Fine-tune a multilingual transformer for sentiment classification.")
    parser.add_argument(
        "--model_name",
        default=DEFAULT_MODEL_NAME,
        help="Hugging Face model ID or local model path. Default: castorini/afriberta_small.",
    )
    parser.add_argument(
        "--run_name",
        default=None,
        help="Optional short name used for model and report output files.",
    )
    args = parser.parse_args()

    summary = train_transformer(model_name=args.model_name, run_name=args.run_name)
    print("Transformer training complete.")
    print(f"Model: {summary['model_name']}")
    print(f"Run ID: {summary['run_id']}")
    print(f"Test macro F1: {summary['test_metrics']['macro_f1']:.4f}")


if __name__ == "__main__":
    main()
