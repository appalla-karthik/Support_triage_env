from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

from support_triage_env.synthetic_dataset import build_synthetic_dataset


TARGET_LABELS = [
    "billing_approval",
    "billing_refund",
    "incident_coordination",
    "product_bug",
    "security_escalation",
    "security_account_takeover",
    "account_access",
]


def _normalize(text: str) -> str:
    return " ".join((text or "").lower().replace("_", " ").replace("-", " ").split())


def infer_support_label(*parts: str) -> str | None:
    text = " ".join(_normalize(part) for part in parts if part)
    if not text:
        return None

    security_escalation_terms = [
        "trust and safety",
        "executive",
        "board member",
        "urgent security review",
    ]
    security_terms = [
        "account takeover",
        "fraud",
        "unauthorized",
        "security",
        "phishing",
        "mfa",
        "2fa",
        "compromised",
        "one time code",
        "otp",
        "hacked",
    ]
    billing_approval_terms = [
        "approval",
        "finance close",
        "month end",
        "month-end",
        "high value refund",
        "large refund",
        "policy review",
        "finance review",
        "reopen",
    ]
    billing_terms = [
        "refund",
        "charged twice",
        "duplicate charge",
        "billing",
        "invoice",
        "payment",
        "subscription",
        "chargeback",
        "credit card",
        "dispute",
    ]
    incident_coordination_terms = [
        "incident",
        "major outage",
        "sev1",
        "sev 1",
        "bridge call",
        "executive dashboard",
        "enterprise export",
        "cross-team",
    ]
    access_terms = [
        "login",
        "log in",
        "password reset",
        "cannot sign in",
        "account locked",
        "access",
        "recovery email",
        "verification",
        "username",
    ]
    product_terms = [
        "bug",
        "error",
        "500",
        "502",
        "export",
        "crash",
        "broken",
        "outage",
        "not working",
        "issue with app",
        "failed",
    ]

    if any(term in text for term in security_terms):
        if any(term in text for term in security_escalation_terms):
            return "security_escalation"
        return "security_account_takeover"
    if any(term in text for term in billing_approval_terms) and any(
        term in text for term in billing_terms
    ):
        return "billing_approval"
    if any(term in text for term in billing_terms):
        return "billing_refund"
    if any(term in text for term in incident_coordination_terms) and any(
        term in text for term in product_terms
    ):
        return "incident_coordination"
    if any(term in text for term in product_terms):
        return "product_bug"
    if any(term in text for term in access_terms):
        return "account_access"
    return None


def _build_training_row(
    source: str,
    text: str,
    label: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "source": source,
        "text": text.strip(),
        "label": label,
        "metadata": metadata or {},
    }


def _repo_dataset_file(*names: str) -> str | None:
    base = Path(__file__).resolve().parent.parent / "datasets"
    for name in names:
        candidate = base / name
        if candidate.exists():
            return str(candidate)
    return None


def rows_from_synthetic(examples_per_task: int, seed: int) -> list[dict[str, Any]]:
    rows = []
    for example in build_synthetic_dataset(examples_per_task=examples_per_task, seed=seed):
        ticket = example["ticket"]
        expected = example["expected"]
        ticket_text = " ".join(message["content"] for message in ticket["messages"])
        rows.append(
            _build_training_row(
                source="synthetic",
                text=f"{ticket['subject']}\n{ticket_text}",
                label=expected["category"],
                metadata={
                    "task_id": example["task_id"],
                    "difficulty": example["difficulty"],
                    "ticket_id": ticket["ticket_id"],
                    "scenario_seed": example["scenario_seed"],
                },
            )
        )
    return rows


def load_local_customer_support_csv(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for raw in reader:
            subject = raw.get("Ticket Subject") or raw.get("ticket_subject") or ""
            description = (
                raw.get("Ticket Description") or raw.get("ticket_description") or ""
            )
            ticket_type = raw.get("Ticket Type") or raw.get("ticket_type") or ""
            priority = raw.get("Ticket Priority") or raw.get("ticket_priority")
            status = raw.get("Ticket Status") or raw.get("ticket_status")
            channel = raw.get("Ticket Channel") or raw.get("ticket_channel")
            text = f"{subject}\n{description}".strip()
            if not text:
                continue
            label = infer_support_label(ticket_type, subject, description)
            if label is None:
                continue
            rows.append(
                _build_training_row(
                    source="customer_support_tickets",
                    text=text,
                    label=label,
                    metadata={
                        "ticket_type": ticket_type,
                        "priority": priority,
                        "status": status,
                        "channel": channel,
                    },
                )
            )
    return rows


def load_local_customer_support_200k_csv(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for raw in reader:
            category = raw.get("category") or ""
            product = raw.get("product") or ""
            description = raw.get("issue_description") or ""
            resolution_notes = raw.get("resolution_notes") or ""
            text = "\n".join(part for part in [product, category, description] if part).strip()
            if not text:
                continue
            label = infer_support_label(category, description, resolution_notes)
            if label is None:
                continue
            rows.append(
                _build_training_row(
                    source="customer_support_tickets_200k",
                    text=text,
                    label=label,
                    metadata={
                        "category": category,
                        "priority": raw.get("priority"),
                        "status": raw.get("status"),
                        "language": raw.get("language"),
                        "escalated": raw.get("escalated"),
                    },
                )
            )
    return rows


def load_multilingual_support_csv(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for raw in reader:
            text = (raw.get("text") or "").strip()
            queue = raw.get("queue") or ""
            if not text:
                continue
            label = infer_support_label(queue, text)
            if label is None:
                continue
            rows.append(
                _build_training_row(
                    source="multilingual_support",
                    text=text,
                    label=label,
                    metadata={
                        "queue": queue,
                        "priority": raw.get("priority"),
                        "language": raw.get("language"),
                    },
                )
            )
    return rows


def load_ticket_tagger_csv(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader, None)
        for values in reader:
            if len(values) < 2:
                continue
            text, raw_label = values[0].strip(), values[1].strip()
            if not text:
                continue
            label = infer_support_label(raw_label, text)
            if label is None:
                continue
            rows.append(
                _build_training_row(
                    source="ticket_tagger",
                    text=text,
                    label=label,
                    metadata={"raw_label": raw_label, "header": header or []},
                )
            )
    return rows


def load_banking_complaints_csv(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for raw in reader:
            narrative = (
                raw.get("Consumer complaint narrative")
                or raw.get("Consumer_Complaint_Narrative")
                or raw.get("narrative")
                or raw.get("complaint_what_happened")
                or ""
            ).strip()
            issue = raw.get("Issue") or raw.get("issue") or ""
            product = raw.get("Product") or raw.get("product") or ""
            if not narrative:
                continue
            label = infer_support_label(issue, product, narrative)
            if label is None:
                continue
            rows.append(
                _build_training_row(
                    source="banking_complaints",
                    text=f"{product}\n{issue}\n{narrative}",
                    label=label,
                    metadata={"issue": issue, "product": product},
                )
            )
    return rows


def load_complaint_data_csv(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for raw in reader:
            product = raw.get("product") or ""
            narrative = raw.get("narrative") or ""
            if not narrative.strip():
                continue
            label = infer_support_label(product, narrative)
            if label is None:
                continue
            rows.append(
                _build_training_row(
                    source="complaint_data",
                    text=f"{product}\n{narrative}".strip(),
                    label=label,
                    metadata={"product": product},
                )
            )
    return rows


def build_combined_training_dataset(
    synthetic_examples_per_task: int = 1000,
    synthetic_seed: int = 0,
    multilingual_csv: str | None = None,
    ticket_tagger_csv: str | None = None,
    banking_csv: str | None = None,
    customer_support_csv: str | None = None,
    customer_support_200k_csv: str | None = None,
    complaint_data_csv: str | None = None,
) -> list[dict[str, Any]]:
    rows = rows_from_synthetic(
        examples_per_task=synthetic_examples_per_task,
        seed=synthetic_seed,
    )
    if customer_support_csv:
        rows.extend(load_local_customer_support_csv(Path(customer_support_csv)))
    if customer_support_200k_csv:
        rows.extend(load_local_customer_support_200k_csv(Path(customer_support_200k_csv)))
    if multilingual_csv:
        rows.extend(load_multilingual_support_csv(Path(multilingual_csv)))
    if ticket_tagger_csv:
        rows.extend(load_ticket_tagger_csv(Path(ticket_tagger_csv)))
    if banking_csv:
        rows.extend(load_banking_complaints_csv(Path(banking_csv)))
    if complaint_data_csv:
        rows.extend(load_complaint_data_csv(Path(complaint_data_csv)))
    return rows


def save_training_dataset(rows: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")


def summarize_labels(rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(sorted(Counter(row["label"] for row in rows).items()))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--synthetic-examples-per-task", type=int, default=1000)
    parser.add_argument("--synthetic-seed", type=int, default=0)
    parser.add_argument(
        "--customer-support-csv",
        default=_repo_dataset_file("customer_support_tickets.csv"),
    )
    parser.add_argument(
        "--customer-support-200k-csv",
        default=_repo_dataset_file("customer_support_tickets_200k.csv"),
    )
    parser.add_argument("--multilingual-csv", default=None)
    parser.add_argument("--ticket-tagger-csv", default=None)
    parser.add_argument(
        "--banking-csv",
        default=_repo_dataset_file("complaints.csv"),
    )
    parser.add_argument(
        "--complaint-data-csv",
        default=_repo_dataset_file("complaint_data.csv"),
    )
    parser.add_argument(
        "--output",
        default="outputs/combined_training_dataset.jsonl",
    )
    args = parser.parse_args()

    rows = build_combined_training_dataset(
        synthetic_examples_per_task=args.synthetic_examples_per_task,
        synthetic_seed=args.synthetic_seed,
        customer_support_csv=args.customer_support_csv,
        customer_support_200k_csv=args.customer_support_200k_csv,
        multilingual_csv=args.multilingual_csv,
        ticket_tagger_csv=args.ticket_tagger_csv,
        banking_csv=args.banking_csv,
        complaint_data_csv=args.complaint_data_csv,
    )
    output_path = Path(args.output)
    save_training_dataset(rows, output_path)
    print(
        json.dumps(
            {
                "output": str(output_path),
                "rows": len(rows),
                "labels": summarize_labels(rows),
            }
        )
    )


if __name__ == "__main__":
    main()
