# Implementation Plan: Cloud-Agnostic Infrastructure Module Strategy

**Branch**: `020-cloud-agnostic-iac` | **Date**: 2026-03-22 | **Spec**: [spec.md](~/Projects/youtube-mcp-server/specs/020-cloud-agnostic-iac/spec.md)
**Input**: Feature specification from `/specs/020-cloud-agnostic-iac/spec.md`

## Summary

Organize the existing Infrastructure as Code foundation around a shared platform contract instead of a GCP-only infrastructure shape, then define provider adapter boundaries that keep local execution, hosted-like local verification, and hosted deployment under one consistent model. The design will keep the current Python service, deployment script, and local Redis-backed verification path, treat `infrastructure/gcp` as the first complete provider adapter, and add a planning-grade secondary provider adapter contract to prove the layout is portable beyond the current Cloud Run target.

Canonical portability terms for this feature are `shared platform contract`, `provider adapter`, `capability mapping`, and `execution mode`.

## Technical Context

**Language/Version**: Python 3.11 for service and verification tooling; Terraform-compatible IaC definitions for hosted infrastructure modules  
**Primary Dependencies**: FastAPI, Pydantic v2, Uvicorn, Redis client, Terraform-compatible IaC assets under `infrastructure/`, Docker Compose for hosted-like local dependency startup  
**Storage**: In-memory runtime state for the app; Redis-compatible shared ephemeral state for hosted session durability; file-based infrastructure definitions, contracts, and operator documentation  
**Testing**: `pytest` for unit, contract, and integration suites; documentation and workflow verification for infrastructure, deployment, and local execution modes  
**Target Platform**: Local developer environments, hosted-like local Docker environments, GCP-hosted deployments, and one planning-grade secondary cloud provider adapter path  
**Project Type**: Python web service with infrastructure automation, provider adapter contracts, and operator runbooks  
**Performance Goals**: Preserve the PRD hosted reliability and latency expectations while keeping the minimum local runtime path lightweight and keeping secondary-provider mapping reviewable in one planning session  
**Constraints**: Local execution must not require cloud-provider modules; secrets must remain secret-backed and absent from logs; provider adapters must preserve one application deployment model; the existing GCP foundation and local dependency path must remain understandable as instances of the shared contract rather than separate systems  
**Scale/Scope**: One MCP service, three documented execution modes (`minimal_local`, `hosted_like_local`, `hosted`), one complete primary provider adapter (`gcp`), one planning-grade secondary provider adapter (`aws`), and one shared platform contract covering runtime, networking, secrets, observability, and durable session support

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

Pre-design gate result: PASS. The feature changes operator-facing infrastructure strategy and documentation rather than MCP request payloads, so the contract surface is the shared platform capability model, provider adapter obligations, and execution-mode boundaries. Full-suite proof command: `pytest`.

## Project Structure

### Documentation (this feature)

```text
specs/020-cloud-agnostic-iac/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── shared-platform-contract.md
│   ├── aws-provider-adapter-contract.md
│   └── execution-mode-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
infrastructure/
├── gcp/
└── local/

scripts/
├── deploy_cloud_run.sh
└── verify_cloud_run_foundation.py

src/
└── mcp_server/

tests/
├── contract/
├── integration/
└── unit/
```

**Structure Decision**: Keep the existing single Python service layout and the current `infrastructure/gcp` plus `infrastructure/local` directories, but reinterpret them through a provider-agnostic platform contract. FND-020 planning does not introduce a new application package or deployment path; it adds design artifacts that define how future provider adapters fit beside the existing GCP implementation without disturbing the local-first workflow.

## Implementation Phases

### Phase 0 - Research and Scope Lock

- **Red**: Capture the current portability gap explicitly by showing that the existing infrastructure foundation is GCP-first, that cross-provider capability boundaries are not yet named, and that local, hosted-like, and hosted paths are documented but not yet unified under one shared contract.
- **Green**: Resolve the planning decisions for shared platform capability boundaries, provider adapter responsibilities, secondary-provider selection, deployment-model preservation, and execution-mode relationships in `research.md`.
- **Refactor**: Remove ambiguous portability language, align terms with FND-019 and the README, and confirm the research decisions support a simple handoff into data model, contracts, and quickstart artifacts without over-designing implementation.

### Phase 1 - Design and Contracts

- **Red**: Define failing contract expectations for a shared platform contract, one planning-grade secondary provider adapter, and a unified execution-mode contract that preserves local-first development.
- **Green**: Produce `data-model.md`, contract documents in `/contracts/`, and `quickstart.md` describing how GCP, the secondary provider path, and local modes align to one shared infrastructure model.
- **Refactor**: Normalize capability names, inputs, outputs, and failure language across the design artifacts, then rerun the constitution check against the completed design.

### Phase 2 - Implementation Planning Preview

- **Red**: Identify the tests that must fail first once implementation starts, including missing shared-platform contract coverage, missing provider-adapter mapping checks, and missing documentation coverage for local-versus-hosted portability boundaries.
- **Green**: Organize implementation around the minimum path that makes those tests pass: refactor the current GCP infrastructure docs/assets behind shared capability concepts, add secondary-provider planning or scaffold assets, and update existing documentation and tests without changing the application deployment model.
- **Refactor**: Remove duplicated provider-specific assumptions across contracts, infrastructure docs, and test fixtures, then run the full repository suite with `pytest` after implementation changes.

## User Story Delivery Strategy

### User Story 1 - Define a Shared Platform Contract Across Providers

- **Red**: Add failing contract and integration coverage proving the infrastructure model is still described primarily through GCP-specific assumptions and that shared platform capabilities are not yet independently reviewable.
- **Green**: Add the minimum shared-platform artifacts that define portable capabilities, shared inputs and outputs, and the portability boundary between the application deployment model and provider adapters.
- **Refactor**: Remove duplicated capability language from provider-specific docs, align the shared contract with current GCP and local workflows, and rerun `pytest`.

### User Story 2 - Add or Adapt a Provider Path Without Rewriting the Platform Model

- **Red**: Add failing checks proving a secondary provider cannot yet be reasoned about without inventing a new platform model.
- **Green**: Add a planning-grade secondary provider adapter contract and design artifacts that map the shared platform contract onto that provider's capabilities and limitations.
- **Refactor**: Tighten the provider-adapter boundary so the shared contract stays stable and rerun `pytest`.

### User Story 3 - Preserve Local-First Development While Explaining Hosted Variants

- **Red**: Add failing checks proving the local, hosted-like local, and hosted paths are documented independently but not yet clearly related under one shared contract.
- **Green**: Add execution-mode documentation and design artifacts that keep the minimum local path free of cloud prerequisites while explaining how hosted-like and hosted modes consume the same capability model.
- **Refactor**: Remove overlapping local-versus-hosted language, confirm security and observability guidance still applies consistently, and rerun `pytest`.

## Coverage Strategy

- Unit coverage should validate any shared-contract parsing or capability mapping helpers introduced during implementation.
- Contract coverage should lock the shared platform contract, the provider-adapter contract, and the execution-mode contract documented in `/specs/020-cloud-agnostic-iac/contracts/`.
- Integration coverage should verify the current GCP foundation, deployment handoff, and local hosted-like path can be interpreted through the shared-platform vocabulary without changing behavior.
- Regression coverage should preserve the current GCP Terraform handoff, deployment script input model, local Docker Compose workflow, and README guidance added in FND-019.
- The full repository test-suite command required before completion is `pytest`.

## Observability, Security, and Simplicity

- Observability: the portability model must preserve operator-visible outputs and failure guidance so providers can be compared and verified without obscuring current deployment evidence.
- Security: provider adapters must keep secrets as external references only and must not weaken the current secret-backed deployment expectations for `YOUTUBE_API_KEY`, `MCP_AUTH_TOKEN`, or session-store connection data.
- Simplicity: the design introduces only one shared-platform layer and one planning-grade secondary provider adapter; it does not replace the current deployment workflow or split the application into provider-specific runtimes.

## Post-Design Constitution Check

- [x] Contracts defined or updated for all external/MCP-facing behavior changes
- [x] Plan includes explicit Red-Green-Refactor steps for each phase and user story
- [x] Red phase identifies failing tests before implementation tasks begin
- [x] Green phase limits implementation to minimum code required for passing tests
- [x] Refactor phase includes cleanup tasks with a full repository test-suite re-run
- [x] Integration and regression coverage strategy is documented
- [x] Plan names the command that proves the full repository test suite passes before completion
- [x] Observability, security, and simplicity constraints are addressed

Post-design gate result: PASS. The design artifacts define the contract surface explicitly, preserve the current local and GCP workflows, and introduce only the minimum abstraction needed to make provider expansion reviewable. The required full-suite completion command remains `pytest`.

## Complexity Tracking

No constitution violations require exception tracking for this feature.
