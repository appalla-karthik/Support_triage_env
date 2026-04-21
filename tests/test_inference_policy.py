from inference import _scripted_policy_action, postprocess_action
from support_triage_env.simulator import SupportTriageSimulator


def _run_scripted_task(task_id: str) -> tuple[float, int]:
    env = SupportTriageSimulator()
    observation = env.reset(task_id=task_id, seed=7)
    done = False

    while not done:
        state = env.state()
        observation_payload = observation.model_dump(mode="json")
        state_payload = state.model_dump(mode="json")
        action = _scripted_policy_action(observation_payload, state_payload)
        assert action is not None
        action = postprocess_action(action, observation_payload, state_payload)
        observation, _, done, _ = env.step(action)

    final_state = env.state()
    return final_state.final_score, final_state.step_count


def test_scripted_policy_solves_billing_refund_easy():
    score, steps = _run_scripted_task("billing_refund_easy")

    assert score == 0.99
    assert steps <= 4


def test_scripted_policy_solves_export_outage_medium():
    score, steps = _run_scripted_task("export_outage_medium")

    assert score == 0.99
    assert steps <= 4


def test_scripted_policy_solves_security_and_refund_hard():
    score, steps = _run_scripted_task("security_and_refund_hard")

    assert score == 0.99
    assert steps <= 7


def test_scripted_policy_solves_enterprise_refund_investigation():
    score, steps = _run_scripted_task("enterprise_refund_investigation")

    assert score >= 0.97
    assert steps <= 7


def test_scripted_policy_solves_incident_coordination_outage():
    score, steps = _run_scripted_task("incident_coordination_outage")

    assert score >= 0.97
    assert steps <= 7


def test_scripted_policy_solves_executive_security_escalation():
    score, steps = _run_scripted_task("executive_security_escalation")

    assert score >= 0.97
    assert steps <= 7
