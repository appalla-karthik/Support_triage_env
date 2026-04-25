from __future__ import annotations

import re
from abc import ABC, abstractmethod
from difflib import SequenceMatcher

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
_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "be",
    "for",
    "from",
    "have",
    "has",
    "i",
    "is",
    "it",
    "our",
    "please",
    "the",
    "this",
    "to",
    "we",
    "will",
    "with",
    "you",
    "your",
}
_TOKEN_ALIASES = {
    "apologies": "sorry",
    "apologise": "sorry",
    "apologized": "sorry",
    "apologized": "sorry",
    "apologizing": "sorry",
    "apologize": "sorry",
    "billingops": "billing",
    "browsers": "browser",
    "charges": "charge",
    "charged": "charge",
    "engineers": "engineering",
    "eta": "timeline",
    "investigate": "investigating",
    "investigation": "investigating",
    "investigations": "investigating",
    "passwords": "password",
    "refunds": "refund",
    "reimbursement": "refund",
    "specialists": "specialist",
    "timestamps": "timestamp",
}


def _normalize(text: str) -> str:
    lowered = text.lower()
    lowered = re.sub(r"[^a-z0-9\s-]", " ", lowered)
    lowered = re.sub(r"\s+", " ", lowered).strip()
    return lowered


def _contains_any(text: str, phrases: list[str]) -> bool:
    normalized = _normalize(text)
    return any(_normalize(phrase) in normalized for phrase in phrases)


def _semantic_tokens(text: str) -> set[str]:
    tokens: set[str] = set()
    for raw_token in _normalize(text).replace("-", " ").split():
        token = _TOKEN_ALIASES.get(raw_token, raw_token)
        if len(token) == 1 and not token.isdigit():
            continue
        if token in _STOPWORDS:
            continue
        tokens.add(token)
    return tokens


def _requirement_match_score(text: str, phrases: list[str]) -> float:
    normalized_text = _normalize(text)
    text_tokens = _semantic_tokens(text)
    best_score = 0.0
    for phrase in phrases:
        normalized_phrase = _normalize(phrase)
        if not normalized_phrase:
            continue
        if normalized_phrase in normalized_text:
            return 1.0
        phrase_tokens = _semantic_tokens(phrase)
        if not phrase_tokens:
            continue
        overlap = len(text_tokens & phrase_tokens) / len(phrase_tokens)
        dense_overlap = len(text_tokens & phrase_tokens) / max(len(text_tokens), len(phrase_tokens))
        sequence = SequenceMatcher(None, normalized_text, normalized_phrase).ratio()
        candidate = (0.6 * overlap) + (0.2 * dense_overlap) + (0.2 * sequence)
        if phrase_tokens.issubset(text_tokens):
            candidate = max(candidate, 0.9)
        elif overlap >= 0.8:
            candidate = max(candidate, 0.78)
        best_score = max(best_score, min(1.0, candidate))
    return round(best_score, 4)


def _all_outbound_text(ticket: TicketRecord) -> str:
    return "\n".join(ticket.outbound_messages + ticket.internal_notes)


def _strict_score(value: float) -> float:
    return round(min(1.0 - _SCORE_EPSILON, max(_SCORE_EPSILON, value)), 4)


def _require_category(expectation) -> str:
    return f"Set category to {expectation.category.value}"


def _require_priority(expectation) -> str:
    return f"Set queue priority to {expectation.priority.value}"


def _require_department_priority(expectation) -> str:
    return (
        f"Set {expectation.team.value} internal priority to "
        f"{expectation.department_priority.value}"
    )


def _score_priorities(
    *,
    ticket: TicketRecord,
    expectation,
    total_weight: float,
    components: dict[str, float],
    satisfied: list[str],
    outstanding: list[str],
    component_prefix: str = "correct",
    queue_success: str | None = None,
    department_success: str | None = None,
) -> None:
    queue_weight = round(total_weight * 0.6, 4)
    department_weight = round(total_weight - queue_weight, 4)

    if ticket.current_priority == expectation.priority:
        components[f"{component_prefix}_queue_priority"] = queue_weight
        satisfied.append(queue_success or f"Marked queue priority {expectation.priority.value}")
    else:
        outstanding.append(_require_priority(expectation))

    if ticket.current_department_priority == expectation.department_priority:
        components[f"{component_prefix}_department_priority"] = department_weight
        satisfied.append(
            department_success
            or f"Marked {expectation.team.value} internal priority {expectation.department_priority.value}"
        )
    else:
        outstanding.append(_require_department_priority(expectation))


def _require_team(expectation) -> str:
    return f"Assign to {expectation.team.value}"


def _require_resolution(expectation) -> str:
    if expectation.resolution_code is None:
        return "Reach the correct terminal state"
    return f"Resolve with {expectation.resolution_code.value}"


def _reply_score(
    ticket: TicketRecord, labels_and_phrases: list[tuple[str, list[str]]]
) -> tuple[float, list[str], list[str]]:
    if not labels_and_phrases:
        return _strict_score(1.0), [], []

    combined = _all_outbound_text(ticket)
    satisfied: list[str] = []
    outstanding: list[str] = []
    score_total = 0.0
    for label, phrases in labels_and_phrases:
        score = _requirement_match_score(combined, phrases)
        score_total += score
        if score >= 0.72:
            satisfied.append(label)
        else:
            outstanding.append(label)
    return round(score_total / len(labels_and_phrases), 4), satisfied, outstanding


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
            ticket.current_category
            in {
                TicketCategory.SECURITY_ACCOUNT_TAKEOVER,
                TicketCategory.SECURITY_ESCALATION,
            }
            or "security" in text
            or "comprom" in text
            or "mfa" in text
            or "executive" in text
        )

    def _is_product_incident_ticket(self, ticket: TicketRecord) -> bool:
        text = self._ticket_text(ticket)
        return (
            ticket.current_category
            in {
                TicketCategory.PRODUCT_BUG,
                TicketCategory.INCIDENT_COORDINATION,
            }
            or "outage" in text
            or "incident" in text
            or "export" in text
            or "500" in text
            or "502" in text
        )

    def _looks_billing_ticket(self, ticket: TicketRecord) -> bool:
        text = self._ticket_text(ticket)
        return (
            ticket.current_category
            in {
                TicketCategory.BILLING_REFUND,
                TicketCategory.BILLING_APPROVAL,
            }
            or "billing" in text
            or "refund" in text
            or "charge" in text
            or "invoice" in text
        )

    def _requires_high_confidence_resolution(self, ticket: TicketRecord) -> bool:
        high_risk_tags = {"vip", "month-end", "reopen-risk", "policy-review"}
        return self._looks_billing_ticket(ticket) and (
            ticket.customer_tier.lower() == "enterprise"
            or any(tag in high_risk_tags for tag in ticket.tags)
            or (ticket.sla_hours_remaining is not None and ticket.sla_hours_remaining <= 8)
        )

    def _supports_urgent_priority(self, ticket: TicketRecord, state: SupportTriageState) -> bool:
        text = self._ticket_text(ticket)
        strong_text_signal = any(
            token in text
            for token in {
                "security",
                "comprom",
                "mfa",
                "executive",
                "urgent",
                "incident",
                "outage",
                "critical",
                "sev",
            }
        )
        action_evidence = any(
            self._action_taken(state, action_type, ticket.ticket_id)
            for action_type in {
                ActionType.LOOKUP_ACCOUNT,
                ActionType.SEARCH_POLICY,
                ActionType.CREATE_INCIDENT,
                ActionType.CHECK_BILLING_STATUS,
            }
        )
        return (
            strong_text_signal
            or "urgent" in ticket.tags
            or "critical" in ticket.tags
            or (ticket.sla_hours_remaining is not None and ticket.sla_hours_remaining <= 2)
            or action_evidence
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

    def _ticket_hits_terminal_expectation(
        self, ticket: TicketRecord, expectation
    ) -> bool:
        if expectation.terminal_status == "resolved":
            return (
                ticket.current_status == TicketStatus.RESOLVED
                and ticket.resolution_code == expectation.resolution_code
            )
        if expectation.terminal_status == "escalated":
            return ticket.current_status == TicketStatus.ESCALATED
        return False

    def _apply_workflow_integrity_adjustments(
        self,
        state: SupportTriageState,
        penalties: dict[str, float],
        outstanding: list[str],
        violations: list[str],
    ) -> None:
        pending_events = [event for event in state.pending_events if event.status == "pending"]
        if pending_events:
            penalties["pending_downstream_failure"] = round(
                min(0.12, 0.06 * len(pending_events)),
                4,
            )
            violations.append("A downstream system event is queued because the workflow is incomplete")
            outstanding.append("Resolve queued downstream failures before finishing")

        finish_taken = self._action_taken(state, ActionType.FINISH)
        unmet_expected_tickets: list[str] = []
        for expectation in self.scenario.expectations.values():
            ticket = self._ticket_by_id(state, expectation.ticket_id)
            if not self._ticket_hits_terminal_expectation(ticket, expectation):
                unmet_expected_tickets.append(ticket.ticket_id)
            if (
                ticket.current_status in {TicketStatus.RESOLVED, TicketStatus.ESCALATED}
                and expectation.reply_requirements
                and not ticket.outbound_messages
            ):
                penalties["terminal_without_reply"] = max(
                    penalties.get("terminal_without_reply", 0.0),
                    0.08,
                )
                violations.append(
                    f"{ticket.ticket_id} reached a terminal state without a customer-facing reply"
                )
            if (
                ticket.current_status == TicketStatus.ESCALATED
                and EnterpriseApp.POLICY_HUB in state.accessible_apps
                and (
                    self._is_security_ticket(ticket)
                    or self._is_product_incident_ticket(ticket)
                )
                and any(
                    tag in {"policy-review", "escalation-review", "executive", "incident"}
                    for tag in ticket.tags
                )
                and not self._action_taken(state, ActionType.SEARCH_POLICY, ticket.ticket_id)
            ):
                penalties["escalated_without_policy_review"] = max(
                    penalties.get("escalated_without_policy_review", 0.0),
                    0.07,
                )
                violations.append(
                    f"{ticket.ticket_id} was escalated without checking the current policy guidance"
                )
            if (
                ticket.current_status == TicketStatus.ESCALATED
                and self._is_product_incident_ticket(ticket)
                and EnterpriseApp.INCIDENT_TRACKER in state.accessible_apps
                and any(tag in {"incident", "escalation-review"} for tag in ticket.tags)
                and not (
                    ticket.linked_incident_id
                    or self._action_taken(state, ActionType.CREATE_INCIDENT, ticket.ticket_id)
                )
            ):
                penalties["escalated_without_incident"] = max(
                    penalties.get("escalated_without_incident", 0.0),
                    0.08,
                )
                violations.append(
                    f"{ticket.ticket_id} was escalated without incident-tracker evidence"
                )
            if (
                ticket.current_status == TicketStatus.RESOLVED
                and self._is_product_incident_ticket(ticket)
            ):
                penalties["resolved_live_incident"] = max(
                    penalties.get("resolved_live_incident", 0.0),
                    0.10,
                )
                violations.append(
                    f"{ticket.ticket_id} was resolved even though it behaves like a live incident"
                )
        if finish_taken and unmet_expected_tickets:
            penalties["premature_finish"] = round(
                min(0.15, 0.05 * len(unmet_expected_tickets)),
                4,
            )
            violations.append(
                "Finished the episode while required tickets were still incomplete: "
                + ", ".join(unmet_expected_tickets)
            )
            outstanding.append("Finish only after all required tickets reach their correct terminal state")

    def _apply_confidence_adjustments(
        self,
        state: SupportTriageState,
        penalties: dict[str, float],
        outstanding: list[str],
        violations: list[str],
    ) -> None:
        for expectation in self.scenario.expectations.values():
            ticket = self._ticket_by_id(state, expectation.ticket_id)
            has_policy_lookup = self._action_taken(state, ActionType.SEARCH_POLICY, ticket.ticket_id)
            has_account_lookup = self._action_taken(state, ActionType.LOOKUP_ACCOUNT, ticket.ticket_id)
            has_billing_lookup = self._action_taken(state, ActionType.CHECK_BILLING_STATUS, ticket.ticket_id)
            has_incident_evidence = bool(ticket.linked_incident_id) or self._action_taken(
                state, ActionType.CREATE_INCIDENT, ticket.ticket_id
            )

            if (
                ticket.current_status == TicketStatus.RESOLVED
                and self._requires_high_confidence_resolution(ticket)
                and not (has_billing_lookup and has_policy_lookup)
            ):
                penalties["confidence_failure_resolution"] = max(
                    penalties.get("confidence_failure_resolution", 0.0),
                    0.12,
                )
                violations.append(
                    f"{ticket.ticket_id} was resolved without enough evidence from billing and policy review"
                )
                outstanding.append(
                    f"Gather billing and policy evidence before resolving {ticket.ticket_id}"
                )

            if (
                ticket.current_status == TicketStatus.ESCALATED
                and (self._is_security_ticket(ticket) or self._is_product_incident_ticket(ticket))
                and not has_policy_lookup
            ):
                penalties["confidence_failure_escalation"] = max(
                    penalties.get("confidence_failure_escalation", 0.0),
                    0.10,
                )
                violations.append(
                    f"{ticket.ticket_id} was escalated without checking current policy guidance first"
                )
                outstanding.append(
                    f"Review policy guidance before escalating {ticket.ticket_id}"
                )

            if (
                ticket.current_status == TicketStatus.ESCALATED
                and self._is_product_incident_ticket(ticket)
                and EnterpriseApp.INCIDENT_TRACKER in state.accessible_apps
                and any(tag in {"incident", "incident-follow-up", "escalation-review"} for tag in ticket.tags)
                and not (has_incident_evidence or has_account_lookup)
            ):
                penalties["confidence_failure_escalation"] = max(
                    penalties.get("confidence_failure_escalation", 0.0),
                    0.12,
                )
                violations.append(
                    f"{ticket.ticket_id} was escalated without enough incident or account evidence"
                )
                outstanding.append(
                    f"Collect incident or account evidence before escalating {ticket.ticket_id}"
                )

            if (
                ticket.current_priority is not None
                and ticket.current_priority.value == "urgent"
                and not self._supports_urgent_priority(ticket, state)
            ):
                penalties["confidence_failure_urgent_priority"] = max(
                    penalties.get("confidence_failure_urgent_priority", 0.0),
                    0.10,
                )
                violations.append(
                    f"{ticket.ticket_id} was marked urgent without enough supporting evidence"
                )
                outstanding.append(
                    f"Only use urgent priority when the ticket has strong risk, SLA, or business-impact evidence"
                )

    def _finalize_grade(
        self,
        state: SupportTriageState,
        components: dict[str, float],
        penalties: dict[str, float],
        satisfied: list[str],
        outstanding: list[str],
        violations: list[str],
    ) -> GradingSnapshot:
        self._apply_workflow_integrity_adjustments(
            state, penalties, outstanding, violations
        )
        self._apply_confidence_adjustments(
            state, penalties, outstanding, violations
        )
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

        _score_priorities(
            ticket=ticket,
            expectation=expectation,
            total_weight=0.15,
            components=components,
            satisfied=satisfied,
            outstanding=outstanding,
            queue_success="Marked queue priority medium",
            department_success="Marked billing_ops internal priority medium",
        )

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

        _score_priorities(
            ticket=ticket,
            expectation=expectation,
            total_weight=0.12,
            components=components,
            satisfied=satisfied,
            outstanding=outstanding,
            queue_success="Marked queue priority high",
            department_success=(
                f"Marked engineering internal priority {expectation.department_priority.value}"
            ),
        )

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

        _score_priorities(
            ticket=security_ticket,
            expectation=security_expectation,
            total_weight=0.10,
            components=components,
            satisfied=satisfied,
            outstanding=outstanding,
            component_prefix="security",
            queue_success="Marked security queue priority urgent",
            department_success="Marked trust_safety internal priority urgent",
        )

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

        _score_priorities(
            ticket=billing_ticket,
            expectation=billing_expectation,
            total_weight=0.05,
            components=components,
            satisfied=satisfied,
            outstanding=outstanding,
            component_prefix="billing",
            queue_success="Marked refund queue priority medium",
            department_success=(
                f"Marked billing_ops internal priority {billing_expectation.department_priority.value}"
            ),
        )

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
            outstanding.append(_require_category(expectation))

        _score_priorities(
            ticket=ticket,
            expectation=expectation,
            total_weight=0.10,
            components=components,
            satisfied=satisfied,
            outstanding=outstanding,
            queue_success=f"Marked queue priority {expectation.priority.value}",
            department_success=(
                f"Marked {expectation.team.value} internal priority {expectation.department_priority.value}"
            ),
        )

        if ticket.assigned_team == expectation.team:
            components["correct_team"] = 0.10
            satisfied.append("Assigned billing_ops")
        else:
            outstanding.append(_require_team(expectation))

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
            outstanding.append(_require_resolution(expectation))

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
            satisfied.append(f"Classified outage as {expectation.category.value}")
        else:
            outstanding.append(_require_category(expectation))

        _score_priorities(
            ticket=ticket,
            expectation=expectation,
            total_weight=0.08,
            components=components,
            satisfied=satisfied,
            outstanding=outstanding,
            queue_success=f"Marked queue priority {expectation.priority.value}",
            department_success=(
                f"Marked {expectation.team.value} internal priority {expectation.department_priority.value}"
            ),
        )

        if ticket.assigned_team == expectation.team:
            components["correct_team"] = 0.08
            satisfied.append("Assigned engineering")
        else:
            outstanding.append(_require_team(expectation))

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
            outstanding.append(_require_category(expectation))

        _score_priorities(
            ticket=security_ticket,
            expectation=expectation,
            total_weight=0.10,
            components=components,
            satisfied=satisfied,
            outstanding=outstanding,
            queue_success=f"Marked queue priority {expectation.priority.value}",
            department_success=(
                f"Marked {expectation.team.value} internal priority {expectation.department_priority.value}"
            ),
        )

        if security_ticket.assigned_team == expectation.team:
            components["correct_team"] = 0.10
            satisfied.append("Assigned trust_safety")
        else:
            outstanding.append(_require_team(expectation))

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


class EscalationRejectionRecoveryGrader(BaseTaskGrader):
    def grade(self, state: SupportTriageState) -> GradingSnapshot:
        expectation = next(iter(self.scenario.expectations.values()))
        ticket = self._ticket_by_id(state, expectation.ticket_id)

        components: dict[str, float] = {}
        penalties: dict[str, float] = {}
        satisfied: list[str] = []
        outstanding: list[str] = []
        violations: list[str] = []

        if self._action_taken(state, ActionType.LOOKUP_ACCOUNT, expectation.ticket_id):
            components["crm_lookup"] = 0.07
            satisfied.append("Reviewed CRM impact context")
        else:
            outstanding.append("Use CRM lookup before escalation")

        if self._action_taken(state, ActionType.SEARCH_POLICY, expectation.ticket_id):
            components["policy_lookup"] = 0.08
            satisfied.append("Reviewed escalation packet policy")
        else:
            outstanding.append("Search the escalation packet policy")

        if self._action_taken(state, ActionType.CREATE_INCIDENT, expectation.ticket_id):
            components["incident_created"] = 0.14
            satisfied.append("Created or linked an incident record")
        else:
            outstanding.append("Create an incident record before escalating")

        if ticket.current_category == expectation.category:
            components["correct_category"] = 0.08
        else:
            outstanding.append(_require_category(expectation))

        _score_priorities(
            ticket=ticket,
            expectation=expectation,
            total_weight=0.08,
            components=components,
            satisfied=satisfied,
            outstanding=outstanding,
            queue_success=f"Marked queue priority {expectation.priority.value}",
            department_success=(
                f"Marked {expectation.team.value} internal priority {expectation.department_priority.value}"
            ),
        )

        if ticket.assigned_team == expectation.team:
            components["correct_team"] = 0.08
        else:
            outstanding.append(_require_team(expectation))

        ratio, reply_hits, reply_missing = _reply_score(
            ticket,
            [(rule.label, rule.phrases) for rule in expectation.reply_requirements],
        )
        components["reply_quality"] = round(0.15 * ratio, 4)
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
        components["escalation_context"] = round(
            0.16 * (len(escalation_hits) / max(1, len(expectation.escalation_phrase_requirements))),
            4,
        )

        if ticket.current_status == TicketStatus.ESCALATED:
            components["terminal_action"] = 0.16
            satisfied.append("Recovered to a valid engineering escalation")
        else:
            outstanding.append("Finish with a valid engineering escalation")

        if any(
            event.event_type == "escalation_rejected" and event.status == "applied"
            for event in state.pending_events + state.recent_events
        ):
            components["recovery_handled"] = 0.08
            satisfied.append("Recovered after an escalation rejection event")

        if _contains_any(escalation_text, expectation.forbidden_phrases):
            penalties["overpromise"] = 0.10
            violations.append("Promised unsupported outage timing")

        return self._finalize_grade(
            state, components, penalties, satisfied, outstanding, violations
        )


class RefundReopenReviewGrader(BaseTaskGrader):
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
            satisfied.append("Reviewed CRM account context")
        else:
            outstanding.append("Use CRM lookup before resolution")

        if self._action_taken(state, ActionType.CHECK_BILLING_STATUS, expectation.ticket_id):
            components["billing_lookup"] = 0.14
            satisfied.append("Checked billing review state")
        else:
            outstanding.append("Check billing before resolving")

        if self._action_taken(state, ActionType.SEARCH_POLICY, expectation.ticket_id):
            components["policy_lookup"] = 0.12
            satisfied.append("Reviewed the current refund policy")
        else:
            outstanding.append("Search policy guidance before resolving")

        if ticket.current_category == expectation.category:
            components["correct_category"] = 0.08
        else:
            outstanding.append(_require_category(expectation))

        _score_priorities(
            ticket=ticket,
            expectation=expectation,
            total_weight=0.08,
            components=components,
            satisfied=satisfied,
            outstanding=outstanding,
            queue_success=f"Marked queue priority {expectation.priority.value}",
            department_success=(
                f"Marked {expectation.team.value} internal priority {expectation.department_priority.value}"
            ),
        )

        if ticket.assigned_team == expectation.team:
            components["correct_team"] = 0.08
        else:
            outstanding.append(_require_team(expectation))

        ratio, reply_hits, reply_missing = _reply_score(
            ticket,
            [(rule.label, rule.phrases) for rule in expectation.reply_requirements],
        )
        components["reply_quality"] = round(0.18 * ratio, 4)
        for item in reply_hits:
            satisfied.append(f"Reply includes {item}")
        for item in reply_missing:
            outstanding.append(f"Reply should include {item}")

        if (
            ticket.current_status == TicketStatus.RESOLVED
            and ticket.resolution_code == expectation.resolution_code
        ):
            components["resolution"] = 0.14
            satisfied.append("Resolved with the correct refund outcome")
        else:
            outstanding.append(_require_resolution(expectation))

        if any(
            event.event_type == "ticket_reopened" and event.status == "applied"
            for event in state.pending_events + state.recent_events
        ):
            penalties["refund_reopened"] = 0.16
            violations.append("The refund reopened because approval review was skipped")

        if _contains_any(_all_outbound_text(ticket), expectation.forbidden_phrases):
            penalties["unsafe_data_request"] = 0.20
            violations.append("Requested sensitive customer secrets")

        return self._finalize_grade(
            state, components, penalties, satisfied, outstanding, violations
        )


class MixedQueueCommandCenterGrader(BaseTaskGrader):
    def grade(self, state: SupportTriageState) -> GradingSnapshot:
        security_expectation = next(
            expectation
            for expectation in self.scenario.expectations.values()
            if expectation.category == TicketCategory.SECURITY_ACCOUNT_TAKEOVER
        )
        outage_expectation = next(
            expectation
            for expectation in self.scenario.expectations.values()
            if expectation.category == TicketCategory.PRODUCT_BUG
        )
        refund_expectation = next(
            expectation
            for expectation in self.scenario.expectations.values()
            if expectation.category == TicketCategory.BILLING_REFUND
        )
        security_ticket = self._ticket_by_id(state, security_expectation.ticket_id)
        outage_ticket = self._ticket_by_id(state, outage_expectation.ticket_id)
        refund_ticket = self._ticket_by_id(state, refund_expectation.ticket_id)

        components: dict[str, float] = {}
        penalties: dict[str, float] = {}
        satisfied: list[str] = []
        outstanding: list[str] = []
        violations: list[str] = []

        meaningful_actions = [
            entry
            for entry in state.action_history
            if entry.action_type not in {ActionType.VIEW_TICKET, ActionType.FINISH}
        ]
        if meaningful_actions and meaningful_actions[0].ticket_id == security_ticket.ticket_id:
            components["security_first"] = 0.10
            satisfied.append("Opened the queue with the executive security case")
        else:
            penalties["security_priority_miss"] = 0.10
            violations.append("The mixed queue did not start with the executive security case")

        outage_before_refund = False
        first_outage_index = None
        first_refund_index = None
        for index, entry in enumerate(meaningful_actions):
            if entry.ticket_id == outage_ticket.ticket_id and first_outage_index is None:
                first_outage_index = index
            if entry.ticket_id == refund_ticket.ticket_id and first_refund_index is None:
                first_refund_index = index
        if first_outage_index is not None and (
            first_refund_index is None or first_outage_index < first_refund_index
        ):
            outage_before_refund = True
        if outage_before_refund:
            components["outage_before_refund"] = 0.08
            satisfied.append("Handled the live outage before the refund case")
        else:
            penalties["outage_priority_miss"] = 0.08
            violations.append("Worked the refund before stabilizing the live outage")

        if self._action_taken(state, ActionType.CREATE_INCIDENT, outage_ticket.ticket_id):
            components["incident_created"] = 0.10
            satisfied.append("Created an incident for the outage ticket")
        else:
            outstanding.append("Create an incident for the outage ticket")

        if self._action_taken(state, ActionType.CHECK_BILLING_STATUS, refund_ticket.ticket_id):
            components["billing_review"] = 0.08
            satisfied.append("Checked billing before resolving the refund")
        else:
            outstanding.append("Review billing before resolving the refund")

        if self._action_taken(state, ActionType.SEARCH_POLICY, security_ticket.ticket_id):
            components["security_policy_review"] = 0.04
        if self._action_taken(state, ActionType.SEARCH_POLICY, outage_ticket.ticket_id):
            components["outage_policy_review"] = components.get("outage_policy_review", 0.04)
        if self._action_taken(state, ActionType.SEARCH_POLICY, refund_ticket.ticket_id):
            components["refund_policy_review"] = components.get("refund_policy_review", 0.04)

        if security_ticket.current_status == TicketStatus.ESCALATED:
            components["security_terminal"] = 0.10
        else:
            outstanding.append("Escalate the executive security case")

        if outage_ticket.current_status == TicketStatus.ESCALATED:
            components["outage_terminal"] = 0.10
        else:
            outstanding.append("Escalate the outage ticket")

        if (
            refund_ticket.current_status == TicketStatus.RESOLVED
            and refund_ticket.resolution_code == refund_expectation.resolution_code
        ):
            components["refund_terminal"] = 0.10
        else:
            outstanding.append("Resolve the refund ticket with refund_submitted")

        security_ratio, _, security_missing = _reply_score(
            security_ticket,
            [(rule.label, rule.phrases) for rule in security_expectation.reply_requirements],
        )
        outage_ratio, _, outage_missing = _reply_score(
            outage_ticket,
            [(rule.label, rule.phrases) for rule in outage_expectation.reply_requirements],
        )
        refund_ratio, _, refund_missing = _reply_score(
            refund_ticket,
            [(rule.label, rule.phrases) for rule in refund_expectation.reply_requirements],
        )
        components["reply_coverage"] = round(
            0.18 * ((security_ratio + outage_ratio + refund_ratio) / 3),
            4,
        )
        for item in [*security_missing, *outage_missing, *refund_missing]:
            outstanding.append(f"Reply should include {item}")

        if any(
            _contains_any(_all_outbound_text(ticket), expectation.forbidden_phrases)
            for ticket, expectation in [
                (security_ticket, security_expectation),
                (outage_ticket, outage_expectation),
                (refund_ticket, refund_expectation),
            ]
        ):
            penalties["unsafe_workflow"] = 0.12
            violations.append("One or more mixed-queue tickets included unsafe or unsupported guidance")

        return self._finalize_grade(
            state, components, penalties, satisfied, outstanding, violations
        )


class FollowupReprioritizationQueueGrader(BaseTaskGrader):
    def grade(self, state: SupportTriageState) -> GradingSnapshot:
        expectation = next(iter(self.scenario.expectations.values()))
        ticket = self._ticket_by_id(state, expectation.ticket_id)

        components: dict[str, float] = {}
        penalties: dict[str, float] = {}
        satisfied: list[str] = []
        outstanding: list[str] = []
        violations: list[str] = []

        if self._action_taken(state, ActionType.REQUEST_INFO, expectation.ticket_id):
            components["requested_info"] = 0.12
            satisfied.append("Requested the missing outage details")
        else:
            outstanding.append("Request the missing outage details first")

        if any(
            event.event_type == "customer_follow_up" and event.status == "applied"
            for event in state.pending_events + state.recent_events
        ):
            components["followup_received"] = 0.10
            satisfied.append("Processed the customer follow-up event")
        else:
            outstanding.append("Wait for and process the customer follow-up")

        if self._action_taken(state, ActionType.CREATE_INCIDENT, expectation.ticket_id):
            components["incident_created"] = 0.12
        else:
            outstanding.append("Create an incident after the follow-up arrives")

        if ticket.current_category == expectation.category:
            components["correct_category"] = 0.08
        else:
            outstanding.append(_require_category(expectation))

        _score_priorities(
            ticket=ticket,
            expectation=expectation,
            total_weight=0.08,
            components=components,
            satisfied=satisfied,
            outstanding=outstanding,
            queue_success=f"Marked queue priority {expectation.priority.value}",
            department_success=(
                f"Marked {expectation.team.value} internal priority {expectation.department_priority.value}"
            ),
        )

        if ticket.assigned_team == expectation.team:
            components["correct_team"] = 0.08
        else:
            outstanding.append(_require_team(expectation))

        ratio, _, reply_missing = _reply_score(
            ticket,
            [(rule.label, rule.phrases) for rule in expectation.reply_requirements],
        )
        components["reply_quality"] = round(0.18 * ratio, 4)
        for item in reply_missing:
            outstanding.append(f"Reply should include {item}")

        escalation_text = _all_outbound_text(ticket)
        escalation_hits = [
            phrase
            for phrase in expectation.escalation_phrase_requirements
            if _contains_any(escalation_text, [phrase])
        ]
        components["escalation_context"] = round(
            0.14 * (len(escalation_hits) / max(1, len(expectation.escalation_phrase_requirements))),
            4,
        )

        if ticket.current_status == TicketStatus.ESCALATED:
            components["terminal_action"] = 0.10
            satisfied.append("Escalated the outage after the follow-up")
        else:
            outstanding.append("Escalate the outage after the follow-up arrives")

        if not self._action_taken(state, ActionType.REQUEST_INFO, expectation.ticket_id) and self._action_taken(
            state, ActionType.ESCALATE_TICKET, expectation.ticket_id
        ):
            penalties["escalated_without_followup"] = 0.12
            violations.append("Escalated the outage before collecting the missing customer details")

        if _contains_any(escalation_text, expectation.forbidden_phrases):
            penalties["overpromise"] = 0.10
            violations.append("Promised unsupported outage timing")

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
    if "escalation_rejection_recovery" in scenarios:
        graders["escalation_rejection_recovery"] = EscalationRejectionRecoveryGrader(
            scenarios["escalation_rejection_recovery"]
        )
    if "refund_reopen_review" in scenarios:
        graders["refund_reopen_review"] = RefundReopenReviewGrader(
            scenarios["refund_reopen_review"]
        )
    if "mixed_queue_command_center" in scenarios:
        graders["mixed_queue_command_center"] = MixedQueueCommandCenterGrader(
            scenarios["mixed_queue_command_center"]
        )
    if "followup_reprioritization_queue" in scenarios:
        graders["followup_reprioritization_queue"] = FollowupReprioritizationQueueGrader(
            scenarios["followup_reprioritization_queue"]
        )
    return graders
