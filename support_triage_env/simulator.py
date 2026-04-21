from __future__ import annotations

import copy
import random
import uuid
from typing import Any

from support_triage_env.graders import BaseTaskGrader, build_graders
from support_triage_env.models import (
    ActionLogEntry,
    ActionType,
    EnterpriseApp,
    EnterpriseAppSnapshot,
    GradingSnapshot,
    IncidentRecord,
    IncidentSeverity,
    QueueTicketView,
    SupportTriageAction,
    SupportTriageObservation,
    SupportTriageReward,
    SupportTriageState,
    TaskCard,
    TicketCategory,
    TicketMessage,
    TicketRecord,
    TicketStatus,
    WorldEvent,
)
from support_triage_env.tasks import TaskScenario, build_task_scenario, task_ids


def _join_text(items: list[str]) -> str:
    return "\n".join(items)


_REQUIRED_TOOL_APPS: dict[ActionType, EnterpriseApp] = {
    ActionType.LOOKUP_ACCOUNT: EnterpriseApp.CRM_WORKSPACE,
    ActionType.CHECK_BILLING_STATUS: EnterpriseApp.BILLING_SYSTEM,
    ActionType.SEARCH_POLICY: EnterpriseApp.POLICY_HUB,
    ActionType.CREATE_INCIDENT: EnterpriseApp.INCIDENT_TRACKER,
}

_ALLOWED_NOTE_APPS = {
    EnterpriseApp.TICKETING_CONSOLE,
    EnterpriseApp.TRUST_SAFETY_CONSOLE,
    EnterpriseApp.INCIDENT_TRACKER,
}


class SupportTriageSimulator:
    """Local Gym-style simulator with step/reset/state APIs."""

    def __init__(self):
        self._rng = random.Random(0)
        self._task_order = task_ids()
        self._task_index = 0
        self._scenario: TaskScenario | None = None
        self._grader: BaseTaskGrader | None = None
        self._last_reward = SupportTriageReward(
            value=0.0,
            task_score=0.01,
            score_delta=0.0,
            components={},
            penalties={},
            rationale=[],
        )
        self._state = SupportTriageState()

    def reset(
        self,
        seed: int | None = None,
        episode_id: str | None = None,
        task_id: str | None = None,
        **_: Any,
    ) -> SupportTriageObservation:
        if seed is not None:
            self._rng = random.Random(seed)

        if task_id is None:
            task_id = self._task_order[self._task_index % len(self._task_order)]
            self._task_index += 1

        if task_id not in self._task_order:
            raise ValueError(f"Unknown task_id '{task_id}'")

        scenario = build_task_scenario(task_id, self._rng)
        self._scenario = scenario
        self._grader = build_graders({task_id: scenario})[task_id]
        initial_state = SupportTriageState(
            episode_id=episode_id or str(uuid.uuid4()),
            step_count=0,
            task_id=scenario.card.task_id,
            difficulty=scenario.card.difficulty,
            objective=scenario.card.objective,
            max_steps=scenario.card.max_steps,
            focused_ticket_id=None,
            accessible_apps=list(scenario.accessible_apps),
            tickets=[copy.deepcopy(ticket) for ticket in scenario.tickets],
            customer_accounts=[copy.deepcopy(account) for account in scenario.customer_accounts],
            billing_accounts=[copy.deepcopy(account) for account in scenario.billing_accounts],
            incidents=[copy.deepcopy(incident) for incident in scenario.incidents],
            policy_articles=[copy.deepcopy(article) for article in scenario.policy_articles],
            world_summary=list(scenario.world_summary),
            pending_events=[],
            recent_events=[],
            last_tool_result=None,
            action_history=[],
            cumulative_reward=0.0,
            final_score=0.01,
            done=False,
            progress=GradingSnapshot(score=0.01),
        )
        initial_grade = self._grader.grade(initial_state)
        initial_payload = initial_state.model_dump()
        initial_payload["final_score"] = initial_grade.score
        initial_payload["progress"] = initial_grade
        self._state = SupportTriageState(**initial_payload)
        self._last_reward = SupportTriageReward(
            value=0.0,
            task_score=initial_grade.score,
            score_delta=0.0,
            components={},
            penalties={},
            rationale=["Episode reset."],
        )
        return self._build_observation(
            scenario,
            last_action_result="New queue loaded. Review the tickets and begin triage.",
            reward=self._last_reward,
        )

    def step(
        self, action: SupportTriageAction
    ) -> tuple[SupportTriageObservation, SupportTriageReward, bool, dict[str, Any]]:
        if not self._state.task_id:
            raise RuntimeError("Call reset() before step().")
        if self._scenario is None or self._grader is None:
            raise RuntimeError("No active scenario loaded. Call reset() before step().")

        scenario = self._scenario
        previous_score = self._state.progress.score
        invalid_reasons: list[str] = []
        repeated_penalty = 0.0
        result_message = ""
        tool_result: dict[str, Any] | None = None

        if self._state.done:
            reward = SupportTriageReward(
                value=0.0,
                task_score=self._state.final_score,
                score_delta=0.0,
                components={},
                penalties={},
                rationale=["Episode already finished. Call reset() to start again."],
            )
            observation = self._build_observation(
                scenario,
                last_action_result="Episode already finished.",
                reward=reward,
            )
            return observation, reward, True, {"state": self.state().model_dump()}

        self._state.step_count += 1
        self._state.recent_events = []
        applied_event_messages = self._apply_pending_events()

        last_entry = self._state.action_history[-1] if self._state.action_history else None
        if (
            last_entry
            and last_entry.action_type == action.action_type
            and last_entry.ticket_id == action.ticket_id
        ):
            repeated_penalty = 0.03

        if action.action_type in {
            ActionType.VIEW_TICKET,
            ActionType.CLASSIFY_TICKET,
            ActionType.DRAFT_REPLY,
            ActionType.REQUEST_INFO,
            ActionType.ESCALATE_TICKET,
            ActionType.RESOLVE_TICKET,
            ActionType.LOOKUP_ACCOUNT,
            ActionType.CHECK_BILLING_STATUS,
            ActionType.SEARCH_POLICY,
            ActionType.CREATE_INCIDENT,
            ActionType.ADD_INTERNAL_NOTE,
        }:
            ticket = self._find_ticket(action.ticket_id, invalid_reasons)
        else:
            ticket = None

        self._validate_action_app(action, invalid_reasons)

        if invalid_reasons:
            result_message = " ".join(invalid_reasons)
        elif action.action_type == ActionType.VIEW_TICKET and ticket is not None:
            self._state.focused_ticket_id = ticket.ticket_id
            result_message = f"Opened {ticket.ticket_id}: {ticket.subject}"
        elif action.action_type == ActionType.CLASSIFY_TICKET and ticket is not None:
            if action.category is None or action.priority is None or action.team is None:
                invalid_reasons.append(
                    "classify_ticket requires category, priority, and team."
                )
            else:
                ticket.current_category = action.category
                ticket.current_priority = action.priority
                ticket.assigned_team = action.team
                ticket.current_status = TicketStatus.IN_PROGRESS
                self._state.focused_ticket_id = ticket.ticket_id
                result_message = (
                    f"{ticket.ticket_id} classified as {action.category.value}, "
                    f"{action.priority.value}, assigned to {action.team.value}."
                )
        elif action.action_type == ActionType.DRAFT_REPLY and ticket is not None:
            if not action.message:
                invalid_reasons.append("draft_reply requires a customer-facing message.")
            else:
                ticket.outbound_messages.append(action.message)
                ticket.messages.append(
                    TicketMessage(role="agent", content=action.message)
                )
                ticket.current_status = TicketStatus.IN_PROGRESS
                self._state.focused_ticket_id = ticket.ticket_id
                result_message = f"Saved outbound reply for {ticket.ticket_id}."
        elif action.action_type == ActionType.REQUEST_INFO and ticket is not None:
            if not action.message:
                invalid_reasons.append("request_info requires the requested details.")
            else:
                ticket.requested_information.append(action.message)
                ticket.outbound_messages.append(action.message)
                ticket.messages.append(
                    TicketMessage(role="agent", content=action.message)
                )
                ticket.current_status = TicketStatus.WAITING_FOR_CUSTOMER
                result_message = f"Requested additional information from {ticket.ticket_id}."
        elif action.action_type == ActionType.ESCALATE_TICKET and ticket is not None:
            if action.team is None:
                invalid_reasons.append("escalate_ticket requires a destination team.")
            else:
                ticket.assigned_team = action.team
                ticket.current_status = TicketStatus.ESCALATED
                if action.message:
                    ticket.internal_notes.append(action.message)
                self._state.focused_ticket_id = ticket.ticket_id
                result_message = f"Escalated {ticket.ticket_id} to {action.team.value}."
        elif action.action_type == ActionType.RESOLVE_TICKET and ticket is not None:
            if action.resolution_code is None:
                invalid_reasons.append("resolve_ticket requires a resolution_code.")
            else:
                ticket.current_status = TicketStatus.RESOLVED
                ticket.resolution_code = action.resolution_code
                if action.message:
                    ticket.internal_notes.append(action.message)
                self._state.focused_ticket_id = ticket.ticket_id
                result_message = (
                    f"Resolved {ticket.ticket_id} with {action.resolution_code.value}."
                )
        elif action.action_type == ActionType.LOOKUP_ACCOUNT and ticket is not None:
            account = self._find_account(ticket.account_id)
            if account is None:
                invalid_reasons.append("No linked CRM account was found for this ticket.")
            else:
                self._state.focused_ticket_id = ticket.ticket_id
                tool_result = {
                    "app": EnterpriseApp.CRM_WORKSPACE.value,
                    "account_id": account.account_id,
                    "customer_tier": account.customer_tier,
                    "plan_name": account.plan_name,
                    "lifecycle_stage": account.lifecycle_stage,
                    "security_flags": list(account.security_flags),
                    "support_history": list(account.support_history),
                }
                result_message = f"Reviewed CRM account {account.account_id} for {ticket.ticket_id}."
        elif action.action_type == ActionType.CHECK_BILLING_STATUS and ticket is not None:
            billing_account = self._find_billing_account(ticket.billing_account_id)
            if billing_account is None:
                invalid_reasons.append("No linked billing account was found for this ticket.")
            else:
                self._state.focused_ticket_id = ticket.ticket_id
                tool_result = {
                    "app": EnterpriseApp.BILLING_SYSTEM.value,
                    "billing_account_id": billing_account.billing_account_id,
                    "invoice_id": billing_account.invoice_id,
                    "payment_status": billing_account.payment_status,
                    "duplicate_charge_detected": billing_account.duplicate_charge_detected,
                    "refund_eligibility": billing_account.refund_eligibility,
                    "pending_refund_amount_usd": billing_account.pending_refund_amount_usd,
                    "ledger_notes": list(billing_account.ledger_notes),
                }
                result_message = (
                    f"Checked billing account {billing_account.billing_account_id} for {ticket.ticket_id}."
                )
        elif action.action_type == ActionType.SEARCH_POLICY and ticket is not None:
            article = self._find_policy_article(action.message or "", ticket)
            if article is None:
                invalid_reasons.append("No relevant policy article was found for this query.")
            else:
                self._state.focused_ticket_id = ticket.ticket_id
                tool_result = {
                    "app": EnterpriseApp.POLICY_HUB.value,
                    "article_id": article.article_id,
                    "title": article.title,
                    "summary": article.summary,
                    "tags": list(article.tags),
                }
                result_message = f"Reviewed policy article {article.article_id} for {ticket.ticket_id}."
        elif action.action_type == ActionType.CREATE_INCIDENT and ticket is not None:
            if action.team is None:
                invalid_reasons.append("create_incident requires an owning team.")
            else:
                incident_id = action.target_id or f"INC-{self._rng.randint(1000, 9999)}"
                incident = IncidentRecord(
                    incident_id=incident_id,
                    ticket_id=ticket.ticket_id,
                    title=action.message or ticket.subject,
                    severity=action.severity or self._infer_incident_severity(ticket),
                    owning_team=action.team,
                    summary=action.message or f"Incident created from ticket {ticket.ticket_id}.",
                )
                self._state.incidents.append(incident)
                ticket.linked_incident_id = incident.incident_id
                self._state.focused_ticket_id = ticket.ticket_id
                tool_result = {
                    "app": EnterpriseApp.INCIDENT_TRACKER.value,
                    "incident_id": incident.incident_id,
                    "severity": incident.severity.value,
                    "owning_team": incident.owning_team.value,
                }
                result_message = f"Created incident {incident.incident_id} for {ticket.ticket_id}."
        elif action.action_type == ActionType.ADD_INTERNAL_NOTE and ticket is not None:
            if not action.message:
                invalid_reasons.append("add_internal_note requires a note message.")
            else:
                note_prefix = action.app.value if action.app is not None else "internal"
                ticket.internal_notes.append(f"[{note_prefix}] {action.message}")
                self._state.focused_ticket_id = ticket.ticket_id
                tool_result = {
                    "app": (action.app or EnterpriseApp.TICKETING_CONSOLE).value,
                    "note_saved": True,
                    "ticket_id": ticket.ticket_id,
                }
                result_message = f"Added internal note to {ticket.ticket_id}."
        elif action.action_type == ActionType.FINISH:
            result_message = "Episode finished by agent."
            self._state.done = True
        else:
            invalid_reasons.append(f"Unsupported action {action.action_type.value}.")

        if not invalid_reasons:
            self._maybe_schedule_delayed_outcomes(action, ticket)

        if invalid_reasons:
            result_message = " ".join(invalid_reasons)
        elif applied_event_messages:
            result_message = " ".join([*applied_event_messages, result_message]).strip()

        if tool_result is not None:
            self._state.last_tool_result = tool_result

        self._state.action_history.append(
            ActionLogEntry(
                step_number=self._state.step_count,
                action_type=action.action_type,
                ticket_id=action.ticket_id,
                app=action.app,
                target_id=action.target_id,
                summary=result_message,
            )
        )

        self._advance_world_state(action)

        grade = self._grader.grade(self._state)
        self._state.progress = grade
        self._state.final_score = grade.score

        invalid_penalty = 0.07 if invalid_reasons else 0.0
        step_penalty = scenario.card.step_penalty
        reward_value = round(
            (grade.score - previous_score) - step_penalty - repeated_penalty - invalid_penalty,
            4,
        )
        reward = SupportTriageReward(
            value=reward_value,
            task_score=grade.score,
            score_delta=round(grade.score - previous_score, 4),
            components=grade.components,
            penalties={
                **grade.penalties,
                "step_cost": step_penalty,
                **({"repeat_action": repeated_penalty} if repeated_penalty else {}),
                **({"invalid_action": invalid_penalty} if invalid_penalty else {}),
            },
            rationale=[
                result_message,
                *grade.violations,
                *([] if not invalid_reasons else invalid_reasons),
            ],
        )
        self._last_reward = reward

        if self._state.step_count >= scenario.card.max_steps:
            self._state.done = True
            result_message += " Maximum step count reached."

        self._state.cumulative_reward = round(
            self._state.cumulative_reward + reward.value, 4
        )

        observation = self._build_observation(
            scenario,
            last_action_result=result_message,
            reward=reward,
        )
        info = {
            "reward": reward.model_dump(),
            "grading": grade.model_dump(),
            "state": self.state().model_dump(),
        }
        return observation, reward, self._state.done, info

    def state(self) -> SupportTriageState:
        return self._state.model_copy(deep=True)

    def _validate_action_app(
        self,
        action: SupportTriageAction,
        invalid_reasons: list[str],
    ) -> None:
        if action.app is not None and action.app not in self._state.accessible_apps:
            invalid_reasons.append(
                f"{action.app.value} is not available in this task environment."
            )
            return

        required_app = _REQUIRED_TOOL_APPS.get(action.action_type)
        if required_app is not None:
            if action.app is None:
                invalid_reasons.append(
                    f"{action.action_type.value} requires app={required_app.value}."
                )
            elif action.app != required_app:
                invalid_reasons.append(
                    f"{action.action_type.value} must be run in {required_app.value}, not {action.app.value}."
                )
            return

        if action.action_type == ActionType.ADD_INTERNAL_NOTE:
            if action.app is None:
                invalid_reasons.append(
                    "add_internal_note requires an app context such as ticketing_console or trust_safety_console."
                )
            elif action.app not in _ALLOWED_NOTE_APPS:
                allowed_apps = ", ".join(
                    app.value for app in sorted(_ALLOWED_NOTE_APPS, key=lambda app: app.value)
                )
                invalid_reasons.append(
                    f"add_internal_note only supports these apps: {allowed_apps}."
                )

    def _find_ticket(
        self, ticket_id: str | None, invalid_reasons: list[str]
    ) -> TicketRecord | None:
        if not ticket_id:
            invalid_reasons.append("This action requires a ticket_id.")
            return None
        for ticket in self._state.tickets:
            if ticket.ticket_id == ticket_id:
                return ticket
        invalid_reasons.append(f"Unknown ticket_id '{ticket_id}'.")
        return None

    def _find_account(self, account_id: str | None):
        if not account_id:
            return None
        for account in self._state.customer_accounts:
            if account.account_id == account_id:
                return account
        return None

    def _find_billing_account(self, billing_account_id: str | None):
        if not billing_account_id:
            return None
        for billing_account in self._state.billing_accounts:
            if billing_account.billing_account_id == billing_account_id:
                return billing_account
        return None

    def _find_policy_article(self, query: str, ticket: TicketRecord):
        normalized_query = " ".join(
            part.lower()
            for part in [query, ticket.subject, " ".join(ticket.tags)]
            if part
        )
        matches = []
        for article in self._state.policy_articles:
            haystack = " ".join([article.title, article.summary, article.content, *article.tags]).lower()
            score = sum(1 for token in normalized_query.split() if token and token in haystack)
            if score > 0:
                matches.append((score, article))
        if matches:
            matches.sort(key=lambda item: item[0], reverse=True)
            return matches[0][1]
        return self._state.policy_articles[0] if self._state.policy_articles else None

    def _infer_incident_severity(self, ticket: TicketRecord) -> IncidentSeverity:
        text = f"{ticket.subject} {' '.join(message.content for message in ticket.messages)}".lower()
        if any(token in text for token in ["urgent", "ceo", "compromised", "security"]):
            return IncidentSeverity.CRITICAL
        if any(token in text for token in ["outage", "500 error", "502 error", "blocked"]):
            return IncidentSeverity.HIGH
        return IncidentSeverity.MEDIUM

    def _action_taken(
        self, action_type: ActionType, ticket_id: str | None = None
    ) -> bool:
        return any(
            entry.action_type == action_type
            and (ticket_id is None or entry.ticket_id == ticket_id)
            for entry in self._state.action_history
        )

    def _schedule_event(
        self,
        ticket_id: str,
        event_type: str,
        message: str,
        trigger_step: int | None = None,
    ) -> None:
        scheduled_step = trigger_step if trigger_step is not None else self._state.step_count + 1
        if any(
            event.ticket_id == ticket_id
            and event.event_type == event_type
            and event.status == "pending"
            for event in self._state.pending_events
        ):
            return
        self._state.pending_events.append(
            WorldEvent(
                event_id=f"EVT-{self._rng.randint(1000, 9999)}",
                ticket_id=ticket_id,
                event_type=event_type,
                trigger_step=scheduled_step,
                message=message,
            )
        )

    def _tag_value(self, ticket: TicketRecord, prefix: str) -> str | None:
        for tag in ticket.tags:
            if tag.startswith(prefix):
                return tag.split(":", 1)[1].strip()
        return None

    def _build_followup_message(self, ticket: TicketRecord) -> str:
        workspace = self._tag_value(ticket, "followup_workspace:")
        browser = self._tag_value(ticket, "followup_browser:")
        time_reference = self._tag_value(ticket, "followup_time:")
        details = [
            part
            for part in [
                f"workspace {workspace}" if workspace else None,
                f"browser {browser}" if browser else None,
                f"around {time_reference}" if time_reference else None,
            ]
            if part
        ]
        if details:
            return "Following up with the details you requested: " + ", ".join(details) + "."
        return "Following up with the extra details you requested for the ticket."

    def _apply_pending_events(self) -> list[str]:
        applied_messages: list[str] = []
        for event in self._state.pending_events:
            if event.status != "pending" or event.trigger_step > self._state.step_count:
                continue
            ticket = next(
                (candidate for candidate in self._state.tickets if candidate.ticket_id == event.ticket_id),
                None,
            )
            if ticket is None:
                event.status = "applied"
                continue

            if event.event_type == "escalation_rejected":
                if ticket.current_status == TicketStatus.ESCALATED:
                    ticket.current_status = TicketStatus.IN_PROGRESS
                ticket.internal_notes.append(f"[system] {event.message}")
                ticket.messages.append(TicketMessage(role="internal", content=event.message))
            elif event.event_type == "ticket_reopened":
                ticket.current_status = TicketStatus.OPEN
                ticket.resolution_code = None
                ticket.messages.append(TicketMessage(role="customer", content=event.message))
                ticket.internal_notes.append("[system] Ticket reopened after downstream review.")
            elif event.event_type == "customer_follow_up":
                ticket.messages.append(TicketMessage(role="customer", content=event.message))
                if ticket.current_status == TicketStatus.WAITING_FOR_CUSTOMER:
                    ticket.current_status = TicketStatus.OPEN
            elif event.event_type == "incident_update":
                ticket.internal_notes.append(f"[incident_tracker] {event.message}")
            elif event.event_type == "policy_drift":
                ticket.internal_notes.append(f"[policy_hub] {event.message}")

            event.status = "applied"
            applied_messages.append(event.message)
            self._state.recent_events.append(event.model_copy(deep=True))
        return applied_messages

    def _missing_escalation_requirements(
        self, ticket: TicketRecord, expectation_text: str
    ) -> list[str]:
        if self._scenario is None:
            return []
        expectation = self._scenario.expectations.get(ticket.ticket_id)
        if expectation is None:
            return []
        return [
            phrase
            for phrase in expectation.escalation_phrase_requirements
            if phrase and phrase.lower() not in expectation_text.lower()
        ]

    def _maybe_schedule_delayed_outcomes(
        self, action: SupportTriageAction, ticket: TicketRecord | None
    ) -> None:
        if ticket is None:
            return

        if (
            action.action_type == ActionType.ESCALATE_TICKET
            and "escalation-review" in ticket.tags
        ):
            escalation_text = _join_text(ticket.internal_notes)
            missing_requirements = self._missing_escalation_requirements(ticket, escalation_text)
            if (
                ticket.linked_incident_id is None
                or not self._action_taken(ActionType.SEARCH_POLICY, ticket.ticket_id)
                or len(missing_requirements) >= 2
            ):
                self._schedule_event(
                    ticket.ticket_id,
                    "escalation_rejected",
                    (
                        "Engineering rejected the escalation packet. Add an incident link plus "
                        "workspace, timing, and repro detail before resubmitting."
                    ),
                )

        if (
            action.action_type == ActionType.RESOLVE_TICKET
            and "reopen-risk" in ticket.tags
        ):
            billing_review_complete = self._action_taken(
                ActionType.CHECK_BILLING_STATUS, ticket.ticket_id
            )
            policy_review_complete = self._action_taken(
                ActionType.SEARCH_POLICY, ticket.ticket_id
            )
            if not (billing_review_complete and policy_review_complete):
                billing_account = self._find_billing_account(ticket.billing_account_id)
                if billing_account is not None:
                    billing_account.payment_status = "pending_review"
                    billing_account.refund_eligibility = "needs_review"
                    billing_account.ledger_notes.append(
                        "Refund reopened because finance approval context was missing."
                    )
                self._schedule_event(
                    ticket.ticket_id,
                    "ticket_reopened",
                    (
                        "Finance reopened the refund because the current approval workflow was not "
                        "confirmed. Please review billing and policy before resolving again."
                    ),
                )

        if (
            action.action_type == ActionType.REQUEST_INFO
            and "responds-fast" in ticket.tags
        ):
            self._schedule_event(
                ticket.ticket_id,
                "customer_follow_up",
                self._build_followup_message(ticket),
            )

        if (
            action.action_type == ActionType.CREATE_INCIDENT
            and "incident-follow-up" in ticket.tags
        ):
            self._schedule_event(
                ticket.ticket_id,
                "incident_update",
                (
                    "Engineering accepted the incident and asked support to keep the customer updated "
                    "with workspace, timing, and browser context."
                ),
            )

    def _advance_world_state(self, action: SupportTriageAction) -> None:
        acted_ticket_id = action.ticket_id

        for ticket in self._state.tickets:
            if ticket.current_status in {TicketStatus.RESOLVED, TicketStatus.ESCALATED}:
                continue
            if ticket.ticket_id == acted_ticket_id:
                continue
            if ticket.sla_hours_remaining is not None:
                ticket.sla_hours_remaining -= 1

        for incident in self._state.incidents:
            linked_ticket = next(
                (
                    ticket
                    for ticket in self._state.tickets
                    if ticket.ticket_id == incident.ticket_id
                    or ticket.linked_incident_id == incident.incident_id
                ),
                None,
            )
            if linked_ticket is None:
                continue
            if linked_ticket.current_status == TicketStatus.RESOLVED:
                incident.status = "resolved"
            elif linked_ticket.current_status == TicketStatus.ESCALATED:
                incident.status = "investigating"
            elif linked_ticket.current_status in {
                TicketStatus.IN_PROGRESS,
                TicketStatus.WAITING_FOR_CUSTOMER,
            }:
                incident.status = "open"

        for account in self._state.customer_accounts:
            related_tickets = [
                ticket
                for ticket in self._state.tickets
                if ticket.ticket_id in account.open_ticket_ids
            ]
            active_tickets = [
                ticket
                for ticket in related_tickets
                if ticket.current_status
                not in {TicketStatus.RESOLVED, TicketStatus.ESCALATED}
            ]
            if any(
                self._is_security_ticket(ticket)
                and ticket.sla_hours_remaining is not None
                and ticket.sla_hours_remaining <= 1
                for ticket in active_tickets
            ):
                account.lifecycle_stage = "security_hold"
            elif any(
                self._is_product_incident_ticket(ticket)
                or (
                    ticket.sla_hours_remaining is not None
                    and ticket.sla_hours_remaining <= 2
                )
                for ticket in active_tickets
            ):
                account.lifecycle_stage = "at_risk"
            elif any(
                ticket.current_status == TicketStatus.ESCALATED for ticket in related_tickets
            ):
                account.lifecycle_stage = "under_review"
            else:
                account.lifecycle_stage = "active"

        self._refresh_world_summary()

    def _is_security_ticket(self, ticket: TicketRecord) -> bool:
        text = " ".join([ticket.subject, *ticket.tags]).lower()
        return (
            ticket.current_category == TicketCategory.SECURITY_ACCOUNT_TAKEOVER
            or "security" in text
            or "comprom" in text
            or "mfa" in text
            or "executive" in text
        )

    def _is_product_incident_ticket(self, ticket: TicketRecord) -> bool:
        text = " ".join([ticket.subject, *ticket.tags]).lower()
        return (
            ticket.current_category == TicketCategory.PRODUCT_BUG
            or "outage" in text
            or "incident" in text
            or "export" in text
            or "500" in text
            or "502" in text
        )

    def _refresh_world_summary(self) -> None:
        unresolved = [
            ticket
            for ticket in self._state.tickets
            if ticket.current_status not in {TicketStatus.RESOLVED, TicketStatus.ESCALATED}
        ]
        escalated = [
            ticket for ticket in self._state.tickets if ticket.current_status == TicketStatus.ESCALATED
        ]
        breached = [
            ticket
            for ticket in unresolved
            if ticket.sla_hours_remaining is not None and ticket.sla_hours_remaining <= 0
        ]
        at_risk_accounts = [
            account
            for account in self._state.customer_accounts
            if account.lifecycle_stage in {"at_risk", "security_hold"}
        ]
        active_incidents = [
            incident
            for incident in self._state.incidents
            if incident.status != "resolved"
        ]

        summary = [
            (
                f"Queue status: {len(unresolved)} active, {len(escalated)} escalated, "
                f"{sum(1 for ticket in self._state.tickets if ticket.current_status == TicketStatus.RESOLVED)} resolved."
            ),
            (
                f"SLA watchlist: {len(breached)} breached, "
                f"{sum(1 for ticket in unresolved if ticket.sla_hours_remaining is not None and ticket.sla_hours_remaining <= 2)} near breach."
            ),
            (
                f"Enterprise systems: {len(active_incidents)} active incidents, "
                f"{len(at_risk_accounts)} accounts in at-risk or security-hold states."
            ),
        ]
        if any(event.status == "pending" for event in self._state.pending_events):
            summary.append(
                f"Pending events: {sum(1 for event in self._state.pending_events if event.status == 'pending')} downstream updates queued."
            )
        self._state.world_summary = summary

    def _build_observation(
        self,
        scenario: TaskScenario,
        last_action_result: str,
        reward: SupportTriageReward,
    ) -> SupportTriageObservation:
        focused_ticket = None
        if self._state.focused_ticket_id:
            for ticket in self._state.tickets:
                if ticket.ticket_id == self._state.focused_ticket_id:
                    focused_ticket = ticket.model_copy(deep=True)
                    break

        return SupportTriageObservation(
            done=self._state.done,
            reward=reward.value,
            task=TaskCard(**scenario.card.model_dump()),
            instructions=list(scenario.instructions),
            policy_hints=list(scenario.policy_hints),
            queue=[
                QueueTicketView(**ticket.to_queue_view().model_dump())
                for ticket in self._state.tickets
            ],
            focused_ticket=focused_ticket,
            last_action_result=last_action_result,
            accessible_apps=list(self._state.accessible_apps),
            app_snapshots=self._build_app_snapshots(),
            world_summary=list(self._state.world_summary),
            recent_events=[event.model_copy(deep=True) for event in self._state.recent_events],
            last_tool_result=copy.deepcopy(self._state.last_tool_result),
            progress=self._state.progress.model_copy(deep=True),
            available_actions=[action.value for action in ActionType],
        )

    def _build_app_snapshots(self) -> list[EnterpriseAppSnapshot]:
        snapshots = [
            EnterpriseAppSnapshot(
                app=EnterpriseApp.TICKETING_CONSOLE,
                summary=f"{len(self._state.tickets)} tickets in the active queue.",
                target_ids=[ticket.ticket_id for ticket in self._state.tickets],
            ),
            EnterpriseAppSnapshot(
                app=EnterpriseApp.CRM_WORKSPACE,
                summary=f"{len(self._state.customer_accounts)} customer accounts available for lookup.",
                target_ids=[account.account_id for account in self._state.customer_accounts],
            ),
            EnterpriseAppSnapshot(
                app=EnterpriseApp.BILLING_SYSTEM,
                summary=f"{len(self._state.billing_accounts)} billing ledgers available.",
                target_ids=[account.billing_account_id for account in self._state.billing_accounts],
            ),
            EnterpriseAppSnapshot(
                app=EnterpriseApp.INCIDENT_TRACKER,
                summary=f"{len(self._state.incidents)} incidents currently open or tracked.",
                target_ids=[incident.incident_id for incident in self._state.incidents],
            ),
            EnterpriseAppSnapshot(
                app=EnterpriseApp.TRUST_SAFETY_CONSOLE,
                summary=(
                    f"{sum(1 for ticket in self._state.tickets if 'security' in ' '.join(ticket.tags).lower())} "
                    "tickets currently have security-sensitive context."
                ),
                target_ids=[
                    ticket.ticket_id
                    for ticket in self._state.tickets
                    if "security" in " ".join(ticket.tags).lower()
                ],
            ),
            EnterpriseAppSnapshot(
                app=EnterpriseApp.POLICY_HUB,
                summary=f"{len(self._state.policy_articles)} policy articles searchable.",
                target_ids=[article.article_id for article in self._state.policy_articles],
            ),
        ]
        accessible = set(self._state.accessible_apps)
        return [snapshot for snapshot in snapshots if snapshot.app in accessible]
