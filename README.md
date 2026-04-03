---
title: Support Triage OpenEnv
sdk: docker
app_port: 8000
tags:
  - openenv
---

# Support Triage OpenEnv

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

Final grader scores are deterministic and clipped to `0.0-1.0`.

## Tasks

Three deterministic tasks are included, each with a programmatic grader:

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

## Baseline Inference

The baseline runner uses the OpenAI Python client and reads credentials from `OPENAI_API_KEY`.

```bash
set OPENAI_API_KEY=your_key_here
python -m support_triage_env.baseline.run_baseline --model gpt-4.1-mini-2025-04-14
```

It writes results to `outputs/baseline_scores.json`.

### Baseline Scores

This workspace did not have `OPENAI_API_KEY` configured, so the OpenAI baseline could not be executed here. Once credentials are present, the script emits:

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

## Files

- `support_triage_env/models.py`: typed action, observation, reward, and state models
- `support_triage_env/simulator.py`: local `step/reset/state` simulator
- `support_triage_env/graders.py`: deterministic task graders
- `support_triage_env/tasks.py`: task definitions and expectations
- `support_triage_env/baseline/run_baseline.py`: OpenAI baseline script
- `server/app.py`: OpenEnv FastAPI entrypoint
- `openenv.yaml`: OpenEnv manifest
