from support_triage_env.models import (
    ActionType,
    EnterpriseApp,
    IncidentSeverity,
    ResolutionCode,
    SupportTriageAction,
    TicketCategory,
    TicketPriority,
    TicketStatus,
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
    assert env.state().final_score == 0.99


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


def test_enterprise_refund_task_supports_multi_app_investigation():
    env = SupportTriageSimulator()
    observation = env.reset(task_id="enterprise_refund_investigation", seed=7)
    ticket_id = env.state().tickets[0].ticket_id

    assert EnterpriseApp.CRM_WORKSPACE in observation.accessible_apps
    assert EnterpriseApp.BILLING_SYSTEM in observation.accessible_apps
    assert EnterpriseApp.POLICY_HUB in observation.accessible_apps

    env.step(
        SupportTriageAction(
            action_type=ActionType.LOOKUP_ACCOUNT,
            ticket_id=ticket_id,
            app=EnterpriseApp.CRM_WORKSPACE,
        )
    )
    env.step(
        SupportTriageAction(
            action_type=ActionType.CHECK_BILLING_STATUS,
            ticket_id=ticket_id,
            app=EnterpriseApp.BILLING_SYSTEM,
        )
    )
    env.step(
        SupportTriageAction(
            action_type=ActionType.SEARCH_POLICY,
            ticket_id=ticket_id,
            app=EnterpriseApp.POLICY_HUB,
            message="duplicate charge refund workflow",
        )
    )
    env.step(
        SupportTriageAction(
            action_type=ActionType.CLASSIFY_TICKET,
            ticket_id=ticket_id,
            category=TicketCategory.BILLING_APPROVAL,
            priority=TicketPriority.HIGH,
            team=TicketTeam.BILLING_OPS,
        )
    )
    env.step(
        SupportTriageAction(
            action_type=ActionType.DRAFT_REPLY,
            ticket_id=ticket_id,
            message=(
                "Sorry for the duplicate charge. We reviewed the billing records and confirmed "
                "the extra payment. The refund has been submitted and should appear within 7 business days."
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
    assert env.state().final_score == 0.99
    assert env.state().last_tool_result["app"] == EnterpriseApp.POLICY_HUB.value


def test_create_incident_links_ticket_to_incident_tracker():
    env = SupportTriageSimulator()
    env.reset(task_id="export_outage_medium", seed=7)
    ticket_id = env.state().tickets[0].ticket_id

    observation, _, _, _ = env.step(
        SupportTriageAction(
            action_type=ActionType.CREATE_INCIDENT,
            ticket_id=ticket_id,
            app=EnterpriseApp.INCIDENT_TRACKER,
            team=TicketTeam.ENGINEERING,
            severity=IncidentSeverity.HIGH,
            message="CSV export outage blocking finance close.",
        )
    )

    assert env.state().tickets[0].linked_incident_id is not None
    assert len(env.state().incidents) == 1
    assert env.state().incidents[0].ticket_id == ticket_id
    assert observation.last_tool_result["app"] == EnterpriseApp.INCIDENT_TRACKER.value


def test_incident_coordination_task_rewards_multi_app_outage_workflow():
    env = SupportTriageSimulator()
    env.reset(task_id="incident_coordination_outage", seed=7)
    ticket = env.state().tickets[0]
    ticket_id = ticket.ticket_id
    workspace_id = ticket.workspace_id
    customer_context = ticket.messages[0].content

    env.step(
        SupportTriageAction(
            action_type=ActionType.LOOKUP_ACCOUNT,
            ticket_id=ticket_id,
            app=EnterpriseApp.CRM_WORKSPACE,
        )
    )
    env.step(
        SupportTriageAction(
            action_type=ActionType.SEARCH_POLICY,
            ticket_id=ticket_id,
            app=EnterpriseApp.POLICY_HUB,
            message="product outage escalation checklist",
        )
    )
    env.step(
        SupportTriageAction(
            action_type=ActionType.CREATE_INCIDENT,
            ticket_id=ticket_id,
            app=EnterpriseApp.INCIDENT_TRACKER,
            team=TicketTeam.ENGINEERING,
            severity=IncidentSeverity.HIGH,
            message=customer_context,
        )
    )
    env.step(
        SupportTriageAction(
            action_type=ActionType.CLASSIFY_TICKET,
            ticket_id=ticket_id,
            category=TicketCategory.INCIDENT_COORDINATION,
            priority=TicketPriority.HIGH,
            team=TicketTeam.ENGINEERING,
        )
    )
    env.step(
        SupportTriageAction(
            action_type=ActionType.DRAFT_REPLY,
            ticket_id=ticket_id,
            message=(
                f"Sorry this is blocking your finance close. We opened an incident and escalated the issue "
                f"to engineering for investigation. Please share the workspace {workspace_id}, approximate "
                "timestamp, and browser details so we can keep the incident updated."
            ),
        )
    )
    env.step(
        SupportTriageAction(
            action_type=ActionType.ESCALATE_TICKET,
            ticket_id=ticket_id,
            team=TicketTeam.ENGINEERING,
            message=(
                f"Enterprise outage escalation for workspace {workspace_id}. {customer_context} "
                "Include browser and timestamp in engineering investigation."
            ),
        )
    )
    env.step(SupportTriageAction(action_type=ActionType.FINISH))

    assert env.state().final_score == 0.99
    assert env.state().incidents[-1].status == "investigating"
    assert "active incidents" in " ".join(env.state().world_summary)


def test_executive_security_task_supports_safe_trust_escalation():
    env = SupportTriageSimulator()
    env.reset(task_id="executive_security_escalation", seed=7)
    security_ticket = next(
        ticket
        for ticket in env.state().tickets
        if "security" in ticket.subject.lower() or "executive" in " ".join(ticket.tags).lower()
    )
    security_ticket_id = security_ticket.ticket_id
    customer_context = security_ticket.messages[0].content
    safe_context = customer_context.split("Can you")[0].strip()

    env.step(
        SupportTriageAction(
            action_type=ActionType.LOOKUP_ACCOUNT,
            ticket_id=security_ticket_id,
            app=EnterpriseApp.CRM_WORKSPACE,
        )
    )
    env.step(
        SupportTriageAction(
            action_type=ActionType.SEARCH_POLICY,
            ticket_id=security_ticket_id,
            app=EnterpriseApp.POLICY_HUB,
            message="account takeover response policy",
        )
    )
    env.step(
        SupportTriageAction(
            action_type=ActionType.ADD_INTERNAL_NOTE,
            ticket_id=security_ticket_id,
            app=EnterpriseApp.TRUST_SAFETY_CONSOLE,
            message=f"Trust escalation note: executive account with takeover indicators. {safe_context}",
        )
    )
    env.step(
        SupportTriageAction(
            action_type=ActionType.CLASSIFY_TICKET,
            ticket_id=security_ticket_id,
            category=TicketCategory.SECURITY_ESCALATION,
            priority=TicketPriority.URGENT,
            team=TicketTeam.TRUST_SAFETY,
        )
    )
    env.step(
        SupportTriageAction(
            action_type=ActionType.DRAFT_REPLY,
            ticket_id=security_ticket_id,
            message=(
                "I am sorry you are dealing with this. I have escalated this to our Trust and Safety "
                "specialists and security team. Please do not share passwords or one-time codes, and "
                "use the secure recovery link or password reset flow."
            ),
        )
    )
    env.step(
        SupportTriageAction(
            action_type=ActionType.ESCALATE_TICKET,
            ticket_id=security_ticket_id,
            team=TicketTeam.TRUST_SAFETY,
            message=f"Executive takeover escalation: {safe_context} Keep MFA enabled and continue secure recovery only.",
        )
    )
    env.step(SupportTriageAction(action_type=ActionType.FINISH))

    assert env.state().final_score == 0.99
    assert any(
        "trust" in note.lower()
        for ticket in env.state().tickets
        for note in ticket.internal_notes
    )


def test_queue_progression_decrements_unworked_sla_and_adds_queue_penalties():
    env = SupportTriageSimulator()
    env.reset(task_id="security_and_refund_hard", seed=7)
    security_ticket = next(
        ticket
        for ticket in env.state().tickets
        if "security" in " ".join(ticket.tags).lower()
    )
    billing_ticket = next(
        ticket
        for ticket in env.state().tickets
        if "refund" in " ".join(ticket.tags).lower()
    )

    env.step(
        SupportTriageAction(
            action_type=ActionType.CLASSIFY_TICKET,
            ticket_id=billing_ticket.ticket_id,
            category=TicketCategory.BILLING_REFUND,
            priority=TicketPriority.MEDIUM,
            team=TicketTeam.BILLING_OPS,
        )
    )

    updated_security_ticket = next(
        ticket for ticket in env.state().tickets if ticket.ticket_id == security_ticket.ticket_id
    )
    assert updated_security_ticket.sla_hours_remaining == security_ticket.sla_hours_remaining - 1
    assert "security_exposure" in env.state().progress.penalties


def test_premature_finish_is_penalized_when_work_is_incomplete():
    env = SupportTriageSimulator()
    env.reset(task_id="export_outage_medium", seed=7)

    env.step(SupportTriageAction(action_type=ActionType.FINISH))

    assert "premature_finish" in env.state().progress.penalties


def test_escalation_rejection_recovery_adds_pending_event_and_bounce_back():
    env = SupportTriageSimulator()
    env.reset(task_id="escalation_rejection_recovery", seed=7)
    ticket = env.state().tickets[0]

    env.step(
        SupportTriageAction(
            action_type=ActionType.CLASSIFY_TICKET,
            ticket_id=ticket.ticket_id,
            category=TicketCategory.INCIDENT_COORDINATION,
            priority=TicketPriority.URGENT,
            team=TicketTeam.ENGINEERING,
        )
    )
    env.step(
        SupportTriageAction(
            action_type=ActionType.ESCALATE_TICKET,
            ticket_id=ticket.ticket_id,
            team=TicketTeam.ENGINEERING,
            message="Quick escalation for the export issue.",
        )
    )

    assert "pending_downstream_failure" in env.state().progress.penalties
    assert any(
        event.event_type == "escalation_rejected" and event.status == "pending"
        for event in env.state().pending_events
    )

    env.step(
        SupportTriageAction(action_type=ActionType.VIEW_TICKET, ticket_id=ticket.ticket_id)
    )

    updated_ticket = env.state().tickets[0]
    assert updated_ticket.current_status == TicketStatus.IN_PROGRESS
    assert any(
        event.event_type == "escalation_rejected"
        for event in env.state().recent_events
    )


def test_refund_reopen_review_reopens_after_shortcut_resolution():
    env = SupportTriageSimulator()
    env.reset(task_id="refund_reopen_review", seed=7)
    ticket = env.state().tickets[0]

    env.step(
        SupportTriageAction(
            action_type=ActionType.CLASSIFY_TICKET,
            ticket_id=ticket.ticket_id,
            category=TicketCategory.BILLING_APPROVAL,
            priority=TicketPriority.HIGH,
            team=TicketTeam.BILLING_OPS,
        )
    )
    env.step(
        SupportTriageAction(
            action_type=ActionType.RESOLVE_TICKET,
            ticket_id=ticket.ticket_id,
            resolution_code=ResolutionCode.REFUND_SUBMITTED,
        )
    )

    assert any(
        event.event_type == "ticket_reopened" and event.status == "pending"
        for event in env.state().pending_events
    )
    env.step(
        SupportTriageAction(action_type=ActionType.VIEW_TICKET, ticket_id=ticket.ticket_id)
    )
    reopened_ticket = env.state().tickets[0]
    assert reopened_ticket.current_status == TicketStatus.OPEN
    assert reopened_ticket.resolution_code is None
    assert any(
        event.event_type == "ticket_reopened" for event in env.state().recent_events
    )


def test_followup_reprioritization_queue_emits_customer_followup():
    env = SupportTriageSimulator()
    env.reset(task_id="followup_reprioritization_queue", seed=7)
    outage_ticket = next(
        ticket
        for ticket in env.state().tickets
        if "responds-fast" in ticket.tags
    )

    env.step(
        SupportTriageAction(
            action_type=ActionType.REQUEST_INFO,
            ticket_id=outage_ticket.ticket_id,
            message="Please share the workspace, browser, and approximate timestamp.",
        )
    )

    assert any(
        event.event_type == "customer_follow_up" and event.status == "pending"
        for event in env.state().pending_events
    )

    env.step(
        SupportTriageAction(action_type=ActionType.VIEW_TICKET, ticket_id=outage_ticket.ticket_id)
    )

    updated_ticket = next(
        ticket for ticket in env.state().tickets if ticket.ticket_id == outage_ticket.ticket_id
    )
    assert updated_ticket.current_status == TicketStatus.OPEN
    assert any(
        event.event_type == "customer_follow_up" for event in env.state().recent_events
    )


def test_mixed_queue_command_center_supports_multi_ticket_progression():
    env = SupportTriageSimulator()
    observation = env.reset(task_id="mixed_queue_command_center", seed=7)

    assert len(observation.queue) == 4
    assert EnterpriseApp.TRUST_SAFETY_CONSOLE in observation.accessible_apps
    assert EnterpriseApp.INCIDENT_TRACKER in observation.accessible_apps

    security_ticket = next(
        ticket for ticket in env.state().tickets if "security" in " ".join(ticket.tags).lower()
    )
    refund_ticket = next(
        ticket for ticket in env.state().tickets if "reopen-risk" in ticket.tags
    )

    env.step(
        SupportTriageAction(
            action_type=ActionType.CLASSIFY_TICKET,
            ticket_id=security_ticket.ticket_id,
            category=TicketCategory.SECURITY_ACCOUNT_TAKEOVER,
            priority=TicketPriority.URGENT,
            team=TicketTeam.TRUST_SAFETY,
        )
    )

    assert "security_first" in env.state().progress.components

    env.step(
        SupportTriageAction(
            action_type=ActionType.CLASSIFY_TICKET,
            ticket_id=refund_ticket.ticket_id,
            category=TicketCategory.BILLING_REFUND,
            priority=TicketPriority.HIGH,
            team=TicketTeam.BILLING_OPS,
        )
    )

    assert env.state().progress.penalties.get("outage_priority_miss", 0.0) >= 0.08

