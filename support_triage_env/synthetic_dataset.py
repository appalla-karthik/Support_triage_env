from __future__ import annotations

import argparse
import json
from pathlib import Path
from random import Random
from typing import Any

from support_triage_env.tasks import build_task_scenario, task_ids


def scenario_to_examples(scenario_seed: int, scenario: Any) -> list[dict[str, Any]]:
    examples: list[dict[str, Any]] = []
    for ticket in scenario.tickets:
        expectation = scenario.expectations.get(ticket.ticket_id)
        if expectation is None:
            continue
        examples.append(
            {
                "dataset_type": "support_triage_synthetic",
                "scenario_seed": scenario_seed,
                "task_id": scenario.card.task_id,
                "title": scenario.card.title,
                "difficulty": scenario.card.difficulty,
                "objective": scenario.card.objective,
                "max_steps": scenario.card.max_steps,
                "instructions": list(scenario.instructions),
                "policy_hints": list(scenario.policy_hints),
                "accessible_apps": [app.value for app in scenario.accessible_apps],
                "world_summary": list(scenario.world_summary),
                "ticket": {
                    "ticket_id": ticket.ticket_id,
                    "customer_name": ticket.customer_name,
                    "customer_tier": ticket.customer_tier,
                    "account_id": ticket.account_id,
                    "billing_account_id": ticket.billing_account_id,
                    "workspace_id": ticket.workspace_id,
                    "subject": ticket.subject,
                    "messages": [message.model_dump(mode="json") for message in ticket.messages],
                },
                "expected": {
                    "category": expectation.category.value,
                    "priority": expectation.priority.value,
                    "department_priority": expectation.department_priority.value,
                    "team": expectation.team.value,
                    "terminal_status": expectation.terminal_status,
                    "resolution_code": (
                        expectation.resolution_code.value
                        if expectation.resolution_code is not None
                        else None
                    ),
                    "reply_requirements": [
                        rule.model_dump(mode="json")
                        for rule in expectation.reply_requirements
                    ],
                    "forbidden_phrases": list(expectation.forbidden_phrases),
                    "escalation_phrase_requirements": list(
                        expectation.escalation_phrase_requirements
                    ),
                },
            }
        )
    return examples


def build_synthetic_dataset(
    examples_per_task: int = 1000,
    seed: int = 0,
) -> list[dict[str, Any]]:
    rng = Random(seed)
    rows: list[dict[str, Any]] = []
    for task_id in task_ids():
        for _ in range(examples_per_task):
            scenario_seed = rng.randint(0, 10**9)
            scenario_rng = Random(scenario_seed)
            scenario = build_task_scenario(task_id, scenario_rng)
            rows.extend(scenario_to_examples(scenario_seed, scenario))
    return rows


def write_jsonl(rows: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--examples-per-task",
        type=int,
        default=1000,
        help="Number of generated scenarios per task family.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=0,
        help="Global seed for dataset generation.",
    )
    parser.add_argument(
        "--output",
        default="outputs/synthetic_support_triage_dataset.jsonl",
        help="Destination JSONL file.",
    )
    args = parser.parse_args()

    rows = build_synthetic_dataset(
        examples_per_task=args.examples_per_task,
        seed=args.seed,
    )
    output_path = Path(args.output)
    write_jsonl(rows, output_path)
    print(
        json.dumps(
            {
                "output": str(output_path),
                "rows": len(rows),
                "examples_per_task": args.examples_per_task,
                "task_families": len(task_ids()),
                "seed": args.seed,
            }
        )
    )


if __name__ == "__main__":
    main()
