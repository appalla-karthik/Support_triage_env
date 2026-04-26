from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import torch
from datasets import Dataset
from unsloth import FastLanguageModel

# Compatibility shim:
# `llm_blender` used by some TRL GRPO builds still imports
# `TRANSFORMERS_CACHE` from `transformers.utils.hub`, while newer
# transformers builds removed that symbol. Inject it before importing TRL.
from huggingface_hub.constants import HF_HUB_CACHE
import transformers.utils.hub as transformers_hub

if not hasattr(transformers_hub, "TRANSFORMERS_CACHE"):
    transformers_hub.TRANSFORMERS_CACHE = HF_HUB_CACHE

from trl import GRPOConfig, GRPOTrainer

try:
    from unsloth import PatchFastRL
except ImportError:  # pragma: no cover - older Unsloth builds
    PatchFastRL = None

from inference import (
    _recommended_next_action,
    _scripted_policy_action,
    normalize_action_payload,
    postprocess_action,
)
from support_triage_env.models import DEFAULT_STRICT_SCORE, SupportTriageAction
from support_triage_env.simulator import SupportTriageSimulator


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run GRPO over first-action simulator states, using full-episode "
            "verifiable reward after the sampled action."
        )
    )
    parser.add_argument(
        "--adapter-path",
        required=True,
        help="Warm-start model/adaptor path, e.g. artifacts/unsloth_sft_final.",
    )
    parser.add_argument(
        "--dataset-path",
        default="outputs/rlvr_grpo_dataset.jsonl",
        help="GRPO prompt dataset exported by export_rlvr_grpo_dataset.py.",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs/unsloth_rlvr_grpo",
        help="Output directory for GRPO checkpoints and final adapter.",
    )
    parser.add_argument("--max-seq-length", type=int, default=2048)
    parser.add_argument("--max-prompt-length", type=int, default=1536)
    parser.add_argument("--max-completion-length", type=int, default=160)
    parser.add_argument("--num-generations", type=int, default=4)
    parser.add_argument("--per-device-train-batch-size", type=int, default=1)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=4)
    parser.add_argument("--learning-rate", type=float, default=5e-6)
    parser.add_argument("--max-steps", type=int, default=120)
    parser.add_argument("--logging-steps", type=int, default=5)
    parser.add_argument("--save-steps", type=int, default=40)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--lora-r", type=int, default=16)
    parser.add_argument(
        "--load-in-4bit",
        action="store_true",
        default=True,
        help="Load the warm-start adapter in 4-bit mode.",
    )
    return parser.parse_args()


def _extract_json_object(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.replace("json", "", 1).strip()

    decoder = json.JSONDecoder()
    first_brace = cleaned.find("{")
    if first_brace == -1:
        raise ValueError("No JSON object found in model output.")

    for start in range(first_brace, len(cleaned)):
        if cleaned[start] != "{":
            continue
        try:
            payload, _ = decoder.raw_decode(cleaned[start:])
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload

    raise ValueError("No JSON object found in model output.")


def _load_rows(dataset_path: str) -> list[dict[str, Any]]:
    path = Path(dataset_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset file not found: {path}")

    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle]


def _build_dataset(rows: list[dict[str, Any]]) -> Dataset:
    return Dataset.from_list(
        [
            {
                "prompt": row["prompt"],
                "task_id": row["task_id"],
                "scenario_seed": int(row["scenario_seed"]),
            }
            for row in rows
        ]
    )


def _teacher_action(observation: dict[str, Any], state: dict[str, Any]) -> SupportTriageAction:
    action = _scripted_policy_action(observation, state)
    if action is None:
        action = _recommended_next_action(state)
    return postprocess_action(action, observation, state)


def _shape_first_action_reward(
    action: SupportTriageAction,
    teacher: SupportTriageAction,
    *,
    final_score: float,
) -> float:
    reward = final_score

    if action.action_type == teacher.action_type:
        reward += 0.08
    if action.ticket_id and teacher.ticket_id and action.ticket_id == teacher.ticket_id:
        reward += 0.03
    if action.team is not None and teacher.team is not None and action.team == teacher.team:
        reward += 0.02
    if action.category is not None and teacher.category is not None and action.category == teacher.category:
        reward += 0.02
    if action.priority is not None and teacher.priority is not None and action.priority == teacher.priority:
        reward += 0.01
    if (
        action.department_priority is not None
        and teacher.department_priority is not None
        and action.department_priority == teacher.department_priority
    ):
        reward += 0.01
    if (
        action.resolution_code is not None
        and teacher.resolution_code is not None
        and action.resolution_code == teacher.resolution_code
    ):
        reward += 0.02
    if action.action_type.value == "finish":
        reward -= 0.12

    return float(min(1.0, max(DEFAULT_STRICT_SCORE, reward)))


def _completion_to_text(completion: Any) -> str:
    if isinstance(completion, str):
        return completion
    if isinstance(completion, list):
        parts: list[str] = []
        for item in completion:
            if isinstance(item, dict) and item.get("content"):
                parts.append(str(item["content"]))
            else:
                parts.append(str(item))
        return "".join(parts)
    return str(completion)


def _score_first_action_rollout(
    completion_text: str,
    *,
    task_id: str,
    scenario_seed: int,
) -> float:
    env = SupportTriageSimulator()
    observation = env.reset(task_id=task_id, seed=scenario_seed)
    observation_payload = observation.model_dump(mode="json")
    state_payload = env.state().model_dump(mode="json")
    teacher = _teacher_action(observation_payload, state_payload)

    try:
        payload = normalize_action_payload(_extract_json_object(completion_text))
        action = SupportTriageAction(**payload)
        action = postprocess_action(action, observation_payload, state_payload)
    except Exception:
        return DEFAULT_STRICT_SCORE

    observation, _, done, _ = env.step(action)
    steps_left = max(0, env.state().max_steps - env.state().step_count)

    for _ in range(steps_left):
        if done:
            break
        observation_payload = observation.model_dump(mode="json")
        state_payload = env.state().model_dump(mode="json")
        teacher = _teacher_action(observation_payload, state_payload)
        observation, _, done, _ = env.step(teacher)

    final_score = env.state().final_score
    return _shape_first_action_reward(action, teacher, final_score=final_score)


def _reward_func(completions, task_id, scenario_seed, **kwargs):
    rewards: list[float] = []
    for completion, item_task_id, item_seed in zip(completions, task_id, scenario_seed):
        completion_text = _completion_to_text(completion)
        rewards.append(
            _score_first_action_rollout(
                completion_text,
                task_id=item_task_id,
                scenario_seed=int(item_seed),
            )
        )
    return rewards


def main() -> None:
    args = _parse_args()
    rows = _load_rows(args.dataset_path)
    dataset = _build_dataset(rows)

    if PatchFastRL is not None:
        PatchFastRL("GRPO", FastLanguageModel)

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=args.adapter_path,
        max_seq_length=args.max_seq_length,
        load_in_4bit=args.load_in_4bit,
    )
    model.generation_config.max_length = None
    if not hasattr(model, "peft_config"):
        model = FastLanguageModel.get_peft_model(
            model,
            r=args.lora_r,
            target_modules=[
                "q_proj",
                "k_proj",
                "v_proj",
                "o_proj",
                "gate_proj",
                "up_proj",
                "down_proj",
            ],
            lora_alpha=args.lora_r,
            lora_dropout=0,
            bias="none",
            use_gradient_checkpointing="unsloth",
            random_state=args.seed,
            use_rslora=False,
            loftq_config=None,
        )
    if not hasattr(model, "warnings_issued"):
        model.warnings_issued = {}

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "run_config.json").write_text(
        json.dumps(
            {
                "adapter_path": args.adapter_path,
                "dataset_path": args.dataset_path,
                "dataset_rows": len(dataset),
                "max_seq_length": args.max_seq_length,
                "max_prompt_length": args.max_prompt_length,
                "max_completion_length": args.max_completion_length,
                "num_generations": args.num_generations,
                "learning_rate": args.learning_rate,
                "max_steps": args.max_steps,
                "seed": args.seed,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    trainer = GRPOTrainer(
        model=model,
        processing_class=tokenizer,
        reward_funcs=[_reward_func],
        train_dataset=dataset,
        args=GRPOConfig(
            output_dir=str(output_dir),
            learning_rate=args.learning_rate,
            per_device_train_batch_size=args.per_device_train_batch_size,
            gradient_accumulation_steps=args.gradient_accumulation_steps,
            max_steps=args.max_steps,
            logging_steps=args.logging_steps,
            save_steps=args.save_steps,
            report_to="none",
            fp16=not torch.cuda.is_bf16_supported(),
            bf16=torch.cuda.is_bf16_supported(),
            max_prompt_length=args.max_prompt_length,
            max_completion_length=args.max_completion_length,
            num_generations=args.num_generations,
            seed=args.seed,
        ),
    )

    train_result = trainer.train()
    metrics_path = output_dir / "train_metrics.json"
    metrics_path.write_text(json.dumps(train_result.metrics, indent=2), encoding="utf-8")

    adapter_dir = output_dir / "final_adapter"
    model.save_pretrained(str(adapter_dir))
    tokenizer.save_pretrained(str(adapter_dir))

    print(
        json.dumps(
            {
                "output_dir": str(output_dir),
                "adapter_dir": str(adapter_dir),
                "dataset_rows": len(dataset),
                "metrics": train_result.metrics,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
