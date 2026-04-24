from __future__ import annotations

import argparse
import json
from pathlib import Path
from random import Random
from typing import Any

from support_triage_env.models import (
    ActionType,
    EnterpriseApp,
    IncidentSeverity,
    SupportTriageAction,
    TicketCategory,
    TicketPriority,
    TicketStatus,
    TicketTeam,
)
from support_triage_env.simulator import SupportTriageSimulator
from support_triage_env.tasks import TicketExpectation, task_ids


def _has_action(state_payload: dict[str, Any], action_type: str, ticket_id: str) -> bool:
    history = state_payload.get("action_history") or []
    return any(
        entry.get("action_type") == action_type and entry.get("ticket_id") == ticket_id
        for entry in history
    )


def _priority_rank(ticket: dict[str, Any], expectation: TicketExpectation) -> tuple[int, int]:
    category = expectation.category.value
    if category in {
        TicketCategory.SECURITY_ACCOUNT_TAKEOVER.value,
        TicketCategory.SECURITY_ESCALATION.value,
    }:
        return (0, ticket.get("sla_hours_remaining") or 999)
    if category in {
        TicketCategory.INCIDENT_COORDINATION.value,
        TicketCategory.PRODUCT_BUG.value,
    }:
        return (1, ticket.get("sla_hours_remaining") or 999)
    if category in {
        TicketCategory.BILLING_APPROVAL.value,
        TicketCategory.BILLING_REFUND.value,
    }:
        return (2, ticket.get("sla_hours_remaining") or 999)
    return (3, ticket.get("sla_hours_remaining") or 999)


def _policy_query(expectation: TicketExpectation, ticket: dict[str, Any]) -> str:
    category = expectation.category.value
    if category == TicketCategory.BILLING_APPROVAL.value:
        return "enterprise refund approval thresholds"
    if category == TicketCategory.BILLING_REFUND.value:
        return "duplicate charge refund workflow"
    if category in {
        TicketCategory.INCIDENT_COORDINATION.value,
        TicketCategory.PRODUCT_BUG.value,
    }:
        if "escalation-review" in (ticket.get("tags") or []):
            return "escalation packet review policy"
        return "product outage escalation checklist"
    if category in {
        TicketCategory.SECURITY_ACCOUNT_TAKEOVER.value,
        TicketCategory.SECURITY_ESCALATION.value,
    }:
        return "account takeover response policy"
    return "account access policy"


def _draft_reply(expectation: TicketExpectation, ticket: dict[str, Any]) -> str:
    parts: list[str] = []
    for requirement in expectation.reply_requirements:
        if requirement.phrases:
            parts.append(requirement.phrases[0])
    if not parts:
        parts.append("We are reviewing this request.")
    if ticket.get("workspace_id"):
        parts.append(f"Workspace: {ticket['workspace_id']}.")
    return " ".join(parts)


def _draft_escalation(expectation: TicketExpectation, ticket: dict[str, Any]) -> str:
    phrases = list(expectation.escalation_phrase_requirements)
    summary = f"Escalating {ticket['ticket_id']} for {expectation.team.value}. Subject: {ticket['subject']}."
    if phrases:
        summary += " " + " ".join(phrases)
    return summary


def _teacher_action(env: SupportTriageSimulator, observation_payload: dict[str, Any]) -> SupportTriageAction:
    scenario = getattr(env, "_scenario", None)
    if scenario is None:
        return SupportTriageAction(action_type=ActionType.FINISH)

    state_payload = env.state().model_dump(mode="json")
    active_tickets = [
        ticket
        for ticket in state_payload.get("tickets", [])
        if ticket.get("current_status") not in {TicketStatus.RESOLVED.value, TicketStatus.ESCALATED.value}
        and ticket["ticket_id"] in scenario.expectations
    ]
    if not active_tickets:
        return SupportTriageAction(action_type=ActionType.FINISH)

    ranked = sorted(
        active_tickets,
        key=lambda ticket: _priority_rank(ticket, scenario.expectations[ticket["ticket_id"]]),
    )
    ticket = ranked[0]
    expectation = scenario.expectations[ticket["ticket_id"]]
    ticket_id = ticket["ticket_id"]
    tags = set(ticket.get("tags") or [])
    accessible_apps = set(observation_payload.get("accessible_apps") or [])

    if (
        EnterpriseApp.CRM_WORKSPACE.value in accessible_apps
        and not _has_action(state_payload, ActionType.LOOKUP_ACCOUNT.value, ticket_id)
    ):
        return SupportTriageAction(
            action_type=ActionType.LOOKUP_ACCOUNT,
            ticket_id=ticket_id,
            app=EnterpriseApp.CRM_WORKSPACE,
        )

    if (
        expectation.category in {TicketCategory.BILLING_APPROVAL, TicketCategory.BILLING_REFUND}
        and EnterpriseApp.BILLING_SYSTEM.value in accessible_apps
        and not _has_action(state_payload, ActionType.CHECK_BILLING_STATUS.value, ticket_id)
    ):
        return SupportTriageAction(
            action_type=ActionType.CHECK_BILLING_STATUS,
            ticket_id=ticket_id,
            app=EnterpriseApp.BILLING_SYSTEM,
        )

    if (
        EnterpriseApp.POLICY_HUB.value in accessible_apps
        and not _has_action(state_payload, ActionType.SEARCH_POLICY.value, ticket_id)
    ):
        return SupportTriageAction(
            action_type=ActionType.SEARCH_POLICY,
            ticket_id=ticket_id,
            app=EnterpriseApp.POLICY_HUB,
            message=_policy_query(expectation, ticket),
        )

    if (
        expectation.category in {TicketCategory.INCIDENT_COORDINATION, TicketCategory.PRODUCT_BUG}
        and EnterpriseApp.INCIDENT_TRACKER.value in accessible_apps
        and ticket.get("linked_incident_id") is None
        and not _has_action(state_payload, ActionType.CREATE_INCIDENT.value, ticket_id)
    ):
        severity = IncidentSeverity.CRITICAL if expectation.priority == TicketPriority.URGENT else IncidentSeverity.HIGH
        return SupportTriageAction(
            action_type=ActionType.CREATE_INCIDENT,
            ticket_id=ticket_id,
            app=EnterpriseApp.INCIDENT_TRACKER,
            team=expectation.team,
            severity=severity,
            message=f"Incident created for {ticket_id}: {ticket['subject']}",
        )

    if (
        expectation.category in {TicketCategory.SECURITY_ACCOUNT_TAKEOVER, TicketCategory.SECURITY_ESCALATION}
        and EnterpriseApp.TRUST_SAFETY_CONSOLE.value in accessible_apps
        and not _has_action(state_payload, ActionType.ADD_INTERNAL_NOTE.value, ticket_id)
    ):
        return SupportTriageAction(
            action_type=ActionType.ADD_INTERNAL_NOTE,
            ticket_id=ticket_id,
            app=EnterpriseApp.TRUST_SAFETY_CONSOLE,
            message="Trust escalation note captured with security context.",
        )

    if "responds-fast" in tags and not ticket.get("requested_information"):
        return SupportTriageAction(
            action_type=ActionType.REQUEST_INFO,
            ticket_id=ticket_id,
            message="Please share the workspace, browser, and approximate timestamp so we can investigate.",
        )

    if (
        ticket.get("current_category") != expectation.category.value
        or ticket.get("current_priority") != expectation.priority.value
        or ticket.get("assigned_team") != expectation.team.value
    ):
        return SupportTriageAction(
            action_type=ActionType.CLASSIFY_TICKET,
            ticket_id=ticket_id,
            category=expectation.category,
            priority=expectation.priority,
            team=expectation.team,
        )

    if not ticket.get("outbound_messages"):
        return SupportTriageAction(
            action_type=ActionType.DRAFT_REPLY,
            ticket_id=ticket_id,
            message=_draft_reply(expectation, ticket),
        )

    if expectation.terminal_status == TicketStatus.RESOLVED.value:
        return SupportTriageAction(
            action_type=ActionType.RESOLVE_TICKET,
            ticket_id=ticket_id,
            resolution_code=expectation.resolution_code,
        )

    return SupportTriageAction(
        action_type=ActionType.ESCALATE_TICKET,
        ticket_id=ticket_id,
        team=expectation.team,
        message=_draft_escalation(expectation, ticket),
    )


def _observation_prompt(
    observation_payload: dict[str, Any],
    state_payload: dict[str, Any] | None = None,
) -> str:
    task = observation_payload.get("task") or {}
    queue = observation_payload.get("queue") or []
    world_summary = observation_payload.get("world_summary") or []
    recent_events = observation_payload.get("recent_events") or []
    progress = observation_payload.get("progress") or (state_payload or {}).get("progress") or {}

    lines = [
        "You are an enterprise support triage agent.",
        f"Task: {task.get('task_id', '')}",
        f"Objective: {task.get('objective', '')}",
    ]
    if observation_payload.get("instructions"):
        lines.append("Instructions:")
        lines.extend(f"- {item}" for item in observation_payload["instructions"])
    if observation_payload.get("policy_hints"):
        lines.append("Policy hints:")
        lines.extend(f"- {item}" for item in observation_payload["policy_hints"])
    if progress:
        lines.append("Progress:")
        if "score" in progress:
            lines.append(f"- score: {progress.get('score')}")
        components = progress.get("components") or {}
        if components:
            lines.append("- components:")
            for key, value in components.items():
                lines.append(f"  - {key}: {value}")
        penalties = progress.get("penalties") or {}
        if penalties:
            lines.append("- penalties:")
            for key, value in penalties.items():
                lines.append(f"  - {key}: {value}")
        violations = progress.get("violations") or []
        if violations:
            lines.append("- violations:")
            for item in violations:
                lines.append(f"  - {item}")
    lines.append("Queue:")
    for ticket in queue:
        lines.append(
            "- "
            + json.dumps(
                {
                    "ticket_id": ticket.get("ticket_id"),
                    "subject": ticket.get("subject"),
                    "tier": ticket.get("customer_tier"),
                    "status": ticket.get("current_status"),
                    "sla_hours_remaining": ticket.get("sla_hours_remaining"),
                    "tags": ticket.get("tags") or [],
                    "workspace_id": ticket.get("workspace_id"),
                    "latest_customer_message": ticket.get("latest_customer_message"),
                },
                ensure_ascii=False,
            )
        )
    if world_summary:
        lines.append("World summary:")
        lines.extend(f"- {item}" for item in world_summary)
    if recent_events:
        lines.append("Recent events:")
        lines.extend(f"- {event.get('event_type')}: {event.get('message')}" for event in recent_events)
    if observation_payload.get("last_tool_result"):
        lines.append("Latest tool result:")
        lines.append(json.dumps(observation_payload["last_tool_result"], ensure_ascii=False))
    history = (state_payload or {}).get("action_history") or []
    if history:
        lines.append("Action history (most recent last):")
        # Keep this short so SFT prompts do not blow up in token count.
        for entry in history[-8:]:
            lines.append(
                "- "
                + json.dumps(
                    {
                        "step_number": entry.get("step_number"),
                        "action_type": entry.get("action_type"),
                        "ticket_id": entry.get("ticket_id"),
                    },
                    ensure_ascii=False,
                )
            )
    lines.append("Return only the next valid JSON action.")
    return "\n".join(lines)


def build_trajectory_dataset(
    episodes_per_task: int = 100,
    seed: int = 0,
    min_final_score: float = 0.0,
    output_format: str = "trajectory",
) -> list[dict[str, Any]]:
    rng = Random(seed)
    rows: list[dict[str, Any]] = []

    for task_id in task_ids():
        for _ in range(episodes_per_task):
            scenario_seed = rng.randint(0, 10**9)
            env = SupportTriageSimulator()
            observation = env.reset(task_id=task_id, seed=scenario_seed)
            episode_rows: list[dict[str, Any]] = []
            done = False

            while not done:
                observation_payload = observation.model_dump(mode="json")
                state_before = env.state().model_dump(mode="json")
                action = _teacher_action(env, observation_payload)
                action_payload = action.model_dump(mode="json", exclude_none=True)
                next_observation, reward, done, info = env.step(action)
                state_payload = info.get("state") or env.state().model_dump(mode="json")
                progress_after = (next_observation.model_dump(mode="json").get("progress") if next_observation else None) or state_payload.get("progress")

                row = {
                    "dataset_type": "support_triage_trajectory",
                    "task_id": task_id,
                    "scenario_seed": scenario_seed,
                    "episode_id": state_payload.get("episode_id"),
                    "step_index": state_payload.get("step_count", 1) - 1,
                    "observation": observation_payload,
                    "state_before": state_before,
                    "action": action_payload,
                    "reward": reward.value,
                    "score_after_step": state_payload.get("final_score"),
                    "progress_after_step": progress_after,
                    "done": done,
                }
                if output_format == "sft":
                    row = {
                        "dataset_type": "support_triage_sft_trajectory",
                        "task_id": task_id,
                        "scenario_seed": scenario_seed,
                        "step_index": row["step_index"],
                        "text": _observation_prompt(observation_payload, state_before)
                        + "\n\nResponse:\n"
                        + json.dumps(action_payload, ensure_ascii=False),
                        "reward": reward.value,
                        "done": done,
                        "progress_after_step": progress_after,
                    }
                episode_rows.append(row)
                observation = next_observation

            final_score = env.state().final_score
            if final_score >= min_final_score:
                rows.extend(episode_rows)
    return rows


def write_jsonl(rows: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes-per-task", type=int, default=100)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--min-final-score", type=float, default=0.6)
    parser.add_argument(
        "--format",
        choices=["trajectory", "sft"],
        default="trajectory",
        help="trajectory = full step traces, sft = observation-to-next-action rows.",
    )
    parser.add_argument(
        "--output",
        default="outputs/synthetic_support_triage_trajectories.jsonl",
    )
    args = parser.parse_args()

    rows = build_trajectory_dataset(
        episodes_per_task=args.episodes_per_task,
        seed=args.seed,
        min_final_score=args.min_final_score,
        output_format=args.format,
    )
    output_path = Path(args.output)
    write_jsonl(rows, output_path)
    print(
        json.dumps(
            {
                "output": str(output_path),
                "rows": len(rows),
                "episodes_per_task": args.episodes_per_task,
                "task_families": len(task_ids()),
                "seed": args.seed,
                "min_final_score": args.min_final_score,
                "format": args.format,
            }
        )
    )


if __name__ == "__main__":
    main()
