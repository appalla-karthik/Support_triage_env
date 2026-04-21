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
]


def task_ids() -> list[str]:
    return list(TASK_IDS)


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
            article_id="POL-SEC-003",
            title="Account takeover response policy",
            summary="Security incidents must be escalated urgently without asking for secrets.",
            content=(
                "Possible account takeover must be escalated to trust_safety. Never ask for passwords "
                "or one-time codes, and never disable MFA by email."
            ),
            tags=["security", "trust", "mfa"],
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
        category=TicketCategory.BILLING_REFUND,
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
        category=TicketCategory.PRODUCT_BUG,
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


def build_task_scenario(task_id: str, rng: random.Random) -> TaskScenario:
    if task_id == "billing_refund_easy":
        return _billing_refund_scenario(rng)
    if task_id == "export_outage_medium":
        return _export_outage_scenario(rng)
    if task_id == "security_and_refund_hard":
        return _security_and_refund_scenario(rng)
    if task_id == "enterprise_refund_investigation":
        return _enterprise_refund_investigation_scenario(rng)
    if task_id == "incident_coordination_outage":
        return _incident_coordination_outage_scenario(rng)
    if task_id == "executive_security_escalation":
        return _executive_security_escalation_scenario(rng)
    raise ValueError(f"Unknown task_id '{task_id}'")

