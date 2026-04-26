from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _fmt(value: Any, digits: int = 4) -> str:
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def build_markdown_summary(report: dict[str, Any]) -> str:
    headline = report.get("headline", {})
    environment = report.get("environment", {})
    trained_summary = environment.get("trained_summary", {})
    heuristic_summary = environment.get("heuristic_summary", {})
    trained_per_task = trained_summary.get("per_task", {})
    heuristic_per_task = heuristic_summary.get("per_task", {})

    lines: list[str] = []
    lines.append("# Train And Evaluate Summary")
    lines.append("")
    lines.append("## Headline")
    lines.append("")
    lines.append("| Metric | Baseline | Trained | Delta |")
    lines.append("| --- | --- | --- | --- |")
    lines.append(
        "| Classification accuracy | "
        f"{_fmt(report['classification']['heuristic_accuracy'])} | "
        f"{_fmt(report['classification']['trained_accuracy'])} | "
        f"{_fmt(headline.get('classification_accuracy_delta', 0.0))} |"
    )
    lines.append(
        "| Environment mean score | "
        f"{_fmt(environment.get('heuristic_mean_score', 0.0))} | "
        f"{_fmt(environment.get('trained_mean_score', 0.0))} | "
        f"{_fmt(headline.get('environment_score_delta', 0.0))} |"
    )
    lines.append(
        "| Environment success rate | "
        f"{_fmt(headline.get('heuristic_success_rate', 0.0))} | "
        f"{_fmt(headline.get('trained_success_rate', 0.0))} | "
        f"{_fmt(headline.get('success_rate_delta', 0.0))} |"
    )
    lines.append(
        "| Mean episode steps | "
        f"{_fmt(heuristic_summary.get('mean_steps', 0.0), 2)} | "
        f"{_fmt(trained_summary.get('mean_steps', 0.0), 2)} | "
        f"{_fmt(float(trained_summary.get('mean_steps', 0.0)) - float(heuristic_summary.get('mean_steps', 0.0)), 2)} |"
    )
    lines.append("")
    lines.append("## Evaluation Setup")
    lines.append("")
    lines.append(f"- Tasks: {', '.join(report.get('tasks', []))}")
    lines.append(f"- Eval seeds: {', '.join(str(seed) for seed in report.get('eval_seeds', []))}")
    hard_task_ids = report.get("hard_task_ids") or []
    if hard_task_ids:
        lines.append(f"- Hard-task oversampling: {', '.join(hard_task_ids)} x{report.get('hard_task_multiplier', 1)}")
    lines.append("")
    lines.append("## Per-Task Comparison")
    lines.append("")
    lines.append("| Task | Baseline Score | Trained Score | Baseline Success | Trained Success |")
    lines.append("| --- | --- | --- | --- | --- |")
    for task_id in sorted(trained_per_task):
        trained = trained_per_task.get(task_id, {})
        baseline = heuristic_per_task.get(task_id, {})
        lines.append(
            f"| `{task_id}` | "
            f"{_fmt(baseline.get('mean_score', 0.0))} | "
            f"{_fmt(trained.get('mean_score', 0.0))} | "
            f"{_fmt(baseline.get('success_rate', 0.0))} | "
            f"{_fmt(trained.get('success_rate', 0.0))} |"
        )

    weakest = sorted(
        trained_per_task.items(),
        key=lambda item: (item[1].get("success_rate", 0.0), item[1].get("mean_score", 0.0)),
    )[:3]
    strongest = sorted(
        trained_per_task.items(),
        key=lambda item: (item[1].get("success_rate", 0.0), item[1].get("mean_score", 0.0)),
        reverse=True,
    )[:3]

    lines.append("")
    lines.append("## Quick Read")
    lines.append("")
    lines.append("- Strongest trained tasks:")
    for task_id, summary in strongest:
        lines.append(
            f"  - `{task_id}`: score {_fmt(summary.get('mean_score', 0.0))}, "
            f"success {_fmt(summary.get('success_rate', 0.0))}"
        )
    lines.append("- Weakest trained tasks:")
    for task_id, summary in weakest:
        lines.append(
            f"  - `{task_id}`: score {_fmt(summary.get('mean_score', 0.0))}, "
            f"success {_fmt(summary.get('success_rate', 0.0))}"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--report",
        default="outputs/train_eval_report.json",
        help="Path to the train_and_evaluate JSON report.",
    )
    parser.add_argument(
        "--output",
        default="outputs/train_eval_summary.md",
        help="Where to write the markdown summary.",
    )
    args = parser.parse_args()

    report_path = Path(args.report)
    output_path = Path(args.output)
    report = _load_json(report_path)
    summary = build_markdown_summary(report)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(summary, encoding="utf-8")
    print(json.dumps({"report": str(report_path), "output": str(output_path)}))


if __name__ == "__main__":
    main()
