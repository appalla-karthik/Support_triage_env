from random import Random

from support_triage_env.tasks import build_task_scenario
from support_triage_env.trajectory_dataset import build_trajectory_dataset


def test_mixed_queue_scenario_contains_expected_archetypes() -> None:
    scenario = build_task_scenario("mixed_queue_command_center", Random(7))
    categories = {expectation.category.value for expectation in scenario.expectations.values()}
    teams = {expectation.team.value for expectation in scenario.expectations.values()}

    assert "security_account_takeover" in categories
    assert "product_bug" in categories
    assert "billing_refund" in categories
    assert "trust_safety" in teams
    assert "engineering" in teams
    assert "billing_ops" in teams


def test_build_trajectory_dataset_sft_smoke_run() -> None:
    rows = build_trajectory_dataset(episodes_per_task=1, seed=7, output_format="sft")

    assert rows
    assert any(row["task_id"] == "mixed_queue_command_center" for row in rows)
    assert all("text" in row for row in rows)
