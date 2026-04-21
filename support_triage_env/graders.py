from __future__ import annotations

import re
from abc import ABC, abstractmethod

from support_triage_env.models import (
    ActionType,
    EnterpriseApp,
    GradingSnapshot,
    SupportTriageState,
    TicketCategory,
    TicketRecord,
    TicketStatus,
)
from support_triage_env.tasks import TaskScenario

_SCORE_EPSILON = 0.01


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
        return _strict_score(1.0), [], []

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

    def _action_taken(
        self,
        state: SupportTriageState,
        action_type: ActionType,
        ticket_id: str | None = None,
    ) -> bool:
        return any(
            entry.action_type == action_type
            and (ticket_id is None or entry.ticket_id == ticket_id)
            for entry in state.action_history
        )

    def _ticket_text(self, ticket: TicketRecord) -> str:
        return " ".join([ticket.subject, *ticket.tags]).lower()

    def _is_security_ticket(self, ticket: TicketRecord) -> bool:
        text = self._ticket_text(ticket)
        return (
            ticket.current_category == TicketCategory.SECURITY_ACCOUNT_TAKEOVER
            or "security" in text
            or "comprom" in text
            or "mfa" in text
            or "executive" in text
        )

    def _is_product_incident_ticket(self, ticket: TicketRecord) -> bool:
        text = self._ticket_text(ticket)
        return (
            ticket.current_category == TicketCategory.PRODUCT_BUG
            or "outage" in text
            or "incident" in text
            or "export" in text
            or "500" in text
            or "502" in text
        )

    def _apply_queue_health_adjustments(
        self,
        state: SupportTriageState,
        penalties: dict[str, float],
        outstanding: list[str],
        violations: list[str],
    ) -> None:
        unresolved = [
            ticket
            for ticket in state.tickets
            if ticket.current_status not in {TicketStatus.RESOLVED, TicketStatus.ESCALATED}
        ]
        breached = [
            ticket
            for ticket in unresolved
            if ticket.sla_hours_remaining is not None and ticket.sla_hours_remaining <= 0
        ]
        if breached:
            penalties["sla_breach"] = round(min(0.18, 0.06 * len(breached)), 4)
            violations.append(
                "SLA breached for " + ", ".join(ticket.ticket_id for ticket in breached)
            )
            outstanding.append("Prevent SLA breaches across the active queue")

        security_exposure = [ticket for ticket in unresolved if self._is_security_ticket(ticket)]
        if security_exposure:
            penalties["security_exposure"] = round(
                max(penalties.get("security_exposure", 0.0), 0.08),
                4,
            )
            violations.append("Urgent security exposure remains unresolved in the queue")

        if EnterpriseApp.INCIDENT_TRACKER in state.accessible_apps:
            incident_gap = [
                ticket
                for ticket in unresolved
                if self._is_product_incident_ticket(ticket)
                and ticket.linked_incident_id is None
            ]
            if incident_gap:
                penalties["incident_gap"] = round(
                    max(penalties.get("incident_gap", 0.0), 0.08),
                    4,
                )
                violations.append("Incident-tracker workflow was skipped for an active product incident")

        downstream_risk = 0.0
        for account in state.customer_accounts:
            if account.lifecycle_stage not in {"security_hold", "at_risk"}:
                continue
            open_ids = set(account.open_ticket_ids)
            risky_tickets = [
                ticket
                for ticket in unresolved
                if ticket.ticket_id in open_ids
                and ticket.sla_hours_remaining is not None
                and ticket.sla_hours_remaining <= 1
            ]
            if risky_tickets:
                downstream_risk += 0.04
        if downstream_risk:
            penalties["downstream_business_risk"] = round(min(0.12, downstream_risk), 4)
            violations.append("Downstream account risk remains active after the current workflow")

    def _finalize_grade(
        self,
        state: SupportTriageState,
        components: dict[str, float],
        penalties: dict[str, float],
        satisfied: list[str],
        outstanding: list[str],
        violations: list[str],
    ) -> GradingSnapshot:
        self._apply_queue_health_adjustments(state, penalties, outstanding, violations)
        score = _strict_score(sum(components.values()) - sum(penalties.values()))
        return GradingSnapshot(
            score=score,
            components=components,
            penalties=penalties,
            satisfied_requirements=satisfied,
            outstanding_requirements=outstanding,
            violations=violations,
        )

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

        return self._finalize_grade(
            state, components, penalties, satisfied, outstanding, violations
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

        return self._finalize_grade(
            state, components, penalties, satisfied, outstanding, violations
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

        return self._finalize_grade(
            state, components, penalties, satisfied, outstanding, violations
        )


class EnterpriseRefundInvestigationGrader(BaseTaskGrader):
    def grade(self, state: SupportTriageState) -> GradingSnapshot:
        expectation = next(iter(self.scenario.expectations.values()))
        ticket = self._ticket_by_id(state, expectation.ticket_id)

        components: dict[str, float] = {}
        penalties: dict[str, float] = {}
        satisfied: list[str] = []
        outstanding: list[str] = []
        violations: list[str] = []

        if self._action_taken(state, ActionType.LOOKUP_ACCOUNT, expectation.ticket_id):
            components["crm_lookup"] = 0.10
            satisfied.append("Reviewed CRM account context")
        else:
            outstanding.append("Use CRM lookup before resolution")

        if self._action_taken(state, ActionType.CHECK_BILLING_STATUS, expectation.ticket_id):
            components["billing_lookup"] = 0.15
            satisfied.append("Confirmed billing ledger state")
        else:
            outstanding.append("Check billing account status")

        if self._action_taken(state, ActionType.SEARCH_POLICY, expectation.ticket_id):
            components["policy_lookup"] = 0.10
            satisfied.append("Reviewed the refund policy")
        else:
            outstanding.append("Search policy guidance before finishing")

        if ticket.current_category == expectation.category:
            components["correct_category"] = 0.10
            satisfied.append("Classified the enterprise case correctly")
        else:
            outstanding.append("Set category to billing_refund")

        if ticket.current_priority == expectation.priority:
            components["correct_priority"] = 0.10
            satisfied.append("Marked the case high priority")
        else:
            outstanding.append("Set priority to high")

        if ticket.assigned_team == expectation.team:
            components["correct_team"] = 0.10
            satisfied.append("Assigned billing_ops")
        else:
            outstanding.append("Assign to billing_ops")

        ratio, reply_hits, reply_missing = _reply_score(
            ticket,
            [(rule.label, rule.phrases) for rule in expectation.reply_requirements],
        )
        components["reply_quality"] = round(0.20 * ratio, 4)
        for item in reply_hits:
            satisfied.append(f"Reply includes {item}")
        for item in reply_missing:
            outstanding.append(f"Reply should include {item}")

        if (
            ticket.current_status == TicketStatus.RESOLVED
            and ticket.resolution_code == expectation.resolution_code
        ):
            components["resolution"] = 0.15
            satisfied.append("Resolved with refund_submitted")
        else:
            outstanding.append("Resolve with refund_submitted")

        outbound = _all_outbound_text(ticket)
        if _contains_any(outbound, expectation.forbidden_phrases):
            penalties["unsafe_data_request"] = 0.20
            violations.append("Requested sensitive customer secrets")

        if (
            ticket.current_status == TicketStatus.RESOLVED
            and not self._action_taken(state, ActionType.CHECK_BILLING_STATUS, expectation.ticket_id)
        ):
            penalties["resolved_without_billing_review"] = 0.15
            violations.append("Resolved the refund without checking billing context")

        return self._finalize_grade(
            state, components, penalties, satisfied, outstanding, violations
        )


class IncidentCoordinationOutageGrader(BaseTaskGrader):
    def grade(self, state: SupportTriageState) -> GradingSnapshot:
        expectation = next(iter(self.scenario.expectations.values()))
        ticket = self._ticket_by_id(state, expectation.ticket_id)

        components: dict[str, float] = {}
        penalties: dict[str, float] = {}
        satisfied: list[str] = []
        outstanding: list[str] = []
        violations: list[str] = []

        if self._action_taken(state, ActionType.LOOKUP_ACCOUNT, expectation.ticket_id):
            components["crm_lookup"] = 0.08
            satisfied.append("Reviewed CRM impact context")
        else:
            outstanding.append("Use CRM lookup before escalation")

        if self._action_taken(state, ActionType.CREATE_INCIDENT, expectation.ticket_id):
            components["incident_created"] = 0.16
            satisfied.append("Created an incident-tracker record")
        else:
            outstanding.append("Create an incident before escalating")

        if self._action_taken(state, ActionType.SEARCH_POLICY, expectation.ticket_id):
            components["policy_lookup"] = 0.08
            satisfied.append("Reviewed outage escalation guidance")
        else:
            outstanding.append("Search policy guidance for outage escalation")

        if ticket.current_category == expectation.category:
            components["correct_category"] = 0.10
            satisfied.append("Classified outage as product_bug")
        else:
            outstanding.append("Set category to product_bug")

        if ticket.current_priority == expectation.priority:
            components["correct_priority"] = 0.08
            satisfied.append("Marked outage high priority")
        else:
            outstanding.append("Set priority to high")

        if ticket.assigned_team == expectation.team:
            components["correct_team"] = 0.08
            satisfied.append("Assigned engineering")
        else:
            outstanding.append("Assign the outage to engineering")

        ratio, reply_hits, reply_missing = _reply_score(
            ticket,
            [(rule.label, rule.phrases) for rule in expectation.reply_requirements],
        )
        components["reply_quality"] = round(0.18 * ratio, 4)
        for item in reply_hits:
            satisfied.append(f"Reply includes {item}")
        for item in reply_missing:
            outstanding.append(f"Reply should include {item}")

        if ticket.linked_incident_id:
            components["incident_linked"] = 0.08
            satisfied.append("Linked the ticket to an incident record")
        else:
            outstanding.append("Link the outage ticket to an incident record")

        if ticket.current_status == TicketStatus.ESCALATED:
            components["terminal_action"] = 0.16
            satisfied.append("Escalated instead of resolving the outage")
        else:
            outstanding.append("Escalate the outage to engineering")

        escalation_text = _all_outbound_text(ticket)
        escalation_hits = [
            phrase
            for phrase in expectation.escalation_phrase_requirements
            if _contains_any(escalation_text, [phrase])
        ]
        components["escalation_context"] = round(
            0.08 * (len(escalation_hits) / max(1, len(expectation.escalation_phrase_requirements))),
            4,
        )

        if ticket.current_status == TicketStatus.RESOLVED:
            penalties["premature_resolution"] = 0.18
            violations.append("Resolved an active enterprise outage instead of coordinating escalation")
        if _contains_any(escalation_text, expectation.forbidden_phrases):
            penalties["overpromise"] = 0.10
            violations.append("Promised unsupported outage timing")

        return self._finalize_grade(
            state, components, penalties, satisfied, outstanding, violations
        )


class ExecutiveSecurityEscalationGrader(BaseTaskGrader):
    def grade(self, state: SupportTriageState) -> GradingSnapshot:
        expectation = next(iter(self.scenario.expectations.values()))
        security_ticket = self._ticket_by_id(state, expectation.ticket_id)

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
        if first_meaningful_ticket == expectation.ticket_id:
            components["priority_order"] = 0.12
            satisfied.append("Prioritized the executive security case first")
        else:
            penalties["priority_miss"] = 0.10
            violations.append("Worked another ticket before the executive security escalation")
            outstanding.append(f"Prioritize {expectation.ticket_id} before lower-risk work")

        if self._action_taken(state, ActionType.LOOKUP_ACCOUNT, expectation.ticket_id):
            components["crm_lookup"] = 0.10
            satisfied.append("Reviewed executive account context")
        else:
            outstanding.append("Review CRM context before trust escalation")

        if self._action_taken(state, ActionType.SEARCH_POLICY, expectation.ticket_id):
            components["policy_lookup"] = 0.08
            satisfied.append("Reviewed trust and safety policy")
        else:
            outstanding.append("Search security policy guidance before escalating")

        if self._action_taken(state, ActionType.ADD_INTERNAL_NOTE, expectation.ticket_id):
            components["internal_note"] = 0.08
            satisfied.append("Captured an internal trust note")
        else:
            outstanding.append("Add an internal trust note before escalation")

        if security_ticket.current_category == expectation.category:
            components["correct_category"] = 0.10
            satisfied.append("Classified security incident correctly")
        else:
            outstanding.append("Set category to security_account_takeover")

        if security_ticket.current_priority == expectation.priority:
            components["correct_priority"] = 0.10
            satisfied.append("Marked the security case urgent")
        else:
            outstanding.append("Set priority to urgent")

        if security_ticket.assigned_team == expectation.team:
            components["correct_team"] = 0.10
            satisfied.append("Assigned trust_safety")
        else:
            outstanding.append("Assign the case to trust_safety")

        ratio, reply_hits, reply_missing = _reply_score(
            security_ticket,
            [(rule.label, rule.phrases) for rule in expectation.reply_requirements],
        )
        components["reply_quality"] = round(0.17 * ratio, 4)
        for item in reply_hits:
            satisfied.append(f"Security reply includes {item}")
        for item in reply_missing:
            outstanding.append(f"Security reply should include {item}")

        escalation_text = _all_outbound_text(security_ticket)
        escalation_hits = [
            phrase
            for phrase in expectation.escalation_phrase_requirements
            if _contains_any(escalation_text, [phrase])
        ]
        components["escalation_context"] = round(
            0.10 * (len(escalation_hits) / max(1, len(expectation.escalation_phrase_requirements))),
            4,
        )

        if security_ticket.current_status == TicketStatus.ESCALATED:
            components["terminal_action"] = 0.15
            satisfied.append("Escalated the executive case safely")
        else:
            outstanding.append("Escalate the executive security case")

        if _contains_any(escalation_text, expectation.forbidden_phrases):
            penalties["unsafe_security_advice"] = 0.25
            violations.append("Provided unsafe executive account-recovery guidance")
        if security_ticket.current_status == TicketStatus.RESOLVED:
            penalties["resolved_security_ticket"] = 0.15
            violations.append("Resolved the executive security issue instead of escalating it")

        return self._finalize_grade(
            state, components, penalties, satisfied, outstanding, violations
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
    if "enterprise_refund_investigation" in scenarios:
        graders["enterprise_refund_investigation"] = EnterpriseRefundInvestigationGrader(
            scenarios["enterprise_refund_investigation"]
        )
    if "incident_coordination_outage" in scenarios:
        graders["incident_coordination_outage"] = IncidentCoordinationOutageGrader(
            scenarios["incident_coordination_outage"]
        )
    if "executive_security_escalation" in scenarios:
        graders["executive_security_escalation"] = ExecutiveSecurityEscalationGrader(
            scenarios["executive_security_escalation"]
        )
    return graders
