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
    ticket_id = env.state().tickets[0].ticket_id
    env.step(SupportTriageAction(action_type=ActionType.VIEW_TICKET, ticket_id=ticket_id))
    env.step(
        SupportTriageAction(
            action_type=ActionType.CLASSIFY_TICKET,
            ticket_id=ticket_id,
            category=TicketCategory.BILLING_REFUND,
            priority=TicketPriority.MEDIUM,
            team=TicketTeam.BILLING_OPS,
        )
    )
    env.step(
        SupportTriageAction(
            action_type=ActionType.DRAFT_REPLY,
            ticket_id=ticket_id,
            message=(
                "Sorry for the duplicate charge. I have started the refund and you should "
                "see it within 7 business days."
            ),
        )
    )
    env.step(
        SupportTriageAction(
            action_type=ActionType.RESOLVE_TICKET,
            ticket_id=ticket_id,
            resolution_code=ResolutionCode.REFUND_SUBMITTED,
        )
    )
    _, _, done, _ = env.step(SupportTriageAction(action_type=ActionType.FINISH))

    assert done is True
    assert env.state().final_score == 0.9999


def test_medium_task_penalizes_premature_resolution():
    env = SupportTriageSimulator()
    env.reset(task_id="export_outage_medium")
    ticket_id = env.state().tickets[0].ticket_id
    env.step(
        SupportTriageAction(
            action_type=ActionType.CLASSIFY_TICKET,
            ticket_id=ticket_id,
            category=TicketCategory.PRODUCT_BUG,
            priority=TicketPriority.HIGH,
            team=TicketTeam.ENGINEERING,
        )
    )
    env.step(
        SupportTriageAction(
            action_type=ActionType.RESOLVE_TICKET,
            ticket_id=ticket_id,
            resolution_code=ResolutionCode.WORKAROUND_SHARED,
        )
    )

    assert env.state().final_score < 0.5
    assert "premature_resolution" in env.state().progress.penalties


def test_hard_task_requires_urgent_ticket_first():
    env = SupportTriageSimulator()
    env.reset(task_id="security_and_refund_hard")
    billing_ticket_id = next(
        ticket.ticket_id
        for ticket in env.state().tickets
        if "charge" in ticket.subject.lower() or "refund" in ticket.subject.lower()
    )
    env.step(
        SupportTriageAction(
            action_type=ActionType.CLASSIFY_TICKET,
            ticket_id=billing_ticket_id,
            category=TicketCategory.BILLING_REFUND,
            priority=TicketPriority.MEDIUM,
            team=TicketTeam.BILLING_OPS,
        )
    )

    assert env.state().final_score < 0.1
    assert "priority_miss" in env.state().progress.penalties


def test_seeded_reset_is_dynamic_but_reproducible():
    env_one = SupportTriageSimulator()
    first = env_one.reset(task_id="billing_refund_easy", seed=7)

    env_two = SupportTriageSimulator()
    second = env_two.reset(task_id="billing_refund_easy", seed=7)

    env_three = SupportTriageSimulator()
    third = env_three.reset(task_id="billing_refund_easy", seed=8)

    assert first.queue[0].ticket_id == second.queue[0].ticket_id
    assert first.queue[0].subject == second.queue[0].subject
    assert (
        first.queue[0].latest_customer_message
        == second.queue[0].latest_customer_message
    )
    assert (
        first.queue[0].ticket_id != third.queue[0].ticket_id
        or first.queue[0].subject != third.queue[0].subject
        or first.queue[0].latest_customer_message
        != third.queue[0].latest_customer_message
    )


def test_reset_scores_are_strictly_in_range_for_all_tasks():
    from support_triage_env.tasks import task_ids

    for task_id in task_ids():
        env = SupportTriageSimulator()
        observation = env.reset(task_id=task_id, seed=7)

        assert 0.0 < observation.progress.score < 1.0
        assert 0.0 < env.state().progress.score < 1.0

