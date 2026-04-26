---
title: Reward and Evaluation
description: How deterministic grading, shaped reward, and penalties are implemented.
---

# Reward and Evaluation

## What is strong about the current design

One of the best parts of this project is that the evaluation logic is not vague.
It is implemented in code and tied directly to the task expectations.

The grader returns a `GradingSnapshot` with:

- score
- component contributions
- penalties
- satisfied requirements
- outstanding requirements
- violations

That makes the environment much easier to explain to judges and much easier to
improve through training.

## Reward structure

The simulator computes shaped reward from several pieces:

- score delta from the previous step
- per-step cost
- repeated-action penalty
- invalid-action penalty

This is a good middle ground. It rewards progress, discourages wasteful behavior,
and punishes unsafe or malformed actions.

## What each task grader measures

### Billing refund grader

Major reward components:

- correct category
- correct global queue priority
- correct billing internal priority
- correct team
- reply quality
- correct resolution action

Major penalties:

- requesting sensitive data such as full card numbers or passwords

### Export outage grader

Major reward components:

- correct category
- correct global queue priority
- correct engineering internal priority
- correct team
- reply quality
- escalation note quality
- escalation instead of premature resolution

Major penalties:

- resolving a live outage too early
- promising an unsupported ETA

### Security and refund grader

Major reward components:

- handling the urgent security ticket before routine billing work
- correct classification, queue priority, internal priority, and team for security
- safe security reply
- informative escalation context
- correct escalation outcome
- correct completion of the secondary billing task

Major penalties:

- prioritizing billing before security
- unsafe recovery advice
- resolving the security ticket instead of escalating it
- requesting sensitive data

## Why this evaluation is convincing

This reward model is strong for a hackathon because it is:

- deterministic
- interpretable
- decomposed into components
- aligned with business behavior
- safety aware

That is much better than a vague "looks good" reward.

## What the evaluation already models beyond the immediate step

The evaluation is not only local to the current action anymore. The current repo
already includes several longer-range checks and side effects such as:

- SLA pressure and queue-health penalties
- downstream business-risk penalties
- escalation rejection for weak packets
- refund reopen events when approval review is skipped
- follow-up-driven reprioritization in queue tasks

Those mechanics are especially important for the hackathon story because they make
the environment harder to game through shallow "label and finish" behavior.

## Confidence-aware penalties

The current repo also includes explicit confidence-aware penalties. These
penalize risky actions that skip the evidence-gathering process instead of only
punishing malformed actions or obvious workflow mistakes.

Current named examples include:

- `confidence_failure_resolution`
  Example: resolving a high-risk refund workflow before billing and policy checks are complete.
- `confidence_failure_escalation`
  Example: escalating a security or outage workflow before checking policy, or escalating an incident-style ticket without enough supporting evidence.
- `confidence_failure_urgent_priority`
  Example: marking a routine ticket as `urgent` without enough risk, SLA, or business-impact evidence.

Why this matters:

- it makes the reward more process-aware
- it discourages reward hacking through risky shortcuts
- it creates a very demo-friendly before/after story because the penalty names are explicit

## Best next improvements

If you want to improve the environment for Round 2, the most valuable reward
extensions would be:

1. **Larger queue-level metrics** such as total risk reduction, weighted backlog health, or enterprise retention pressure across more tickets.
2. **Richer tool-use quality** where poor note-taking or missing metadata more directly affects future steps.
3. **Policy drift handling** where reward changes when operating procedures evolve mid-episode.
4. **Cross-team quality checks** that score whether engineering, billing, and trust queues receive the right internal urgency level.

Those changes would make the environment feel more like a living enterprise system
and less like a compact task pack.
