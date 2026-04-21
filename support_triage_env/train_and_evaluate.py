from __future__ import annotations

import argparse
import json
import pickle
from collections import Counter
from pathlib import Path
from typing import Callable

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from support_triage_env.models import (
    ActionType,
    EnterpriseApp,
    IncidentSeverity,
    ResolutionCode,
    SupportTriageAction,
    TicketCategory,
    TicketPriority,
    TicketStatus,
    TicketTeam,
)
from support_triage_env.simulator import SupportTriageSimulator
from support_triage_env.tasks import task_ids
from support_triage_env.training_data import (
    _repo_dataset_file,
    build_combined_training_dataset,
    infer_support_label,
    summarize_labels,
)


DEFAULT_TASKS = task_ids()


def _majority_label(labels: list[str]) -> str:
    return Counter(labels).most_common(1)[0][0]


def _ticket_text(ticket: dict) -> str:
    messages = ticket.get("messages") or []
    message_text = " ".join(message.get("content", "") for message in messages)
    return f"{ticket.get('subject', '')}\n{message_text}".strip()


def _predict_heuristic(text: str, fallback_label: str) -> str:
    subject_only = text.splitlines()[0] if text else ""
    return infer_support_label(subject_only) or fallback_label


def _has_action(state_payload: dict, action_type: str, ticket_id: str) -> bool:
    history = state_payload.get("action_history") or []
    return any(
        entry.get("action_type") == action_type and entry.get("ticket_id") == ticket_id
        for entry in history
    )


def _find_ticket(state_payload: dict, ticket_id: str) -> dict | None:
    for ticket in state_payload.get("tickets", []):
        if ticket.get("ticket_id") == ticket_id:
            return ticket
    return None


def _route_for_label(label: str, ticket: dict) -> tuple[str, str, str]:
    tag_text = " ".join(ticket.get("tags") or []).lower()
    tier = (ticket.get("customer_tier") or "").lower()
    if label == TicketCategory.SECURITY_ESCALATION.value:
        return (
            TicketCategory.SECURITY_ESCALATION.value,
            TicketPriority.URGENT.value,
            TicketTeam.TRUST_SAFETY.value,
        )
    if label == TicketCategory.SECURITY_ACCOUNT_TAKEOVER.value:
        return (
            TicketCategory.SECURITY_ACCOUNT_TAKEOVER.value,
            TicketPriority.URGENT.value,
            TicketTeam.TRUST_SAFETY.value,
        )
    if label == TicketCategory.INCIDENT_COORDINATION.value:
        priority = TicketPriority.URGENT.value if "critical" in tag_text else TicketPriority.HIGH.value
        return (
            TicketCategory.INCIDENT_COORDINATION.value,
            priority,
            TicketTeam.ENGINEERING.value,
        )
    if label == TicketCategory.PRODUCT_BUG.value:
        priority = TicketPriority.URGENT.value if "critical" in tag_text else TicketPriority.HIGH.value
        return (TicketCategory.PRODUCT_BUG.value, priority, TicketTeam.ENGINEERING.value)
    if label == TicketCategory.BILLING_APPROVAL.value:
        return (
            TicketCategory.BILLING_APPROVAL.value,
            TicketPriority.HIGH.value,
            TicketTeam.BILLING_OPS.value,
        )
    if label == TicketCategory.BILLING_REFUND.value:
        priority = (
            TicketPriority.HIGH.value
            if tier == "enterprise" or any(tag in tag_text for tag in ["vip", "month-end", "reopen-risk"])
            else TicketPriority.MEDIUM.value
        )
        return (TicketCategory.BILLING_REFUND.value, priority, TicketTeam.BILLING_OPS.value)
    return (
        TicketCategory.ACCOUNT_ACCESS.value,
        TicketPriority.MEDIUM.value,
        TicketTeam.CUSTOMER_SUPPORT.value,
    )


def _priority_rank(ticket: dict, predicted_label: str) -> int:
    tag_text = " ".join(ticket.get("tags") or []).lower()
    if predicted_label in {
        TicketCategory.SECURITY_ACCOUNT_TAKEOVER.value,
        TicketCategory.SECURITY_ESCALATION.value,
    } or "security" in tag_text:
        return 0
    if predicted_label in {
        TicketCategory.PRODUCT_BUG.value,
        TicketCategory.INCIDENT_COORDINATION.value,
    } or "outage" in tag_text:
        return 1
    if predicted_label in {
        TicketCategory.BILLING_REFUND.value,
        TicketCategory.BILLING_APPROVAL.value,
    }:
        return 2
    return 3


def _default_reply(ticket: dict, category: str) -> str:
    if category == TicketCategory.BILLING_APPROVAL.value:
        return (
            "I am sorry for the billing disruption. We reviewed the account context and started "
            "the finance approval workflow for the refund. We will keep you updated as billing "
            "finalizes the review, and approved refunds typically land within 5-7 business days."
        )
    if category == TicketCategory.BILLING_REFUND.value:
        return (
            "I am sorry for the duplicate charge. We reviewed the billing context and have started "
            "the refund workflow. You should see the refund within 5-7 business days."
        )
    if category == TicketCategory.INCIDENT_COORDINATION.value:
        return (
            "I am sorry this is blocking your team. We created an incident and escalated this "
            "to engineering for investigation. Please share the workspace, browser, and approximate timestamp."
        )
    if category == TicketCategory.PRODUCT_BUG.value:
        return (
            "I am sorry this is blocking your work. We have opened an incident and escalated this "
            "to engineering for investigation. Please share the workspace, browser, and approximate timestamp."
        )
    if category == TicketCategory.SECURITY_ESCALATION.value:
        return (
            "I am sorry you are dealing with this. I have escalated this to Trust and Safety for "
            "urgent specialist review. Please do not share passwords or one-time codes, and continue "
            "with the secure recovery flow only."
        )
    if category == TicketCategory.SECURITY_ACCOUNT_TAKEOVER.value:
        return (
            "I am sorry you are dealing with this. I have escalated this to our Trust and Safety "
            "specialists. Please do not share passwords or one-time codes, and use the secure recovery flow."
        )
    return (
        "I am sorry you are having trouble accessing the account. Please use the secure password "
        "reset flow and let us know if access is still blocked afterward."
    )


def _default_escalation(ticket: dict, category: str) -> str:
    if category in {
        TicketCategory.SECURITY_ACCOUNT_TAKEOVER.value,
        TicketCategory.SECURITY_ESCALATION.value,
    }:
        return (
            f"Escalating {ticket['ticket_id']} to Trust and Safety. Subject: {ticket['subject']}. "
            "Keep MFA enabled and continue secure recovery only."
        )
    return (
        f"Escalating {ticket['ticket_id']} for specialist review. Subject: {ticket['subject']}. "
        "Include workspace, impact summary, browser, and timestamp in the incident context."
    )


def _task_specific_action(task_id: str, ticket: dict, state_payload: dict) -> dict | None:
    ticket_id = ticket["ticket_id"]
    tags = set(ticket.get("tags") or [])

    pending_events = state_payload.get("pending_events") or []
    if any(event.get("ticket_id") == ticket_id for event in pending_events):
        return {"action_type": ActionType.VIEW_TICKET.value, "ticket_id": ticket_id}

    if task_id in {"enterprise_refund_investigation", "refund_reopen_review"} or "reopen-risk" in tags:
        if not _has_action(state_payload, ActionType.LOOKUP_ACCOUNT.value, ticket_id):
            return {"action_type": ActionType.LOOKUP_ACCOUNT.value, "ticket_id": ticket_id, "app": EnterpriseApp.CRM_WORKSPACE.value}
        if not _has_action(state_payload, ActionType.CHECK_BILLING_STATUS.value, ticket_id):
            return {"action_type": ActionType.CHECK_BILLING_STATUS.value, "ticket_id": ticket_id, "app": EnterpriseApp.BILLING_SYSTEM.value}
        if not _has_action(state_payload, ActionType.SEARCH_POLICY.value, ticket_id):
            query = "enterprise refund approval thresholds" if task_id == "refund_reopen_review" or "reopen-risk" in tags else "duplicate charge refund workflow"
            return {"action_type": ActionType.SEARCH_POLICY.value, "ticket_id": ticket_id, "app": EnterpriseApp.POLICY_HUB.value, "message": query}

    if task_id in {"incident_coordination_outage", "escalation_rejection_recovery"} or "incident" in tags or "incident-follow-up" in tags:
        if not _has_action(state_payload, ActionType.LOOKUP_ACCOUNT.value, ticket_id):
            return {"action_type": ActionType.LOOKUP_ACCOUNT.value, "ticket_id": ticket_id, "app": EnterpriseApp.CRM_WORKSPACE.value}
        if not _has_action(state_payload, ActionType.SEARCH_POLICY.value, ticket_id):
            query = "escalation packet review policy" if task_id == "escalation_rejection_recovery" or "escalation-review" in tags else "product outage escalation checklist"
            return {"action_type": ActionType.SEARCH_POLICY.value, "ticket_id": ticket_id, "app": EnterpriseApp.POLICY_HUB.value, "message": query}
        if not _has_action(state_payload, ActionType.CREATE_INCIDENT.value, ticket_id):
            return {
                "action_type": ActionType.CREATE_INCIDENT.value,
                "ticket_id": ticket_id,
                "app": EnterpriseApp.INCIDENT_TRACKER.value,
                "team": TicketTeam.ENGINEERING.value,
                "severity": IncidentSeverity.HIGH.value,
                "message": f"Incident created for {ticket_id}: {ticket['subject']}",
            }

    if task_id in {"executive_security_escalation"} or "trust" in tags or "executive" in tags:
        if not _has_action(state_payload, ActionType.LOOKUP_ACCOUNT.value, ticket_id):
            return {"action_type": ActionType.LOOKUP_ACCOUNT.value, "ticket_id": ticket_id, "app": EnterpriseApp.CRM_WORKSPACE.value}
        if not _has_action(state_payload, ActionType.SEARCH_POLICY.value, ticket_id):
            return {"action_type": ActionType.SEARCH_POLICY.value, "ticket_id": ticket_id, "app": EnterpriseApp.POLICY_HUB.value, "message": "account takeover response policy"}
        if not _has_action(state_payload, ActionType.ADD_INTERNAL_NOTE.value, ticket_id):
            return {
                "action_type": ActionType.ADD_INTERNAL_NOTE.value,
                "ticket_id": ticket_id,
                "app": EnterpriseApp.TRUST_SAFETY_CONSOLE.value,
                "message": "Trust escalation note captured with executive security indicators.",
            }

    if task_id == "followup_reprioritization_queue" or "responds-fast" in tags:
        if not _has_action(state_payload, ActionType.REQUEST_INFO.value, ticket_id):
            return {
                "action_type": ActionType.REQUEST_INFO.value,
                "ticket_id": ticket_id,
                "message": "Please share the workspace, browser, and approximate timestamp so we can investigate the outage.",
            }

    return None


def _build_policy_action(
    observation_payload: dict,
    state_payload: dict,
    predictor: Callable[[str], str],
) -> SupportTriageAction:
    tickets = [
        ticket
        for ticket in state_payload.get("tickets", [])
        if ticket.get("current_status") not in {TicketStatus.RESOLVED.value, TicketStatus.ESCALATED.value}
    ]
    if not tickets:
        return SupportTriageAction(action_type=ActionType.FINISH)

    scored_tickets = []
    for ticket in tickets:
        label = predictor(_ticket_text(ticket))
        scored_tickets.append((_priority_rank(ticket, label), ticket, label))
    scored_tickets.sort(key=lambda item: item[0])

    task_id = state_payload.get("task_id") or observation_payload.get("task", {}).get("task_id")

    for _, ticket, predicted_label in scored_tickets:
        task_action = _task_specific_action(task_id, ticket, state_payload)
        if task_action:
            return SupportTriageAction(**task_action)

        category, priority, team = _route_for_label(predicted_label, ticket)
        if (
            ticket.get("current_category") != category
            or ticket.get("current_priority") != priority
            or ticket.get("assigned_team") != team
        ):
            return SupportTriageAction(
                action_type=ActionType.CLASSIFY_TICKET,
                ticket_id=ticket["ticket_id"],
                category=TicketCategory(category),
                priority=TicketPriority(priority),
                team=TicketTeam(team),
            )

        if not ticket.get("outbound_messages"):
            return SupportTriageAction(
                action_type=ActionType.DRAFT_REPLY,
                ticket_id=ticket["ticket_id"],
                message=_default_reply(ticket, category),
            )

        if category in {
            TicketCategory.BILLING_REFUND.value,
            TicketCategory.BILLING_APPROVAL.value,
        }:
            return SupportTriageAction(
                action_type=ActionType.RESOLVE_TICKET,
                ticket_id=ticket["ticket_id"],
                resolution_code=ResolutionCode.REFUND_SUBMITTED,
            )

        if category == TicketCategory.ACCOUNT_ACCESS.value:
            return SupportTriageAction(
                action_type=ActionType.RESOLVE_TICKET,
                ticket_id=ticket["ticket_id"],
                resolution_code=ResolutionCode.PASSWORD_RESET_SENT,
            )

        return SupportTriageAction(
            action_type=ActionType.ESCALATE_TICKET,
            ticket_id=ticket["ticket_id"],
            team=TicketTeam(team),
            message=_default_escalation(ticket, category),
        )

    return SupportTriageAction(action_type=ActionType.FINISH)


def _evaluate_environment_policy(
    predictor: Callable[[str], str],
    seeds: list[int],
    tasks: list[str],
) -> dict:
    runs = []
    for task_id in tasks:
        for seed in seeds:
            env = SupportTriageSimulator()
            observation = env.reset(task_id=task_id, seed=seed)
            done = False
            while not done:
                action = _build_policy_action(
                    observation.model_dump(mode="json"),
                    env.state().model_dump(mode="json"),
                    predictor,
                )
                observation, _, done, _ = env.step(action)
            final_state = env.state()
            runs.append(
                {
                    "task_id": task_id,
                    "seed": seed,
                    "score": final_state.final_score,
                    "steps": final_state.step_count,
                }
            )
    mean_score = sum(run["score"] for run in runs) / max(1, len(runs))
    return {"mean_score": round(mean_score, 4), "runs": runs}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--synthetic-examples-per-task", type=int, default=500)
    parser.add_argument("--synthetic-seed", type=int, default=7)
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument("--eval-seeds", default="7,11")
    parser.add_argument("--model-output", default="outputs/triageos_classifier.pkl")
    parser.add_argument("--report-output", default="outputs/train_eval_report.json")
    parser.add_argument(
        "--customer-support-csv",
        default=_repo_dataset_file("customer_support_tickets.csv"),
    )
    parser.add_argument(
        "--customer-support-200k-csv",
        default=_repo_dataset_file("customer_support_tickets_200k.csv"),
    )
    parser.add_argument(
        "--banking-csv",
        default=_repo_dataset_file("complaints.csv"),
    )
    parser.add_argument(
        "--complaint-data-csv",
        default=_repo_dataset_file("complaint_data.csv"),
    )
    args = parser.parse_args()

    rows = build_combined_training_dataset(
        synthetic_examples_per_task=args.synthetic_examples_per_task,
        synthetic_seed=args.synthetic_seed,
        customer_support_csv=args.customer_support_csv,
        customer_support_200k_csv=args.customer_support_200k_csv,
        banking_csv=args.banking_csv,
        complaint_data_csv=args.complaint_data_csv,
    )
    texts = [row["text"] for row in rows]
    labels = [row["label"] for row in rows]
    majority_label = _majority_label(labels)

    x_train, x_test, y_train, y_test = train_test_split(
        texts,
        labels,
        test_size=args.test_size,
        random_state=args.random_state,
        stratify=labels,
    )

    heuristic_predictions = [_predict_heuristic(text, majority_label) for text in x_test]
    heuristic_accuracy = accuracy_score(y_test, heuristic_predictions)

    model = Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=40000)),
            ("clf", LogisticRegression(max_iter=600, class_weight="balanced")),
        ]
    )
    model.fit(x_train, y_train)
    trained_predictions = model.predict(x_test)
    trained_accuracy = accuracy_score(y_test, trained_predictions)

    eval_seeds = [int(seed.strip()) for seed in args.eval_seeds.split(",") if seed.strip()]
    heuristic_env = _evaluate_environment_policy(
        predictor=lambda text: _predict_heuristic(text, majority_label),
        seeds=eval_seeds,
        tasks=DEFAULT_TASKS,
    )
    trained_env = _evaluate_environment_policy(
        predictor=lambda text: str(model.predict([text])[0]),
        seeds=eval_seeds,
        tasks=DEFAULT_TASKS,
    )

    model_output = Path(args.model_output)
    model_output.parent.mkdir(parents=True, exist_ok=True)
    with model_output.open("wb") as handle:
        pickle.dump(model, handle)

    payload = {
        "rows": len(rows),
        "labels": summarize_labels(rows),
        "classification": {
            "heuristic_accuracy": round(float(heuristic_accuracy), 4),
            "trained_accuracy": round(float(trained_accuracy), 4),
            "accuracy_delta": round(float(trained_accuracy - heuristic_accuracy), 4),
            "trained_report": classification_report(y_test, trained_predictions, output_dict=True),
        },
        "environment": {
            "heuristic_mean_score": heuristic_env["mean_score"],
            "trained_mean_score": trained_env["mean_score"],
            "score_delta": round(trained_env["mean_score"] - heuristic_env["mean_score"], 4),
            "heuristic_runs": heuristic_env["runs"],
            "trained_runs": trained_env["runs"],
        },
        "artifacts": {
            "model_output": str(model_output),
        },
    }

    output_path = Path(args.report_output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
