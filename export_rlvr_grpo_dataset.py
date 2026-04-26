from __future__ import annotations

import argparse
import json
from pathlib import Path
from random import Random

from inference import SYSTEM_PROMPT
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
            "Export a GRPO-ready prompt dataset for first-action RL over the "
            "Support Triage simulator."
        )
    )
    parser.add_argument(
        "--tasks",
        default=",".join(DEFAULT_TASKS),
        help="Comma-separated task ids to export.",
    )
    parser.add_argument(
        "--episodes-per-task",
        type=int,
        default=80,
        help="How many seeded initial states to export per task.",
    )
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument(
        "--output",
        default="outputs/rlvr_grpo_dataset.jsonl",
        help="Output JSONL path.",
    )
    return parser.parse_args()


def _build_prompt(task_id: str, scenario_seed: int, observation: dict, state: dict) -> str:
    user_prompt = build_rlvr_user_prompt(observation, state)
    return (
        f"System:\n{SYSTEM_PROMPT}\n\n"
        f"User:\n{user_prompt}\n\n"
        f"Response:\n"
    )


def main() -> None:
    args = _parse_args()
    tasks = [task.strip() for task in args.tasks.split(",") if task.strip()]
    unknown = [task for task in tasks if task not in task_ids()]
    if unknown:
        raise ValueError(f"Unknown task ids: {', '.join(unknown)}")

    rng = Random(args.seed)
    rows: list[dict] = []

    for task_id in tasks:
        for _ in range(args.episodes_per_task):
            scenario_seed = rng.randint(0, 10**9)
            env = SupportTriageSimulator()
            observation = env.reset(task_id=task_id, seed=scenario_seed)
            observation_payload = observation.model_dump(mode="json")
            state_payload = env.state().model_dump(mode="json")
            rows.append(
                {
                    "dataset_type": "support_triage_rlvr_grpo_initial_state",
                    "task_id": task_id,
                    "scenario_seed": scenario_seed,
                    "prompt": _build_prompt(
                        task_id,
                        scenario_seed,
                        observation_payload,
                        state_payload,
                    ),
                }
            )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(
        json.dumps(
            {
                "output": str(output_path),
                "rows": len(rows),
                "tasks": tasks,
                "episodes_per_task": args.episodes_per_task,
                "seed": args.seed,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
