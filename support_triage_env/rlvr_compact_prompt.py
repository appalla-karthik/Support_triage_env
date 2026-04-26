from __future__ import annotations

import json
import textwrap
from typing import Any


def compact_queue_summary(queue: list[dict[str, Any]], *, limit: int = 3) -> list[dict[str, Any]]:
    summary: list[dict[str, Any]] = []
    for ticket in queue[:limit]:
        summary.append(
            {
                "ticket_id": ticket.get("ticket_id"),
                "subject": ticket.get("subject"),
                "customer_tier": ticket.get("customer_tier"),
                "sla_hours_remaining": ticket.get("sla_hours_remaining"),
                "current_status": ticket.get("current_status"),
                "current_category": ticket.get("current_category"),
                "current_priority": ticket.get("current_priority"),
                "current_department_priority": ticket.get("current_department_priority"),
                "assigned_team": ticket.get("assigned_team"),
                "latest_customer_message": ticket.get("latest_customer_message"),
            }
        )
    return summary


def recent_action_summary(state: dict[str, Any], *, limit: int = 3) -> list[dict[str, Any]]:
    history = state.get("action_history", [])
    compact: list[dict[str, Any]] = []
    for action in history[-limit:]:
        compact.append(
            {
                "action_type": action.get("action_type"),
                "ticket_id": action.get("ticket_id"),
                "category": action.get("category"),
                "priority": action.get("priority"),
                "department_priority": action.get("department_priority"),
                "team": action.get("team"),
                "resolution_code": action.get("resolution_code"),
            }
        )
    return compact


def build_rlvr_user_prompt(observation: dict[str, Any], state: dict[str, Any]) -> str:
    task = observation.get("task", {}) or {}
    progress = observation.get("progress", {}) or {}
    focused_ticket = observation.get("focused_ticket")
    queue = observation.get("queue", []) or []
    last_action_result = observation.get("last_action_result", "")
    recent_tool = state.get("last_tool_result")

    compact_state = {
        "step_count": state.get("step_count"),
        "max_steps": state.get("max_steps"),
        "focused_ticket_id": state.get("focused_ticket_id"),
        "recent_actions": recent_action_summary(state),
        "last_tool_result": recent_tool,
    }

    return textwrap.dedent(
        f"""
        Return exactly one JSON object for the next action.

        Goal:
        {task.get("objective", "")}

        Task metadata:
        {json.dumps({
            "task_id": task.get("task_id"),
            "title": task.get("title"),
            "difficulty": task.get("difficulty"),
        }, indent=2)}

        Focused ticket:
        {json.dumps(focused_ticket, indent=2)}

        Queue summary:
        {json.dumps(compact_queue_summary(queue), indent=2)}

        Progress:
        {json.dumps({
            "score": progress.get("score"),
            "satisfied_requirements": progress.get("satisfied_requirements", []),
            "outstanding_requirements": progress.get("outstanding_requirements", []),
            "violations": progress.get("violations", []),
        }, indent=2)}

        Last action result:
        {last_action_result}

        Compact state:
        {json.dumps(compact_state, indent=2)}

        Decision rules:
        - Choose one concrete next action only.
        - Prefer the focused ticket or the highest-risk ticket in the queue summary.
        - Do not repeat the same action on the same ticket unless the last result clearly failed.
        - For outage/escalation tasks, gather missing repro details, classify correctly, create incident if needed, and escalate with workspace/browser/time context.
        - If the objective is satisfied and score is strong, return {{"action_type":"finish"}}.
        """
    ).strip()


def build_rlvr_sft_text(system_prompt: str, observation: dict[str, Any], state: dict[str, Any], action_payload: dict[str, Any]) -> str:
    user_prompt = build_rlvr_user_prompt(observation, state)
    return (
        f"System:\n{system_prompt}\n\n"
        f"User:\n{user_prompt}\n\n"
        f"Response:\n{json.dumps(action_payload, ensure_ascii=False)}"
    )
