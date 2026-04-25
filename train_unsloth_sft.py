from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import torch
import unsloth
from datasets import Dataset, load_dataset
from huggingface_hub import HfApi
from trl import SFTTrainer
from transformers import TrainingArguments
from unsloth import FastLanguageModel


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Unsloth SFT for the Support Triage environment dataset."
    )
    parser.add_argument(
        "--dataset-path",
        default="outputs/synthetic_trajectory_sft_30k_balanced.jsonl",
        help="Local JSONL dataset path. Ignored if --dataset-repo is provided.",
    )
    parser.add_argument(
        "--dataset-repo",
        default="",
        help="Optional Hugging Face dataset repo id containing data/train.jsonl.",
    )
    parser.add_argument(
        "--dataset-file",
        default="data/train.jsonl",
        help="Path inside the dataset repo when using --dataset-repo.",
    )
    parser.add_argument(
        "--model-name",
        default="unsloth/Qwen2.5-3B-Instruct-bnb-4bit",
        help="Unsloth-compatible base model.",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs/unsloth_full_run_3b",
        help="Local output directory for checkpoints and final adapter.",
    )
    parser.add_argument(
        "--output-repo",
        default="",
        help="Optional Hugging Face model repo to upload the final adapter folder.",
    )
    parser.add_argument("--max-seq-length", type=int, default=1024)
    parser.add_argument("--eval-size", type=float, default=0.02)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-steps", type=int, default=300)
    parser.add_argument("--warmup-steps", type=int, default=20)
    parser.add_argument("--learning-rate", type=float, default=2e-4)
    parser.add_argument("--per-device-train-batch-size", type=int, default=2)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=4)
    parser.add_argument("--logging-steps", type=int, default=10)
    parser.add_argument("--eval-steps", type=int, default=50)
    parser.add_argument("--save-steps", type=int, default=100)
    parser.add_argument(
        "--train-limit",
        type=int,
        default=0,
        help="Optional cap on training rows for quick smoke runs. 0 means full dataset.",
    )
    parser.add_argument(
        "--eval-limit",
        type=int,
        default=0,
        help="Optional cap on eval rows for quick smoke runs. 0 means full eval split.",
    )
    parser.add_argument(
        "--lora-r",
        type=int,
        default=16,
    )
    parser.add_argument(
        "--load-in-4bit",
        action="store_true",
        default=True,
        help="Use the quantized 4-bit checkpoint variant.",
    )
    return parser.parse_args()


def _load_rows(dataset_path: str, dataset_repo: str, dataset_file: str) -> list[dict]:
    if dataset_repo:
        dataset = load_dataset(
            "json",
            data_files=f"hf://datasets/{dataset_repo}/{dataset_file}",
            split="train",
            token=os.getenv("HF_TOKEN"),
        )
        return [dict(row) for row in dataset]

    path = Path(dataset_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset file not found: {path}")

    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle]


def _build_dataset(rows: list[dict], eval_size: float, seed: int) -> tuple[Dataset, Dataset]:
    dataset = Dataset.from_list(
        [{"text": row["text"], "task_id": row.get("task_id", "")} for row in rows]
    ).train_test_split(test_size=eval_size, seed=seed)

    train_dataset = dataset["train"].remove_columns(["task_id"])
    eval_dataset = dataset["test"].remove_columns(["task_id"])
    return train_dataset, eval_dataset


def _save_run_metadata(args: argparse.Namespace, train_rows: int, eval_rows: int, output_dir: Path) -> None:
    metadata = {
        "model_name": args.model_name,
        "dataset_path": args.dataset_path,
        "dataset_repo": args.dataset_repo,
        "dataset_file": args.dataset_file,
        "train_rows": train_rows,
        "eval_rows": eval_rows,
        "max_seq_length": args.max_seq_length,
        "max_steps": args.max_steps,
        "learning_rate": args.learning_rate,
        "per_device_train_batch_size": args.per_device_train_batch_size,
        "gradient_accumulation_steps": args.gradient_accumulation_steps,
        "seed": args.seed,
    }
    (output_dir / "run_config.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")


def _upload_adapter(adapter_dir: Path, output_repo: str) -> None:
    token = os.getenv("HF_TOKEN")
    if not token:
        raise RuntimeError("HF_TOKEN is required to upload adapter artifacts to the Hub.")

    api = HfApi(token=token)
    api.create_repo(repo_id=output_repo, repo_type="model", exist_ok=True)
    api.upload_folder(
        repo_id=output_repo,
        repo_type="model",
        folder_path=str(adapter_dir),
        commit_message="Upload Support Triage Unsloth adapter",
    )


def main() -> None:
    args = _parse_args()

    rows = _load_rows(args.dataset_path, args.dataset_repo, args.dataset_file)
    train_dataset, eval_dataset = _build_dataset(rows, args.eval_size, args.seed)

    if args.train_limit > 0:
        train_dataset = train_dataset.select(range(min(args.train_limit, len(train_dataset))))
    if args.eval_limit > 0:
        eval_dataset = eval_dataset.select(range(min(args.eval_limit, len(eval_dataset))))

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=args.model_name,
        max_seq_length=args.max_seq_length,
        load_in_4bit=args.load_in_4bit,
    )

    model = FastLanguageModel.get_peft_model(
        model,
        r=args.lora_r,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_alpha=args.lora_r,
        lora_dropout=0,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=args.seed,
        use_rslora=False,
        loftq_config=None,
    )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    _save_run_metadata(args, len(train_dataset), len(eval_dataset), output_dir)

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        dataset_text_field="text",
        max_seq_length=args.max_seq_length,
        packing=False,
        args=TrainingArguments(
            per_device_train_batch_size=args.per_device_train_batch_size,
            gradient_accumulation_steps=args.gradient_accumulation_steps,
            warmup_steps=args.warmup_steps,
            max_steps=args.max_steps,
            learning_rate=args.learning_rate,
            logging_steps=args.logging_steps,
            eval_steps=args.eval_steps,
            eval_strategy="steps",
            save_steps=args.save_steps,
            save_strategy="steps",
            output_dir=str(output_dir),
            report_to="none",
            fp16=not torch.cuda.is_bf16_supported(),
            bf16=torch.cuda.is_bf16_supported(),
            seed=args.seed,
        ),
    )

    train_result = trainer.train()
    metrics_path = output_dir / "train_metrics.json"
    metrics_path.write_text(json.dumps(train_result.metrics, indent=2), encoding="utf-8")

    adapter_dir = output_dir / "final_adapter"
    model.save_pretrained(str(adapter_dir))
    tokenizer.save_pretrained(str(adapter_dir))

    if args.output_repo:
        _upload_adapter(adapter_dir, args.output_repo)

    print(
        json.dumps(
            {
                "output_dir": str(output_dir),
                "adapter_dir": str(adapter_dir),
                "output_repo": args.output_repo,
                "train_rows": len(train_dataset),
                "eval_rows": len(eval_dataset),
                "metrics": train_result.metrics,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
