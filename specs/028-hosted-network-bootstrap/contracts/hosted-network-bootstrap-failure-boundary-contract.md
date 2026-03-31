# Contract: Hosted Network Bootstrap Failure Boundary

## Purpose

Define the minimum operator-visible failure classes required to distinguish bootstrap and network-reconcile failures from later hosted rollout failures.

## Actors

- Operator diagnosing a failed hosted deployment run
- Maintainer reviewing workflow artifacts and deployment records
- Workflow runner producing stage summaries and reviewable artifacts

## Required Failure Classes

The hosted deployment path must make these release-blocking failure classes distinguishable:

1. `bootstrap_input_failure`
   - one-time external prerequisites were missing or unusable before reconciliation could start
2. `network_reconcile_failure`
   - managed hosted networking failed during `infrastructure_reconcile`
3. `deployment_failure`
   - application rollout failed after bootstrap and output export completed
4. `hosted_verification_failure`
   - post-deploy hosted verification failed after rollout completed

## Failure Interpretation Rules

- A missing bootstrap prerequisite must remain distinct from a failure inside managed infrastructure reconciliation.
- A managed network reconciliation failure must remain distinct from an application deployment failure.
- A deployment failure must remain distinct from a hosted verification failure.
- Each failed run must expose enough stage and artifact information for an operator to determine the primary failure class without consulting undocumented tribal knowledge.

## Workflow Guarantees

- Failed runs are operator-readable at the boundary level needed for remediation.
- The hosted deployment path preserves the existing ordered stage model while adding clearer bootstrap and network failure interpretation.
- Failure summaries may remain concise, but they must map cleanly to one of the required failure classes.

## Verification Evidence

Successful use of this contract produces:

- one workflow result that identifies the first failed stage
- one deployment or workflow artifact set that supports classification of the primary failure boundary
- operator guidance that explains how to remediate each boundary without collapsing all failures into generic infrastructure failure

## Failure Contract

- If bootstrap-input failures and managed network reconcile failures are reported as the same undifferentiated condition, the contract is violated.
- If a failed run does not expose enough information to distinguish deploy failure from hosted verification failure, the contract is violated.
- If the operator must infer the failure boundary from undocumented implementation details, the contract is violated.
