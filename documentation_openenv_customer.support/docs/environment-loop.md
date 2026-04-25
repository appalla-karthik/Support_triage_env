---
title: Environment Loop
description: How reset, step, state, task structure, and partial observability work in the simulator.
---

# Environment Loop

## Standard loop

The project follows a familiar environment pattern:

```python
from support_triage_env import SupportTriageAction, SupportTriageSimulator

env = SupportTriageSimulator()
obs = env.reset(task_id="billing_refund_easy", seed=7)
obs, reward, done, info = env.step(
    SupportTriageAction(action_type="view_ticket", ticket_id="TCK-1001")
)
state = env.state()
```

This is important because it makes the environment usable for:

- scripted baselines
- model-driven rollouts
- future RL or post-training pipelines
- server-based evaluation through OpenEnv

## Observation design

The observation includes both immediate task context and progress feedback:

- `task`
- `instructions`
- `policy_hints`
- `queue`
- `focused_ticket`
- `last_action_result`
- `accessible_apps`
- `world_summary`
- `recent_events`
- `last_tool_result`
- `progress`
- `reward`
- `done`

This is a strong design choice because it preserves partial observability while
still giving the agent structured signals about whether it is on track.

## State design

The full state goes deeper than the observation. It includes:

- all ticket records
- action history
- focused ticket id
- pending and recent world events
- customer, billing, incident, and policy records
- cumulative reward
- final score
- step count
- environment completion status

This full state is especially useful for debugging, evaluation, and local baseline
policies.

## Why the environment is only partially observable

The environment is not a pure hidden-state world, but it is not trivial either.
The agent must infer the correct action from:

- ticket text
- queue context
- current status
- previous actions
- policy hints

The harder task adds another layer: queue prioritization across multiple tickets,
which means the agent must reason not just about ticket content but about the
correct order of work. In the current repo that prioritization is now two-level:

- a **global queue priority** for support-queue ordering
- a **department-level internal priority** after the ticket is routed to the target team

## Task design pattern

Each task scenario contains:

- a task card
- instructions
- policy hints
- ticket records
- accessible enterprise apps
- optional downstream events
- per-ticket expectations

That structure is good because it keeps the environment modular. You can add new
families later without changing the agent interface.

## Current task progression

### Billing refund

Expected progression:

1. classify correctly
2. draft a safe apology and refund timeline
3. resolve with `refund_submitted`

### Export outage

Expected progression:

1. classify as product bug
2. set high queue priority and urgent engineering internal priority
3. route to engineering
4. reply with urgency-aware guidance
5. escalate instead of resolving

### Security plus refund

Expected progression:

1. prioritize the security incident first
2. classify it as urgent account takeover with urgent trust-and-safety internal priority
3. escalate to `trust_safety`
4. avoid unsafe recovery advice
5. then complete the billing refund task

## Current world dynamics already in the repo

The environment is no longer just a static step-checker. Several task families
already exercise delayed or changing world state through:

- customer follow-up events
- escalation rejection
- ticket reopen events
- queue reprioritization after new information arrives
- account lifecycle risk such as `at_risk` and `security_hold`

That means the agent is already training against a small but meaningful dynamic
world, not only one-shot ticket labeling.

## Why this matters for hackathon themes

This loop already supports meaningful agent behavior because it requires:

- action sequencing
- safety constraints
- policy following
- state tracking across steps
- task completion rather than single-turn response generation

That is why the repo already maps well to a professional world-modeling theme.
