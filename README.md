---
title: Support Triage Env
sdk: docker
app_port: 8000
tags:
  - openenv
---

# TriageOS: Support Triage Env

`support_triage_env` is an OpenEnv-ready enterprise support workflow environment. Instead of benchmarking a reply-only chatbot, it benchmarks an agent operating across a realistic support stack: queue intake, CRM, billing review, incident coordination, trust and safety escalation, and policy lookup.

The current project is fully wired around a **10-task enterprise benchmark set**. The simulator, server UI, synthetic dataset generator, training pipeline, and default inference scripts now all point at the same expanded task family list.

## Environment Goal

This environment is designed for **Theme 3.1: World Modeling for professional tasks**:

- partially observable enterprise workflows
- multi-app tool usage
- queue-level prioritization
- policy-aware customer communication
- delayed downstream consequences such as reopen events and rejected escalations

## Core Ideas

- The agent does not just draft replies. It decides how to operate the queue.
- Correct behavior often requires reading hidden context from CRM, billing, policy, incident, or trust systems.
- Reward is not only based on a final label. It tracks queue health, SLA pressure, workflow completion, and downstream risks.
- Several tasks require multi-step workflows before a ticket can be safely resolved or escalated.

## Task Families

The project currently ships with these seeded task families:

1. `billing_refund_easy`
   Straightforward duplicate-charge refund.
2. `export_outage_medium`
   Product outage requiring engineering escalation.
3. `security_and_refund_hard`
   Mixed queue with urgent security plus routine billing.
4. `enterprise_refund_investigation`
   Enterprise refund that requires CRM, billing, and policy review.
5. `incident_coordination_outage`
   Incident-driven outage that should create an incident before escalation.
6. `executive_security_escalation`
   Executive security workflow involving trust and safety review.
7. `escalation_rejection_recovery`
   Rejected escalation packet that must be repaired and resent.
8. `refund_reopen_review`
   Refund workflow that can reopen if approval and policy checks are skipped.
9. `mixed_queue_command_center`
   Four-ticket queue mixing security, outage, refund, and routine access work.
10. `followup_reprioritization_queue`
    Queue where a customer follow-up changes what should be prioritized next.

## Action Space

`SupportTriageAction` supports both ticket actions and enterprise tool actions.

- `view_ticket`
- `classify_ticket`
- `draft_reply`
- `request_info`
- `escalate_ticket`
- `resolve_ticket`
- `lookup_account`
- `check_billing_status`
- `search_policy`
- `create_incident`
- `add_internal_note`
- `finish`

Important structured fields:

- `ticket_id`
- `category`
- `priority`
- `team`
- `app`
- `target_id`
- `message`
- `severity`
- `details`
- `resolution_code`

Supported categories:

- `billing_refund`
- `billing_approval`
- `product_bug`
- `incident_coordination`
- `security_account_takeover`
- `security_escalation`
- `account_access`

## Observation And State

Each step exposes:

- `task`, `instructions`, and `policy_hints`
- queue snapshot and focused ticket details
- `accessible_apps`
- `app_snapshots`
- `world_summary`
- `progress` with deterministic grading details
- `recent_events`
- `last_tool_result`

The internal state also keeps:

- full tickets
- customer accounts
- incidents
- pending events
- recent events
- action history

## Reward Model

Reward is deterministic and combines:

- positive score deltas for satisfying workflow requirements
- queue-aware routing and prioritization credit
- reply quality credit
- escalation packet quality
- penalties for SLA damage, unsafe behavior, incident gaps, premature finish, and downstream failures
- a per-task configurable step penalty

Several advanced tasks also schedule delayed events such as:

- `customer_follow_up`
- `escalation_rejected`
- `ticket_reopened`
- `incident_update`
- `policy_drift`

## Quickstart

### Setup

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e ".[dev,train]"
```

### Run The Local Server

```bash
python -m server.app
```

Then open:

```text
http://localhost:8000
```

### Run Tests

```bash
pytest
```

### Validate OpenEnv Layout

```bash
openenv validate .
openenv validate --url http://localhost:8000
```

## Synthetic Data And Training Data

Generate synthetic scenarios from all 10 task families:

```bash
synthetic-dataset --examples-per-task 1000 --seed 42 --output outputs/synthetic_support_triage_dataset.jsonl
```

Build a mixed training corpus using synthetic data plus repo seed CSVs:

```bash
build-training-data ^
  --synthetic-examples-per-task 1000 ^
  --synthetic-seed 42 ^
  --output outputs\combined_training_dataset.jsonl
```

Repo seed datasets used automatically when present:

- `datasets/customer_support_tickets.csv`
- `datasets/customer_support_tickets_200k.csv`
- `datasets/complaints.csv`
- `datasets/complaint_data.csv`

## Training Pipelines

### Lightweight Classifier Baseline

```bash
train-support-classifier ^
  --synthetic-examples-per-task 1000 ^
  --synthetic-seed 42 ^
  --report-output outputs\training_report.json
```

This trains a lightweight TF-IDF plus logistic-regression model and reports classification metrics over the current expanded label set.

### Before/After Environment Evaluation

```bash
train-and-evaluate-triage ^
  --synthetic-examples-per-task 300 ^
  --synthetic-seed 7 ^
  --eval-seeds 7,11 ^
  --report-output outputs\train_eval_report.json ^
  --model-output outputs\triageos_classifier.pkl
```

This script:

- builds training data from the full environment
- trains a classifier
- compares heuristic routing versus trained routing
- reports both classification deltas and environment-score deltas across the task suite

## Inference Entry Point

The required submission entrypoint is root-level `inference.py`.

It now defaults to the full benchmark task family list rather than the original three-task subset. The inference policy supports:

- multi-app actions
- advanced categories
- task-specific workflow steps
- fallback logging
- dynamic step budgets for longer enterprise tasks

Environment variables:

- `API_BASE_URL`
- `MODEL_NAME`
- `API_KEY`
- `HF_TOKEN`
- `ENV_BASE_URL`
- `LOCAL_IMAGE_NAME`
- `SUPPORT_TRIAGE_TASK`
- `MAX_STEPS`

Run against a local server:

```bash
set API_BASE_URL=https://router.huggingface.co/v1
set MODEL_NAME=Qwen/Qwen2.5-72B-Instruct
set API_KEY=your_token_here
set ENV_BASE_URL=http://localhost:8000
python inference.py
```

The script writes a run artifact to `outputs/inference_last_run.json`.

## Local Baseline Runner

For local experimentation, the package also includes a direct baseline runner:

```bash
set OPENAI_API_KEY=your_key_here
python -m support_triage_env.baseline.run_baseline --model gpt-4.1-mini-2025-04-14
```

By default, this runs **all task families**. You can also run a subset:

```bash
python -m support_triage_env.baseline.run_baseline --tasks billing_refund_easy,incident_coordination_outage
```

## Project Structure

- `support_triage_env/models.py`: typed models for actions, observations, rewards, state, enterprise apps, and delayed events
- `support_triage_env/tasks.py`: all task-family definitions
- `support_triage_env/simulator.py`: local simulator and state transitions
- `support_triage_env/graders.py`: deterministic task graders and reward helpers
- `support_triage_env/synthetic_dataset.py`: synthetic benchmark dataset generator
- `support_triage_env/training_data.py`: mixed training corpus builder
- `support_triage_env/train_classifier.py`: lightweight classifier trainer
- `support_triage_env/train_and_evaluate.py`: before/after training and environment evaluation pipeline
- `support_triage_env/baseline/run_baseline.py`: local baseline runner
- `server/app.py`: OpenEnv HTTP server and judge-facing dashboard
- `inference.py`: submission entrypoint

## Recommended Local Verification

Before a submission or demo, run:

```bash
pytest
python -m server.app
openenv validate --url http://localhost:8000
python inference.py
```

Then inspect:

```bash
type outputs\inference_last_run.json
type outputs\train_eval_report.json
```
