from __future__ import annotations

from enum import Enum
from typing import Literal

from openenv.core.env_server.types import Action, Observation, State
from pydantic import BaseModel, Field, field_validator


STRICT_SCORE_EPSILON = 1e-4


def strict_unit_interval(value: float) -> float:
    return round(min(1.0 - STRICT_SCORE_EPSILON, max(STRICT_SCORE_EPSILON, float(value))), 4)


class ActionType(str, Enum):
    VIEW_TICKET = "view_ticket"
    CLASSIFY_TICKET = "classify_ticket"
    DRAFT_REPLY = "draft_reply"
    REQUEST_INFO = "request_info"
    ESCALATE_TICKET = "escalate_ticket"
    RESOLVE_TICKET = "resolve_ticket"
    FINISH = "finish"


class TicketCategory(str, Enum):
    BILLING_REFUND = "billing_refund"
    PRODUCT_BUG = "product_bug"
    SECURITY_ACCOUNT_TAKEOVER = "security_account_takeover"
    ACCOUNT_ACCESS = "account_access"


class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TicketTeam(str, Enum):
    BILLING_OPS = "billing_ops"
    ENGINEERING = "engineering"
    TRUST_SAFETY = "trust_safety"
    CUSTOMER_SUPPORT = "customer_support"


class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_FOR_CUSTOMER = "waiting_for_customer"
    ESCALATED = "escalated"
    RESOLVED = "resolved"


class ResolutionCode(str, Enum):
    REFUND_SUBMITTED = "refund_submitted"
    WORKAROUND_SHARED = "workaround_shared"
    PASSWORD_RESET_SENT = "password_reset_sent"
    NO_ACTION_NEEDED = "no_action_needed"


class TicketMessage(BaseModel):
    role: Literal["customer", "agent", "internal"] = Field(
        ..., description="Who authored the message."
    )
    content: str = Field(..., description="Natural-language ticket message.")


class QueueTicketView(BaseModel):
    ticket_id: str
    customer_name: str
    customer_tier: str
    subject: str
    latest_customer_message: str
    current_status: TicketStatus
    current_category: TicketCategory | None = None
    current_priority: TicketPriority | None = None
    assigned_team: TicketTeam | None = None


class TicketRecord(BaseModel):
    ticket_id: str
    customer_name: str
    customer_tier: str
    subject: str
    messages: list[TicketMessage] = Field(default_factory=list)
    current_status: TicketStatus = TicketStatus.OPEN
    current_category: TicketCategory | None = None
    current_priority: TicketPriority | None = None
    assigned_team: TicketTeam | None = None
    outbound_messages: list[str] = Field(default_factory=list)
    internal_notes: list[str] = Field(default_factory=list)
    requested_information: list[str] = Field(default_factory=list)
    resolution_code: ResolutionCode | None = None

    def to_queue_view(self) -> QueueTicketView:
        latest_customer_message = ""
        for message in reversed(self.messages):
            if message.role == "customer":
                latest_customer_message = message.content
                break
        return QueueTicketView(
            ticket_id=self.ticket_id,
            customer_name=self.customer_name,
            customer_tier=self.customer_tier,
            subject=self.subject,
            latest_customer_message=latest_customer_message,
            current_status=self.current_status,
            current_category=self.current_category,
            current_priority=self.current_priority,
            assigned_team=self.assigned_team,
        )


class TaskCard(BaseModel):
    task_id: str
    title: str
    difficulty: Literal["easy", "medium", "hard"]
    objective: str
    max_steps: int


class GradingSnapshot(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0)
    components: dict[str, float] = Field(default_factory=dict)
    penalties: dict[str, float] = Field(default_factory=dict)
    satisfied_requirements: list[str] = Field(default_factory=list)
    outstanding_requirements: list[str] = Field(default_factory=list)
    violations: list[str] = Field(default_factory=list)

    @field_validator("score", mode="before")
    @classmethod
    def _clamp_score(cls, value: float) -> float:
        return strict_unit_interval(value)


class SupportTriageReward(BaseModel):
    value: float = Field(..., description="Scalar reward for the current step.")
    task_score: float = Field(..., ge=0.0, le=1.0)
    score_delta: float = Field(..., description="Change in graded task score.")
    components: dict[str, float] = Field(default_factory=dict)
    penalties: dict[str, float] = Field(default_factory=dict)
    rationale: list[str] = Field(default_factory=list)

    @field_validator("task_score", mode="before")
    @classmethod
    def _clamp_task_score(cls, value: float) -> float:
        return strict_unit_interval(value)


class ActionLogEntry(BaseModel):
    step_number: int
    action_type: ActionType
    ticket_id: str | None = None
    summary: str


class SupportTriageAction(Action):
    action_type: ActionType = Field(..., description="The operation to perform.")
    ticket_id: str | None = Field(
        default=None, description="Ticket being targeted by the action."
    )
    category: TicketCategory | None = None
    priority: TicketPriority | None = None
    team: TicketTeam | None = None
    message: str | None = Field(
        default=None,
        description="Reply text, internal escalation note, or information request.",
    )
    resolution_code: ResolutionCode | None = None


class SupportTriageObservation(Observation):
    reward: float = 0.0
    done: bool = False
    task: TaskCard
    instructions: list[str] = Field(default_factory=list)
    policy_hints: list[str] = Field(default_factory=list)
    queue: list[QueueTicketView] = Field(default_factory=list)
    focused_ticket: TicketRecord | None = None
    last_action_result: str = ""
    progress: GradingSnapshot = Field(default_factory=lambda: GradingSnapshot(score=0.0001))
    available_actions: list[str] = Field(default_factory=list)


class SupportTriageState(State):
    episode_id: str | None = None
    step_count: int = 0
    task_id: str | None = None
    difficulty: Literal["easy", "medium", "hard"] | None = None
    objective: str = ""
    max_steps: int = 0
    focused_ticket_id: str | None = None
    tickets: list[TicketRecord] = Field(default_factory=list)
    action_history: list[ActionLogEntry] = Field(default_factory=list)
    cumulative_reward: float = 0.0
    final_score: float = 0.0001
    done: bool = False
    progress: GradingSnapshot = Field(default_factory=lambda: GradingSnapshot(score=0.0001))

    @field_validator("final_score", mode="before")
    @classmethod
    def _clamp_final_score(cls, value: float) -> float:
        return strict_unit_interval(value)
