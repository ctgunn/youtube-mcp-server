# Contract: Hosted Networking Output Handoff

## Purpose

Define the output contract that carries managed hosted-networking evidence from Terraform reconciliation into deployment records, hosted verification, and operator review.

## Actors

- Terraform reconciliation workflow exporting infrastructure outputs
- Deployment workflow consuming infrastructure outputs
- Maintainer or reviewer validating rollout evidence

## Required Inputs

The networking handoff for the supported GCP durable-session path must expose or document:

- hosted environment
- durable session connectivity model
- managed hosted network references
- Cloud Run connectivity resource reference
- durable session backend reference
- deployment or verification surface that consumes the exported networking evidence

## Workflow Guarantees

- Terraform outputs remain the canonical handoff into the existing deployment and hosted verification chain.
- Networking outputs must provide enough reviewable evidence for operators to trace the managed path without reconstructing resource values manually.
- The output handoff may include resource references, but it must not expose secret values or bearer tokens.
- Deployment evidence must distinguish declared connectivity intent from proof that the managed networking path was actually provisioned.

## Failure Contract

- If the supported GCP path exports only the connectivity model without the managed network references needed for review, the handoff contract is violated.
- If the deployment workflow bypasses the Terraform-output handoff and cannot show the managed network evidence, the handoff contract is violated.
- If hosted verification cannot identify the managed connectivity path from the exported evidence, the rollout is incomplete.
- If networking references are present only in ad hoc operator notes rather than the reviewed handoff artifacts, the handoff contract is violated.

## Verification Evidence

Successful use of this contract produces:

- one reviewable output set showing the managed hosted-network path
- deployment evidence that preserves the networking handoff without converting it into secret-bearing runtime config
- hosted verification inputs or artifacts that can reference the managed network path when diagnosing durable-session issues
