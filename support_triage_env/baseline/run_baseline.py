from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from openai import OpenAI

from support_triage_env.models import SupportTriageAction
from support_triage_env.simulator import SupportTriageSimulator


DEFAULT_MODEL = "gpt-4.1-mini-2025-04-14"
DEFAULT_TASKS = [
    "billing_refund_easy",
    "export_outage_medium",
    "security_and_refund_hard",
]


def build_prompt(observation: dict[str, Any], state: dict[str, Any]) -> str:
    return (
        "You are a customer support triage agent. Return only valid JSON for the next action.\n"
        "The JSON object must match this schema:\n"
        '{'
        '"action_type":"view_ticket|classify_ticket|draft_reply|request_info|escalate_ticket|resolve_ticket|finish",'
        '"ticket_id":"optional string or null",'
        '"category":"optional enum or null",'
        '"priority":"optional enum or null",'
        '"team":"optional enum or null",'
        '"message":"optional string or null",'
        '"resolution_code":"optional enum or null"'
        "}\n"
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


def run_task(client: OpenAI, model: str, task_id: str, max_turns: int = 12) -> dict[str, Any]:
    env = SupportTriageSimulator()
    observation = env.reset(task_id=task_id)
    trajectory: list[dict[str, Any]] = []

    for _ in range(max_turns):
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
        "difficulty": final_state.difficulty,
        "score": final_state.final_score,
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
    args = parser.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required to run the baseline.")

    client = OpenAI(api_key=api_key)
    results = [run_task(client, args.model, task_id) for task_id in DEFAULT_TASKS]
    mean_score = sum(item["score"] for item in results) / len(results)
    payload = {
        "model": args.model,
        "mean_score": round(mean_score, 4),
        "results": results,
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))

