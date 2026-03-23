# Contract: Local Hosted-Like Dependency Path

## Purpose

Define the operator-facing contract for starting the extra local dependencies required to exercise hosted-like durable session behavior without turning cloud provisioning into a prerequisite for normal local development.

## Actors

- Developer running the minimal local runtime
- Developer or operator running hosted-like local verification

## Modes

### Minimal Local Runtime

- Uses the application with local configuration only
- Default session backend is `memory`
- Requires no cloud provisioning
- Must remain the lightest-weight local path

### Hosted-Like Local Verification

- Starts a Redis-compatible dependency locally
- Configures the application to use a shared durable session backend
- Exercises the same session durability settings expected by the hosted path
- Remains separate from the minimal local runtime path

## Inputs

- Local container runtime capable of running Docker Compose
- Optional local port overrides for the Redis-compatible dependency
- Environment values required by the application when switching from `memory` to `redis`

## Required Outputs

- A local connection value for `MCP_SESSION_STORE_URL`
- A documented `MCP_SESSION_BACKEND=redis` switch for hosted-like local verification
- Clear separation between commands for:
  - starting local dependencies
  - running the app
  - executing verification
  - stopping local dependencies

## Workflow Guarantees

- Developers can still run the service locally without starting the hosted-like dependency path.
- Hosted-like local verification uses only repository-defined assets plus standard local tooling.
- Documentation clearly states when to use `memory` versus the Redis-compatible local dependency.

## Failure Contract

- If the local Redis-compatible dependency is not running, hosted-like verification must fail with guidance to start it.
- If a developer follows only the minimal local path, they must not be required to configure hosted infrastructure inputs.
- If the hosted-like path is selected, the prerequisite commands and expected evidence must be documented in one place.

## Verification Evidence

Successful use of this contract produces:

- A running local Redis-compatible dependency
- A successful local app start configured for shared durable sessions
- Verification output showing session continuity behavior can be exercised outside the cloud path
