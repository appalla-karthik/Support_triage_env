from __future__ import annotations

from typing import Any
from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

try:
    from openenv.core.env_server.types import Action, Observation, State
except ModuleNotFoundError:
    # Local test fallback when openenv-core is not installed. When the real
    # package is available, these shims are not used.
    class Action(BaseModel):
        metadata: dict = Field(default_factory=dict)

    class Observation(BaseModel):
        metadata: dict = Field(default_factory=dict)

    class State(BaseModel):
        pass


STRICT_SCORE_EPSILON = 0.01


def strict_unit_interval(value: float) -> float:
    return round(min(1.0 - STRICT_SCORE_EPSILON, max(STRICT_SCORE_EPSILON, float(value))), 4)


DEFAULT_STRICT_SCORE = 0.01


class ActionType(str, Enum):
    VIEW_TICKET = "view_ticket"
    CLASSIFY_TICKET = "classify_ticket"
    DRAFT_REPLY = "draft_reply"
    REQUEST_INFO = "request_info"
    ESCALATE_TICKET = "escalate_ticket"
    RESOLVE_TICKET = "resolve_ticket"
    LOOKUP_ACCOUNT = "lookup_account"
    CHECK_BILLING_STATUS = "check_billing_status"
    SEARCH_POLICY = "search_policy"
    CREATE_INCIDENT = "create_incident"
    ADD_INTERNAL_NOTE = "add_internal_note"
    FINISH = "finish"


class EnterpriseApp(str, Enum):
    TICKETING_CONSOLE = "ticketing_console"
    CRM_WORKSPACE = "crm_workspace"
    BILLING_SYSTEM = "billing_system"
    INCIDENT_TRACKER = "incident_tracker"
    TRUST_SAFETY_CONSOLE = "trust_safety_console"
    POLICY_HUB = "policy_hub"


class TicketCategory(str, Enum):
    BILLING_REFUND = "billing_refund"
    BILLING_APPROVAL = "billing_approval"
    PRODUCT_BUG = "product_bug"
    INCIDENT_COORDINATION = "incident_coordination"
    SECURITY_ACCOUNT_TAKEOVER = "security_account_takeover"
    SECURITY_ESCALATION = "security_escalation"
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


class IncidentSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


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
    sla_hours_remaining: int | None = None
    current_category: TicketCategory | None = None
    current_priority: TicketPriority | None = None
    assigned_team: TicketTeam | None = None


class TicketRecord(BaseModel):
    ticket_id: str
    customer_name: str
    customer_tier: str
    subject: str
    account_id: str | None = None
    billing_account_id: str | None = None
    workspace_id: str | None = None
    messages: list[TicketMessage] = Field(default_factory=list)
    current_status: TicketStatus = TicketStatus.OPEN
    sla_hours_remaining: int | None = None
    current_category: TicketCategory | None = None
    current_priority: TicketPriority | None = None
    assigned_team: TicketTeam | None = None
    outbound_messages: list[str] = Field(default_factory=list)
    internal_notes: list[str] = Field(default_factory=list)
    requested_information: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    linked_incident_id: str | None = None
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
            sla_hours_remaining=self.sla_hours_remaining,
            current_category=self.current_category,
            current_priority=self.current_priority,
            assigned_team=self.assigned_team,
        )


class CustomerAccountRecord(BaseModel):
    account_id: str
    workspace_id: str | None = None
    customer_name: str
    customer_tier: str
    plan_name: str
    lifecycle_stage: Literal[
        "active", "at_risk", "security_hold", "past_due", "under_review"
    ] = "active"
    security_flags: list[str] = Field(default_factory=list)
    support_history: list[str] = Field(default_factory=list)
    open_ticket_ids: list[str] = Field(default_factory=list)


class BillingAccountRecord(BaseModel):
    billing_account_id: str
    account_id: str
    invoice_id: str | None = None
    payment_status: Literal["paid", "due", "refunded", "pending_review"] = "paid"
    duplicate_charge_detected: bool = False
    refund_eligibility: Literal["eligible", "needs_review", "blocked"] = "eligible"
    pending_refund_amount_usd: float = 0.0
    ledger_notes: list[str] = Field(default_factory=list)


class IncidentRecord(BaseModel):
    incident_id: str
    ticket_id: str
    title: str
    severity: IncidentSeverity
    owning_team: TicketTeam
    status: Literal["open", "investigating", "mitigated", "resolved"] = "open"
    summary: str = ""


class PolicyArticle(BaseModel):
    article_id: str
    title: str
    app: EnterpriseApp = EnterpriseApp.POLICY_HUB
    summary: str
    content: str
    tags: list[str] = Field(default_factory=list)


class EnterpriseAppSnapshot(BaseModel):
    app: EnterpriseApp
    summary: str
    target_ids: list[str] = Field(default_factory=list)


class WorldEvent(BaseModel):
    event_id: str
    ticket_id: str
    event_type: Literal[
        "customer_follow_up",
        "escalation_rejected",
        "ticket_reopened",
        "incident_update",
        "policy_drift",
    ]
    trigger_step: int
    status: Literal["pending", "applied"] = "pending"
    message: str


class TaskCard(BaseModel):
    task_id: str
    title: str
    difficulty: Literal["easy", "medium", "hard"]
    objective: str
    max_steps: int
    step_penalty: float = Field(default=0.01, ge=0.0, le=0.1)


class GradingSnapshot(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    score: float = Field(default=0.01, gt=0.0, lt=1.0)
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
    model_config = ConfigDict(validate_assignment=True)

    value: float = Field(..., description="Scalar reward for the current step.")
    task_score: float = Field(default=0.01, gt=0.0, lt=1.0)
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
    app: EnterpriseApp | None = None
    target_id: str | None = None
    summary: str


class SupportTriageAction(Action):
    action_type: ActionType = Field(..., description="The operation to perform.")
    ticket_id: str | None = Field(
        default=None, description="Ticket being targeted by the action."
    )
    category: TicketCategory | None = None
    priority: TicketPriority | None = None
    team: TicketTeam | None = None
    app: EnterpriseApp | None = None
    target_id: str | None = None
    message: str | None = Field(
        default=None,
        description="Reply text, internal escalation note, or information request.",
    )
    severity: IncidentSeverity | None = None
    details: dict[str, Any] | None = None
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
    accessible_apps: list[EnterpriseApp] = Field(default_factory=list)
    app_snapshots: list[EnterpriseAppSnapshot] = Field(default_factory=list)
    world_summary: list[str] = Field(default_factory=list)
    recent_events: list[WorldEvent] = Field(default_factory=list)
    last_tool_result: dict[str, Any] | None = None
    progress: GradingSnapshot = Field(
        default_factory=lambda: GradingSnapshot(score=DEFAULT_STRICT_SCORE)
    )
    available_actions: list[str] = Field(default_factory=list)


class SupportTriageState(State):
    model_config = ConfigDict(validate_assignment=True)

    episode_id: str | None = None
    step_count: int = 0
    task_id: str | None = None
    difficulty: Literal["easy", "medium", "hard"] | None = None
    objective: str = ""
    max_steps: int = 0
    focused_ticket_id: str | None = None
    accessible_apps: list[EnterpriseApp] = Field(default_factory=list)
    tickets: list[TicketRecord] = Field(default_factory=list)
    customer_accounts: list[CustomerAccountRecord] = Field(default_factory=list)
    billing_accounts: list[BillingAccountRecord] = Field(default_factory=list)
    incidents: list[IncidentRecord] = Field(default_factory=list)
    policy_articles: list[PolicyArticle] = Field(default_factory=list)
    world_summary: list[str] = Field(default_factory=list)
    pending_events: list[WorldEvent] = Field(default_factory=list)
    recent_events: list[WorldEvent] = Field(default_factory=list)
    last_tool_result: dict[str, Any] | None = None
    action_history: list[ActionLogEntry] = Field(default_factory=list)
    cumulative_reward: float = 0.0
    final_score: float = DEFAULT_STRICT_SCORE
    done: bool = False
    progress: GradingSnapshot = Field(
        default_factory=lambda: GradingSnapshot(score=DEFAULT_STRICT_SCORE)
    )

    @field_validator("final_score", mode="before")
    @classmethod
    def _clamp_final_score(cls, value: float) -> float:
        return strict_unit_interval(value)
