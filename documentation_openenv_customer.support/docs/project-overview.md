---
title: Project Overview
description: A practical overview of the Support_triage_env repository and what it currently implements.
---

# Project Overview

## Core idea

This project simulates a customer support operations workflow rather than a toy
classification benchmark. The agent does not simply predict a label and stop.
It must operate inside an environment with:

- a queue of tickets
- typed actions
- mutable ticket state
- explicit policy hints
- task-specific grading logic
- penalties for unsafe or low-quality decisions

That is the main reason the project is interesting from an OpenEnv and hackathon
perspective.

## What the agent can do

The main action surface is defined by `SupportTriageAction` and includes:

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

These actions are typed, and several require supporting fields such as:

- `ticket_id`
- `category`
- `priority`
- `department_priority`
- `team`
- `app`
- `target_id`
- `message`
- `severity`
- `details`
- `resolution_code`

## What the environment returns

Each step returns a structured observation with:

- task metadata
- instructions
- policy hints
- queue summary
- focused ticket details
- accessible apps
- world summary
- recent events
- last tool result
- progress snapshot
- reward
- done flag

The underlying state tracks the full mutable world:

- all ticket records
- action history
- pending downstream events
- step count
- cumulative reward
- final score
- current grading snapshot

## Task families in the repo

The environment currently ships with **ten** seeded task families:

| Task | Difficulty | What it tests |
| --- | --- | --- |
| `billing_refund_easy` | Easy | Straightforward refund classification, safe reply, billing routing, clean resolution |
| `export_outage_medium` | Medium | High-priority product outage handling, escalation judgment, avoiding premature resolution |
| `security_and_refund_hard` | Hard | Queue prioritization, urgent security handling, safe escalation, and completion of a secondary refund task |
| `enterprise_refund_investigation` | Medium | Refund resolution only after CRM, billing, and policy review |
| `incident_coordination_outage` | Medium | Incident creation before engineering escalation |
| `executive_security_escalation` | Medium | Trust and safety workflow for executive account compromise |
| `escalation_rejection_recovery` | Hard | Repairing a rejected escalation packet after downstream failure |
| `refund_reopen_review` | Hard | Reopen-prone refund handling with approval-policy checks |
| `mixed_queue_command_center` | Hard | Multi-ticket prioritization across security, outage, refund, and routine access work |
| `followup_reprioritization_queue` | Hard | Queue reprioritization after a customer follow-up changes the state of play |

## Why this is stronger than a plain classifier

The environment is closer to a workflow world than a static dataset because:

- the same issue can require multiple actions
- order matters
- some tasks have delayed reward and delayed events
- the agent can make stateful mistakes
- policy violations are explicitly penalized
- queue priority and department-level internal priority are both modeled
- tasks are reproducible but not identical across seeds

## Current strengths

The existing implementation already gives you a credible base for a hackathon:

- realistic business setting
- deterministic grading
- clear reward shaping
- OpenEnv server support
- local simulator for fast iteration
- inference entrypoint compatible with evaluator-style execution
- data-generation pipeline for post-training experiments
- delayed-event mechanics such as reopen, rejection, and follow-up
- two-level priority handling: queue priority plus department internal priority
- an existing Unsloth + TRL training notebook for Colab-style fine-tuning

## Current limitations

The project is strong today, but the remaining gaps are mostly submission-facing
rather than environment-foundation problems. Compared with a top-end submission,
the current repo is still weaker on:

- polished before/after reward evidence in the README
- final public-facing assets such as a mini-blog or short demo video
- live linked Hugging Face Space and final submission metadata
- larger long-horizon queue sessions beyond the current compact benchmark suite
- deeper multi-agent interaction beyond one primary acting agent
- a final documented trained-model comparison from the Unsloth/TRL path

Those limitations are not fatal. They simply point to the highest-value next
improvements before submission.
