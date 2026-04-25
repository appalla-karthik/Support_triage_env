---
title: Training and Submission
description: How the repo supports dataset generation, baselines, inference, and hackathon submission readiness.
---

# Training and Submission

## What the repo already supports

The repository already includes several building blocks that are useful for a
hackathon submission:

- synthetic scenario generation
- combined training data generation
- a lightweight classifier baseline
- a local model-driven baseline runner
- a trajectory dataset generator for multi-step supervision
- an Unsloth + TRL Colab notebook
- a competition-facing `inference.py`
- a submission validation shell script

## Synthetic dataset pipeline

`support_triage_env/synthetic_dataset.py` expands seeded task families into JSONL
examples containing:

- ticket details
- task metadata
- policy hints
- expected routing
- expected queue priority
- expected department-level internal priority
- expected terminal actions
- reply requirements
- forbidden phrases

This is useful for:

- imitation-style warm starts
- supervised post-training
- reward model design
- evaluation dataset creation

## Combined training data

`support_triage_env/training_data.py` can merge synthetic data with optional local
CSV sources from a `datasets/` folder. The loader already contains heuristics to
map raw support and complaint data into the project's target labels:

- `billing_refund`
- `product_bug`
- `security_account_takeover`
- `account_access`

## Lightweight baseline model

`train_classifier.py` trains a simple:

- TF-IDF vectorizer
- logistic regression classifier

This is not the final hackathon story, but it is still useful because it proves the
data pipeline can support measurable learning. The repo also now includes a
weighted train/eval path that can upweight the hardest task families during
dataset assembly and evaluation runs.

## Inference entrypoint

The root `inference.py` matters a lot for submission readiness. It:

- creates a model client from evaluator-style environment variables
- forces at least one real proxy request
- runs tasks through the environment loop
- applies postprocessing and fallback logic
- writes structured logs
- saves a machine-readable run artifact

This is good engineering for a competition environment.

## Validation workflow

`validate-submission.sh` checks three important surfaces:

1. the live Hugging Face Space responds to `/reset`
2. Docker build succeeds
3. `openenv validate` passes

That script is worth calling out in demos because it shows the project is not only
interesting but also packaged with submission hygiene in mind.

## What is still missing for Round 2 minimum requirements

The repo now clears the training-artifact requirement because it already includes
a minimal Unsloth + TRL notebook. The highest-value remaining gaps are:

- running that notebook and preserving final metrics or plots
- linking the Hugging Face Space, blog/video, and training evidence from the README
- packaging one compact before/after evaluation story for judges
- showing trained improvement specifically on the hardest multi-step queue tasks, not only label accuracy

## Best post-training story for this project

The cleanest training story would be a staged approach:

1. **Supervised warm start**
   Train on synthetic and mixed support data to learn routing, prioritization,
   and safe reply patterns.

2. **Environment rollouts**
   Evaluate on the actual simulator using task-level rewards and progress snapshots.

3. **Preference or RL-style refinement**
   Optimize for improved final score, lower violation rate, shorter trajectories,
   and better queue-ordering decisions.

4. **Before/after comparison**
   Show reward curves, success rates, policy violation counts, and sample trajectory improvements.

That staged story is already supported by the current repo layout:

- `trajectory_dataset.py` for multi-step supervised traces
- `train_classifier.py` for a lightweight measurable baseline
- `train_and_evaluate.py` for before/after environment scoring
- hard-task weighting controls in `training_data.py` and `train_and_evaluate.py`
- `notebooks/triageos_training_colab.ipynb` for an Unsloth + TRL fine-tuning path

## Practical commands already in the repo

```bash
python -m server.app
pytest
synthetic-dataset --examples-per-task 5000 --seed 42 --output outputs/synthetic_support_triage_dataset.jsonl
build-training-data --synthetic-examples-per-task 5000 --synthetic-seed 42 --output outputs/combined_training_dataset.jsonl
train-support-classifier --synthetic-examples-per-task 5000 --synthetic-seed 42 --report-output outputs/training_report.json
python inference.py
```

## Best next documentation artifact to add after this site

If you want to increase hackathon readiness further, the next best asset is a short
submission page or blog post that:

- links the live Space
- embeds one or two training plots
- compares baseline versus trained behavior
- shows one reward-hacking safeguard example
- explains the two-level priority system with one concrete workflow example
- points judges to the notebook and the repo commands they can rerun
