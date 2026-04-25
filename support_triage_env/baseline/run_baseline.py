from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from openai import OpenAI

from support_triage_env.models import SupportTriageAction
from support_triage_env.simulator import SupportTriageSimulator
from support_triage_env.tasks import task_ids


DEFAULT_MODEL = "gpt-4.1-mini-2025-04-14"
DEFAULT_MAX_TURNS = int(os.environ.get("BASELINE_MAX_TURNS", "24"))
DEFAULT_TASKS = task_ids()
DEFAULT_SEED = int(os.environ.get("BASELINE_SEED", "7"))
SUCCESS_SCORE_THRESHOLD = 0.85


def build_prompt(observation: dict[str, Any], state: dict[str, Any]) -> str:
    return (
        "You are an enterprise support operations agent. Return only valid JSON for the next action.\n"
        "The JSON object must match this schema:\n"
        '{'
        '"action_type":"view_ticket|classify_ticket|draft_reply|request_info|escalate_ticket|resolve_ticket|lookup_account|check_billing_status|search_policy|create_incident|add_internal_note|finish",'
        '"ticket_id":"optional string or null",'
        '"category":"optional enum or null",'
        '"priority":"optional enum or null",'
        '"team":"optional enum or null",'
        '"app":"optional enum or null",'
        '"target_id":"optional string or null",'
        '"message":"optional string or null",'
        '"severity":"optional enum or null",'
        '"details":"optional object or null",'
        '"resolution_code":"optional enum or null"'
        "}\n"
        "Allowed categories: billing_refund, billing_approval, product_bug, incident_coordination, security_account_takeover, security_escalation, account_access.\n"
        "Allowed apps: ticketing_console, crm_workspace, billing_system, incident_tracker, trust_safety_console, policy_hub.\n"
        "Allowed priorities: low, medium, high, urgent. Allowed teams: billing_ops, engineering, trust_safety, customer_support.\n"
        "Choose exactly one next action. Do not wrap the JSON in markdown.\n\n"
        f"Observation:\n{json.dumps(observation, indent=2)}\n\n"
        f"State:\n{json.dumps(state, indent=2)}\n"
    )


def parse_action(text: str) -> SupportTriageAction:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        cleaned = cleaned.replace("json", "", 1).strip()
    data = json.loads(cleaned)
    return SupportTriageAction(**data)


def run_task(
    client: OpenAI,
    model: str,
    task_id: str,
    max_turns: int = DEFAULT_MAX_TURNS,
    seed: int = DEFAULT_SEED,
) -> dict[str, Any]:
    env = SupportTriageSimulator()
    observation = env.reset(task_id=task_id, seed=seed)
    trajectory: list[dict[str, Any]] = []
    task_budget = max(max_turns, int(observation.task.max_steps))

    for _ in range(task_budget):
        state = env.state()
        prompt = build_prompt(
            observation.model_dump(mode="json"),
            state.model_dump(mode="json"),
        )
        response = client.responses.create(
            model=model,
            input=prompt,
            temperature=0,
            max_output_tokens=400,
        )
        action = parse_action(response.output_text)
        observation, reward, done, info = env.step(action)
        trajectory.append(
            {
                "action": action.model_dump(mode="json", exclude_none=True),
                "reward": reward.model_dump(mode="json"),
                "score": info["grading"]["score"],
            }
        )
        if done:
            break

    final_state = env.state()
    return {
        "task_id": task_id,
        "seed": seed,
        "difficulty": final_state.difficulty,
        "score": final_state.final_score,
        "success": final_state.final_score >= SUCCESS_SCORE_THRESHOLD,
        "cumulative_reward": final_state.cumulative_reward,
        "steps": final_state.step_count,
        "trajectory": trajectory,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model",
        default=os.environ.get("OPENAI_MODEL", DEFAULT_MODEL),
        help="OpenAI model name or snapshot.",
    )
    parser.add_argument(
        "--output",
        default="outputs/baseline_scores.json",
        help="Where to save the baseline score report.",
    )
    parser.add_argument(
        "--tasks",
        default=",".join(DEFAULT_TASKS),
        help="Comma-separated task ids to run. Defaults to all task families.",
    )
    parser.add_argument(
        "--max-turns",
        type=int,
        default=DEFAULT_MAX_TURNS,
        help="Maximum turns per task before local cutoff. Defaults to 24.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help="Deterministic simulator seed to use for every baseline task run. Defaults to 7.",
    )
    args = parser.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required to run the baseline.")

    client = OpenAI(api_key=api_key)
    task_ids_to_run = [task_id.strip() for task_id in args.tasks.split(",") if task_id.strip()]
    results = [
        run_task(client, args.model, task_id, max_turns=args.max_turns, seed=args.seed)
        for task_id in task_ids_to_run
    ]
    mean_score = sum(item["score"] for item in results) / len(results)
    success_count = sum(1 for item in results if item["success"])
    payload = {
        "model": args.model,
        "seed": args.seed,
        "mean_score": round(mean_score, 4),
        "success_rate": round(success_count / len(results), 4),
        "task_count": len(results),
        "results": results,
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))

