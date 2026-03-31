# Contract: Hosted Networking Prerequisite Boundary

## Purpose

Define the operator-facing boundary between Terraform-managed hosted networking for the supported GCP durable-session path and the responsibilities that remain outside this feature.

## Actors

- Operator following the supported GCP runbook
- Maintainer reviewing operator documentation and release readiness
- Reviewer confirming local and hosted workflow boundaries remain clear

## Execution Modes

### Minimal Local

- Does not require hosted GCP networking.
- Remains the fastest developer path for ordinary coding and verification.

### Hosted-Like Local

- May use a shared local session backend for behavior verification.
- Does not prove Cloud Run-to-backend networking and must not be documented as a substitute for the hosted GCP path.

### Hosted GCP Durable Sessions

- Requires the managed hosted network layer documented by this feature.
- Must not require operators to pre-create the supported VPC, subnet, or Cloud Run connectivity resources manually.

## Workflow Guarantees

- The supported GCP runbook must describe one Terraform-managed networking workflow before application rollout.
- Operator documentation must clearly separate Terraform-managed infrastructure responsibilities from remaining operator-managed tasks.
- Local development documentation must remain free of hosted GCP networking prerequisites.
- Failure guidance must help operators distinguish missing managed networking from later deployment or runtime issues.

## Failure Contract

- If the supported GCP runbook still instructs operators to manually create VPC, subnet, or Cloud Run connectivity resources for durable sessions, the boundary contract is violated.
- If local workflows imply that hosted GCP network provisioning is required for ordinary development, the boundary contract is violated.
- If documentation leaves the ownership boundary between Terraform and the operator ambiguous, the supported workflow is incomplete.

## Verification Evidence

Successful use of this contract produces:

- one supported GCP runbook that sequences Terraform-managed networking before application deployment
- clear evidence that local and hosted-like local paths remain separate from hosted GCP networking
- operator-facing remediation guidance for networking provisioning failures without inventing hidden prerequisites
