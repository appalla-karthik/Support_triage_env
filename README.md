---
title: Support Triage Env
sdk: docker
app_port: 8000
tags:
  - openenv
---

# Support Triage Env

`support_triage_env` is a real-world customer support triage simulator for OpenEnv. The agent works a queue of realistic support tickets, classifies them, prioritizes them, drafts safe customer replies, routes issues to the correct internal team, and decides when a ticket should be escalated versus resolved.

## Why This Environment

Support operations are a real business workflow with clear policy constraints, partial progress, and meaningful consequences for bad decisions. This environment is designed to train or benchmark multi-step agents on:

- structured ticket routing
- customer-safe written communication
- escalation versus resolution decisions
- queue prioritization under limited steps

## API Surface

The local simulator exposes the standard Gym-like loop:

```python
from support_triage_env import SupportTriageAction, SupportTriageSimulator

env = SupportTriageSimulator()
observation = env.reset(task_id="billing_refund_easy")
observation, reward, done, info = env.step(
    SupportTriageAction(action_type="view_ticket", ticket_id="TCK-1001")
)
state = env.state()
```

The OpenEnv server exposes the same environment over `/reset`, `/step`, `/state`, `/schema`, and `/metadata`.

## Action Space

`SupportTriageAction` is a typed Pydantic model with these fields:

- `action_type`: one of `view_ticket`, `classify_ticket`, `draft_reply`, `request_info`, `escalate_ticket`, `resolve_ticket`, `finish`
- `ticket_id`: target ticket for all ticket-level actions
- `category`: typed enum for ticket classification
- `priority`: typed enum for urgency
- `team`: typed enum for routing or escalation
- `message`: customer reply text or internal escalation note
- `resolution_code`: required when resolving a ticket

## Observation Space

`SupportTriageObservation` includes:

- `task`: task metadata and objective
- `instructions`: episode-specific goals
- `policy_hints`: safe operating guidance
- `queue`: current queue snapshot for each ticket
- `focused_ticket`: full details for the most recently opened or edited ticket
- `last_action_result`: environment feedback from the previous action
- `progress`: deterministic grader snapshot with current score, satisfied requirements, outstanding requirements, and penalties
- `reward`: scalar step reward
- `done`: episode termination flag

## Reward Model

`SupportTriageReward` is a typed Pydantic model returned by the local simulator. Reward shaping is based on:

- positive score deltas when the agent completes correct subgoals
- partial reply credit for including required policy-compliant content
- penalties for unsafe advice, premature resolution, repeated actions, invalid actions, and per-step cost

Final grader scores are deterministic and clipped strictly inside `(0.0, 1.0)`.

## Tasks

Three seeded task families are included, each with a programmatic grader. Each reset keeps the same policy goal, but can vary ticket IDs, customer details, phrasing, and queue composition while remaining reproducible under a fixed seed:

1. `billing_refund_easy`
   Straightforward duplicate-charge refund. The agent should classify the issue, route it to `billing_ops`, reply with an apology and refund timeline, then resolve it with `refund_submitted`.
2. `export_outage_medium`
   Reproducible CSV export outage blocking finance close. The agent should mark the issue as a high-priority product bug, escalate it to engineering, send a useful reply, and avoid resolving it prematurely.
3. `security_and_refund_hard`
   Mixed queue with an urgent account-takeover report and a routine refund. The agent must prioritize the security incident first, escalate it safely to `trust_safety`, avoid unsafe recovery advice, then complete the refund ticket.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .
```

Reproduce a specific randomized episode with a seed:

```python
from support_triage_env import SupportTriageSimulator

env = SupportTriageSimulator()
observation = env.reset(task_id="billing_refund_easy", seed=7)
```

Generate a larger synthetic RL-style dataset:

```bash
synthetic-dataset --examples-per-task 5000 --seed 42 --output outputs/synthetic_support_triage_dataset.jsonl
```

This produces a JSONL corpus with labeled ticket records, expected routing, expected terminal actions, reply requirements, and policy constraints. With the default three task families, `--examples-per-task 5000` generates more than 15,000 labeled rows because the hard task can emit multiple tickets per scenario.

Build a larger mixed training set by combining synthetic data with the local files in the repo `datasets` folder:

```bash
build-training-data ^
  --synthetic-examples-per-task 5000 ^
  --synthetic-seed 42 ^
  --output outputs\combined_training_dataset.jsonl
```

By default, the pipeline now uses these local dataset files when present:

- `datasets/customer_support_tickets.csv`
- `datasets/customer_support_tickets_200k.csv`
- `datasets/complaints.csv`
- `datasets/complaint_data.csv`

You can still pass additional CSVs manually for the notebook-derived sources:

- `multilingual-customer-support-tickets-using-xlm-r.ipynb`
- `customer-support-ticket-tagger.ipynb`
- `banking-consumer-complaint-analysis.ipynb`

Train a lightweight baseline classifier and report accuracy:

```bash
train-support-classifier ^
  --synthetic-examples-per-task 5000 ^
  --synthetic-seed 42 ^
  --report-output outputs\training_report.json
```

This writes an accuracy report with per-class metrics to `outputs\training_report.json`.

Run the server locally:

```bash
python -m server.app
```

Run tests:

```bash
pytest
```

Validate the environment layout:

```bash
openenv validate .
```

Validate a running server:

```bash
openenv validate --url http://localhost:8000
```

## Competition Inference

The required submission entrypoint is the root-level `inference.py`. It uses the OpenAI Python client and reads the evaluator-compatible environment variables:

- `API_BASE_URL`: model API base URL
- `MODEL_NAME`: model identifier
- `API_KEY`: preferred model API key provided by the evaluator
- `HF_TOKEN`: accepted fallback token name if the evaluator exposes the key under this variable
- `ENV_BASE_URL`: optional URL of a running environment server
- `LOCAL_IMAGE_NAME`: optional Docker image name used when `ENV_BASE_URL` is not set

For competition submissions, `inference.py` initializes the client with
`base_url=os.environ["API_BASE_URL"]` and prefers `api_key=os.environ["API_KEY"]`,
falling back to `os.environ["HF_TOKEN"]` when needed. It then makes an initial
chat completion through that proxy before running the task loop. Do not use
`OPENAI_API_KEY` or any hardcoded provider URL in the submission entrypoint.

Run against a locally running server:

```bash
set API_BASE_URL=https://router.huggingface.co/v1
set MODEL_NAME=Qwen/Qwen2.5-72B-Instruct
set API_KEY=your_token_here
set ENV_BASE_URL=http://localhost:8000
python inference.py
```

Or run using a local Docker image:

```bash
set API_BASE_URL=https://router.huggingface.co/v1
set MODEL_NAME=Qwen/Qwen2.5-72B-Instruct
set API_KEY=your_token_here
set LOCAL_IMAGE_NAME=support-triage-openenv
python inference.py
```

The script emits structured stdout logs in `[START]`, `[STEP]`, and `[END]` format for evaluator compatibility.
It also writes a local JSON artifact to `outputs/inference_last_run.json` so you can confirm:

- `final_score`
- `cumulative_reward`
- `steps`
- `success`
- detailed grader `progress`

Inspect the saved score report with:

```bash
type outputs\inference_last_run.json
```

## Local Baseline Runner

For local experimentation, the package also includes a baseline runner that executes all three tasks directly against the in-process simulator. This helper uses `OPENAI_API_KEY`.

```bash
set OPENAI_API_KEY=your_key_here
python -m support_triage_env.baseline.run_baseline --model gpt-4.1-mini-2025-04-14
```

It writes results to `outputs/baseline_scores.json`.

### Baseline Scores

Observed local inference runs with the current patched `inference.py` and `Qwen/Qwen2.5-72B-Instruct`:

- `billing_refund_easy`: `final_score=0.99`, `cumulative_reward=0.85`, `steps=5`, `success=true`
- `export_outage_medium`: `final_score=0.99`, `cumulative_reward=0.94`, `steps=6`, `success=true`
- `security_and_refund_hard`: passed locally in `7` steps with `success=true` using the same inference policy

The baseline runner still emits:

- per-task score
- per-task cumulative reward
- step count
- mean score across all three tasks

## Hugging Face Spaces

This repo is configured for a containerized Hugging Face Space:

- README front matter sets `sdk: docker`
- `Dockerfile` starts the OpenEnv FastAPI app on port `8000`
- the Space is tagged with `openenv`

Build locally:

```bash
docker build -t support-triage-openenv .
docker run -p 8000:8000 support-triage-openenv
```

## Pre-Submission Checklist

Before submitting, verify the same surfaces the evaluator is likely to inspect:

```bash
pytest
openenv validate .
python -m server.app
openenv validate --url http://localhost:8000
python inference.py
```

After `python inference.py`, confirm the final score locally:

```bash
type outputs\inference_last_run.json
```

## Files

- `support_triage_env/models.py`: typed action, observation, reward, and state models
- `support_triage_env/simulator.py`: local `step/reset/state` simulator
- `support_triage_env/graders.py`: deterministic task graders
- `support_triage_env/tasks.py`: task definitions and expectations
- `support_triage_env/synthetic_dataset.py`: large synthetic dataset generator for RL-style training or evaluation
- `support_triage_env/training_data.py`: merges synthetic data with external customer-support CSVs into a unified training corpus
- `support_triage_env/train_classifier.py`: trains a lightweight TF-IDF + logistic regression baseline and reports accuracy
- `support_triage_env/baseline/run_baseline.py`: OpenAI baseline script
- `server/app.py`: OpenEnv FastAPI entrypoint
- `openenv.yaml`: OpenEnv manifest
