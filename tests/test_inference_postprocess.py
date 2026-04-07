from inference import _default_escalation_note, postprocess_action
from support_triage_env.models import SupportTriageAction


def test_postprocess_fills_missing_classification_fields():
    observation = {"progress": {"score": 0.0, "outstanding_requirements": []}}
    state = {
        "task_id": "billing_refund_easy",
        "focused_ticket_id": "TCK-1001",
        "action_history": [],
        "tickets": [
            {
                "ticket_id": "TCK-1001",
                "subject": "Duplicate charge on invoice INV-1001",
                "messages": [
                    {
                        "role": "customer",
                        "content": "We were charged twice and need a refund.",
                    }
                ],
                "current_status": "open",
                "current_category": None,
                "current_priority": None,
                "assigned_team": None,
                "outbound_messages": [],
            }
        ],
    }

    action = SupportTriageAction(
        action_type="classify_ticket",
        ticket_id="TCK-1001",
        category="billing_refund",
        priority="medium",
    )

    processed = postprocess_action(action, observation, state)

    assert processed.team.value == "billing_ops"


def test_postprocess_moves_on_after_repeated_escalation_loop():
    observation = {
        "progress": {
            "score": 0.42,
            "outstanding_requirements": [
                "Set TCK-2002 category to billing_refund",
                "Resolve TCK-2002 with refund_submitted",
            ],
        }
    }
    state = {
        "task_id": "security_and_refund_hard",
        "focused_ticket_id": "TCK-2001",
        "action_history": [
            {
                "action_type": "escalate_ticket",
                "ticket_id": "TCK-2001",
            }
        ],
        "tickets": [
            {
                "ticket_id": "TCK-2001",
                "subject": "Urgent: suspicious activity on leadership account",
                "messages": [
                    {
                        "role": "customer",
                        "content": "We got unexpected MFA prompts and the recovery email looks different.",
                    }
                ],
                "current_status": "escalated",
                "current_category": "security_account_takeover",
                "current_priority": "urgent",
                "assigned_team": "trust_safety",
                "outbound_messages": [
                    "I have escalated this to our security team."
                ],
            },
            {
                "ticket_id": "TCK-2002",
                "subject": "Charged twice after upgrading my plan",
                "messages": [
                    {
                        "role": "customer",
                        "content": "Please refund the duplicate charge.",
                    }
                ],
                "current_status": "open",
                "current_category": None,
                "current_priority": None,
                "assigned_team": None,
                "outbound_messages": [],
            },
        ],
    }

    action = SupportTriageAction(action_type="escalate_ticket", ticket_id="TCK-2001")

    processed = postprocess_action(action, observation, state)

    assert processed.action_type.value == "classify_ticket"
    assert processed.ticket_id == "TCK-2002"
    assert processed.team.value == "billing_ops"


def test_security_escalation_note_keeps_context_without_unsafe_request():
    ticket = {
        "ticket_id": "TCK-3001",
        "subject": "Our CEO account may be compromised",
        "messages": [
            {
                "role": "customer",
                "content": (
                    "We got one-time codes we did not ask for, the backup email was changed, "
                    "and we need access back as soon as possible. Can you disable 2FA by email "
                    "so we can log in?"
                ),
            }
        ],
        "current_status": "in_progress",
        "current_category": "security_account_takeover",
        "current_priority": "urgent",
        "assigned_team": "trust_safety",
        "outbound_messages": [],
    }

    note = _default_escalation_note(ticket)

    assert "one-time codes we did not ask for" in note
    assert "backup email was changed" in note
    assert "as soon as possible" in note
    assert "disable 2fa" not in note.lower()


def test_security_reply_replaces_forbidden_phrase_with_safe_fallback():
    observation = {"progress": {"score": 0.0, "outstanding_requirements": []}}
    state = {
        "task_id": "security_and_refund_hard",
        "focused_ticket_id": "TCK-3001",
        "action_history": [],
        "tickets": [
            {
                "ticket_id": "TCK-3001",
                "subject": "Our CEO account may be compromised",
                "messages": [
                    {
                        "role": "customer",
                        "content": (
                            "We got one-time codes we did not ask for and the backup email was changed."
                        ),
                    }
                ],
                "current_status": "in_progress",
                "current_category": "security_account_takeover",
                "current_priority": "urgent",
                "assigned_team": "trust_safety",
                "outbound_messages": [],
            }
        ],
    }

    action = SupportTriageAction(
        action_type="draft_reply",
        ticket_id="TCK-3001",
        message="Please do not disable 2FA and do not share passwords.",
    )

    processed = postprocess_action(action, observation, state)

    assert "disable 2fa" not in processed.message.lower()
    assert "keep mfa enabled" in processed.message.lower()
