from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate before/after line-chart PNGs from train/eval reports."
    )
    parser.add_argument(
        "--report",
        default="outputs/train_eval_report.json",
        help="Path to the main train/eval report JSON.",
    )
    parser.add_argument(
        "--verify-report",
        default="outputs/train_eval_verify.json",
        help="Optional second report JSON for a smaller verification dashboard.",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs/figures",
        help="Directory where PNG graphs will be written.",
    )
    return parser.parse_args()


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _task_axis(report: dict) -> list[str]:
    return list(report["environment"]["heuristic_summary"]["per_task"].keys())


def _series_from_task_summary(summary: dict, tasks: list[str], key: str) -> list[float]:
    return [summary["per_task"][task][key] for task in tasks]


def _plot_dashboard(report: dict, output_path: Path, title_suffix: str) -> None:
    tasks = _task_axis(report)
    env = report["environment"]
    heuristic_summary = env["heuristic_summary"]
    trained_summary = env["trained_summary"]

    headline_labels = [
        "Classification Accuracy",
        "Mean Env Score",
        "Success Rate",
        "Mean Steps",
    ]
    headline_before = [
        report["classification"]["heuristic_accuracy"],
        env["heuristic_mean_score"],
        heuristic_summary["success_rate"],
        heuristic_summary["mean_steps"],
    ]
    headline_after = [
        report["classification"]["trained_accuracy"],
        env["trained_mean_score"],
        trained_summary["success_rate"],
        trained_summary["mean_steps"],
    ]

    score_before = _series_from_task_summary(heuristic_summary, tasks, "mean_score")
    score_after = _series_from_task_summary(trained_summary, tasks, "mean_score")
    success_before = _series_from_task_summary(heuristic_summary, tasks, "success_rate")
    success_after = _series_from_task_summary(trained_summary, tasks, "success_rate")
    steps_before = _series_from_task_summary(heuristic_summary, tasks, "mean_steps")
    steps_after = _series_from_task_summary(trained_summary, tasks, "mean_steps")

    x_headline = list(range(len(headline_labels)))
    x_tasks = list(range(len(tasks)))

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(18, 11), constrained_layout=True)
    fig.suptitle(f"TriageOS Before vs After Training {title_suffix}", fontsize=18, fontweight="bold")

    ax = axes[0, 0]
    ax.plot(x_headline, headline_before, marker="o", linewidth=2.5, label="Baseline")
    ax.plot(x_headline, headline_after, marker="o", linewidth=2.5, label="Trained")
    ax.set_title("Headline Metrics")
    ax.set_xticks(x_headline)
    ax.set_xticklabels(headline_labels, rotation=15, ha="right")
    ax.legend()

    ax = axes[0, 1]
    ax.plot(x_tasks, score_before, marker="o", linewidth=2.2, label="Baseline")
    ax.plot(x_tasks, score_after, marker="o", linewidth=2.2, label="Trained")
    ax.set_title("Per-Task Mean Score")
    ax.set_xticks(x_tasks)
    ax.set_xticklabels(tasks, rotation=45, ha="right")
    ax.set_ylim(0.0, 1.05)
    ax.legend()

    ax = axes[1, 0]
    ax.plot(x_tasks, success_before, marker="o", linewidth=2.2, label="Baseline")
    ax.plot(x_tasks, success_after, marker="o", linewidth=2.2, label="Trained")
    ax.set_title("Per-Task Success Rate")
    ax.set_xticks(x_tasks)
    ax.set_xticklabels(tasks, rotation=45, ha="right")
    ax.set_ylim(0.0, 1.05)
    ax.legend()

    ax = axes[1, 1]
    ax.plot(x_tasks, steps_before, marker="o", linewidth=2.2, label="Baseline")
    ax.plot(x_tasks, steps_after, marker="o", linewidth=2.2, label="Trained")
    ax.set_title("Per-Task Mean Steps")
    ax.set_xticks(x_tasks)
    ax.set_xticklabels(tasks, rotation=45, ha="right")
    ax.legend()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def _plot_headline_only(report: dict, output_path: Path, title_suffix: str) -> None:
    env = report["environment"]
    heuristic_summary = env["heuristic_summary"]
    trained_summary = env["trained_summary"]
    labels = [
        "Classification Accuracy",
        "Mean Env Score",
        "Success Rate",
        "Mean Steps",
    ]
    before = [
        report["classification"]["heuristic_accuracy"],
        env["heuristic_mean_score"],
        heuristic_summary["success_rate"],
        heuristic_summary["mean_steps"],
    ]
    after = [
        report["classification"]["trained_accuracy"],
        env["trained_mean_score"],
        trained_summary["success_rate"],
        trained_summary["mean_steps"],
    ]

    x = list(range(len(labels)))
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(x, before, marker="o", linewidth=2.8, label="Baseline")
    ax.plot(x, after, marker="o", linewidth=2.8, label="Trained")
    ax.set_title(f"Headline Before/After Metrics {title_suffix}", fontsize=16, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=15, ha="right")
    ax.legend()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    args = _parse_args()
    output_dir = Path(args.output_dir)

    report = _load_json(Path(args.report))
    _plot_dashboard(
        report,
        output_dir / "train_eval_dashboard.png",
        "(Main Evaluation)",
    )
    _plot_headline_only(
        report,
        output_dir / "train_eval_headline.png",
        "(Main Evaluation)",
    )

    verify_path = Path(args.verify_report)
    if verify_path.exists():
        verify_report = _load_json(verify_path)
        _plot_dashboard(
            verify_report,
            output_dir / "train_eval_verify_dashboard.png",
            "(Verification Run)",
        )
        _plot_headline_only(
            verify_report,
            output_dir / "train_eval_verify_headline.png",
            "(Verification Run)",
        )

    print(
        json.dumps(
            {
                "output_dir": str(output_dir),
                "generated": sorted(path.name for path in output_dir.glob("*.png")),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
