from __future__ import annotations

import random

from pydantic import BaseModel, Field

from support_triage_env.models import (
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
    expectations: dict[str, TicketExpectation]


TASK_IDS = [
    "billing_refund_easy",
    "export_outage_medium",
    "security_and_refund_hard",
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


def _billing_refund_scenario(rng: random.Random) -> TaskScenario:
    ticket_id = _ticket_id(rng)
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
        messages=[TicketMessage(role="customer", content=customer_message)],
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
        tickets=[ticket],
        expectations={ticket_id: expectation},
    )


def _export_outage_scenario(rng: random.Random) -> TaskScenario:
    ticket_id = _ticket_id(rng)
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
        messages=[TicketMessage(role="customer", content=customer_message)],
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
        tickets=[ticket],
        expectations={ticket_id: expectation},
    )


def _security_and_refund_scenario(rng: random.Random) -> TaskScenario:
    security_ticket_id = _ticket_id(rng)
    billing_ticket_id = _ticket_id(rng)

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
    )
    billing_ticket = TicketRecord(
        ticket_id=billing_ticket_id,
        customer_name=billing_name,
        customer_tier=billing_tier,
        subject=billing_subject,
        messages=[TicketMessage(role="customer", content=billing_message)],
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
        tickets=tickets,
        expectations=expectations,
    )


def build_task_scenario(task_id: str, rng: random.Random) -> TaskScenario:
    if task_id == "billing_refund_easy":
        return _billing_refund_scenario(rng)
    if task_id == "export_outage_medium":
        return _export_outage_scenario(rng)
    if task_id == "security_and_refund_hard":
        return _security_and_refund_scenario(rng)
    raise ValueError(f"Unknown task_id '{task_id}'")

