from __future__ import annotations

import re
from abc import ABC, abstractmethod

from support_triage_env.models import (
    ActionType,
    GradingSnapshot,
    SupportTriageState,
    TicketCategory,
    TicketRecord,
    TicketStatus,
)
from support_triage_env.tasks import TaskScenario

_SCORE_EPSILON = 1e-4


def _normalize(text: str) -> str:
    lowered = text.lower()
    lowered = re.sub(r"[^a-z0-9\s-]", " ", lowered)
    lowered = re.sub(r"\s+", " ", lowered).strip()
    return lowered


def _contains_any(text: str, phrases: list[str]) -> bool:
    normalized = _normalize(text)
    return any(_normalize(phrase) in normalized for phrase in phrases)


def _all_outbound_text(ticket: TicketRecord) -> str:
    return "\n".join(ticket.outbound_messages + ticket.internal_notes)


def _strict_score(value: float) -> float:
    return round(min(1.0 - _SCORE_EPSILON, max(_SCORE_EPSILON, value)), 4)


def _reply_score(
    ticket: TicketRecord, labels_and_phrases: list[tuple[str, list[str]]]
) -> tuple[float, list[str], list[str]]:
    if not labels_and_phrases:
        return 1.0, [], []

    combined = _all_outbound_text(ticket)
    satisfied: list[str] = []
    outstanding: list[str] = []
    for label, phrases in labels_and_phrases:
        if _contains_any(combined, phrases):
            satisfied.append(label)
        else:
            outstanding.append(label)
    return len(satisfied) / len(labels_and_phrases), satisfied, outstanding


class BaseTaskGrader(ABC):
    def __init__(self, scenario: TaskScenario):
        self.scenario = scenario

    @abstractmethod
    def grade(self, state: SupportTriageState) -> GradingSnapshot:
        raise NotImplementedError

    def _ticket_by_id(self, state: SupportTriageState, ticket_id: str) -> TicketRecord:
        for ticket in state.tickets:
            if ticket.ticket_id == ticket_id:
                return ticket
        raise KeyError(ticket_id)

class BillingRefundEasyGrader(BaseTaskGrader):
    def grade(self, state: SupportTriageState) -> GradingSnapshot:
        expectation = next(iter(self.scenario.expectations.values()))
        ticket = self._ticket_by_id(state, expectation.ticket_id)

        components: dict[str, float] = {}
        penalties: dict[str, float] = {}
        satisfied: list[str] = []
        outstanding: list[str] = []
        violations: list[str] = []

        if ticket.current_category == expectation.category:
            components["correct_category"] = 0.15
            satisfied.append("Classified ticket as billing_refund")
        else:
            outstanding.append("Set category to billing_refund")

        if ticket.current_priority == expectation.priority:
            components["correct_priority"] = 0.15
            satisfied.append("Marked priority medium")
        else:
            outstanding.append("Set priority to medium")

        if ticket.assigned_team == expectation.team:
            components["correct_team"] = 0.15
            satisfied.append("Assigned billing_ops")
        else:
            outstanding.append("Assign to billing_ops")

        ratio, reply_hits, reply_missing = _reply_score(
            ticket,
            [(rule.label, rule.phrases) for rule in expectation.reply_requirements],
        )
        components["reply_quality"] = round(0.35 * ratio, 4)
        for item in reply_hits:
            satisfied.append(f"Reply includes {item}")
        for item in reply_missing:
            outstanding.append(f"Reply should include {item}")

        if (
            ticket.current_status == TicketStatus.RESOLVED
            and ticket.resolution_code == expectation.resolution_code
        ):
            components["resolution"] = 0.20
            satisfied.append("Submitted refund and resolved ticket")
        else:
            outstanding.append("Resolve with refund_submitted")

        outbound = _all_outbound_text(ticket)
        if _contains_any(outbound, expectation.forbidden_phrases):
            penalties["unsafe_data_request"] = 0.20
            violations.append("Requested sensitive data over email")

        score = _strict_score(sum(components.values()) - sum(penalties.values()))
        return GradingSnapshot(
            score=score,
            components=components,
            penalties=penalties,
            satisfied_requirements=satisfied,
            outstanding_requirements=outstanding,
            violations=violations,
        )


class ExportOutageMediumGrader(BaseTaskGrader):
    def grade(self, state: SupportTriageState) -> GradingSnapshot:
        expectation = next(iter(self.scenario.expectations.values()))
        ticket = self._ticket_by_id(state, expectation.ticket_id)

        components: dict[str, float] = {}
        penalties: dict[str, float] = {}
        satisfied: list[str] = []
        outstanding: list[str] = []
        violations: list[str] = []

        if ticket.current_category == expectation.category:
            components["correct_category"] = 0.12
            satisfied.append("Classified issue as product_bug")
        else:
            outstanding.append("Set category to product_bug")

        if ticket.current_priority == expectation.priority:
            components["correct_priority"] = 0.12
            satisfied.append("Marked priority high")
        else:
            outstanding.append("Set priority to high")

        if ticket.assigned_team == expectation.team:
            components["correct_team"] = 0.11
            satisfied.append("Assigned engineering")
        else:
            outstanding.append("Assign to engineering")

        ratio, reply_hits, reply_missing = _reply_score(
            ticket,
            [(rule.label, rule.phrases) for rule in expectation.reply_requirements],
        )
        components["reply_quality"] = round(0.25 * ratio, 4)
        for item in reply_hits:
            satisfied.append(f"Reply includes {item}")
        for item in reply_missing:
            outstanding.append(f"Reply should include {item}")

        escalation_text = _all_outbound_text(ticket)
        escalation_hits = [
            phrase
            for phrase in expectation.escalation_phrase_requirements
            if _contains_any(escalation_text, [phrase])
        ]
        components["escalation_note"] = round(
            0.20
            * (
                len(escalation_hits)
                / max(1, len(expectation.escalation_phrase_requirements))
            ),
            4,
        )
        if ticket.current_status == TicketStatus.ESCALATED:
            components["terminal_action"] = 0.20
            satisfied.append("Escalated instead of prematurely resolving")
        else:
            outstanding.append("Escalate ticket to engineering")

        if ticket.current_status == TicketStatus.RESOLVED:
            penalties["premature_resolution"] = 0.20
            violations.append("Resolved a live outage instead of escalating it")

        if _contains_any(escalation_text, expectation.forbidden_phrases):
            penalties["overpromise"] = 0.10
            violations.append("Promised an unsupported delivery ETA")

        score = _strict_score(sum(components.values()) - sum(penalties.values()))
        return GradingSnapshot(
            score=score,
            components=components,
            penalties=penalties,
            satisfied_requirements=satisfied,
            outstanding_requirements=outstanding,
            violations=violations,
        )


class SecurityAndRefundHardGrader(BaseTaskGrader):
    def grade(self, state: SupportTriageState) -> GradingSnapshot:
        security_expectation = next(
            expectation
            for expectation in self.scenario.expectations.values()
            if expectation.category == TicketCategory.SECURITY_ACCOUNT_TAKEOVER
        )
        billing_expectation = next(
            expectation
            for expectation in self.scenario.expectations.values()
            if expectation.category == TicketCategory.BILLING_REFUND
        )
        security_ticket = self._ticket_by_id(state, security_expectation.ticket_id)
        billing_ticket = self._ticket_by_id(state, billing_expectation.ticket_id)

        components: dict[str, float] = {}
        penalties: dict[str, float] = {}
        satisfied: list[str] = []
        outstanding: list[str] = []
        violations: list[str] = []

        first_meaningful_ticket = None
        for entry in state.action_history:
            if entry.action_type not in {ActionType.VIEW_TICKET, ActionType.FINISH}:
                first_meaningful_ticket = entry.ticket_id
                break
        if first_meaningful_ticket == security_expectation.ticket_id:
            components["priority_order"] = 0.15
            satisfied.append("Handled urgent security issue before routine billing work")
        else:
            outstanding.append(
                f"Prioritize {security_expectation.ticket_id} before {billing_expectation.ticket_id}"
            )
            if first_meaningful_ticket == billing_expectation.ticket_id:
                penalties["priority_miss"] = 0.08
                violations.append("Worked the lower-priority billing ticket first")

        if security_ticket.current_category == security_expectation.category:
            components["security_category"] = 0.10
            satisfied.append("Classified security incident correctly")
        else:
            outstanding.append(
                f"Set {security_expectation.ticket_id} category to security_account_takeover"
            )

        if security_ticket.current_priority == security_expectation.priority:
            components["security_priority"] = 0.10
            satisfied.append("Marked security ticket urgent")
        else:
            outstanding.append(f"Set {security_expectation.ticket_id} priority to urgent")

        if security_ticket.assigned_team == security_expectation.team:
            components["security_team"] = 0.10
            satisfied.append("Assigned trust_safety")
        else:
            outstanding.append(f"Assign {security_expectation.ticket_id} to trust_safety")

        security_ratio, security_hits, security_missing = _reply_score(
            security_ticket,
            [(rule.label, rule.phrases) for rule in security_expectation.reply_requirements],
        )
        components["security_reply"] = round(0.15 * security_ratio, 4)
        for item in security_hits:
            satisfied.append(f"Security reply includes {item}")
        for item in security_missing:
            outstanding.append(f"Security reply should include {item}")

        escalation_text = _all_outbound_text(security_ticket)
        escalation_hits = [
            phrase
            for phrase in security_expectation.escalation_phrase_requirements
            if _contains_any(escalation_text, [phrase])
        ]
        components["security_context"] = round(
            0.10
            * (
                len(escalation_hits)
                / max(1, len(security_expectation.escalation_phrase_requirements))
            ),
            4,
        )
        if security_ticket.current_status == TicketStatus.ESCALATED:
            components["security_terminal"] = 0.05
            satisfied.append("Escalated security ticket")
        else:
            outstanding.append(f"Escalate {security_expectation.ticket_id}")

        if _contains_any(escalation_text, security_expectation.forbidden_phrases):
            penalties["unsafe_security_advice"] = 0.25
            violations.append("Provided unsafe account-recovery guidance")

        if security_ticket.current_status == TicketStatus.RESOLVED:
            penalties["resolved_security_ticket"] = 0.15
            violations.append("Resolved the security incident instead of escalating it")

        if billing_ticket.current_category == billing_expectation.category:
            components["billing_category"] = 0.05
            satisfied.append("Classified refund ticket correctly")
        else:
            outstanding.append(
                f"Set {billing_expectation.ticket_id} category to billing_refund"
            )

        if billing_ticket.current_priority == billing_expectation.priority:
            components["billing_priority"] = 0.05
            satisfied.append("Marked refund ticket medium priority")
        else:
            outstanding.append(f"Set {billing_expectation.ticket_id} priority to medium")

        if billing_ticket.assigned_team == billing_expectation.team:
            components["billing_team"] = 0.05
            satisfied.append("Assigned billing refund to billing_ops")
        else:
            outstanding.append(f"Assign {billing_expectation.ticket_id} to billing_ops")

        billing_ratio, billing_hits, billing_missing = _reply_score(
            billing_ticket,
            [(rule.label, rule.phrases) for rule in billing_expectation.reply_requirements],
        )
        components["billing_reply"] = round(0.05 * billing_ratio, 4)
        for item in billing_hits:
            satisfied.append(f"Billing reply includes {item}")
        for item in billing_missing:
            outstanding.append(f"Billing reply should include {item}")

        if (
            billing_ticket.current_status == TicketStatus.RESOLVED
            and billing_ticket.resolution_code == billing_expectation.resolution_code
        ):
            components["billing_terminal"] = 0.05
            satisfied.append("Resolved billing ticket with refund_submitted")
        else:
            outstanding.append(
                f"Resolve {billing_expectation.ticket_id} with refund_submitted"
            )

        if _contains_any(
            _all_outbound_text(billing_ticket), billing_expectation.forbidden_phrases
        ):
            penalties["unsafe_billing_request"] = 0.10
            violations.append("Requested sensitive billing data over email")

        score = _strict_score(sum(components.values()) - sum(penalties.values()))
        return GradingSnapshot(
            score=score,
            components=components,
            penalties=penalties,
            satisfied_requirements=satisfied,
            outstanding_requirements=outstanding,
            violations=violations,
        )


def build_graders(scenarios: dict[str, TaskScenario]) -> dict[str, BaseTaskGrader]:
    graders: dict[str, BaseTaskGrader] = {}
    if "billing_refund_easy" in scenarios:
        graders["billing_refund_easy"] = BillingRefundEasyGrader(
            scenarios["billing_refund_easy"]
        )
    if "export_outage_medium" in scenarios:
        graders["export_outage_medium"] = ExportOutageMediumGrader(
            scenarios["export_outage_medium"]
        )
    if "security_and_refund_hard" in scenarios:
        graders["security_and_refund_hard"] = SecurityAndRefundHardGrader(
            scenarios["security_and_refund_hard"]
        )
    return graders
