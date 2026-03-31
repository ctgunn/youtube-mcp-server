# Contract: Hosted Network Bootstrap Prerequisite Boundary

## Purpose

Define the remaining one-time external prerequisites for the supported hosted path after managed hosted networking became part of the recurring automated deployment workflow.

## Actors

- Operator preparing the hosted environment for automated rollout
- Maintainer documenting the supported hosted deployment path
- Workflow runner consuming prepared prerequisites during a hosted deployment run

## Remaining External Prerequisites

The documented prerequisite boundary must identify, at minimum:

1. repository and cloud access prerequisites
   - project, region, service, artifact, and automation identity inputs required by the pipeline
2. environment-specific infrastructure inputs
   - the reviewed Terraform variable file and the environment values it supplies to the hosted path
3. operator-managed secret values
   - required secret values that must already exist before deploy and hosted verification run

## Automation-Managed Responsibilities

- reconcile the managed hosted network layer through the reviewed infrastructure path
- export Terraform outputs for deployment handoff
- deploy the current application revision through `scripts/deploy_cloud_run.sh`
- run hosted verification through `scripts/verify_cloud_run_foundation.py`
- publish artifacts needed for operator review and failure diagnosis

## Boundary Rules

- The supported hosted path must not require a separate recurring manual network provisioning sequence outside the automatic deployment chain.
- Environment-specific Terraform inputs may describe the hosted network shape, but they must not be documented as a separate recurring operator-run network bootstrap workflow.
- Required secret values remain outside automation ownership even when secret references and runtime identities are automation-managed.
- local development and hosted-like local verification remain outside the hosted network bootstrap prerequisite boundary.

## Workflow Guarantees

- A first-time operator can identify what still must be prepared outside the recurring deployment run.
- Reviewers can confirm that recurring hosted network provisioning is automation-managed for the supported hosted path.
- Documentation keeps one-time external setup separate from the recurring automatic deployment chain.

## Failure Contract

- If the documented boundary still implies that operators must create the supported hosted network resources manually on each deployment path, the contract is violated.
- If environment-specific Terraform inputs are conflated with recurring manual network provisioning, the contract is violated.
- If automation implies ownership of secret contents rather than secret references and runtime wiring, the contract is violated.
