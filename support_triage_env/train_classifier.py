from __future__ import annotations

import argparse
import json
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from support_triage_env.training_data import (
    _repo_dataset_file,
    build_combined_training_dataset,
    summarize_labels,
)


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
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument(
        "--report-output",
        default="outputs/training_report.json",
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
    texts = [row["text"] for row in rows]
    labels = [row["label"] for row in rows]

    x_train, x_test, y_train, y_test = train_test_split(
        texts,
        labels,
        test_size=args.test_size,
        random_state=args.random_state,
        stratify=labels,
    )

    model = Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=30000)),
            ("clf", LogisticRegression(max_iter=500, class_weight="balanced")),
        ]
    )
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)
    accuracy = accuracy_score(y_test, predictions)
    report = classification_report(y_test, predictions, output_dict=True)

    payload = {
        "rows": len(rows),
        "labels": summarize_labels(rows),
        "accuracy": round(float(accuracy), 4),
        "classification_report": report,
        "train_size": len(x_train),
        "test_size": len(x_test),
    }
    output_path = Path(args.report_output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
