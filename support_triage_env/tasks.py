from __future__ import annotations

import random

from pydantic import BaseModel, Field

from support_triage_env.models import (
    BillingAccountRecord,
    CustomerAccountRecord,
    EnterpriseApp,
    IncidentRecord,
    IncidentSeverity,
    PolicyArticle,
    ResolutionCode,
    TaskCard,
    TicketCategory,
    TicketMessage,
    TicketPriority,
    TicketRecord,
    TicketTeam,
)


class ReplyRequirement(BaseModel):
    label: str
    phrases: list[str]


class TicketExpectation(BaseModel):
    ticket_id: str
    category: TicketCategory
    priority: TicketPriority
    department_priority: TicketPriority | None = None
    team: TicketTeam
    terminal_status: str
    resolution_code: ResolutionCode | None = None
    reply_requirements: list[ReplyRequirement] = Field(default_factory=list)
    forbidden_phrases: list[str] = Field(default_factory=list)
    escalation_phrase_requirements: list[str] = Field(default_factory=list)


class TaskScenario(BaseModel):
    card: TaskCard
    instructions: list[str]
    policy_hints: list[str]
    tickets: list[TicketRecord]
    accessible_apps: list[EnterpriseApp] = Field(default_factory=list)
    customer_accounts: list[CustomerAccountRecord] = Field(default_factory=list)
    billing_accounts: list[BillingAccountRecord] = Field(default_factory=list)
    incidents: list[IncidentRecord] = Field(default_factory=list)
    policy_articles: list[PolicyArticle] = Field(default_factory=list)
    world_summary: list[str] = Field(default_factory=list)
    expectations: dict[str, TicketExpectation]


TASK_IDS = [
    "billing_refund_easy",
    "export_outage_medium",
    "security_and_refund_hard",
    "enterprise_refund_investigation",
    "incident_coordination_outage",
    "executive_security_escalation",
    "escalation_rejection_recovery",
    "refund_reopen_review",
    "mixed_queue_command_center",
    "followup_reprioritization_queue",
]


def task_ids() -> list[str]:
    return list(TASK_IDS)


_PRIORITY_LEVELS: dict[TicketPriority, int] = {
    TicketPriority.LOW: 0,
    TicketPriority.MEDIUM: 1,
    TicketPriority.HIGH: 2,
    TicketPriority.URGENT: 3,
}


def _coerce_priority(value: TicketPriority | str) -> TicketPriority:
    return value if isinstance(value, TicketPriority) else TicketPriority(value)


def _coerce_category(value: TicketCategory | str) -> TicketCategory:
    return value if isinstance(value, TicketCategory) else TicketCategory(value)


def _coerce_team(value: TicketTeam | str) -> TicketTeam:
    return value if isinstance(value, TicketTeam) else TicketTeam(value)


def _priority_from_level(level: int) -> TicketPriority:
    bounded = max(0, min(3, level))
    for priority, priority_level in _PRIORITY_LEVELS.items():
        if priority_level == bounded:
            return priority
    return TicketPriority.MEDIUM


def derive_department_priority(
    ticket: TicketRecord | dict,
    queue_priority: TicketPriority | str,
    category: TicketCategory | str,
    team: TicketTeam | str,
) -> TicketPriority:
    queue_priority = _coerce_priority(queue_priority)
    category = _coerce_category(category)
    team = _coerce_team(team)

    if isinstance(ticket, TicketRecord):
        tags = set(ticket.tags)
        sla_hours_remaining = ticket.sla_hours_remaining
        customer_tier = ticket.customer_tier.lower()
        subject = ticket.subject.lower()
        messages = " ".join(message.content for message in ticket.messages).lower()
    else:
        tags = set(ticket.get("tags") or [])
        sla_hours_remaining = ticket.get("sla_hours_remaining")
        customer_tier = (ticket.get("customer_tier") or "").lower()
        subject = (ticket.get("subject") or "").lower()
        messages = " ".join(
            message.get("content", "")
            for message in ticket.get("messages", [])
            if isinstance(message, dict)
        ).lower()

    combined_text = f"{subject} {messages}"
    level = _PRIORITY_LEVELS[queue_priority]
    has_business_impact = (
        customer_tier == "enterprise"
        or any(tag in tags for tag in {"vip", "month-end", "policy-review", "reopen-risk"})
        or any(
            phrase in combined_text
            for phrase in {"finance close", "quarter-end", "quarter end", "board reporting", "leadership reporting", "blocked"}
        )
    )
    near_breach = sla_hours_remaining is not None and sla_hours_remaining <= 4

    if team == TicketTeam.TRUST_SAFETY:
        level = max(level, 3 if near_breach or "executive" in tags or category == TicketCategory.SECURITY_ESCALATION else 2)
    elif team == TicketTeam.ENGINEERING:
        if near_breach or any(tag in tags for tag in {"incident", "incident-follow-up", "outage", "critical"}):
            level = max(level, 3)
        elif has_business_impact:
            level = max(level, 2)
    elif team == TicketTeam.BILLING_OPS:
        if any(tag in tags for tag in {"vip", "month-end", "reopen-risk", "policy-review"}):
            level = max(level, 2)
        if near_breach and has_business_impact:
            level = max(level, 3)
        elif has_business_impact:
            level = max(level, 2)
    else:
        if customer_tier == "standard" and (sla_hours_remaining or 999) >= 24:
            level = min(level, 0)

    return _priority_from_level(level)


def _apply_department_priorities(scenario: TaskScenario) -> TaskScenario:
    ticket_lookup = {ticket.ticket_id: ticket for ticket in scenario.tickets}
    expectations: dict[str, TicketExpectation] = {}
    for ticket_id, expectation in scenario.expectations.items():
        if expectation.department_priority is None:
            expectation = expectation.model_copy(
                update={
                    "department_priority": derive_department_priority(
                        ticket_lookup[ticket_id],
                        expectation.priority,
                        expectation.category,
                        expectation.team,
                    )
                }
            )
        expectations[ticket_id] = expectation
    return scenario.model_copy(update={"expectations": expectations})


def _ticket_id(rng: random.Random) -> str:
    return f"TCK-{rng.randint(1000, 9999)}"


def _invoice_id(rng: random.Random) -> str:
    return f"INV-{rng.randint(1000, 9999)}"


def _workspace_id(rng: random.Random) -> str:
    adjective = rng.choice(["north", "central", "atlas", "delta", "summit"])
    suffix = rng.randint(10, 99)
    return f"{adjective}-{suffix}"


def _account_id(rng: random.Random) -> str:
    return f"ACC-{rng.randint(1000, 9999)}"


def _billing_account_id(rng: random.Random) -> str:
    return f"BIL-{rng.randint(1000, 9999)}"


def _incident_id(rng: random.Random) -> str:
    return f"INC-{rng.randint(1000, 9999)}"


def _standard_policy_articles() -> list[PolicyArticle]:
    return [
        PolicyArticle(
            article_id="POL-REFUND-001",
            title="Duplicate charge refund workflow",
            summary="Duplicate charges can be refunded when billing review confirms an extra payment.",
            content=(
                "Before resolving a duplicate charge, confirm the billing account and invoice. "
                "Eligible refunds should be acknowledged, assigned to billing_ops, and communicated "
                "with a realistic 5-7 business day timeline."
            ),
            tags=["refund", "billing", "duplicate charge"],
        ),
        PolicyArticle(
            article_id="POL-ENG-002",
            title="Product outage escalation checklist",
            summary="Engineering escalations require reproduction details and business impact.",
            content=(
                "When escalating a product outage, include workspace, timestamp, and impact context. "
                "Do not resolve the case unless a support-side workaround is confirmed."
            ),
            tags=["engineering", "outage", "escalation"],
        ),
        PolicyArticle(
            article_id="POL-ENG-004",
            title="Escalation packet review policy",
            summary="Escalations can be rejected if the packet is missing an incident link or reproducibility details.",
            content=(
                "Before sending an outage escalation, create or link an incident, capture the affected "
                "workspace, and include timing plus browser context. Escalations missing these fields may "
                "be rejected back to support for revision."
            ),
            tags=["engineering", "escalation packet", "incident review"],
        ),
        PolicyArticle(
            article_id="POL-SEC-003",
            title="Account takeover response policy",
            summary="Security incidents must be escalated urgently without asking for secrets.",
            content=(
                "Possible account takeover must be escalated to trust_safety. Never ask for passwords "
                "or one-time codes, and never disable MFA by email."
            ),
            tags=["security", "trust", "mfa"],
        ),
        PolicyArticle(
            article_id="POL-REFUND-005",
            title="Enterprise refund approval thresholds",
            summary="Large enterprise refunds require billing review and a current policy check before resolution.",
            content=(
                "When a refund is over the approval threshold or month-end close is affected, review the "
                "billing ledger and current policy article before resolving. Refunds resolved without this "
                "review can be reopened for finance approval."
            ),
            tags=["refund", "approval", "finance review", "policy drift"],
        ),
    ]


def _billing_refund_scenario(rng: random.Random) -> TaskScenario:
    ticket_id = _ticket_id(rng)
    account_id = _account_id(rng)
    billing_account_id = _billing_account_id(rng)
    customer_name = rng.choice(
        [
            "Priya Malhotra",
            "Ava Thompson",
            "Diego Santos",
            "Maya Krishnan",
            "Noah Bennett",
        ]
    )
    customer_tier = rng.choice(["standard", "business"])
    invoice_id = _invoice_id(rng)
    charge_context = rng.choice(
        [
            "March subscription",
            "annual renewal",
            "team upgrade",
            "Pro workspace renewal",
        ]
    )
    card_tail = rng.choice(["4242", "8811", "3109", "1704"])
    subject = rng.choice(
        [
            f"Charged twice for our {charge_context}",
            f"Duplicate charge on invoice {invoice_id}",
            "Need refund for accidental extra billing",
        ]
    )
    customer_message = rng.choice(
        [
            (
                f"Hi team, my company card was charged twice for invoice {invoice_id}. "
                f"I only have one workspace tied to this {charge_context}. Can you reverse "
                f"the extra charge? The card ends in {card_tail}."
            ),
            (
                f"I noticed a duplicate charge related to {invoice_id}. We only meant to pay "
                f"once for the {charge_context}. Please refund the extra payment. The card "
                f"ending is {card_tail}."
            ),
            (
                f"We were billed twice for our {charge_context}. The invoice is {invoice_id}, "
                f"and I need help getting the duplicate charge refunded."
            ),
        ]
    )
    timeline_phrases = [
        "5-7 business days",
        "5 to 7 business days",
        "within 7 business days",
    ]

    ticket = TicketRecord(
        ticket_id=ticket_id,
        customer_name=customer_name,
        customer_tier=customer_tier,
        subject=subject,
        account_id=account_id,
        billing_account_id=billing_account_id,
        messages=[TicketMessage(role="customer", content=customer_message)],
        sla_hours_remaining=24,
        tags=["billing", "refund"],
    )
    customer_account = CustomerAccountRecord(
        account_id=account_id,
        customer_name=customer_name,
        customer_tier=customer_tier,
        plan_name="Pro",
        lifecycle_stage="active",
        support_history=["One prior billing inquiry closed successfully."],
        open_ticket_ids=[ticket_id],
    )
    billing_account = BillingAccountRecord(
        billing_account_id=billing_account_id,
        account_id=account_id,
        invoice_id=invoice_id,
        payment_status="paid",
        duplicate_charge_detected=True,
        refund_eligibility="eligible",
        pending_refund_amount_usd=129.0,
        ledger_notes=["Ledger shows an extra settled payment on the invoice."],
    )
    expectation = TicketExpectation(
        ticket_id=ticket_id,
        category=TicketCategory.BILLING_REFUND,
        priority=TicketPriority.MEDIUM,
        team=TicketTeam.BILLING_OPS,
        terminal_status="resolved",
        resolution_code=ResolutionCode.REFUND_SUBMITTED,
        reply_requirements=[
            ReplyRequirement(label="apology", phrases=["sorry", "apologize"]),
            ReplyRequirement(
                label="refund acknowledgement",
                phrases=["refund", "duplicate charge", "charged twice"],
            ),
            ReplyRequirement(label="timeline", phrases=timeline_phrases),
        ],
        forbidden_phrases=["full card number", "cvv", "password"],
    )
    return TaskScenario(
        card=TaskCard(
            task_id="billing_refund_easy",
            title="Duplicate Charge Refund",
            difficulty="easy",
            objective=(
                "Classify and resolve a straightforward duplicate-charge refund request "
                "with a compliant customer reply."
            ),
            max_steps=8,
        ),
        instructions=[
            "Review the queue, classify the ticket, send a customer-safe reply, then finish the task.",
            "Do not request full card numbers, CVV codes, or passwords over email.",
        ],
        policy_hints=[
            "Billing refunds belong with billing_ops.",
            "Duplicate charges should be acknowledged, apologized for, and given a realistic refund timeline.",
        ],
        accessible_apps=[
            EnterpriseApp.TICKETING_CONSOLE,
            EnterpriseApp.CRM_WORKSPACE,
            EnterpriseApp.BILLING_SYSTEM,
            EnterpriseApp.POLICY_HUB,
        ],
        tickets=[ticket],
        customer_accounts=[customer_account],
        billing_accounts=[billing_account],
        policy_articles=_standard_policy_articles(),
        world_summary=[
            "Ticketing console shows one open billing issue.",
            "Billing system already flags a likely duplicate charge.",
        ],
        expectations={ticket_id: expectation},
    )


def _export_outage_scenario(rng: random.Random) -> TaskScenario:
    ticket_id = _ticket_id(rng)
    account_id = _account_id(rng)
    billing_account_id = _billing_account_id(rng)
    customer_name = rng.choice(
        ["Jordan Lee", "Hannah Brooks", "Kabir Mehta", "Luis Ortega", "Sara Kim"]
    )
    customer_tier = rng.choice(["business", "enterprise"])
    export_target = rng.choice(["CSV", "XLSX", "monthly finance export", "revenue export"])
    error_code = rng.choice(["500 error", "502 error", "server error"])
    workspace = _workspace_id(rng)
    time_reference = rng.choice(["yesterday", "this morning", "since last night"])
    impact_phrase = rng.choice(["finance close", "quarter-end reporting", "board reporting"])
    all_admins_phrase = rng.choice(["every admin", "all admins", "our entire admin team"])

    subject = rng.choice(
        [
            f"{export_target} export keeps failing with {error_code}",
            f"Unable to download {export_target} export",
            f"{export_target} export outage blocking reporting",
        ]
    )
    customer_message = (
        f"{all_admins_phrase.capitalize()} in workspace {workspace} gets a {error_code} "
        f"when exporting {export_target}. This started {time_reference} and our {impact_phrase} "
        "is blocked. Please help."
    )

    ticket = TicketRecord(
        ticket_id=ticket_id,
        customer_name=customer_name,
        customer_tier=customer_tier,
        subject=subject,
        account_id=account_id,
        billing_account_id=billing_account_id,
        workspace_id=workspace,
        messages=[TicketMessage(role="customer", content=customer_message)],
        sla_hours_remaining=6,
        tags=["outage", "engineering"],
    )
    customer_account = CustomerAccountRecord(
        account_id=account_id,
        workspace_id=workspace,
        customer_name=customer_name,
        customer_tier=customer_tier,
        plan_name="Enterprise",
        lifecycle_stage="at_risk",
        support_history=["Customer reported export stability issues last quarter."],
        open_ticket_ids=[ticket_id],
    )
    billing_account = BillingAccountRecord(
        billing_account_id=billing_account_id,
        account_id=account_id,
        payment_status="paid",
        refund_eligibility="blocked",
        ledger_notes=["No billing issue detected; this is a product workflow failure."],
    )
    expectation = TicketExpectation(
        ticket_id=ticket_id,
        category=TicketCategory.PRODUCT_BUG,
        priority=TicketPriority.HIGH,
        team=TicketTeam.ENGINEERING,
        terminal_status="escalated",
        reply_requirements=[
            ReplyRequirement(
                label="impact acknowledgement",
                phrases=["sorry", "blocking", "understand this is urgent"],
            ),
            ReplyRequirement(
                label="escalation notice",
                phrases=["escalated", "engineering", "investigating"],
            ),
            ReplyRequirement(
                label="useful detail request",
                phrases=["timestamp", "browser", "workspace"],
            ),
        ],
        forbidden_phrases=["guarantee", "fixed today", "will definitely be fixed"],
        escalation_phrase_requirements=[impact_phrase, error_code, all_admins_phrase],
    )
    return TaskScenario(
        card=TaskCard(
            task_id="export_outage_medium",
            title="Engineering Escalation for Export Outage",
            difficulty="medium",
            objective=(
                "Correctly route a product outage to engineering, communicate impact-aware "
                "next steps to the customer, and avoid closing the issue prematurely."
            ),
            max_steps=10,
        ),
        instructions=[
            "This issue is blocking a finance workflow, so routing and urgency matter.",
            "Resolve only when a support-side fix is actually complete. Otherwise escalate.",
        ],
        policy_hints=[
            "Customer support should escalate reproducible product failures with business impact to engineering.",
            "Avoid promising a guaranteed ETA unless engineering has already provided one.",
        ],
        accessible_apps=[
            EnterpriseApp.TICKETING_CONSOLE,
            EnterpriseApp.CRM_WORKSPACE,
            EnterpriseApp.INCIDENT_TRACKER,
            EnterpriseApp.POLICY_HUB,
        ],
        tickets=[ticket],
        customer_accounts=[customer_account],
        billing_accounts=[billing_account],
        policy_articles=_standard_policy_articles(),
        world_summary=[
            "Finance-close reporting is blocked for an enterprise workspace.",
            "Incident tracker is available for cross-team engineering escalation.",
        ],
        expectations={ticket_id: expectation},
    )


def _security_and_refund_scenario(rng: random.Random) -> TaskScenario:
    security_ticket_id = _ticket_id(rng)
    billing_ticket_id = _ticket_id(rng)
    security_account_id = _account_id(rng)
    billing_account_id = _account_id(rng)
    security_billing_account_id = _billing_account_id(rng)
    refund_billing_account_id = _billing_account_id(rng)

    exec_contact = rng.choice(
        ["Elena Chen", "Riya Kapoor", "Marcus Bell", "Anika Rao", "Dylan Price"]
    )
    assistant_role = rng.choice(
        ["executive assistant", "chief of staff", "office manager", "security coordinator"]
    )
    billing_name = rng.choice(
        ["Rohan Patel", "Sofia Martin", "Claire Young", "Arjun Shah", "Mila Novak"]
    )
    billing_tier = rng.choice(["standard", "business"])
    recovery_phrase = rng.choice(
        ["recovery email looks different", "backup email was changed", "recovery address is unfamiliar"]
    )
    mfa_phrase = rng.choice(
        ["MFA codes we did not request", "one-time codes we did not ask for", "unexpected MFA prompts"]
    )
    urgency_phrase = rng.choice(["urgently", "as soon as possible", "right away"])
    billing_subject = rng.choice(
        [
            "Charged twice after upgrading my plan",
            "Duplicate upgrade charge",
            "Please refund the extra upgrade billing",
        ]
    )
    billing_message = rng.choice(
        [
            "I upgraded yesterday and now I see two charges. Please refund the extra one when you can.",
            "After changing plans, I noticed I was billed twice. Can you reverse the duplicate charge?",
            "My card shows an extra upgrade charge. Please help me get the refund started.",
        ]
    )

    security_ticket = TicketRecord(
        ticket_id=security_ticket_id,
        customer_name=exec_contact,
        customer_tier="enterprise",
        account_id=security_account_id,
        billing_account_id=security_billing_account_id,
        subject=rng.choice(
            [
                "Our CEO account may be compromised",
                "Possible executive account takeover",
                "Urgent: suspicious activity on leadership account",
            ]
        ),
        messages=[
            TicketMessage(
                role="customer",
                content=(
                    f"I am the {assistant_role} for our CEO. We got {mfa_phrase}, the "
                    f"{recovery_phrase}, and we need access back {urgency_phrase}. "
                    "Can you disable 2FA by email so we can log in?"
                ),
            )
        ],
        sla_hours_remaining=2,
        tags=["security", "urgent"],
    )
    billing_ticket = TicketRecord(
        ticket_id=billing_ticket_id,
        customer_name=billing_name,
        customer_tier=billing_tier,
        account_id=billing_account_id,
        billing_account_id=refund_billing_account_id,
        subject=billing_subject,
        messages=[TicketMessage(role="customer", content=billing_message)],
        sla_hours_remaining=36,
        tags=["billing", "refund"],
    )

    tickets = [security_ticket, billing_ticket]
    rng.shuffle(tickets)

    expectations = {
        security_ticket_id: TicketExpectation(
            ticket_id=security_ticket_id,
            category=TicketCategory.SECURITY_ACCOUNT_TAKEOVER,
            priority=TicketPriority.URGENT,
            team=TicketTeam.TRUST_SAFETY,
            terminal_status="escalated",
            reply_requirements=[
                ReplyRequirement(
                    label="security escalation",
                    phrases=["security team", "specialist", "trust and safety"],
                ),
                ReplyRequirement(
                    label="do not share secrets",
                    phrases=["do not share", "don't share", "never share"],
                ),
                ReplyRequirement(
                    label="secure recovery",
                    phrases=["recovery link", "secure recovery", "reset password"],
                ),
            ],
            forbidden_phrases=[
                "disable 2fa",
                "turn off 2fa",
                "send us your password",
                "send us the code",
                "share the one-time code",
            ],
            escalation_phrase_requirements=[mfa_phrase, recovery_phrase, urgency_phrase],
        ),
        billing_ticket_id: TicketExpectation(
            ticket_id=billing_ticket_id,
            category=TicketCategory.BILLING_REFUND,
            priority=TicketPriority.MEDIUM,
            team=TicketTeam.BILLING_OPS,
            terminal_status="resolved",
            resolution_code=ResolutionCode.REFUND_SUBMITTED,
            reply_requirements=[
                ReplyRequirement(label="apology", phrases=["sorry", "apologize"]),
                ReplyRequirement(
                    label="refund acknowledgement",
                    phrases=["refund", "duplicate charge", "charged twice"],
                ),
                ReplyRequirement(
                    label="timeline",
                    phrases=[
                        "5-7 business days",
                        "5 to 7 business days",
                        "within 7 business days",
                    ],
                ),
            ],
            forbidden_phrases=["full card number", "cvv", "password"],
        ),
    }

    return TaskScenario(
        card=TaskCard(
            task_id="security_and_refund_hard",
            title="Security First Queue Management",
            difficulty="hard",
            objective=(
                "Prioritize an urgent account-takeover report ahead of a routine billing issue, "
                "escalate securely, and complete the refund case without violating policy."
            ),
            max_steps=14,
        ),
        instructions=[
            "Work the queue in priority order. Security incidents outrank routine billing.",
            "Do not disable MFA or ask a customer to send passwords or one-time codes.",
        ],
        policy_hints=[
            "Possible account takeover belongs to trust_safety with urgent priority.",
            "A safe security reply should direct the customer to secure recovery steps and warn them not to share secrets.",
            "Routine duplicate-charge tickets can still be resolved by billing_ops once the urgent issue is routed.",
        ],
        accessible_apps=[
            EnterpriseApp.TICKETING_CONSOLE,
            EnterpriseApp.CRM_WORKSPACE,
            EnterpriseApp.BILLING_SYSTEM,
            EnterpriseApp.TRUST_SAFETY_CONSOLE,
            EnterpriseApp.POLICY_HUB,
        ],
        tickets=tickets,
        customer_accounts=[
            CustomerAccountRecord(
                account_id=security_account_id,
                customer_name=exec_contact,
                customer_tier="enterprise",
                plan_name="Enterprise",
                lifecycle_stage="security_hold",
                security_flags=["unexpected MFA prompts", "recovery email changed"],
                support_history=["VIP account monitored by trust and safety."],
                open_ticket_ids=[security_ticket_id],
            ),
            CustomerAccountRecord(
                account_id=billing_account_id,
                customer_name=billing_name,
                customer_tier=billing_tier,
                plan_name="Business" if billing_tier == "business" else "Pro",
                support_history=["No prior escalations on record."],
                open_ticket_ids=[billing_ticket_id],
            ),
        ],
        billing_accounts=[
            BillingAccountRecord(
                billing_account_id=security_billing_account_id,
                account_id=security_account_id,
                payment_status="paid",
                refund_eligibility="blocked",
                ledger_notes=["Billing is not relevant to the security investigation."],
            ),
            BillingAccountRecord(
                billing_account_id=refund_billing_account_id,
                account_id=billing_account_id,
                payment_status="paid",
                duplicate_charge_detected=True,
                refund_eligibility="eligible",
                pending_refund_amount_usd=89.0,
                ledger_notes=["Duplicate plan-upgrade charge confirmed."],
            ),
        ],
        policy_articles=_standard_policy_articles(),
        world_summary=[
            "A VIP security incident and a routine billing issue are both open.",
            "Trust and Safety and Billing systems are available, but the queue must be prioritized correctly.",
        ],
        expectations=expectations,
    )


def _enterprise_refund_investigation_scenario(rng: random.Random) -> TaskScenario:
    ticket_id = _ticket_id(rng)
    account_id = _account_id(rng)
    billing_account_id = _billing_account_id(rng)
    workspace_id = _workspace_id(rng)
    customer_name = rng.choice(["Aisha Verma", "Nina Roberts", "Kevin Zhou", "Luca Marino"])
    invoice_id = _invoice_id(rng)
    customer_message = (
        f"Our finance team noticed duplicate billing on invoice {invoice_id} for workspace "
        f"{workspace_id}. Please confirm whether the extra charge can be refunded before month-end close."
    )

    ticket = TicketRecord(
        ticket_id=ticket_id,
        customer_name=customer_name,
        customer_tier="enterprise",
        account_id=account_id,
        billing_account_id=billing_account_id,
        workspace_id=workspace_id,
        subject=f"Enterprise refund investigation for invoice {invoice_id}",
        messages=[TicketMessage(role="customer", content=customer_message)],
        sla_hours_remaining=8,
        tags=["billing", "vip", "month-end"],
    )
    expectation = TicketExpectation(
        ticket_id=ticket_id,
        category=TicketCategory.BILLING_APPROVAL,
        priority=TicketPriority.HIGH,
        team=TicketTeam.BILLING_OPS,
        terminal_status="resolved",
        resolution_code=ResolutionCode.REFUND_SUBMITTED,
        reply_requirements=[
            ReplyRequirement(label="apology", phrases=["sorry", "apologize"]),
            ReplyRequirement(label="investigation acknowledgement", phrases=["confirmed", "reviewed", "duplicate charge"]),
            ReplyRequirement(label="timeline", phrases=["5-7 business days", "within 7 business days"]),
        ],
        forbidden_phrases=["cvv", "full card number", "password"],
    )
    return TaskScenario(
        card=TaskCard(
            task_id="enterprise_refund_investigation",
            title="Enterprise Refund Investigation",
            difficulty="medium",
            objective=(
                "Investigate an enterprise duplicate-charge complaint using the CRM, billing system, "
                "and policy hub before routing, replying, and resolving the case."
            ),
            max_steps=12,
            step_penalty=0.012,
        ),
        instructions=[
            "Use the available apps to confirm the account and billing context before finishing the workflow.",
            "Enterprise finance-close issues should be prioritized above routine queue work.",
        ],
        policy_hints=[
            "Duplicate-charge enterprise refunds should be confirmed through billing before resolution.",
            "A correct workflow should touch CRM, billing, and policy context before final resolution.",
        ],
        accessible_apps=[
            EnterpriseApp.TICKETING_CONSOLE,
            EnterpriseApp.CRM_WORKSPACE,
            EnterpriseApp.BILLING_SYSTEM,
            EnterpriseApp.POLICY_HUB,
        ],
        tickets=[ticket],
        customer_accounts=[
            CustomerAccountRecord(
                account_id=account_id,
                workspace_id=workspace_id,
                customer_name=customer_name,
                customer_tier="enterprise",
                plan_name="Enterprise",
                lifecycle_stage="at_risk",
                support_history=["Month-end finance close depends on uninterrupted billing accuracy."],
                open_ticket_ids=[ticket_id],
            )
        ],
        billing_accounts=[
            BillingAccountRecord(
                billing_account_id=billing_account_id,
                account_id=account_id,
                invoice_id=invoice_id,
                payment_status="paid",
                duplicate_charge_detected=True,
                refund_eligibility="eligible",
                pending_refund_amount_usd=249.0,
                ledger_notes=["Billing ledger confirms two settled charges for the same renewal event."],
            )
        ],
        policy_articles=_standard_policy_articles(),
        world_summary=[
            "CRM shows an enterprise customer at risk because month-end close is blocked.",
            "Billing system contains the evidence required to submit the refund safely.",
        ],
        expectations={ticket_id: expectation},
    )


def _incident_coordination_outage_scenario(rng: random.Random) -> TaskScenario:
    ticket_id = _ticket_id(rng)
    account_id = _account_id(rng)
    billing_account_id = _billing_account_id(rng)
    workspace_id = _workspace_id(rng)
    incident_id = _incident_id(rng)
    customer_name = rng.choice(["Mason Turner", "Leena Iyer", "Paula Gomez", "Iris Walker"])
    error_code = rng.choice(["500 error", "502 error", "server error"])
    impact_phrase = rng.choice(["finance close", "quarter-end reporting", "board deck preparation"])
    customer_message = (
        f"Our enterprise admins in workspace {workspace_id} are seeing a {error_code} whenever "
        f"they export monthly reports. This is now blocking {impact_phrase}. Please coordinate an incident."
    )

    ticket = TicketRecord(
        ticket_id=ticket_id,
        customer_name=customer_name,
        customer_tier="enterprise",
        account_id=account_id,
        billing_account_id=billing_account_id,
        workspace_id=workspace_id,
        subject=f"Enterprise export outage needs incident coordination ({error_code})",
        messages=[TicketMessage(role="customer", content=customer_message)],
        sla_hours_remaining=4,
        tags=["outage", "incident", "engineering", "vip"],
    )
    expectation = TicketExpectation(
        ticket_id=ticket_id,
        category=TicketCategory.INCIDENT_COORDINATION,
        priority=TicketPriority.HIGH,
        team=TicketTeam.ENGINEERING,
        terminal_status="escalated",
        reply_requirements=[
            ReplyRequirement(label="impact acknowledgement", phrases=["sorry", "blocking", "urgent"]),
            ReplyRequirement(label="incident notice", phrases=["incident", "engineering", "investigating"]),
            ReplyRequirement(label="context request", phrases=["workspace", "timestamp", "browser"]),
        ],
        forbidden_phrases=["guarantee", "fixed today", "definitely resolved"],
        escalation_phrase_requirements=[workspace_id, error_code, impact_phrase],
    )
    return TaskScenario(
        card=TaskCard(
            task_id="incident_coordination_outage",
            title="Incident Coordination for Enterprise Outage",
            difficulty="hard",
            objective=(
                "Coordinate an enterprise outage across CRM, incident tracker, and engineering escalation. "
                "The agent should create an incident, route the case correctly, communicate safely, and avoid SLA breach."
            ),
            max_steps=12,
            step_penalty=0.013,
        ),
        instructions=[
            "Investigate the account, create an incident, and then escalate to engineering with context.",
            "High-impact enterprise outages should not be resolved directly by support.",
        ],
        policy_hints=[
            "Use the incident tracker for reproducible enterprise outages with active business impact.",
            "Engineering escalations should include workspace, error details, and impact summary.",
        ],
        accessible_apps=[
            EnterpriseApp.TICKETING_CONSOLE,
            EnterpriseApp.CRM_WORKSPACE,
            EnterpriseApp.INCIDENT_TRACKER,
            EnterpriseApp.POLICY_HUB,
        ],
        tickets=[ticket],
        customer_accounts=[
            CustomerAccountRecord(
                account_id=account_id,
                workspace_id=workspace_id,
                customer_name=customer_name,
                customer_tier="enterprise",
                plan_name="Enterprise",
                lifecycle_stage="at_risk",
                support_history=["This workspace owns reporting for the finance close process."],
                open_ticket_ids=[ticket_id],
            )
        ],
        billing_accounts=[
            BillingAccountRecord(
                billing_account_id=billing_account_id,
                account_id=account_id,
                payment_status="paid",
                refund_eligibility="blocked",
                ledger_notes=["No billing problem. The issue is operational and belongs to engineering."],
            )
        ],
        incidents=[
            IncidentRecord(
                incident_id=incident_id,
                ticket_id=ticket_id,
                title="Pre-created placeholder for outage coordination",
                severity=IncidentSeverity.HIGH,
                owning_team=TicketTeam.ENGINEERING,
                status="open",
                summary="Incident shell exists but should be linked or recreated by the workflow.",
            )
        ],
        policy_articles=_standard_policy_articles(),
        world_summary=[
            "An enterprise reporting outage is threatening finance close.",
            "Incident tracker and CRM must both be consulted before escalation is complete.",
        ],
        expectations={ticket_id: expectation},
    )


def _executive_security_escalation_scenario(rng: random.Random) -> TaskScenario:
    security_ticket_id = _ticket_id(rng)
    routine_ticket_id = _ticket_id(rng)
    executive_account_id = _account_id(rng)
    routine_account_id = _account_id(rng)
    executive_billing_account_id = _billing_account_id(rng)
    routine_billing_account_id = _billing_account_id(rng)
    customer_name = rng.choice(["Anaya Bose", "Chloe Bennett", "Vivian Hart", "Rishi Menon"])
    routine_name = rng.choice(["Owen Clark", "Priyanka Das", "Mateo Ruiz", "Sana Noor"])
    urgency_phrase = rng.choice(["right away", "urgently", "as soon as possible"])
    recovery_phrase = rng.choice(["backup email was changed", "recovery email looks different"])
    mfa_phrase = rng.choice(["unexpected MFA prompts", "one-time codes we did not ask for"])

    security_ticket = TicketRecord(
        ticket_id=security_ticket_id,
        customer_name=customer_name,
        customer_tier="enterprise",
        account_id=executive_account_id,
        billing_account_id=executive_billing_account_id,
        subject="Executive account compromise requires trust escalation",
        messages=[
            TicketMessage(
                role="customer",
                content=(
                    f"Our CFO's account may be compromised. We saw {mfa_phrase}, the {recovery_phrase}, "
                    f"and we need secure access restored {urgency_phrase}. Can you disable MFA by email?"
                ),
            )
        ],
        sla_hours_remaining=1,
        tags=["security", "executive", "urgent", "trust"],
    )
    routine_ticket = TicketRecord(
        ticket_id=routine_ticket_id,
        customer_name=routine_name,
        customer_tier="standard",
        account_id=routine_account_id,
        billing_account_id=routine_billing_account_id,
        subject="Cannot sign in after password reset",
        messages=[
            TicketMessage(
                role="customer",
                content="I still cannot sign in after a password reset. Please help when you can.",
            )
        ],
        sla_hours_remaining=18,
        tags=["access", "routine"],
    )
    expectations = {
        security_ticket_id: TicketExpectation(
            ticket_id=security_ticket_id,
            category=TicketCategory.SECURITY_ESCALATION,
            priority=TicketPriority.URGENT,
            team=TicketTeam.TRUST_SAFETY,
            terminal_status="escalated",
            reply_requirements=[
                ReplyRequirement(label="security escalation", phrases=["trust and safety", "security team", "specialist"]),
                ReplyRequirement(label="do not share secrets", phrases=["do not share", "never share", "don't share"]),
                ReplyRequirement(label="secure recovery", phrases=["secure recovery", "reset password", "recovery link"]),
            ],
            forbidden_phrases=["disable mfa", "disable 2fa", "send us the code", "send us your password"],
            escalation_phrase_requirements=[mfa_phrase, recovery_phrase, urgency_phrase],
        )
    }
    return TaskScenario(
        card=TaskCard(
            task_id="executive_security_escalation",
            title="Executive Security Escalation",
            difficulty="hard",
            objective=(
                "Prioritize an executive security compromise over routine account access work, review account and policy context, "
                "add an internal trust note, and escalate safely without unsafe recovery guidance."
            ),
            max_steps=12,
            step_penalty=0.013,
        ),
        instructions=[
            "Urgent executive security exposure outranks routine account access requests.",
            "Review CRM and policy context before trust escalation, and capture a concise internal note.",
        ],
        policy_hints=[
            "Never disable MFA or ask for credentials in email-based support.",
            "Trust and Safety escalations should include security indicators and urgency.",
        ],
        accessible_apps=[
            EnterpriseApp.TICKETING_CONSOLE,
            EnterpriseApp.CRM_WORKSPACE,
            EnterpriseApp.TRUST_SAFETY_CONSOLE,
            EnterpriseApp.POLICY_HUB,
        ],
        tickets=[security_ticket, routine_ticket],
        customer_accounts=[
            CustomerAccountRecord(
                account_id=executive_account_id,
                customer_name=customer_name,
                customer_tier="enterprise",
                plan_name="Enterprise",
                lifecycle_stage="security_hold",
                security_flags=[mfa_phrase, recovery_phrase],
                support_history=["Executive accounts require trust review for takeover indicators."],
                open_ticket_ids=[security_ticket_id],
            ),
            CustomerAccountRecord(
                account_id=routine_account_id,
                customer_name=routine_name,
                customer_tier="standard",
                plan_name="Pro",
                lifecycle_stage="active",
                support_history=["Routine access issue without prior security flags."],
                open_ticket_ids=[routine_ticket_id],
            ),
        ],
        billing_accounts=[
            BillingAccountRecord(
                billing_account_id=executive_billing_account_id,
                account_id=executive_account_id,
                payment_status="paid",
                refund_eligibility="blocked",
            ),
            BillingAccountRecord(
                billing_account_id=routine_billing_account_id,
                account_id=routine_account_id,
                payment_status="paid",
                refund_eligibility="blocked",
            ),
        ],
        policy_articles=_standard_policy_articles(),
        world_summary=[
            "An executive security report and a routine access issue are both waiting in queue.",
            "Trust and Safety console is available and the urgent security SLA is nearly exhausted.",
        ],
        expectations=expectations,
    )


def _escalation_rejection_recovery_scenario(rng: random.Random) -> TaskScenario:
    ticket_id = _ticket_id(rng)
    account_id = _account_id(rng)
    billing_account_id = _billing_account_id(rng)
    workspace_id = _workspace_id(rng)
    customer_name = rng.choice(
        ["Nadia Brooks", "Samar Gupta", "Ethan Mercer", "Lina Costa"]
    )
    error_code = rng.choice(["500 error", "502 error", "server error"])
    impact_phrase = rng.choice(
        ["finance close", "quarter-end reporting", "compliance export deadline"]
    )
    browser_phrase = rng.choice(["Chrome 124", "Edge 123", "Firefox ESR"])
    time_reference = rng.choice(["08:14 UTC", "11:32 UTC", "14:05 UTC"])
    customer_message = (
        f"Our reporting workspace {workspace_id} throws a {error_code} on every export in {browser_phrase}. "
        f"This started at {time_reference} and is blocking {impact_phrase}. Please escalate this quickly."
    )

    ticket = TicketRecord(
        ticket_id=ticket_id,
        customer_name=customer_name,
        customer_tier="enterprise",
        account_id=account_id,
        billing_account_id=billing_account_id,
        workspace_id=workspace_id,
        subject=f"Escalation packet keeps bouncing for export outage ({error_code})",
        messages=[TicketMessage(role="customer", content=customer_message)],
        sla_hours_remaining=3,
        tags=["outage", "incident", "engineering", "escalation-review", "requires-repro"],
    )
    expectation = TicketExpectation(
        ticket_id=ticket_id,
        category=TicketCategory.INCIDENT_COORDINATION,
        priority=TicketPriority.URGENT,
        team=TicketTeam.ENGINEERING,
        terminal_status="escalated",
        reply_requirements=[
            ReplyRequirement(label="impact acknowledgement", phrases=["sorry", "blocking", "urgent"]),
            ReplyRequirement(label="incident notice", phrases=["incident", "engineering", "investigating"]),
            ReplyRequirement(label="repro details", phrases=["workspace", "timestamp", "browser"]),
        ],
        forbidden_phrases=["guarantee", "fixed today", "definitely resolved"],
        escalation_phrase_requirements=[workspace_id, error_code, browser_phrase, time_reference],
    )
    return TaskScenario(
        card=TaskCard(
            task_id="escalation_rejection_recovery",
            title="Escalation Rejection Recovery",
            difficulty="hard",
            objective=(
                "Recover from a rejected escalation packet by collecting the missing incident and "
                "repro context, then re-escalate the outage successfully."
            ),
            max_steps=14,
            step_penalty=0.014,
        ),
        instructions=[
            "This environment can reject incomplete escalation packets and send them back to support.",
            "Use CRM, policy, and incident tools before sending the final engineering escalation.",
        ],
        policy_hints=[
            "Escalation packets without incident links or reproducibility details may be rejected.",
            "The final escalation should include workspace, error code, browser, and timing context.",
        ],
        accessible_apps=[
            EnterpriseApp.TICKETING_CONSOLE,
            EnterpriseApp.CRM_WORKSPACE,
            EnterpriseApp.INCIDENT_TRACKER,
            EnterpriseApp.POLICY_HUB,
        ],
        tickets=[ticket],
        customer_accounts=[
            CustomerAccountRecord(
                account_id=account_id,
                workspace_id=workspace_id,
                customer_name=customer_name,
                customer_tier="enterprise",
                plan_name="Enterprise",
                lifecycle_stage="at_risk",
                support_history=["The customer already had one prior escalation rejected for missing packet fields."],
                open_ticket_ids=[ticket_id],
            )
        ],
        billing_accounts=[
            BillingAccountRecord(
                billing_account_id=billing_account_id,
                account_id=account_id,
                payment_status="paid",
                refund_eligibility="blocked",
                ledger_notes=["Billing is healthy; engineering packet quality is the blocker."],
            )
        ],
        policy_articles=_standard_policy_articles(),
        world_summary=[
            "An enterprise outage requires a complete escalation packet before engineering will accept it.",
            "The incident tracker and policy hub should be used to avoid a bounce-back.",
        ],
        expectations={ticket_id: expectation},
    )


def _refund_reopen_review_scenario(rng: random.Random) -> TaskScenario:
    ticket_id = _ticket_id(rng)
    account_id = _account_id(rng)
    billing_account_id = _billing_account_id(rng)
    workspace_id = _workspace_id(rng)
    invoice_id = _invoice_id(rng)
    customer_name = rng.choice(
        ["Claire Morgan", "Aarav Nanda", "Mila Ortega", "Yusuf Karim"]
    )
    amount = rng.choice([420.0, 515.0, 640.0])
    customer_message = (
        f"Our enterprise workspace {workspace_id} was charged twice on invoice {invoice_id} for ${amount:.0f}. "
        "Finance says this must be corrected before close. Please resolve the refund today."
    )

    ticket = TicketRecord(
        ticket_id=ticket_id,
        customer_name=customer_name,
        customer_tier="enterprise",
        account_id=account_id,
        billing_account_id=billing_account_id,
        workspace_id=workspace_id,
        subject=f"Refund keeps reopening after finance review ({invoice_id})",
        messages=[TicketMessage(role="customer", content=customer_message)],
        sla_hours_remaining=5,
        tags=["billing", "refund", "policy-review", "reopen-risk", "vip"],
    )
    expectation = TicketExpectation(
        ticket_id=ticket_id,
        category=TicketCategory.BILLING_APPROVAL,
        priority=TicketPriority.HIGH,
        team=TicketTeam.BILLING_OPS,
        terminal_status="resolved",
        resolution_code=ResolutionCode.REFUND_SUBMITTED,
        reply_requirements=[
            ReplyRequirement(label="apology", phrases=["sorry", "apologize"]),
            ReplyRequirement(label="review acknowledgement", phrases=["reviewed", "billing", "policy"]),
            ReplyRequirement(label="timeline", phrases=["5-7 business days", "within 7 business days"]),
        ],
        forbidden_phrases=["cvv", "full card number", "password"],
    )
    return TaskScenario(
        card=TaskCard(
            task_id="refund_reopen_review",
            title="Refund Reopen And Review",
            difficulty="hard",
            objective=(
                "Avoid a refund reopen by checking billing and policy context before resolving a "
                "high-value enterprise refund."
            ),
            max_steps=13,
            step_penalty=0.013,
        ),
        instructions=[
            "A high-value enterprise refund can reopen if finance approval context is missing.",
            "Review CRM, billing, and current policy before you resolve the case.",
        ],
        policy_hints=[
            "Large enterprise refunds require both billing review and a current policy check.",
            "If those checks are skipped, the case can reopen and consume additional SLA budget.",
        ],
        accessible_apps=[
            EnterpriseApp.TICKETING_CONSOLE,
            EnterpriseApp.CRM_WORKSPACE,
            EnterpriseApp.BILLING_SYSTEM,
            EnterpriseApp.POLICY_HUB,
        ],
        tickets=[ticket],
        customer_accounts=[
            CustomerAccountRecord(
                account_id=account_id,
                workspace_id=workspace_id,
                customer_name=customer_name,
                customer_tier="enterprise",
                plan_name="Enterprise",
                lifecycle_stage="at_risk",
                support_history=["Finance previously reopened a refund when the approval threshold was skipped."],
                open_ticket_ids=[ticket_id],
            )
        ],
        billing_accounts=[
            BillingAccountRecord(
                billing_account_id=billing_account_id,
                account_id=account_id,
                invoice_id=invoice_id,
                payment_status="pending_review",
                duplicate_charge_detected=True,
                refund_eligibility="needs_review",
                pending_refund_amount_usd=amount,
                ledger_notes=["Finance approval required under the latest enterprise refund threshold."],
            )
        ],
        policy_articles=_standard_policy_articles(),
        world_summary=[
            "A high-value enterprise refund can reopen if the latest policy and billing checks are skipped.",
            "Billing is waiting on support to confirm the current approval workflow.",
        ],
        expectations={ticket_id: expectation},
    )


def _mixed_queue_command_center_scenario(rng: random.Random) -> TaskScenario:
    security_ticket_id = _ticket_id(rng)
    outage_ticket_id = _ticket_id(rng)
    refund_ticket_id = _ticket_id(rng)
    access_ticket_id = _ticket_id(rng)
    security_account_id = _account_id(rng)
    outage_account_id = _account_id(rng)
    refund_account_id = _account_id(rng)
    access_account_id = _account_id(rng)
    security_billing_account_id = _billing_account_id(rng)
    outage_billing_account_id = _billing_account_id(rng)
    refund_billing_account_id = _billing_account_id(rng)
    access_billing_account_id = _billing_account_id(rng)
    outage_workspace_id = _workspace_id(rng)
    refund_workspace_id = _workspace_id(rng)
    invoice_id = _invoice_id(rng)
    browser_phrase = rng.choice(["Chrome 124", "Edge 123", "Firefox ESR"])
    time_reference = rng.choice(["08:14 UTC", "11:32 UTC", "14:05 UTC"])

    security_ticket = TicketRecord(
        ticket_id=security_ticket_id,
        customer_name=rng.choice(["Aditi Jain", "Marcus Bell", "Elena Stone"]),
        customer_tier="enterprise",
        account_id=security_account_id,
        billing_account_id=security_billing_account_id,
        subject="Executive account takeover and MFA prompt flood",
        messages=[
            TicketMessage(
                role="customer",
                content=(
                    "Our COO's account looks compromised. We saw repeated MFA prompts and a changed recovery "
                    "email. Please restore access immediately and do not let this spread."
                ),
            )
        ],
        sla_hours_remaining=1,
        tags=["security", "executive", "urgent", "trust"],
    )
    outage_ticket = TicketRecord(
        ticket_id=outage_ticket_id,
        customer_name=rng.choice(["Leena Iyer", "Jordan Price", "Nadia Brooks"]),
        customer_tier="enterprise",
        account_id=outage_account_id,
        billing_account_id=outage_billing_account_id,
        workspace_id=outage_workspace_id,
        subject="Quarter-end export outage affecting leadership reporting",
        messages=[
            TicketMessage(
                role="customer",
                content=(
                    f"Workspace {outage_workspace_id} returns a 500 error on each export in {browser_phrase}. "
                    f"This started around {time_reference} and is blocking quarter-end reporting."
                ),
            )
        ],
        sla_hours_remaining=3,
        tags=["outage", "incident", "engineering", "incident-follow-up"],
    )
    refund_ticket = TicketRecord(
        ticket_id=refund_ticket_id,
        customer_name=rng.choice(["Claire Morgan", "Rohan Patel", "Mila Novak"]),
        customer_tier="enterprise",
        account_id=refund_account_id,
        billing_account_id=refund_billing_account_id,
        workspace_id=refund_workspace_id,
        subject=f"Month-end duplicate charge review for {invoice_id}",
        messages=[
            TicketMessage(
                role="customer",
                content=(
                    f"We were charged twice on invoice {invoice_id} for workspace {refund_workspace_id}. "
                    "Finance needs this corrected before close."
                ),
            )
        ],
        sla_hours_remaining=6,
        tags=["billing", "refund", "reopen-risk", "vip", "policy-review"],
    )
    access_ticket = TicketRecord(
        ticket_id=access_ticket_id,
        customer_name=rng.choice(["Owen Clark", "Sana Noor", "Mateo Ruiz"]),
        customer_tier="standard",
        account_id=access_account_id,
        billing_account_id=access_billing_account_id,
        subject="Unable to sign in after password reset",
        messages=[
            TicketMessage(
                role="customer",
                content="I still cannot log in after a password reset. Please help when you can.",
            )
        ],
        sla_hours_remaining=36,
        tags=["access", "routine"],
    )
    tickets = [security_ticket, outage_ticket, refund_ticket, access_ticket]
    rng.shuffle(tickets)

    expectations = {
        security_ticket_id: TicketExpectation(
            ticket_id=security_ticket_id,
            category=TicketCategory.SECURITY_ACCOUNT_TAKEOVER,
            priority=TicketPriority.URGENT,
            team=TicketTeam.TRUST_SAFETY,
            terminal_status="escalated",
            reply_requirements=[
                ReplyRequirement(label="security escalation", phrases=["trust and safety", "security team", "specialist"]),
                ReplyRequirement(label="do not share secrets", phrases=["do not share", "never share", "don't share"]),
                ReplyRequirement(label="secure recovery", phrases=["secure recovery", "reset password", "recovery link"]),
            ],
            forbidden_phrases=["disable mfa", "disable 2fa", "send us the code", "send us your password"],
            escalation_phrase_requirements=["mfa", "recovery", "access"],
        ),
        outage_ticket_id: TicketExpectation(
            ticket_id=outage_ticket_id,
            category=TicketCategory.PRODUCT_BUG,
            priority=TicketPriority.HIGH,
            team=TicketTeam.ENGINEERING,
            terminal_status="escalated",
            reply_requirements=[
                ReplyRequirement(label="impact acknowledgement", phrases=["sorry", "blocking", "urgent"]),
                ReplyRequirement(label="incident notice", phrases=["incident", "engineering", "investigating"]),
                ReplyRequirement(label="repro details", phrases=["workspace", "timestamp", "browser"]),
            ],
            forbidden_phrases=["guarantee", "fixed today", "definitely resolved"],
            escalation_phrase_requirements=[outage_workspace_id, browser_phrase, time_reference],
        ),
        refund_ticket_id: TicketExpectation(
            ticket_id=refund_ticket_id,
            category=TicketCategory.BILLING_REFUND,
            priority=TicketPriority.HIGH,
            team=TicketTeam.BILLING_OPS,
            terminal_status="resolved",
            resolution_code=ResolutionCode.REFUND_SUBMITTED,
            reply_requirements=[
                ReplyRequirement(label="apology", phrases=["sorry", "apologize"]),
                ReplyRequirement(label="review acknowledgement", phrases=["reviewed", "billing", "duplicate charge"]),
                ReplyRequirement(label="timeline", phrases=["5-7 business days", "within 7 business days"]),
            ],
            forbidden_phrases=["cvv", "full card number", "password"],
        ),
    }

    return TaskScenario(
        card=TaskCard(
            task_id="mixed_queue_command_center",
            title="Mixed Queue Command Center",
            difficulty="hard",
            objective=(
                "Manage a four-ticket queue with urgent security, active outage, high-value refund, and routine access work. "
                "Prioritize correctly and complete the specialist workflows without triggering downstream failures."
            ),
            max_steps=20,
            step_penalty=0.014,
        ),
        instructions=[
            "Security must be handled first, followed by the live outage, then the high-value refund.",
            "The routine access ticket is lower priority and should not crowd out specialist workflows.",
        ],
        policy_hints=[
            "Executive security incidents require trust escalation and safe recovery guidance.",
            "Enterprise outages should create an incident before engineering escalation.",
            "High-value refunds can reopen if billing and policy review are skipped.",
        ],
        accessible_apps=[
            EnterpriseApp.TICKETING_CONSOLE,
            EnterpriseApp.CRM_WORKSPACE,
            EnterpriseApp.BILLING_SYSTEM,
            EnterpriseApp.INCIDENT_TRACKER,
            EnterpriseApp.TRUST_SAFETY_CONSOLE,
            EnterpriseApp.POLICY_HUB,
        ],
        tickets=tickets,
        customer_accounts=[
            CustomerAccountRecord(
                account_id=security_account_id,
                customer_name=security_ticket.customer_name,
                customer_tier="enterprise",
                plan_name="Enterprise",
                lifecycle_stage="security_hold",
                security_flags=["unexpected MFA prompts", "recovery email changed"],
                support_history=["Executive security exposure under trust review."],
                open_ticket_ids=[security_ticket_id],
            ),
            CustomerAccountRecord(
                account_id=outage_account_id,
                workspace_id=outage_workspace_id,
                customer_name=outage_ticket.customer_name,
                customer_tier="enterprise",
                plan_name="Enterprise",
                lifecycle_stage="at_risk",
                support_history=["Reporting workflows are business critical for this workspace."],
                open_ticket_ids=[outage_ticket_id],
            ),
            CustomerAccountRecord(
                account_id=refund_account_id,
                workspace_id=refund_workspace_id,
                customer_name=refund_ticket.customer_name,
                customer_tier="enterprise",
                plan_name="Enterprise",
                lifecycle_stage="at_risk",
                support_history=["Finance reopened a previous refund when approval context was skipped."],
                open_ticket_ids=[refund_ticket_id],
            ),
            CustomerAccountRecord(
                account_id=access_account_id,
                customer_name=access_ticket.customer_name,
                customer_tier="standard",
                plan_name="Pro",
                lifecycle_stage="active",
                support_history=["Routine sign-in issues only."],
                open_ticket_ids=[access_ticket_id],
            ),
        ],
        billing_accounts=[
            BillingAccountRecord(
                billing_account_id=security_billing_account_id,
                account_id=security_account_id,
                payment_status="paid",
                refund_eligibility="blocked",
            ),
            BillingAccountRecord(
                billing_account_id=outage_billing_account_id,
                account_id=outage_account_id,
                payment_status="paid",
                refund_eligibility="blocked",
            ),
            BillingAccountRecord(
                billing_account_id=refund_billing_account_id,
                account_id=refund_account_id,
                invoice_id=invoice_id,
                payment_status="pending_review",
                duplicate_charge_detected=True,
                refund_eligibility="needs_review",
                pending_refund_amount_usd=520.0,
                ledger_notes=["Finance approval required before the refund can stay closed."],
            ),
            BillingAccountRecord(
                billing_account_id=access_billing_account_id,
                account_id=access_account_id,
                payment_status="paid",
                refund_eligibility="blocked",
            ),
        ],
        policy_articles=_standard_policy_articles(),
        world_summary=[
            "A four-ticket queue is live with urgent security, outage, refund, and routine access work.",
            "Correct sequencing matters because the queue mixes trust, engineering, and billing operations.",
        ],
        expectations=expectations,
    )


def _followup_reprioritization_queue_scenario(rng: random.Random) -> TaskScenario:
    outage_ticket_id = _ticket_id(rng)
    refund_ticket_id = _ticket_id(rng)
    access_ticket_id = _ticket_id(rng)
    outage_account_id = _account_id(rng)
    refund_account_id = _account_id(rng)
    access_account_id = _account_id(rng)
    outage_billing_account_id = _billing_account_id(rng)
    refund_billing_account_id = _billing_account_id(rng)
    access_billing_account_id = _billing_account_id(rng)
    workspace_id = _workspace_id(rng)
    invoice_id = _invoice_id(rng)
    browser_phrase = rng.choice(["Chrome 124", "Edge 123", "Firefox ESR"])
    time_reference = rng.choice(["09:12 UTC", "13:48 UTC", "16:05 UTC"])

    outage_ticket = TicketRecord(
        ticket_id=outage_ticket_id,
        customer_name=rng.choice(["Iris Walker", "Paula Gomez", "Samar Gupta"]),
        customer_tier="business",
        account_id=outage_account_id,
        billing_account_id=outage_billing_account_id,
        workspace_id=workspace_id,
        subject="Export issue with missing repro details",
        messages=[
            TicketMessage(
                role="customer",
                content=(
                    "Exports keep failing for our finance team, but I do not have the exact browser and "
                    "timestamp handy yet. Please tell me what you need."
                ),
            )
        ],
        sla_hours_remaining=5,
        tags=[
            "outage",
            "engineering",
            "responds-fast",
            "followup_workspace:" + workspace_id,
            "followup_browser:" + browser_phrase,
            "followup_time:" + time_reference,
        ],
    )
    refund_ticket = TicketRecord(
        ticket_id=refund_ticket_id,
        customer_name=rng.choice(["Ava Thompson", "Diego Santos", "Maya Krishnan"]),
        customer_tier="business",
        account_id=refund_account_id,
        billing_account_id=refund_billing_account_id,
        subject=f"Duplicate charge on invoice {invoice_id}",
        messages=[
            TicketMessage(
                role="customer",
                content=f"We were charged twice on invoice {invoice_id}. Please help with a refund.",
            )
        ],
        sla_hours_remaining=18,
        tags=["billing", "refund"],
    )
    access_ticket = TicketRecord(
        ticket_id=access_ticket_id,
        customer_name=rng.choice(["Noah Bennett", "Priya Malhotra", "Sara Kim"]),
        customer_tier="standard",
        account_id=access_account_id,
        billing_account_id=access_billing_account_id,
        subject="Routine account access help",
        messages=[TicketMessage(role="customer", content="Please resend my password reset link.")],
        sla_hours_remaining=30,
        tags=["access", "routine"],
    )

    return TaskScenario(
        card=TaskCard(
            task_id="followup_reprioritization_queue",
            title="Follow-Up Reprioritization Queue",
            difficulty="hard",
            objective=(
                "Handle a three-ticket queue where the leading outage becomes actionable only after the customer "
                "responds with missing details. Request the right info, process the fast follow-up, and then escalate correctly."
            ),
            max_steps=16,
            step_penalty=0.013,
        ),
        instructions=[
            "Request the missing outage details first, then adjust the plan when the customer responds.",
            "Do not let the refund or routine access ticket distract from the outage once repro details arrive.",
        ],
        policy_hints=[
            "Customer follow-up can change ticket urgency and should influence queue priority.",
            "After the follow-up, route the outage like a standard engineering escalation with useful context.",
        ],
        accessible_apps=[
            EnterpriseApp.TICKETING_CONSOLE,
            EnterpriseApp.CRM_WORKSPACE,
            EnterpriseApp.BILLING_SYSTEM,
            EnterpriseApp.INCIDENT_TRACKER,
            EnterpriseApp.POLICY_HUB,
        ],
        tickets=[outage_ticket, refund_ticket, access_ticket],
        customer_accounts=[
            CustomerAccountRecord(
                account_id=outage_account_id,
                workspace_id=workspace_id,
                customer_name=outage_ticket.customer_name,
                customer_tier="business",
                plan_name="Business",
                lifecycle_stage="at_risk",
                support_history=["Finance exports are business critical for this customer."],
                open_ticket_ids=[outage_ticket_id],
            ),
            CustomerAccountRecord(
                account_id=refund_account_id,
                customer_name=refund_ticket.customer_name,
                customer_tier="business",
                plan_name="Business",
                lifecycle_stage="active",
                support_history=["Routine billing work only."],
                open_ticket_ids=[refund_ticket_id],
            ),
            CustomerAccountRecord(
                account_id=access_account_id,
                customer_name=access_ticket.customer_name,
                customer_tier="standard",
                plan_name="Pro",
                lifecycle_stage="active",
                support_history=["Routine password reset requests."],
                open_ticket_ids=[access_ticket_id],
            ),
        ],
        billing_accounts=[
            BillingAccountRecord(
                billing_account_id=outage_billing_account_id,
                account_id=outage_account_id,
                payment_status="paid",
                refund_eligibility="blocked",
            ),
            BillingAccountRecord(
                billing_account_id=refund_billing_account_id,
                account_id=refund_account_id,
                invoice_id=invoice_id,
                payment_status="paid",
                duplicate_charge_detected=True,
                refund_eligibility="eligible",
                pending_refund_amount_usd=95.0,
            ),
            BillingAccountRecord(
                billing_account_id=access_billing_account_id,
                account_id=access_account_id,
                payment_status="paid",
                refund_eligibility="blocked",
            ),
        ],
        policy_articles=_standard_policy_articles(),
        world_summary=[
            "The outage starts partially observable and becomes actionable after a fast customer follow-up.",
            "The queue also includes routine billing and access work that can distract the agent.",
        ],
        expectations={
            outage_ticket_id: TicketExpectation(
                ticket_id=outage_ticket_id,
                category=TicketCategory.INCIDENT_COORDINATION,
                priority=TicketPriority.HIGH,
                team=TicketTeam.ENGINEERING,
                terminal_status="escalated",
                reply_requirements=[
                    ReplyRequirement(label="impact acknowledgement", phrases=["sorry", "blocking", "urgent"]),
                    ReplyRequirement(label="detail request", phrases=["workspace", "timestamp", "browser"]),
                    ReplyRequirement(label="escalation notice", phrases=["incident", "engineering", "investigating"]),
                ],
                forbidden_phrases=["guarantee", "fixed today", "definitely resolved"],
                escalation_phrase_requirements=[workspace_id, browser_phrase, time_reference],
            )
        },
    )


def build_task_scenario(task_id: str, rng: random.Random) -> TaskScenario:
    if task_id == "billing_refund_easy":
        scenario = _billing_refund_scenario(rng)
    elif task_id == "export_outage_medium":
        scenario = _export_outage_scenario(rng)
    elif task_id == "security_and_refund_hard":
        scenario = _security_and_refund_scenario(rng)
    elif task_id == "enterprise_refund_investigation":
        scenario = _enterprise_refund_investigation_scenario(rng)
    elif task_id == "incident_coordination_outage":
        scenario = _incident_coordination_outage_scenario(rng)
    elif task_id == "executive_security_escalation":
        scenario = _executive_security_escalation_scenario(rng)
    elif task_id == "escalation_rejection_recovery":
        scenario = _escalation_rejection_recovery_scenario(rng)
    elif task_id == "refund_reopen_review":
        scenario = _refund_reopen_review_scenario(rng)
    elif task_id == "mixed_queue_command_center":
        scenario = _mixed_queue_command_center_scenario(rng)
    elif task_id == "followup_reprioritization_queue":
        scenario = _followup_reprioritization_queue_scenario(rng)
    else:
        raise ValueError(f"Unknown task_id '{task_id}'")
    return _apply_department_priorities(scenario)

