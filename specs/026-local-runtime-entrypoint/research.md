# Research: Local Runtime Ergonomics and Environment Entry Point

## Implementation Targets

- One repository-owned local startup entry point must become the explicit default for day-to-day development.
- The dedicated local environment defaults file must remain separate from hosted deployment inputs.
- Hosted-like local verification must remain available as a companion flow for durable-session checks.
- Validation must extend the existing contract and integration test layers rather than invent a new testing surface.

## Decision 1: Treat `scripts/dev_local.sh` as the canonical local startup entry point

- **Decision**: Use `scripts/dev_local.sh` as the primary developer-facing startup path for the minimal local runtime.
- **Rationale**: The repository already contains a startup wrapper that loads `.env.local`, exports the baseline local defaults, and launches the ASGI service. Formalizing that wrapper removes the need for developers to reconstruct inline environment exports from documentation every session.
- **Alternatives considered**:
  - Keep manual `python3 -m uvicorn ...` commands as the primary path. Rejected because it preserves the current friction and duplicates runtime settings across docs.
  - Create a second startup wrapper. Rejected because it would split the local workflow and add drift risk.

## Decision 2: Keep `.env.local` as the dedicated local environment defaults file

- **Decision**: Preserve `.env.local` as the maintained defaults file for the minimal local runtime.
- **Rationale**: `.env.local` already contains local metadata, auth defaults, host/port settings, and memory-backed session defaults. It is the correct place to document the baseline local configuration while still allowing developer-specific overrides when needed.
- **Alternatives considered**:
  - Move all local defaults into `infrastructure/local/.env.example`. Rejected because that file is scoped to the Redis-backed hosted-like path and does not represent the full minimal local runtime.
  - Require developers to export local variables manually. Rejected because it conflicts with the feature goal of a predictable one-command local startup path.

## Decision 3: Preserve hosted-like local verification as a companion Redis-backed path

- **Decision**: Keep hosted-like local verification separate from the minimal local runtime and anchor it on the existing Redis bootstrap assets under `infrastructure/local/`.
- **Rationale**: The repository already documents and tests a provider-free local dependency path for durable-session checks. The feature requirements explicitly keep this as a companion flow rather than the default development path.
- **Alternatives considered**:
  - Collapse minimal local and hosted-like local into one startup mode. Rejected because it would add unnecessary dependency overhead to day-to-day development and blur the scope boundary.
  - Remove the hosted-like path from the local workflow. Rejected because durable-session verification remains a required local development capability.

## Decision 4: Model FND-026 as a documentation-backed workflow contract change

- **Decision**: Represent the external surface of this feature with a Markdown workflow contract under `specs/026-local-runtime-entrypoint/contracts/`.
- **Rationale**: FND-026 changes the repository's developer-facing local workflow rather than the remote MCP protocol. The constitution still requires explicit contracts for external behavior changes, and this repository already uses Markdown contracts for operational boundaries.
- **Alternatives considered**:
  - Skip contract artifacts because the feature is “only docs.” Rejected because the local developer workflow is an externally consumed interface.
  - Define an API-style contract. Rejected because the feature scope is startup workflow, environment boundaries, and verification guidance, not a new service endpoint.

## Decision 5: Reuse the existing contract and integration test surfaces

- **Decision**: Extend the current contract and integration tests that already validate README workflow examples and local-hosted dependency boundaries.
- **Rationale**: The repository already has tests that assert the README distinguishes minimal local versus hosted-like local behavior and that the local dependency assets preserve the Redis-backed path. Adding FND-026 coverage there keeps the validation close to the user-facing contract.
- **Alternatives considered**:
  - Add unit-only coverage. Rejected because the primary behavior here is documentation, workflow, and script contract behavior.
  - Add a new test category. Rejected because the existing contract and integration layers already fit the feature.

## Decision 6: Focus implementation on consistency and discoverability rather than new runtime capability

- **Decision**: Scope implementation to aligning the current script, defaults file, and documentation around one unmistakable local workflow.
- **Rationale**: The repository already has the needed runtime pieces; the gap is that the root documentation still leads with manual startup commands and does not clearly elevate the wrapper script as the primary path. Solving consistency is enough to satisfy the feature without widening scope.
- **Alternatives considered**:
  - Treat the feature as already complete because the files exist. Rejected because the top-level guidance still leaves developers to reconstruct runtime settings manually.
  - Expand the feature into a broader local tooling overhaul. Rejected because it would exceed the FND-026 requirements.
