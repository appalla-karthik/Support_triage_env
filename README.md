---
title: Support Triage Env
sdk: docker
app_port: 8000
tags:
  - openenv
---

# TriageOS: Support Triage Env

<p align="center">
  <img src="https://raw.githubusercontent.com/appalla-karthik/Support_triage_env/main/outputs/figures/banner.jpeg" alt="TriageOS banner" width="100%">
</p>

<p align="center">
  <strong>An OpenEnv-ready enterprise support operations environment for agents that must understand, prioritize, act, and resolve inside realistic business workflows.</strong>
</p>

<p align="center">
  <img alt="OpenEnv" src="https://img.shields.io/badge/OpenEnv-Ready-1f6feb">
  <img alt="Theme" src="https://img.shields.io/badge/Theme-World%20Modeling%20for%20Professional%20Tasks-0f766e">
  <img alt="Training" src="https://img.shields.io/badge/Training-SFT%20%2B%20RLVR%20%2B%20GRPO-7c3aed">
  <img alt="Space" src="https://img.shields.io/badge/Hugging%20Face-Space-f59e0b">
</p>

`support_triage_env` does not benchmark a reply-only chatbot. It benchmarks an agent operating across a realistic support stack: queue intake, CRM, billing review, incident coordination, trust and safety escalation, and policy lookup.

The project is fully wired around a **10-task enterprise benchmark set**. The simulator, server UI, synthetic dataset generator, training pipeline, and inference scripts all point at the same expanded task family list.

## Why This Project Is Interesting

TriageOS is built around one core idea: good enterprise support requires more than nice language.

The agent has to:

- pick the right ticket from a live queue
- use the correct internal tools
- route to the right team
- follow policy and safety constraints
- handle delayed downstream failures like reopen events and rejected escalations

That makes this a much stronger fit for world modeling than a one-shot answer benchmark.

## Submission Snapshot

This project is positioned primarily for **Theme 3.1: World Modeling for professional tasks**, with longer-horizon workflow behavior as a secondary strength.

For judges and reviewers, the intended submission package is:

- OpenEnv-compatible environment served from a Hugging Face Space
- judge-facing local dashboard for stepping through tasks
- deterministic reward and grading logic with delayed consequence handling
- training artifacts covering both lightweight baseline evaluation and Unsloth + TRL fine-tuning
- README-linked external assets such as Space URL, mini-blog, demo video, or slide deck

Submission links for judges:

- Hugging Face Space: https://huggingface.co/spaces/Shubham-Godani/TriageOS_Support-triage-openenv
- Training notebook on GitHub: https://github.com/appalla-karthik/Support_triage_env/blob/main/notebooks/triageos_training_colab.ipynb
- Open in Colab: https://colab.research.google.com/github/appalla-karthik/Support_triage_env/blob/main/notebooks/triageos_training_colab.ipynb
- Mini-blog / writeup: `ADD_PUBLIC_URL_HERE`
- Demo video / slides: `ADD_PUBLIC_URL_HERE`
- Training evidence images or dashboard screenshots: `ADD_PUBLIC_URL_HERE`

For the exact pre-training and pre-submission workflow, see [HACKATHON_SETUP.md](./HACKATHON_SETUP.md).


### Core training notebook and outputs

- Colab notebook export (`Untitled0.ipynb`): [training notebook](https://drive.google.com/file/d/1dKinZmHWwaZ32RwfHDX-Q9PEuFUjMrqw/view?usp=sharing)
- Quick RLVR/GRPO dataset sample (`rlvr_grpo_dataset_quick.jsonl`): [RLVR/GRPO dataset sample](https://drive.google.com/file/d/158vteyXN2gDucS840WTX2BVfvx6epHwF/view?usp=sharing)
- RLVR smoke report (`rlvr_smoke_report.json`): [rlvr smoke report](https://drive.google.com/file/d/1xJjPiAxJvZ-9ZkBJnR4ZzjT2vzSXRdOD/view?usp=sharing)

### Training scripts used

- `train_unsloth_sft.py`: `ADD_PUBLIC_URL_HERE`
- `train_openenv_rlvr.py`: `ADD_PUBLIC_URL_HERE`
- `train_openenv_grpo.py`: `ADD_PUBLIC_URL_HERE`
- `export_rlvr_compact_sft.py`: [rlvr sft ](https://drive.google.com/file/d/1tszunASMefR333mRahMSejovYkRGZRYl/view?usp=sharing)
- `export_rlvr_grpo_dataset.py`: [rlvr grpo](https://drive.google.com/file/d/169_AwRaaYyaK-WDVs7nS9JuvRgO2fXzd/view?usp=sharing)


## Results At A Glance

<p align="center">
  <img alt="Classification" src="https://img.shields.io/badge/Classification-0.2918%20%E2%86%92%201.0000-16a34a">
  <img alt="Env score" src="https://img.shields.io/badge/Env%20Score-0.8293%20%E2%86%92%200.9686-2563eb">
  <img alt="Success rate" src="https://img.shields.io/badge/Success%20Rate-0.55%20%E2%86%92%201.00-dc2626">
</p>

| Metric | Baseline | Trained | Delta |
| --- | --- | --- | --- |
| Classification accuracy | `0.2918` | `1.0000` | `+0.7082` |
| Environment mean score | `0.8293` | `0.9686` | `+0.1393` |
| Environment success rate | `0.55` | `1.00` | `+0.45` |
| Eval seeds | `7,11` | `7,11` | `matched` |

<p align="center">
  <em>The strongest overall policy came from supervised fine-tuning, while RLVR and GRPO served as real verifiable-reward post-training experiments on top of the simulator.</em>
</p>

## What Already Exists In The Repo

The current project is already a usable environment package, not just an idea draft.
It includes:

- typed action, observation, reward, and state models
- a simulator with `reset`, `step`, and `state`
- ten seeded task families with deterministic graders
- an OpenEnv/FastAPI server and local judge-facing dashboard
- a competition-style `inference.py` entrypoint
- synthetic dataset generation, trajectory generation, and training-data builders
- a lightweight classifier baseline plus before/after evaluation script
- an Unsloth + TRL Colab notebook for minimal post-training
- tests for simulator, inference policy, logging, and data generation

## Recommended Submission Framing

The strongest way to pitch this project is:

> A policy-aware support operations environment where an agent must manage a
> partially observable enterprise queue, coordinate correct routing and customer
> communication, and optimize for safe outcomes under delayed business impact.

That framing matches what the repository already does today:

- it is an environment, not just a prompt-response benchmark
- it is grounded in real operational workflows
- it uses objective state transitions and deterministic grading
- it creates measurable opportunities for before/after training evaluation

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

## Why This Is A Strong Hackathon Fit

- The environment is **verifiable**: reward comes from explicit state transitions and deterministic graders, not only from a free-form judge.
- The environment is **trainable**: the repo includes synthetic data generation, trajectory generation, baseline evaluation, and an Unsloth + TRL notebook.
- The environment is **demo-friendly**: the FastAPI server exposes a polished local console that lets judges inspect queue state, actions, and reward changes live.
- The environment is **hard to shortcut**: several tasks include delayed events such as escalation rejection, ticket reopen, and customer follow-up so shallow one-step behavior does not score well.

## Results To Report

The clearest way to present improvement for judges is one compact before/after table.
The repo is now structured to support reporting:

- classification accuracy before and after training
- environment mean score before and after training
- environment success rate before and after training
- mean steps per task suite
- per-task score and success-rate summaries for all 10 task families

Recommended sources for the final numbers:

- `outputs/train_eval_report.json` from `train_and_evaluate.py`
- `outputs/baseline_scores.json` from `support_triage_env.baseline.run_baseline`
- `outputs/inference_last_run.json` from the competition entrypoint

Final reported metrics from the completed runs:

| Metric | Baseline | Trained | Delta |
| --- | --- | --- | --- |
| Classification accuracy | `0.2918` | `1.0000` | `+0.7082` |
| Environment mean score | `0.8293` | `0.9686` | `+0.1393` |
| Environment success rate | `0.55` | `1.00` | `+0.45` |
| Eval seeds | `7,11` | `7,11` | `matched` |

Primary SFT highlights captured from the completed run:

- `executive_security_escalation`: `0.6451 -> 0.99`
- `security_and_refund_hard`: `0.6783 -> 0.99`
- `followup_reprioritization_queue`: `0.7745 -> 0.9343`
- `escalation_rejection_recovery`: `0.622 -> 0.952`

Also include one short qualitative comparison:

- baseline behavior on one hard task
- trained behavior on the same task
- what changed in routing, safety, or delayed-outcome handling

Recommended qualitative example from the current report:

- `executive_security_escalation`: baseline-style evaluation scored `0.6451`, trained evaluation scored `0.99`
- `security_and_refund_hard`: baseline-style evaluation averaged `0.6783`, trained evaluation averaged `0.99`
- these gains make a good demo story because they show better prioritization and safer specialist routing

## RLVR And GRPO Results

We also completed two reinforcement-learning-oriented stages on top of the environment:

1. A compact-prompt RLVR warm-start evaluation path using `train_openenv_rlvr.py`
2. An actual GRPO post-training run using Unsloth + TRL over verifiable simulator reward

Best broad RLVR-style evaluation snapshot:

| Metric | Scripted Baseline | RLVR Warm-Start Adapter | Delta |
| --- | --- | --- | --- |
| Mean score | `0.9366` | `0.8730` | `-0.0636` |
| Success rate | `0.75` | `0.375` | `-0.375` |

Task highlights from that RLVR-style run:

- `incident_coordination_outage`: `0.99`, success rate `1.0`
- `security_and_refund_hard`: mean `0.905`
- weakest remaining tasks: `followup_reprioritization_queue`, `escalation_rejection_recovery`

Actual GRPO run snapshot:

| Metric | Scripted Baseline | GRPO Adapter | Delta |
| --- | --- | --- | --- |
| Mean score | `0.9366` | `0.7600` | `-0.1766` |
| Success rate | `0.75` | `0.25` | `-0.50` |

Important GRPO outcome:

- `escalation_rejection_recovery`: mean `0.99`, success rate `1.0`

Takeaway:

- SFT produced the strongest overall policy
- RLVR and GRPO both ran successfully against verifiable simulator reward
- GRPO gave a strong task-level gain on escalation recovery, but broader performance remained mixed

## Training Notebook And Scripts

Judges asked for a runnable training path. The repo now provides both notebook and script entrypoints:

- Notebook: [notebooks/triageos_training_colab.ipynb](./notebooks/triageos_training_colab.ipynb)
- GitHub notebook URL: https://github.com/appalla-karthik/Support_triage_env/blob/main/notebooks/triageos_training_colab.ipynb
- Open in Colab: https://colab.research.google.com/github/appalla-karthik/Support_triage_env/blob/main/notebooks/triageos_training_colab.ipynb

Core training and evaluation scripts:

- `train_unsloth_sft.py`: supervised fine-tuning with Unsloth
- `train_openenv_rlvr.py`: verifiable-reward rollout evaluation / RLVR smoke path
- `export_rlvr_compact_sft.py`: compact prompt warm-start dataset export
- `export_rlvr_grpo_dataset.py`: GRPO prompt export for first-action RL
- `train_openenv_grpo.py`: actual GRPO post-training scaffold used for the recorded RL run

## Evidence Of Actual Training

For submission review, the cleanest proof package is:

1. Notebook link in this README
2. Hugging Face Space link in this README
3. Final metric tables in this README
4. Public writeup/video link in this README
5. Training evidence images linked externally instead of storing large binaries in the repo

At minimum, include public screenshots or plots showing:

- SFT loss curve from the Unsloth run
- GRPO reward / loss logs from the real GRPO run
- one evaluation screenshot or JSON excerpt showing before/after numbers

Recommended proof sources:

- `artifacts/train_metrics.json`
- `artifacts/train_eval_report.json`
- `artifacts/train_eval_summary.md`
- Colab screenshots of the completed Unsloth and GRPO runs
- `outputs/rlvr_smoke_report.json` style evaluation summaries when available

If you publish a mini-blog or video, link the screenshots there and link that public URL back into this README.

## Reward Hacking Safeguards

The environment is intentionally designed so shallow shortcuts do not score well.
Current safeguards include:

- penalties for premature finish and premature resolution
- invalid tool-use penalties when an action is run in the wrong enterprise app
- queue-priority penalties when urgent security or outage work is ignored
- delayed downstream failures such as `ticket_reopened` and `escalation_rejected`
- task-specific workflow requirements such as incident creation before escalation
- policy-aware reply checks and forbidden unsafe phrasing in sensitive tasks

Concrete examples already covered by tests and local audit:

- resolving a reopen-prone refund too early triggers `ticket_reopened`
- sending a weak outage escalation can trigger `escalation_rejected`
- handling billing before an urgent security incident triggers priority penalties
- using the wrong app for a tool action is rejected and penalized

Before final submission, it is worth preserving one short red-team table in the README:

| Shortcut attempt | Expected guardrail | Status |
| --- | --- | --- |
| Premature finish | penalty + low score | checked locally |
| Wrong tool usage | invalid action penalty | checked locally |
| Weak escalation | rejection or downstream penalty | checked locally |
| Refund shortcut without review | reopen event | checked locally |

## Hackathon Theme Fit

### Primary Fit: Theme 3.1 Professional Tasks

This is the strongest theme match because the agent is expected to do real work
inside a partially observable business workflow instead of only generating a
good-looking answer. The environment fits Theme 3.1 well because:

- tickets evolve over time rather than ending in one turn
- actions change the world state
- the agent must use enterprise tools such as CRM, billing, incident, trust, and policy systems
- evaluation is grounded in business logic, routing correctness, and safety policy
- downstream consequences matter, including reopen risk and escalation rejection

### Secondary Fit: Theme 2 Long-Horizon Planning

The environment also has a strong secondary fit with long-horizon planning
because several tasks require:

- queue-level prioritization across multiple tickets
- multi-step workflows before safe resolution
- delayed events such as customer follow-up, rejection, and reopen
- recovery from earlier mistakes instead of one-shot correctness

The current benchmark is still compact compared with an extreme long-horizon
setting, so Theme 2 is best treated as a depth layer rather than the primary
top-line framing.

### Future Extension: Theme 1 Multi-Agent Interactions

The current implementation is mostly single-agent, but support operations are a
natural place to add multi-agent structure later:

- billing specialist agent
- engineering triage agent
- trust and safety agent
- customer simulator
- manager or SLA coordinator

That makes Theme 1 a believable future extension, but not the cleanest primary
submission framing for the current repo.

### Why Not Theme 3.2 Or Theme 4

- Theme 3.2 is a weak fit because this project is enterprise support, not personal assistant task handling.
- Theme 4 is not the best current framing because the repo does not yet center self-play, recursive task creation, or adaptive self-improvement loops.

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
- emits judge-friendly summary fields such as success rate, mean steps, and per-task aggregates

### Unsloth + TRL Colab Path

The repo also includes a notebook-oriented post-training path at `notebooks/triageos_training_colab.ipynb`.

That notebook is designed to:

- build multi-step trajectory data
- prepare an SFT-style dataset from environment rollouts
- fine-tune a compact instruct model with **Unsloth**
- train through **TRL** components
- save a runnable model artifact for follow-up evaluation

This gives the submission a minimal but real training story beyond static environment code.

The same notebook can be used to demonstrate:

- SFT data preparation
- Unsloth fine-tuning
- RLVR evaluation
- GRPO post-training experiments

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
python -m support_triage_env.baseline.run_baseline --model gpt-4.1-mini-2025-04-14 --seed 7
```

By default, this runs **all task families**. You can also run a subset:

```bash
python -m support_triage_env.baseline.run_baseline --tasks billing_refund_easy,incident_coordination_outage --seed 7
```

Using a fixed seed is recommended so baseline and trained comparisons are reproducible.

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

Current local verification status in this workspace:

- `pytest -q`: passed locally
- `openenv validate .`: passed locally

Recommended final submission checklist:

- replace the remaining `ADD_PUBLIC_URL_HERE` placeholders with public links
- keep the Hugging Face Space URL live and public
- keep the Colab notebook link live and public
- include at least one public training screenshot for SFT and one for GRPO
- generate or paste a short writeup / video and link it above
- keep the final metric tables in this README
