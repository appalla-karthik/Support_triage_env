---
title: Submission-Ready Problem Statement
description: A refined hackathon problem statement built from the current Support_triage_env project.
---

# Submission-Ready Problem Statement

## Recommended title

**Support Operations Control Tower**

## Short problem statement

Build an OpenEnv environment in which an agent operates as a frontline support
triage coordinator for an enterprise software company. The agent must inspect a
partially observable support queue, classify and prioritize tickets, write safe and
useful customer responses, route issues to the correct internal teams, and decide
when cases should be escalated versus resolved. The environment should reward not
only correctness, but also queue prioritization, safety compliance, escalation
quality, and long-term business outcomes.

## Why this is a strong fit

This statement is a strong match for your current project because it stays true to
what the repo already implements while sounding broader, more strategic, and more
enterprise-relevant.

## Theme alignment

### Primary theme

**Theme 3.1: World Modeling across professional tasks**

### Secondary theme

**Theme 2: Long-Horizon Planning and Instruction Following**

### Optional expansion theme

**Theme 1: Multi-Agent Interactions**

## Environment

The environment is a simulated enterprise support operations system with:

- a live queue of customer tickets
- multiple issue types with different urgency levels
- business policies and safety constraints
- internal teams such as billing, engineering, and trust and safety
- typed actions that update the underlying world state
- delayed and partial rewards based on downstream outcomes

## Capabilities of the agent

The agent should be able to:

- read and interpret support ticket content
- infer issue category and urgency
- prioritize work across a queue
- produce policy-safe customer communication
- route issues to the correct internal team
- escalate incidents when frontline resolution is unsafe or insufficient
- preserve context across multiple steps
- recover from mistakes without getting stuck in repeated action loops

## Tasks to be performed

The environment should support tasks such as:

- duplicate-charge refund handling
- product outage triage and escalation
- security incident containment and routing
- mixed-queue prioritization under limited steps
- long-horizon queue management with delayed downstream feedback
- policy-change adaptation when operating procedures evolve

## Reward model and evaluation logic

The reward model should include:

- positive reward for correct classification, routing, prioritization, and terminal actions
- partial credit for high-quality, policy-compliant replies
- penalties for unsafe guidance, premature resolution, repeated actions, and invalid actions
- queue-level reward for handling the highest-risk work first
- delayed reward for downstream outcomes such as escalation quality or SLA preservation

## Post-training or self-improvement strategy

The best post-training strategy for this environment is:

1. generate large synthetic datasets from seeded task families
2. warm-start on supervised support-routing and reply-generation data
3. evaluate through environment rollouts
4. refine with reward-aware optimization against success rate, score, and violation metrics
5. gradually increase difficulty through larger queues, policy drift, and more realistic downstream effects

## What makes this statement stronger than the current raw framing

Your current project is already good, but the refined problem statement improves it
in three ways:

- it sounds like a serious enterprise workflow, not a small ticket classifier
- it naturally supports longer horizons and richer reward shaping
- it opens the door to multi-agent and oversight extensions without breaking the core idea

## Alternative hybrid framing

If you want to sound even more differentiated, use this version:

> Build a policy-aware support operations environment where a generalist agent must
> coordinate customer communication, specialist handoffs, and queue-level risk under
> changing policies and delayed outcomes.

That phrasing gives you more room to add agent coordination and policy drift later.
