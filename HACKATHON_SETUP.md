# Hackathon Setup

This file is the pre-training and pre-submission operating checklist for the project.

## Theme Positioning

- Primary: Theme 3.1 Professional Tasks
- Secondary: Theme 2 Long-Horizon Planning
- Future extension: Theme 1 Multi-Agent Interactions

## Minimum Requirement Status

- OpenEnv environment: present
- `openenv.yaml` manifest: present
- FastAPI server / Space-ready app: present
- Unsloth + TRL notebook: present in `notebooks/triageos_training_colab.ipynb`
- Hugging Face Space URL: `TODO`
- Mini-blog / video / slides: `TODO`

## Required Local Commands

### 1. Verify the environment

```powershell
pytest
openenv validate .
python -m server.app
```

### 2. Generate the weighted evaluation report

```powershell
python -m support_triage_env.train_and_evaluate `
  --synthetic-examples-per-task 300 `
  --synthetic-seed 7 `
  --hard-task-multiplier 5 `
  --eval-seeds 7,11 `
  --report-output outputs/train_eval_report.json `
  --model-output outputs/triageos_classifier.pkl
```

### 3. Turn the JSON report into a judge-friendly markdown summary

```powershell
python -m support_triage_env.report_summary `
  --report outputs/train_eval_report.json `
  --output outputs/train_eval_summary.md
```

### 4. Optional LLM baseline

```powershell
$env:OPENAI_API_KEY="your_key_here"
python -m support_triage_env.baseline.run_baseline `
  --model gpt-4.1-mini-2025-04-14 `
  --seed 7 `
  --output outputs/baseline_scores.json
```

## Artifact Contract

The following files should exist before final submission:

- `outputs/train_eval_report.json`
- `outputs/train_eval_summary.md`
- `outputs/triageos_classifier.pkl`
- `outputs/inference_last_run.json`
- `outputs/baseline_scores.json` if an LLM baseline is used

## What To Put In The README

- Hugging Face Space link
- mini-blog / YouTube / slide link
- before/after table from `outputs/train_eval_report.json`
- one short note on reward-hacking safeguards
- one short note on the hardest remaining tasks

## Current Training Interpretation

The environment already trains well on classification-heavy and medium workflow tasks.
The hardest remaining bottlenecks are:

- `mixed_queue_command_center`
- `followup_reprioritization_queue`
- `escalation_rejection_recovery`

That means the next training emphasis should stay focused on multi-step queue control,
follow-up handling, and delayed-event recovery rather than adding more easy tasks.
