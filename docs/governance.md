# Governance and evaluation

## Control objectives

1. Agents may analyze and recommend but cannot approve their own work.
2. State transitions are explicit and invalid transitions fail closed.
3. Each audit event includes the previous event hash, making later modification detectable.
4. Priority is decomposed into strategic alignment, value, urgency, feasibility and risk.
5. Generated management text is assembled only from structured project facts.

## Evaluation

Tests cover transition policy, idempotency, priority ordering, audit-chain integrity, risk detection and approval separation. A production rollout would also evaluate factuality, harmful recommendations, stakeholder usefulness, latency, cost and drift.

## Limitations

The deterministic demo does not replace portfolio governance or expert judgment. Real deployments require identity and access management, persistent storage, confidential-data controls, prompt-injection defenses and organization-specific evaluation datasets.

