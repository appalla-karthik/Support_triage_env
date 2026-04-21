from support_triage_env.training_data import (
    _repo_dataset_file,
    build_combined_training_dataset,
    infer_support_label,
)


def test_infer_support_label_covers_enterprise_specialist_categories():
    assert (
        infer_support_label(
            "High value refund approval needed before month-end close",
            "duplicate charge on enterprise invoice",
        )
        == "billing_approval"
    )
    assert (
        infer_support_label(
            "Executive dashboard export outage",
            "please coordinate an incident bridge with engineering",
        )
        == "incident_coordination"
    )
    assert (
        infer_support_label(
            "CEO account showing suspicious MFA prompts",
            "Trust and Safety review required immediately",
        )
        == "security_escalation"
    )


def test_combined_training_dataset_uses_repo_seed_csvs():
    rows = build_combined_training_dataset(
        synthetic_examples_per_task=1,
        synthetic_seed=3,
        customer_support_csv=_repo_dataset_file("customer_support_tickets.csv"),
        customer_support_200k_csv=_repo_dataset_file("customer_support_tickets_200k.csv"),
        banking_csv=_repo_dataset_file("complaints.csv"),
        complaint_data_csv=_repo_dataset_file("complaint_data.csv"),
    )

    labels = {row["label"] for row in rows}
    sources = {row["source"] for row in rows}

    assert "synthetic" in sources
    assert "customer_support_tickets" in sources
    assert "customer_support_tickets_200k" in sources
    assert "banking_complaints" in sources
    assert "complaint_data" in sources
    assert "billing_approval" in labels
    assert "incident_coordination" in labels
    assert "security_escalation" in labels
