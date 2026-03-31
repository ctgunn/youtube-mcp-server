# Contract: Hosted Networking Provisioning

## Purpose

Define the provider-adapter contract for how the supported GCP path provisions the network resources required for durable Redis-backed hosted sessions.

## Actors

- Operator provisioning a hosted GCP environment
- Maintainer reviewing the GCP provider adapter
- Deployment workflow consuming the provisioned hosted network layer

## Workflow Scope

- This contract applies to hosted GCP environments that claim durable hosted session support.
- It covers the managed network resources required by the hosted runtime and the durable session backend.
- It does not redefine MCP session semantics, application authentication, or local-only execution modes.

## Managed Resource Coverage

The supported GCP hosted durable-session path must provision and document:

- the hosted network reference used by the durable session path
- the subnet resources required by that hosted path
- the Cloud Run runtime connectivity resource required to attach to that path
- the network authorization relationship used by the durable session backend

## Workflow Guarantees

- The supported GCP path must provision the hosted durable-session network layer through reviewable Terraform definitions rather than operator-created manual prerequisites.
- Operators must be able to identify the managed network path from normal infrastructure review artifacts.
- Environments claiming durable hosted session support must not rely on pre-existing manual VPC, subnet, or Cloud Run connectivity resources outside the supported Terraform path.
- The contract must preserve the existing application-layer authentication and hosted MCP behavior while changing only the provider-specific network provisioning path.

## Failure Contract

- If the required hosted network resources are absent from the managed Terraform path, the hosted durable-session provisioning contract is violated.
- If the durable session backend still depends on an externally supplied authorized network for the supported GCP path, the contract is violated.
- If Cloud Run cannot attach to the managed connectivity path required by the durable session model, the hosted rollout cannot be treated as ready.
- If the managed network path is not reviewable through normal infrastructure artifacts, the provisioning contract is incomplete.

## Verification Evidence

Successful use of this contract produces:

- reviewable Terraform evidence that the hosted network layer is in scope
- one clear mapping between the hosted runtime attachment path and the durable session backend network path
- operator-facing proof that the supported GCP path no longer depends on manual creation of VPC, subnet, or connectivity resources
