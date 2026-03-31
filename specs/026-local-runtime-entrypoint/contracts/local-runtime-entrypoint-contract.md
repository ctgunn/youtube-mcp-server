# Contract: Local Runtime Entry Point

## Purpose

Define the developer-facing contract for starting the MCP server locally through one repository-owned entry point while preserving a separate hosted-like local verification path for durable-session checks.

## Actors

- Developer running the minimal local runtime for day-to-day work
- Developer or maintainer running hosted-like local verification
- Maintainer reviewing local runtime defaults and workflow boundaries

## Workflow Surfaces

- Canonical local startup entry point
- Dedicated local environment defaults file
- Hosted-like local dependency bootstrap path
- Root documentation describing when to use each local mode

## Runtime Profiles

### Minimal Local Runtime

- Uses the canonical local startup entry point
- Loads the dedicated local environment defaults file automatically
- Defaults to a memory-backed local session mode
- Requires no cloud provisioning, hosted network setup, or shared-session dependency
- Remains the default path for normal local development

### Hosted-Like Local Verification

- Reuses the same canonical local startup entry point
- Applies hosted-like local session overrides only when explicitly selected
- Requires the local durable-session dependency bootstrap path
- Exists for session continuity, readiness, and replay-oriented local verification
- Remains a companion path rather than the default developer workflow

## Inputs

- Repository workspace with project dependencies already installed
- Dedicated local environment defaults file for the baseline local runtime
- Optional local overrides selected by the developer
- Hosted-like dependency bootstrap commands when durable-session verification is needed

## Required Outputs

- One documented command path for starting the minimal local runtime
- One documented companion path for hosted-like local verification
- Clear grouping of local baseline variables, hosted-like local overrides, and hosted deployment-only inputs
- Clear startup success checks and failure guidance for both local runtime profiles

## Workflow Guarantees

- Developers can start the minimal local runtime without reconstructing runtime settings from multiple documents.
- Developers can switch to hosted-like local verification without changing the canonical startup entry point.
- Hosted-like local verification remains optional and does not become a prerequisite for the minimal local runtime.
- Local runtime documentation states when to use minimal local runtime versus hosted-like local verification.

## Failure Contract

- If the dedicated local environment defaults file is missing, the local startup path must fail with guidance to restore or create the expected local defaults.
- If hosted-like local verification is selected without the required local dependency running, the workflow must fail with guidance to start that dependency.
- If a developer uses the minimal local path, the workflow must not require hosted deployment variables or cloud infrastructure prerequisites.
- If local overrides are used, the baseline local defaults and expected recovery path must remain understandable.

## Verification Evidence

Successful use of this contract produces:

- A documented minimal-local startup path that points to one canonical entry point
- A documented hosted-like local companion path with dependency bootstrap and shutdown commands
- Evidence that the minimal local runtime starts without hosted prerequisites
- Evidence that hosted-like local verification either starts with the dependency available or fails clearly when the dependency is missing
