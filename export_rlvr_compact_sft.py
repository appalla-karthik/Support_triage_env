from __future__ import annotations

import argparse
import json
from pathlib import Path
from random import Random
from typing import Any

from inference import (
    SYSTEM_PROMPT,
    _recommended_next_action,
    _scripted_policy_action,
    postprocess_action,
)
from support_triage_env.rlvr_compact_prompt import build_rlvr_sft_text
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
        description="Export compact-prompt RLVR warm-start SFT data from the scripted policy."
    )
    parser.add_argument(
        "--tasks",
        default=",".join(DEFAULT_TASKS),
        help="Comma-separated task ids to export.",
    )
    parser.add_argument(
        "--episodes-per-task",
        type=int,
        default=40,
        help="Number of scripted episodes per task.",
    )
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument(
        "--output",
        default="outputs/rlvr_compact_sft.jsonl",
        help="Output JSONL dataset path.",
    )
    parser.add_argument(
        "--min-final-score",
        type=float,
        default=0.85,
        help="Only keep episodes whose scripted final score meets this threshold.",
    )
    return parser.parse_args()


def _teacher_action(observation: dict[str, Any], state: dict[str, Any]):
    action = _scripted_policy_action(observation, state)
    if action is None:
        action = _recommended_next_action(state)
    action = postprocess_action(action, observation, state)
    return action


def _write_jsonl(rows: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    args = _parse_args()
    tasks = [task.strip() for task in args.tasks.split(",") if task.strip()]
    unknown = [task for task in tasks if task not in task_ids()]
    if unknown:
        raise ValueError(f"Unknown task ids: {', '.join(unknown)}")

    rng = Random(args.seed)
    rows: list[dict[str, Any]] = []
    kept_episodes = 0

    for task_id in tasks:
        for _ in range(args.episodes_per_task):
            scenario_seed = rng.randint(0, 10**9)
            env = SupportTriageSimulator()
            observation = env.reset(task_id=task_id, seed=scenario_seed)
            episode_rows: list[dict[str, Any]] = []
            done = False

            while not done:
                observation_payload = observation.model_dump(mode="json")
                state_payload = env.state().model_dump(mode="json")
                action = _teacher_action(observation_payload, state_payload)
                action_payload = action.model_dump(mode="json", exclude_none=True)

                episode_rows.append(
                    {
                        "dataset_type": "support_triage_rlvr_compact_sft",
                        "task_id": task_id,
                        "scenario_seed": scenario_seed,
                        "step_index": state_payload.get("step_count", 0),
                        "text": build_rlvr_sft_text(
                            SYSTEM_PROMPT,
                            observation_payload,
                            state_payload,
                            action_payload,
                        ),
                        "action": action_payload,
                    }
                )

                observation, _, done, _ = env.step(action)

            final_score = env.state().final_score
            if final_score >= args.min_final_score:
                kept_episodes += 1
                rows.extend(episode_rows)

    output_path = Path(args.output)
    _write_jsonl(rows, output_path)
    print(
        json.dumps(
            {
                "output": str(output_path),
                "rows": len(rows),
                "tasks": tasks,
                "episodes_per_task": args.episodes_per_task,
                "kept_episodes": kept_episodes,
                "seed": args.seed,
                "min_final_score": args.min_final_score,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
