import inference
from support_triage_env.baseline.run_baseline import DEFAULT_TASKS as BASELINE_TASKS
from support_triage_env.tasks import task_ids


def test_default_task_lists_cover_all_task_families():
    expected = task_ids()

    assert inference.DEFAULT_TASKS == expected
    assert BASELINE_TASKS == expected


def test_normalize_action_payload_keeps_multi_app_fields():
    payload = inference.normalize_action_payload(
        {
            "action_type": "create_incident",
            "ticket_id": "TCK-7311",
            "app": "incident_tracker",
            "team": "engineering",
            "severity": "high",
            "message": "Create incident for export outage",
            "details": {"workspace": "atlas-55"},
            "target_id": "INC-1001",
            "metadata": {"source": "model"},
            "ignored": "drop-me",
        }
    )

    assert payload["app"] == "incident_tracker"
    assert payload["severity"] == "high"
    assert payload["target_id"] == "INC-1001"
    assert payload["details"] == {"workspace": "atlas-55"}
    assert payload["metadata"] == {"source": "model"}
    assert "ignored" not in payload
