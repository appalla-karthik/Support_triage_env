from support_triage_env.simulator import SupportTriageSimulator
from support_triage_env.train_and_evaluate import _build_policy_action


def _constant_predictor(_: str) -> str:
    return "billing_refund"


def _run_hybrid_task(task_id: str) -> tuple[float, int]:
    env = SupportTriageSimulator()
    observation = env.reset(task_id=task_id, seed=7)
    done = False

    while not done:
        action = _build_policy_action(
            observation.model_dump(mode="json"),
            env.state().model_dump(mode="json"),
            _constant_predictor,
            use_hybrid_workflow=True,
        )
        observation, _, done, _ = env.step(action)

    final_state = env.state()
    return final_state.final_score, final_state.step_count


def test_hybrid_policy_solves_mixed_queue_command_center():
    score, steps = _run_hybrid_task("mixed_queue_command_center")

    assert score >= 0.95
    assert steps <= 20


def test_hybrid_policy_solves_followup_reprioritization_queue():
    score, steps = _run_hybrid_task("followup_reprioritization_queue")

    assert score >= 0.9
    assert steps <= 12


def test_hybrid_policy_solves_escalation_rejection_recovery():
    score, steps = _run_hybrid_task("escalation_rejection_recovery")

    assert score >= 0.9
    assert steps <= 9
