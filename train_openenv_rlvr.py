from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable

import torch
from unsloth import FastLanguageModel

from inference import (
    SYSTEM_PROMPT,
    SUCCESS_SCORE_THRESHOLD,
    _recommended_next_action,
    _scripted_policy_action,
    normalize_action_payload,
    postprocess_action,
)
from support_triage_env.models import (
    DEFAULT_STRICT_SCORE,
    SupportTriageAction,
    strict_unit_interval,
)
from support_triage_env.rlvr_compact_prompt import build_rlvr_user_prompt
from support_triage_env.simulator import SupportTriageSimulator
from support_triage_env.tasks import task_ids


DEFAULT_TASKS = [
    "followup_reprioritization_queue",
    "escalation_rejection_recovery",
    "security_and_refund_hard",
    "incident_coordination_outage",
]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run an RLVR smoke/eval harness against the Support Triage simulator "
            "using a local SFT adapter. This script evaluates verifiable reward "
            "rollouts and is intended to be the safe step before full GRPO updates."
        )
    )
    parser.add_argument(
        "--adapter-path",
        required=True,
        help="Path to the saved Unsloth/PEFT adapter directory, such as outputs/unsloth_sft_final/final_adapter.",
    )
    parser.add_argument(
        "--tasks",
        default=",".join(DEFAULT_TASKS),
        help="Comma-separated task ids to evaluate. Defaults to the hard RLVR subset.",
    )
    parser.add_argument(
        "--eval-seeds",
        default="7,11",
        help="Comma-separated deterministic simulator seeds.",
    )
    parser.add_argument("--max-steps", type=int, default=14)
    parser.add_argument("--max-seq-length", type=int, default=1024)
    parser.add_argument("--max-new-tokens", type=int, default=220)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument(
        "--output-dir",
        default="outputs/rlvr_smoke",
        help="Directory for RLVR smoke artifacts.",
    )
    parser.add_argument(
        "--compare-scripted",
        action="store_true",
        default=True,
        help="Also run the current scripted baseline for before/after comparison.",
    )
    parser.add_argument(
        "--skip-scripted",
        action="store_true",
        help="Skip scripted baseline comparison and run only the adapter policy.",
    )
    parser.add_argument(
        "--load-in-4bit",
        action="store_true",
        default=True,
        help="Load the adapter/base in 4-bit mode through Unsloth.",
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
        raise ValueError(f"No JSON object found in model output: {cleaned[:240]}")

    # Walk forward and return the first decodable JSON object, ignoring any
    # leading/trailing junk the model may emit around the valid action payload.
    for start in range(first_brace, len(cleaned)):
        if cleaned[start] != "{":
            continue
        try:
            payload, _ = decoder.raw_decode(cleaned[start:])
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload

    raise ValueError(f"No JSON object found in model output: {cleaned[:240]}")


def _load_policy_model(
    adapter_path: str,
    max_seq_length: int,
    load_in_4bit: bool,
):
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=adapter_path,
        max_seq_length=max_seq_length,
        load_in_4bit=load_in_4bit,
    )
    model.generation_config.max_length = None
    FastLanguageModel.for_inference(model)
    return model, tokenizer


def _generate_model_action(
    model,
    tokenizer,
    observation: dict[str, Any],
    state: dict[str, Any],
    *,
    max_seq_length: int,
    max_new_tokens: int,
    temperature: float,
) -> tuple[SupportTriageAction, str]:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_rlvr_user_prompt(observation, state)},
    ]
    prompt_text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )
    tokenized = tokenizer(
        prompt_text,
        return_tensors="pt",
        truncation=True,
        max_length=max(256, max_seq_length - max_new_tokens),
    )
    prompt_ids = tokenized["input_ids"].to(model.device)
    attention_mask = tokenized["attention_mask"].to(model.device)

    generation_kwargs = {
        "input_ids": prompt_ids,
        "attention_mask": attention_mask,
        "max_new_tokens": max_new_tokens,
        "do_sample": temperature > 0,
        "use_cache": True,
        "pad_token_id": tokenizer.eos_token_id,
    }
    if temperature > 0:
        generation_kwargs["temperature"] = temperature

    with torch.inference_mode():
        outputs = model.generate(**generation_kwargs)

    generated = outputs[0][prompt_ids.shape[-1] :]
    raw_text = tokenizer.decode(generated, skip_special_tokens=True).strip()
    payload = normalize_action_payload(_extract_json_object(raw_text))
    return SupportTriageAction(**payload), raw_text


def _scripted_action(observation: dict[str, Any], state: dict[str, Any]) -> tuple[SupportTriageAction, str | None]:
    action = _scripted_policy_action(observation, state)
    if action is None:
        action = _recommended_next_action(state)
    return action, None


def _model_action_factory(
    model,
    tokenizer,
    *,
    max_seq_length: int,
    max_new_tokens: int,
    temperature: float,
) -> Callable[[dict[str, Any], dict[str, Any]], tuple[SupportTriageAction, str | None]]:
    def _inner(observation: dict[str, Any], state: dict[str, Any]) -> tuple[SupportTriageAction, str | None]:
        action, raw_text = _generate_model_action(
            model,
            tokenizer,
            observation,
            state,
            max_seq_length=max_seq_length,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
        )
        return action, raw_text

    return _inner


def _summarize_runs(runs: list[dict[str, Any]]) -> dict[str, Any]:
    if not runs:
        return {
            "success_threshold": SUCCESS_SCORE_THRESHOLD,
            "success_rate": 0.0,
            "mean_score": DEFAULT_STRICT_SCORE,
            "mean_steps": 0.0,
            "per_task": {},
        }

    success_rate = sum(1 for run in runs if run["success"]) / len(runs)
    mean_score = sum(run["final_score"] for run in runs) / len(runs)
    mean_steps = sum(run["steps"] for run in runs) / len(runs)

    per_task: dict[str, dict[str, Any]] = {}
    for task_id in sorted({run["task_id"] for run in runs}):
        task_runs = [run for run in runs if run["task_id"] == task_id]
        per_task[task_id] = {
            "mean_score": round(
                sum(run["final_score"] for run in task_runs) / len(task_runs), 4
            ),
            "success_rate": round(
                sum(1 for run in task_runs if run["success"]) / len(task_runs), 4
            ),
            "mean_steps": round(
                sum(run["steps"] for run in task_runs) / len(task_runs), 2
            ),
            "num_runs": len(task_runs),
        }

    return {
        "success_threshold": SUCCESS_SCORE_THRESHOLD,
        "success_rate": round(success_rate, 4),
        "mean_score": round(mean_score, 4),
        "mean_steps": round(mean_steps, 2),
        "per_task": per_task,
    }


def _run_policy_rollouts(
    policy_name: str,
    action_fn: Callable[[dict[str, Any], dict[str, Any]], tuple[SupportTriageAction, str | None]],
    *,
    tasks: list[str],
    seeds: list[int],
    max_steps: int,
) -> dict[str, Any]:
    runs: list[dict[str, Any]] = []

    for task_id in tasks:
        for seed in seeds:
            env = SupportTriageSimulator()
            observation = env.reset(task_id=task_id, seed=seed)
            trajectory: list[dict[str, Any]] = []
            done = False
            fallback_events: list[dict[str, Any]] = []
            step_budget = max(max_steps, int(observation.task.max_steps))

            for step in range(1, step_budget + 1):
                if done:
                    break

                observation_payload = observation.model_dump(mode="json")
                state_payload = env.state().model_dump(mode="json")

                try:
                    action, raw_text = action_fn(observation_payload, state_payload)
                except Exception as exc:
                    raw_text = None
                    action = _recommended_next_action(state_payload)
                    fallback_events.append(
                        {
                            "step": step,
                            "reason": "action_generation_failed",
                            "detail": str(exc),
                        }
                    )

                postprocess_fallbacks: list[str] = []
                action = postprocess_action(
                    action,
                    observation_payload,
                    state_payload,
                    fallback_reasons=postprocess_fallbacks,
                )
                for reason in postprocess_fallbacks:
                    fallback_events.append({"step": step, "reason": reason})

                next_observation, reward, done, info = env.step(action)
                trajectory.append(
                    {
                        "step": step,
                        "action": action.model_dump(mode="json", exclude_none=True),
                        "reward": round(float(reward.value), 4),
                        "task_score": round(float(reward.task_score), 4),
                        "score_after_step": round(
                            float(info.get("grading", {}).get("score", DEFAULT_STRICT_SCORE)),
                            4,
                        ),
                        "raw_model_output": raw_text,
                    }
                )
                observation = next_observation

            final_state = env.state()
            runs.append(
                {
                    "policy": policy_name,
                    "task_id": task_id,
                    "seed": seed,
                    "success": final_state.final_score >= SUCCESS_SCORE_THRESHOLD,
                    "steps": final_state.step_count,
                    "final_score": round(strict_unit_interval(final_state.final_score), 4),
                    "cumulative_reward": round(float(final_state.cumulative_reward), 4),
                    "fallback_events": fallback_events,
                    "trajectory": trajectory,
                }
            )

    return {
        "policy": policy_name,
        "summary": _summarize_runs(runs),
        "runs": runs,
    }


def main() -> None:
    args = _parse_args()
    tasks = [task.strip() for task in args.tasks.split(",") if task.strip()]
    unknown_tasks = [task for task in tasks if task not in task_ids()]
    if unknown_tasks:
        raise ValueError(f"Unknown task ids: {', '.join(unknown_tasks)}")

    seeds = [int(seed.strip()) for seed in args.eval_seeds.split(",") if seed.strip()]
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    model, tokenizer = _load_policy_model(
        args.adapter_path,
        max_seq_length=args.max_seq_length,
        load_in_4bit=args.load_in_4bit,
    )
    adapter_policy = _model_action_factory(
        model,
        tokenizer,
        max_seq_length=args.max_seq_length,
        max_new_tokens=args.max_new_tokens,
        temperature=args.temperature,
    )

    adapter_report = _run_policy_rollouts(
        "adapter_policy",
        adapter_policy,
        tasks=tasks,
        seeds=seeds,
        max_steps=args.max_steps,
    )

    payload: dict[str, Any] = {
        "mode": "rlvr_smoke",
        "adapter_path": args.adapter_path,
        "tasks": tasks,
        "eval_seeds": seeds,
        "max_steps": args.max_steps,
        "adapter": adapter_report,
    }

    if args.compare_scripted and not args.skip_scripted:
        scripted_report = _run_policy_rollouts(
            "scripted_baseline",
            _scripted_action,
            tasks=tasks,
            seeds=seeds,
            max_steps=args.max_steps,
        )
        payload["scripted_baseline"] = scripted_report
        payload["headline"] = {
            "baseline_mean_score": scripted_report["summary"]["mean_score"],
            "adapter_mean_score": adapter_report["summary"]["mean_score"],
            "score_delta": round(
                adapter_report["summary"]["mean_score"]
                - scripted_report["summary"]["mean_score"],
                4,
            ),
            "baseline_success_rate": scripted_report["summary"]["success_rate"],
            "adapter_success_rate": adapter_report["summary"]["success_rate"],
            "success_delta": round(
                adapter_report["summary"]["success_rate"]
                - scripted_report["summary"]["success_rate"],
                4,
            ),
        }

    report_path = output_dir / "rlvr_smoke_report.json"
    report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"report": str(report_path), "tasks": tasks, "eval_seeds": seeds}, indent=2))


if __name__ == "__main__":
    main()
