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

## Recommended Hugging Face Final Run

After the local report and balanced SFT dataset are ready, the cleanest final run path is:

1. Upload the balanced SFT dataset to a Hugging Face dataset repo.
2. Launch the script-based Unsloth run on Hugging Face Jobs.
3. Save the final adapter and plots, then link them from the README.

### Prepare the balanced dataset locally

Expected final SFT file:

- `outputs/synthetic_trajectory_sft_30k_balanced.jsonl`

### Upload the dataset to Hugging Face

```bash
hf auth login
hf repo create <your-username>/support-triage-sft --type dataset
hf upload <your-username>/support-triage-sft outputs/synthetic_trajectory_sft_30k_balanced.jsonl data/train.jsonl
```

### Launch the full run with Hugging Face Jobs

`train_unsloth_sft.py` is included in the repo for this purpose.

```bash
hf jobs uv run ^
  --flavor t4-medium ^
  --timeout 4h ^
  --secrets HF_TOKEN ^
  --with unsloth ^
  --with trl ^
  --with datasets ^
  --with accelerate ^
  --with bitsandbytes ^
  train_unsloth_sft.py ^
  --dataset-repo <your-username>/support-triage-sft ^
  --output-repo <your-username>/support-triage-3b-sft ^
  --output-dir outputs/unsloth_full_run_3b ^
  --max-steps 300
```

### Local smoke run of the same script

```bash
python train_unsloth_sft.py ^
  --dataset-path outputs/synthetic_trajectory_sft_30k_balanced.jsonl ^
  --output-dir outputs/unsloth_full_run_3b_local ^
  --train-limit 2000 ^
  --eval-limit 200 ^
  --max-steps 60
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
