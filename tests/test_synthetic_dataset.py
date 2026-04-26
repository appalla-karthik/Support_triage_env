from support_triage_env.synthetic_dataset import build_synthetic_dataset


def test_synthetic_dataset_is_reproducible():
    rows_one = build_synthetic_dataset(examples_per_task=2, seed=11)
    rows_two = build_synthetic_dataset(examples_per_task=2, seed=11)
    rows_three = build_synthetic_dataset(examples_per_task=2, seed=12)

    assert rows_one == rows_two
    assert rows_one != rows_three


def test_synthetic_dataset_contains_expected_fields():
    rows = build_synthetic_dataset(examples_per_task=1, seed=3)

    assert len(rows) >= 3
    first = rows[0]
    assert first["dataset_type"] == "support_triage_synthetic"
    assert "task_id" in first
    assert "ticket" in first
    assert "expected" in first
    assert "accessible_apps" in first
    assert "world_summary" in first
    assert "reply_requirements" in first["expected"]
