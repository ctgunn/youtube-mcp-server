# Implementation Plan: Local Runtime Ergonomics and Environment Entry Point

**Branch**: `026-local-runtime-entrypoint` | **Date**: 2026-03-30 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/026-local-runtime-entrypoint/spec.md)
**Input**: Feature specification from `/specs/026-local-runtime-entrypoint/spec.md`

## Summary

Formalize the repository's local developer entry point around the existing `scripts/dev_local.sh` plus `.env.local` workflow, keep Redis-backed hosted-like local verification as a companion path, and remove ambiguity between local runtime defaults and hosted deployment inputs. The implementation should tighten the developer-facing contract and tests around discoverability, variable boundaries, startup guidance, and clear failure behavior without introducing a second local startup mechanism.

Canonical terms for this feature are `local startup entry point`, `local environment defaults file`, `minimal local runtime`, `hosted-like local verification`, and `local override`.

## Technical Context

**Language/Version**: Python 3.11 for service and verification tooling; Bash for the local startup wrapper  
**Primary Dependencies**: FastAPI, Pydantic v2, Uvicorn, existing runtime/config modules under `src/mcp_server/`, `scripts/dev_local.sh`, `.env.local`, Docker Compose assets under `infrastructure/local/`  
**Storage**: In-memory runtime state only for local execution; file-based local environment defaults, documentation, and specification artifacts  
**Testing**: `pytest` for unit, contract, and integration coverage; `ruff check .`; local startup workflow checks through documentation and script-focused tests  
**Target Platform**: Local developer workstations running the Python service directly, with optional Docker Compose for Redis-backed hosted-like verification  
**Project Type**: Python web service with developer tooling and documentation-backed local workflow contracts  
**Performance Goals**: Developers can start the minimal local runtime through one repository entry point in under 5 minutes from a prepared workspace and can switch to hosted-like local verification in under 10 minutes without consulting hosted deployment instructions  
**Constraints**: Reuse `scripts/dev_local.sh`, `.env.local`, `README.md`, and `infrastructure/local/` rather than creating a parallel startup path; preserve minimal-local versus hosted-like-local separation; keep cloud deployment inputs out of the default local path; keep secrets out of committed docs and logs; preserve clear failure guidance when `.env.local` or Redis prerequisites are missing  
**Scale/Scope**: One canonical local startup entry point, one dedicated local environment defaults file, two local runtime profiles, one hosted-like dependency bootstrap path, and the existing contract/integration test layers that validate local workflow behavior

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Contracts defined or updated for all external/MCP-facing behavior changes
- [x] Plan includes explicit Red-Green-Refactor steps for each phase and user story
- [x] Red phase identifies failing tests before implementation tasks begin
- [x] Green phase limits implementation to minimum code required for passing tests
- [x] Refactor phase includes cleanup tasks with a full repository test-suite re-run
- [x] Integration and regression coverage strategy is documented
- [x] Plan names the command that proves the full repository test suite passes before completion
- [x] Observability, security, and simplicity constraints are addressed

Pre-design gate result: PASS. This feature changes the developer-facing local workflow contract, so a Markdown contract is required even though no MCP protocol surface changes. Full-suite proof command: `pytest`.

## Project Structure

### Documentation (this feature)

```text
specs/026-local-runtime-entrypoint/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── local-runtime-entrypoint-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
README.md
.env.local

infrastructure/
└── local/
    ├── .env.example
    ├── README.md
    └── compose.yaml

scripts/
└── dev_local.sh

src/
└── mcp_server/
    ├── cloud_run_entrypoint.py
    ├── config.py
    ├── infrastructure_contract.py
    └── transport/

tests/
├── contract/
├── integration/
└── unit/
```

**Structure Decision**: Keep the existing single Python service and local developer workflow surface. FND-026 should update the current local startup script, local environment defaults, and documentation/test layers rather than introducing a new service entrypoint, CLI, or infrastructure path.

## Implementation Phases

### Phase 0 - Research and Scope Lock

- **Red**: Capture the current mismatch between the existing local helper assets and the top-level developer guidance, including the fact that the repository already has `scripts/dev_local.sh` and `.env.local` but the root README still leads with manual inline environment exports.
- **Green**: Resolve the planning decisions for the canonical local entry point, local defaults ownership, hosted-like local companion workflow, validation layers, and failure guidance in `research.md`.
- **Refactor**: Normalize terminology across local runtime assets so later implementation work uses one consistent distinction between minimal local runtime and hosted-like local verification.

### Phase 1 - Design and Contracts

- **Red**: Define failing contract and documentation expectations proving the canonical local startup path, variable boundaries, and hosted-like dependency flow are not yet represented consistently.
- **Green**: Produce `data-model.md`, `contracts/local-runtime-entrypoint-contract.md`, and `quickstart.md` describing the local runtime profiles, environment defaults, override rules, startup guarantees, failure behavior, and verification flow.
- **Refactor**: Remove duplicated or conflicting design wording between the root README, local infrastructure docs, and plan artifacts, then rerun the constitution check against the completed design.

### Phase 2 - Implementation Planning Preview

- **Red**: Identify the tests that must fail first once implementation starts, including missing canonical-entrypoint assertions, missing `.env.local` guidance checks, missing hosted-like companion-flow checks, and unclear local-versus-hosted variable-boundary assertions.
- **Green**: Organize implementation around the minimum path that makes those tests pass: align the README and local docs around `scripts/dev_local.sh`, keep `.env.local` as the documented baseline, preserve hosted-like Redis bootstrap as a companion path, and add clear failure guidance for missing prerequisites.
- **Refactor**: Remove duplicated startup instructions and variable lists between docs and scripts, then run the full repository suite with `pytest` after implementation changes and finish with `ruff check .`.

## User Story Delivery Strategy

### User Story 1 - Start Locally in One Step

- **Red**: Add failing integration or documentation tests proving the repository still requires developers to reconstruct the minimal local startup command manually instead of using one canonical entry point.
- **Green**: Add the minimum documentation and script-alignment changes needed so developers can use the documented local startup entry point with the dedicated local defaults file and reach a running local server without cloud prerequisites.
- **Refactor**: Remove duplicated minimal-local startup commands and keep one source of truth for the baseline local runtime path, then rerun `pytest`.

### User Story 2 - Exercise Hosted-Like Local Behavior When Needed

- **Red**: Add failing contract or integration checks proving the hosted-like local companion path is not clearly linked to the local entry point, missing dependency guidance, or unclear about failure behavior when Redis is unavailable.
- **Green**: Add the minimum contract and documentation updates needed so developers can bootstrap the local Redis dependency, switch to hosted-like mode, and understand the expected evidence and failure behavior.
- **Refactor**: Consolidate hosted-like local wording between the root README, `infrastructure/local/README.md`, and any startup guidance so Redis-backed verification remains a clear companion path rather than a competing default, then rerun `pytest`.

### User Story 3 - Understand Local Versus Hosted Settings

- **Red**: Add failing documentation and regression checks proving local defaults, hosted-like overrides, and hosted deployment inputs are still mixed together or left implicit.
- **Green**: Add the minimum environment-file and documentation updates needed to show which variables belong to baseline local runtime, which are overridden for hosted-like local verification, and which remain deployment-only inputs.
- **Refactor**: Tighten naming and variable-grouping language across docs and config examples so future changes can update one consistent model, then rerun `pytest`.

## Coverage Strategy

- Unit coverage should validate any startup-wrapper behavior or environment-selection helpers touched during implementation, especially around missing `.env.local`, hosted-like mode selection, and baseline override handling.
- Contract coverage should lock the local runtime entrypoint contract documented in `/specs/026-local-runtime-entrypoint/contracts/local-runtime-entrypoint-contract.md`.
- Integration coverage should preserve README and local-infrastructure workflow examples, including the distinction between minimal local runtime and hosted-like local verification and the expected dependency bootstrap commands.
- Regression coverage should preserve the local-first execution model from FND-019 and the hosted-like local dependency workflow documented under `infrastructure/local/`.
- The full repository test-suite command required before completion is `pytest`.

## Observability, Security, and Simplicity

- Observability: local workflow failures must produce clear operator-facing messages for missing `.env.local`, missing Redis bootstrap, or invalid local overrides so developers can diagnose setup problems quickly.
- Security: local docs and defaults must avoid committing real secret values and must keep the boundary between safe local defaults and developer-supplied credentials explicit.
- Simplicity: this feature extends the existing local startup wrapper, `.env.local`, and documentation surfaces. It does not add a second launcher, a second defaults file for the minimal path, or hosted-only requirements to the default local workflow.

## Post-Design Constitution Check

- [x] Contracts defined or updated for all external/MCP-facing behavior changes
- [x] Plan includes explicit Red-Green-Refactor steps for each phase and user story
- [x] Red phase identifies failing tests before implementation tasks begin
- [x] Green phase limits implementation to minimum code required for passing tests
- [x] Refactor phase includes cleanup tasks with a full repository test-suite re-run
- [x] Integration and regression coverage strategy is documented
- [x] Plan names the command that proves the full repository test suite passes before completion
- [x] Observability, security, and simplicity constraints are addressed

Post-design gate result: PASS. The design updates the repository's existing local workflow contract without adding a parallel runtime path, preserves the local-first boundary, and keeps the full-suite completion command as `pytest`.

## Complexity Tracking

No constitution violations require exception tracking for this feature.
