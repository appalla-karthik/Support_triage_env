from support_triage_env.training_data import (
    build_combined_training_dataset,
    infer_support_label,
)


def test_infer_support_label_maps_core_issue_types():
    assert infer_support_label("duplicate charge refund request") == "billing_refund"
    assert infer_support_label("500 error while exporting csv") == "product_bug"
    assert infer_support_label("unexpected mfa prompt and compromised account") == (
        "security_account_takeover"
    )
    assert infer_support_label("cannot sign in and need password reset") == (
        "account_access"
    )


def test_combined_training_dataset_includes_synthetic_rows():
    rows = build_combined_training_dataset(
        synthetic_examples_per_task=2,
        synthetic_seed=5,
    )

    assert len(rows) >= 6
    assert all("text" in row for row in rows)
    assert all("label" in row for row in rows)
