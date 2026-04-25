---
title: Architecture
description: How the simulator, tasks, graders, server, and inference components fit together.
---

# Architecture

## High-level structure

The implementation being documented lives inside `Support_triage_env/`.

The most important modules are:

| File or folder | Role |
| --- | --- |
| `support_triage_env/models.py` | Typed domain models for actions, observations, rewards, tickets, and environment state |
| `support_triage_env/tasks.py` | Seeded task scenario generation and expectation definitions |
| `support_triage_env/graders.py` | Deterministic task-specific evaluation logic |
| `support_triage_env/simulator.py` | Local Gym-like environment loop |
| `support_triage_env/client.py` | OpenEnv client wrapper |
| `support_triage_env/synthetic_dataset.py` | Scenario expansion into synthetic JSONL training data |
| `support_triage_env/training_data.py` | Training corpus builder from synthetic plus optional CSV data |
| `support_triage_env/train_classifier.py` | Lightweight TF-IDF + logistic regression baseline |
| `support_triage_env/baseline/run_baseline.py` | Local model-driven baseline runner |
| `server/app.py` | FastAPI and OpenEnv HTTP entrypoint |
| `inference.py` | Competition-facing inference loop |

## System flow

```text
task definition + seed
        ->
scenario generation
        ->
simulator reset
        ->
observation returned to agent
        ->
agent chooses typed action
        ->
simulator mutates ticket state
        ->
grader evaluates full state
        ->
reward + progress snapshot returned
```

## Main architectural layers

### 1. Scenario generation

`tasks.py` produces reproducible variations of each task family. A fixed seed keeps
the policy goal the same while varying:

- ticket identifiers
- customer names
- phrasing
- queue composition
- supporting context

This is good design for training and evaluation because it avoids overfitting to a
single hardcoded prompt while keeping the expected behavior stable.

### 2. Stateful environment execution

`simulator.py` owns the mutable world state. It:

- resets episodes
- validates actions
- updates ticket records
- logs action history
- computes shaped reward
- returns observations and the current state

### 3. Deterministic grading

`graders.py` evaluates whether the agent did the right thing. The graders do not
look only at the final status. They also score:

- correct category
- correct global queue priority
- correct routed-team internal priority
- correct team assignment
- reply quality
- escalation quality
- correct terminal action
- ordering of work in the hard task

They also apply penalties for unsafe or overconfident behavior, queue-ordering
mistakes, SLA pressure, and downstream business-risk failures where relevant.

### 4. Environment serving

`server/app.py` wraps the environment in a FastAPI app via OpenEnv and exposes:

- `POST /reset`
- `POST /step`
- `GET /state`
- `GET /metadata`
- `GET /schema`

The server also includes a browser-based UI for manually running episodes and
inspecting raw JSON payloads. It now also links directly into the Docusaurus
documentation build under `/project-docs/`.

### 5. Inference and submission

`inference.py` is the competition-style entrypoint. It can operate against:

- a running environment server
- a local Docker image
- the in-process simulator fallback

It also contains:

- model prompting logic
- output normalization
- safety-oriented postprocessing
- fallback completion for missing classification fields, including both queue priority and department priority
- structured logs for evaluator compatibility
- run artifact generation

## Why this architecture is OpenEnv-friendly

The project follows a pattern judges typically like:

- typed environment interfaces
- local simulator plus HTTP server
- deterministic evaluation
- clean separation between world state and agent policy
- reproducible tasks
- measurable score progression

That gives you a good foundation for both demo clarity and future training.
