# Contract: Cloud Run Public Access

## Purpose

Define the operator-facing contract for making the hosted Cloud Run MCP service intentionally reachable by trusted remote consumers without replacing MCP bearer-token authentication at the application boundary.

## Actors

- Operator preparing a hosted Cloud Run environment
- Maintainer reviewing hosted exposure intent before rollout
- Remote MCP integrator consuming the published hosted connection point

## Workflow Scope

- This contract applies to hosted environments that are intended to support trusted remote MCP access.
- It covers provider-adapter reachability and rollout intent, not MCP authentication semantics themselves.
- It builds on the existing hosted security contract rather than replacing it.

## Required Inputs

The public-access workflow must define or document:

- Target hosted environment
- Hosted service name
- Published hosted connection point
- Public invocation intent:
  - `public_remote_mcp`
  - `private_only`
- Runtime identity reference
- Hosted security settings that remain in force after the service becomes reachable:
  - MCP bearer-token requirement
  - browser-origin policy settings where applicable

## Workflow Guarantees

- Environments intended for trusted remote MCP access must enable public Cloud Run reachability intentionally through a reviewable workflow.
- Environments marked `private_only` must be identifiable as not supporting public remote MCP access.
- Public Cloud Run reachability must not be described as sufficient proof of authorization to use `/mcp`.
- The published hosted connection point must be recorded in operator-facing deployment evidence.
- Public-access intent must remain visible in normal review artifacts alongside deployment settings.

## Separation of Concerns

- Cloud Run public invocation determines whether the hosted service can be reached at all.
- MCP bearer-token authentication determines whether a reachable caller may use protected `/mcp` routes.
- `/health` and `/ready` remain outside the MCP bearer-token contract.
- Protected `/mcp` behavior continues to follow the hosted security contract in [hosted-mcp-security.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/013-remote-mcp-security/contracts/hosted-mcp-security.md).

## Failure Contract

- If public invocation is not enabled for an environment intended for trusted remote MCP access, hosted verification must report a cloud-level access failure.
- If public invocation is enabled but bearer credentials are missing or invalid, hosted verification must report an MCP-layer denial rather than a platform reachability failure.
- If the published connection point is absent, stale, or inconsistent with the deployed revision, the rollout evidence is incomplete.
- If operator artifacts do not show whether an environment is public or private, the public-access contract is violated.

## Verification Evidence

Successful use of this contract produces:

- Deployment evidence showing the intended public-access state of the hosted environment
- A published hosted connection point for remote consumers
- Hosted verification evidence proving the environment is publicly reachable when intended
- Hosted verification evidence showing that MCP bearer-token authentication still protects `/mcp` after public reachability is enabled
