from __future__ import annotations

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


def get_task_scenarios() -> dict[str, TaskScenario]:
    easy = TaskScenario(
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
        tickets=[
            TicketRecord(
                ticket_id="TCK-1001",
                customer_name="Priya Malhotra",
                customer_tier="standard",
                subject="Charged twice for our March subscription",
                messages=[
                    TicketMessage(
                        role="customer",
                        content=(
                            "Hi team, my company card was charged twice for invoice INV-9321. "
                            "I only have one workspace on the Pro plan. Can you reverse the extra "
                            "charge? The card ends in 4242."
                        ),
                    )
                ],
            )
        ],
        expectations={
            "TCK-1001": TicketExpectation(
                ticket_id="TCK-1001",
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
            )
        },
    )

    medium = TaskScenario(
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
        tickets=[
            TicketRecord(
                ticket_id="TCK-2001",
                customer_name="Jordan Lee",
                customer_tier="business",
                subject="CSV export keeps failing with 500 error",
                messages=[
                    TicketMessage(
                        role="customer",
                        content=(
                            "Every admin in our workspace gets a 500 error when exporting CSVs. "
                            "This started yesterday and our finance close is blocked. Please help."
                        ),
                    )
                ],
            )
        ],
        expectations={
            "TCK-2001": TicketExpectation(
                ticket_id="TCK-2001",
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
                escalation_phrase_requirements=[
                    "finance close",
                    "500 error",
                    "all admins",
                ],
            )
        },
    )

    hard = TaskScenario(
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
        tickets=[
            TicketRecord(
                ticket_id="TCK-3001",
                customer_name="Elena Chen",
                customer_tier="enterprise",
                subject="Our CEO account may be compromised",
                messages=[
                    TicketMessage(
                        role="customer",
                        content=(
                            "I am the CEO's executive assistant. We got MFA codes we didn't request, "
                            "the recovery email looks different, and we need access back urgently. "
                            "Can you disable 2FA by email so we can log in?"
                        ),
                    )
                ],
            ),
            TicketRecord(
                ticket_id="TCK-3002",
                customer_name="Rohan Patel",
                customer_tier="standard",
                subject="Charged twice after upgrading my plan",
                messages=[
                    TicketMessage(
                        role="customer",
                        content=(
                            "I upgraded yesterday and now I see two charges. Please refund the extra "
                            "one when you can."
                        ),
                    )
                ],
            ),
        ],
        expectations={
            "TCK-3001": TicketExpectation(
                ticket_id="TCK-3001",
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
                escalation_phrase_requirements=[
                    "mfa codes",
                    "recovery email",
                    "urgent",
                ],
            ),
            "TCK-3002": TicketExpectation(
                ticket_id="TCK-3002",
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
        },
    )

    return {
        easy.card.task_id: easy,
        medium.card.task_id: medium,
        hard.card.task_id: hard,
    }
