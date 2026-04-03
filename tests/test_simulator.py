from support_triage_env.models import (
    ActionType,
    ResolutionCode,
    SupportTriageAction,
    TicketCategory,
    TicketPriority,
    TicketTeam,
)
from support_triage_env.simulator import SupportTriageSimulator


def test_easy_task_can_reach_full_score():
    env = SupportTriageSimulator()
    env.reset(task_id="billing_refund_easy")
    env.step(SupportTriageAction(action_type=ActionType.VIEW_TICKET, ticket_id="TCK-1001"))
    env.step(
        SupportTriageAction(
            action_type=ActionType.CLASSIFY_TICKET,
            ticket_id="TCK-1001",
            category=TicketCategory.BILLING_REFUND,
            priority=TicketPriority.MEDIUM,
            team=TicketTeam.BILLING_OPS,
        )
    )
    env.step(
        SupportTriageAction(
            action_type=ActionType.DRAFT_REPLY,
            ticket_id="TCK-1001",
            message=(
                "Sorry for the duplicate charge. I have started the refund and you should "
                "see it within 7 business days."
            ),
        )
    )
    env.step(
        SupportTriageAction(
            action_type=ActionType.RESOLVE_TICKET,
            ticket_id="TCK-1001",
            resolution_code=ResolutionCode.REFUND_SUBMITTED,
        )
    )
    _, _, done, _ = env.step(SupportTriageAction(action_type=ActionType.FINISH))

    assert done is True
    assert env.state().final_score == 1.0


def test_medium_task_penalizes_premature_resolution():
    env = SupportTriageSimulator()
    env.reset(task_id="export_outage_medium")
    env.step(
        SupportTriageAction(
            action_type=ActionType.CLASSIFY_TICKET,
            ticket_id="TCK-2001",
            category=TicketCategory.PRODUCT_BUG,
            priority=TicketPriority.HIGH,
            team=TicketTeam.ENGINEERING,
        )
    )
    env.step(
        SupportTriageAction(
            action_type=ActionType.RESOLVE_TICKET,
            ticket_id="TCK-2001",
            resolution_code=ResolutionCode.WORKAROUND_SHARED,
        )
    )

    assert env.state().final_score < 0.5
    assert "premature_resolution" in env.state().progress.penalties


def test_hard_task_requires_urgent_ticket_first():
    env = SupportTriageSimulator()
    env.reset(task_id="security_and_refund_hard")
    env.step(
        SupportTriageAction(
            action_type=ActionType.CLASSIFY_TICKET,
            ticket_id="TCK-3002",
            category=TicketCategory.BILLING_REFUND,
            priority=TicketPriority.MEDIUM,
            team=TicketTeam.BILLING_OPS,
        )
    )

    assert env.state().final_score < 0.1
    assert "priority_miss" in env.state().progress.penalties

