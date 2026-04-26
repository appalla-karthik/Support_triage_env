# Train And Evaluate Summary

## Headline

| Metric | Baseline | Trained | Delta |
| --- | --- | --- | --- |
| Classification accuracy | 0.2918 | 1.0000 | 0.7082 |
| Environment mean score | 0.8293 | 0.9686 | 0.1393 |
| Environment success rate | 0.5500 | 1.0000 | 0.4500 |
| Mean episode steps | 9.00 | 8.10 | -0.90 |

## Evaluation Setup

- Tasks: billing_refund_easy, export_outage_medium, security_and_refund_hard, enterprise_refund_investigation, incident_coordination_outage, executive_security_escalation, escalation_rejection_recovery, refund_reopen_review, mixed_queue_command_center, followup_reprioritization_queue
- Eval seeds: 7, 11
- Hard-task oversampling: mixed_queue_command_center, followup_reprioritization_queue, escalation_rejection_recovery x5

## Per-Task Comparison

| Task | Baseline Score | Trained Score | Baseline Success | Trained Success |
| --- | --- | --- | --- | --- |
| `billing_refund_easy` | 0.9900 | 0.9900 | 1.0000 | 1.0000 |
| `enterprise_refund_investigation` | 0.9000 | 0.9900 | 1.0000 | 1.0000 |
| `escalation_rejection_recovery` | 0.6220 | 0.9520 | 0.0000 | 1.0000 |
| `executive_security_escalation` | 0.6451 | 0.9900 | 0.0000 | 1.0000 |
| `export_outage_medium` | 0.8334 | 0.9900 | 0.5000 | 1.0000 |
| `followup_reprioritization_queue` | 0.7745 | 0.9343 | 0.0000 | 1.0000 |
| `incident_coordination_outage` | 0.9900 | 0.9900 | 1.0000 | 1.0000 |
| `mixed_queue_command_center` | 0.9600 | 0.9600 | 1.0000 | 1.0000 |
| `refund_reopen_review` | 0.9000 | 0.9000 | 1.0000 | 1.0000 |
| `security_and_refund_hard` | 0.6783 | 0.9900 | 0.0000 | 1.0000 |

## Quick Read

- Strongest trained tasks:
  - `billing_refund_easy`: score 0.9900, success 1.0000
  - `enterprise_refund_investigation`: score 0.9900, success 1.0000
  - `executive_security_escalation`: score 0.9900, success 1.0000
- Weakest trained tasks:
  - `refund_reopen_review`: score 0.9000, success 1.0000
  - `followup_reprioritization_queue`: score 0.9343, success 1.0000
  - `escalation_rejection_recovery`: score 0.9520, success 1.0000
