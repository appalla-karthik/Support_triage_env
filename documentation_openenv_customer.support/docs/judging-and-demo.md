---
title: Judging and Demo
description: How to map the project to the judging criteria and present it effectively.
---

# Judging and Demo

## Minimum requirement checklist

From the criteria you shared, the submission should show:

- usage of OpenEnv
- a minimal training script or notebook using Unsloth or HF TRL
- a short public-facing explanation asset such as a mini-blog or short video
- a hosted Hugging Face Space link in the README
- observable training evidence such as curves, metrics, or before/after behavior

## How this project already satisfies part of that

The current repo already gives you:

- an OpenEnv-compatible environment
- a server implementation
- deterministic evaluation
- local inference pipeline
- validation workflow
- data-generation tools
- a minimal Unsloth + TRL notebook in `notebooks/triageos_training_colab.ipynb`
- a train-and-evaluate script for before/after environment metrics

## What still needs to be added

The biggest remaining submission artifacts are now presentation and proof:

- a linked Hugging Face Space URL
- a concise mini-blog, short video, or slide deck
- a README section with final before/after metrics and plots

The training notebook itself already exists, so the next step is to run it or
summarize its outputs in a judge-friendly way rather than describing it as future work.

## Mapping to the judging categories

### 1. Environment innovation

Current score potential is solid because the project already includes:

- realistic business workflow
- typed environment state
- policy-aware reward shaping
- mixed queue prioritization

To increase this score further, add:

- larger dynamic queues
- specialist interactions
- policy drift
- delayed business outcomes

### 2. Storytelling

This is where the documentation site helps. The cleanest story is:

1. enterprise support is a real, high-value workflow
2. agents must do more than classify text
3. safe routing and communication matter
4. bad decisions have realistic consequences
5. the environment measures those consequences explicitly

### 3. Showing improvement in rewards

You should aim to show:

- baseline reward before training
- reward after post-training
- reduction in policy violations
- improvement in final success rate

Even a small but honest improvement curve is more convincing than broad claims.
The strongest version is one table or plot that compares:

- heuristic or baseline policy
- lightweight trained policy
- Unsloth or TRL-tuned policy, if available

### 4. Reward and training pipeline

The project is already strong on reward logic and has both lightweight and Colab
training paths. The next step is to connect those paths to a visible training table,
saved plots, and one clear narrative about what improved after training.

## Recommended 3-minute pitch flow

### Minute 1

Explain the real-world problem:

- enterprise support queues are high stakes
- agents must classify, prioritize, communicate, and escalate safely
- failure means customer harm, security risk, and business delay

### Minute 2

Show the environment:

- reset a task
- inspect the queue
- step through actions
- show score and progress changing live
- highlight a safety penalty or prioritization requirement

### Minute 3

Show evidence of learning and the future path:

- before/after metrics
- why the reward model is meaningful
- how delayed consequences prevent shallow shortcut behavior
- how the environment could later extend to longer-horizon or multi-agent workflows

## Best demo narrative

The best demo is not "our agent got the right label."

The best demo is:

> Our agent handled a realistic support queue, prioritized a security incident
> over a routine billing issue, used safe customer communication, routed work to
> the right team, and improved measurable reward after training.

That narrative is memorable and directly tied to the judging criteria.
