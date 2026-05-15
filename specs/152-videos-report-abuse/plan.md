# Implementation Plan: YT-152 Layer 1 Endpoint `videos.reportAbuse`

**Branch**: `152-videos-report-abuse` | **Date**: 2026-05-15 | **Spec**: [/Users/ctgunn/Projects/youtube-mcp-server/specs/152-videos-report-abuse/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/152-videos-report-abuse/spec.md)
**Input**: Feature specification from `/specs/152-videos-report-abuse/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add the next endpoint-specific Layer 1 wrapper for `videos.reportAbuse` by extending the existing YT-101 and YT-102 integration foundation with a concrete abuse-report mutation contract for `POST /videos/reportAbuse`. The plan keeps the feature internal-only, models `videos.reportAbuse` as an OAuth-required mutation endpoint with a visible 50-unit quota cost, and focuses implementation on deterministic request-body validation, explicit abuse-report reason and optional detail guidance, clear unsupported-input boundaries, normalized 204-success acknowledgement handling, and the smallest extension of the existing wrapper, transport, consumer-summary, and Layer 1 test seams.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Python standard library dataclasses, enums, JSON, and urllib request tooling; existing internal integration modules under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/`; pytest; Ruff  
**Storage**: N/A for feature-specific persistence; wrapper metadata, request validation state, abuse-report execution state, and feature artifacts remain in-memory or file-based only  
**Testing**: `python3 -m pytest` for unit, contract, integration, and transport suites; targeted Layer 1 tests during Red-Green; `python3 -m ruff check .` for lint validation  
**Documentation Style**: Python reStructuredText docstrings for all new or changed functions plus feature-local contract markdown under `/Users/ctgunn/Projects/youtube-mcp-server/specs/152-videos-report-abuse/contracts/`  
**Target Platform**: Local development on macOS/Linux and the existing hosted Linux runtime for the MCP service  
**Project Type**: Python MCP service with an internal YouTube integration layer  
**Performance Goals**: Preserve the current Layer 1 execution path while making `videos.reportAbuse` authorization, request-body boundaries, quota impact, and mutation acknowledgement semantics reviewable in under 1 minute before downstream reuse  
**Constraints**: No new public MCP tool in this slice, no MCP transport or hosted runtime behavior changes, reuse the existing `EndpointMetadata`, `EndpointRequestShape`, `AuthContext`, and `RepresentativeEndpointWrapper` patterns, require deterministic body validation before execution, keep secrets and tokens out of docs and logs, keep the 50-unit quota cost visible in wrapper and review surfaces, and keep the slice scoped to one endpoint-specific wrapper contract  
**Scale/Scope**: One internal `videos.reportAbuse` wrapper slice affecting representative integration modules, Layer 1-focused unit/contract/integration/transport tests, and feature-local contract documentation for later abuse-reporting workflows

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Contracts defined or updated for all external/MCP-facing behavior changes
- [x] Plan includes explicit Red-Green-Refactor steps for each phase and user story
- [x] Red phase identifies failing tests before implementation tasks begin
- [x] Green phase limits implementation to minimum code required for passing tests
- [x] Refactor phase includes cleanup tasks with a full repository test-suite re-run
- [x] Integration and regression coverage strategy is documented
- [x] Plan names the command that proves the full repository test suite passes before completion
- [x] Plan defines how reStructuredText docstrings will be added or preserved for new and changed Python functions
- [x] Observability, security, and simplicity constraints are addressed

Gate rationale:

- YT-152 does not add a public MCP tool, so the contract gate is satisfied by documenting the internal Layer 1 wrapper contract and its downstream reuse expectations for later abuse-reporting work.
- Full repository verification before completion will use `python3 -m pytest` and `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Any new or changed Python functions and methods in scope must keep or add reStructuredText docstrings covering wrapper purpose, metadata and payload inputs, abuse-report reason handling, OAuth requirements, quota cost, 204-success acknowledgement handling, and normalized failure interpretation.
- Security is addressed by requiring OAuth-only access, excluding tokens and credentials from docs/logs/results, and keeping delegated content-owner behavior outside the guaranteed contract unless explicitly added later.

## Project Structure

### Documentation (this feature)

```text
specs/152-videos-report-abuse/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── layer1-videos-report-abuse-wrapper-contract.md
│   └── layer1-videos-report-abuse-auth-payload-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
src/
└── mcp_server/
    └── integrations/
        ├── __init__.py
        ├── consumer.py
        ├── contracts.py
        ├── executor.py
        ├── wrappers.py
        └── youtube.py

tests/
├── contract/
│   ├── test_layer1_consumer_contract.py
│   ├── test_layer1_metadata_contract.py
│   └── test_layer1_videos_contract.py
├── integration/
│   └── test_layer1_foundation.py
└── unit/
    ├── test_layer1_foundation.py
    └── test_youtube_transport.py
```

**Structure Decision**: Keep the feature in the existing single Python service. Limit code changes to the Layer 1 integration modules and the established unit, contract, integration, and transport test suites that already cover adjacent video list, video rate, and video rating lookup slices.

## Phase 0: Research and Open Questions

### Research Focus

- Confirm the smallest supported `videos.reportAbuse` request boundary that satisfies the feature spec, current official documentation, and local tool inventory.
- Confirm how existing mutation-oriented and video-oriented wrappers expose OAuth-only behavior, quota visibility, request-body guidance, and acknowledgement semantics for maintainers.
- Confirm whether optional report details and delegated content-owner behavior should be promised in this slice or documented as outside the guaranteed boundary.
- Confirm the minimum implementation seam for body validation, 204-success payload normalization, transport request construction, and higher-layer summary behavior.

### Research Tasks

- Review official Google documentation for `videos.reportAbuse` and `videoAbuseReportReasons.list` to confirm quota cost, authorization scopes, body fields, 204-success handling, and error boundaries.
- Review adjacent video-oriented feature artifacts under `/Users/ctgunn/Projects/youtube-mcp-server/specs/150-videos-rate/` and `/Users/ctgunn/Projects/youtube-mcp-server/specs/151-videos-get-rating/`.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py` for the smallest extension seam.
- Review `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_videos_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_metadata_contract.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py` for coverage expectations.

### Phase 0 Red-Green-Refactor

- **Red**: Capture any open implementation or contract questions as explicit research topics and confirm whether any current artifact leaves `videos.reportAbuse` request-body fields, OAuth expectations, 204-success acknowledgement, or failure semantics under-specified for planning.
- **Green**: Resolve each research topic in `/Users/ctgunn/Projects/youtube-mcp-server/specs/152-videos-report-abuse/research.md` with concrete decisions on request shape, optional payload boundaries, delegated-content-owner scope, failure separation, implementation seams, and test seams.
- **Refactor**: Remove duplicated or implementation-heavy wording from research notes so the decisions stay reviewable and directly usable by the design and tasking phases.

## Phase 1: Design and Contracts

### Design Goals

- Model `videos.reportAbuse` as one deterministic internal mutation wrapper that requires a body with `videoId` and `reasonId`, remains OAuth-only, and keeps the 50-unit quota cost visible.
- Keep abuse-report payload behavior reviewable by documenting supported optional body fields: `secondaryReasonId`, `comments`, and `language`.
- Keep partner-only `onBehalfOfContentOwner` outside the guaranteed wrapper boundary for this slice unless a later slice explicitly adds delegated content-owner support.
- Preserve a clear distinction between invalid request shapes, missing authorized access, normalized upstream refusal failures, rate-limit failures, video-not-found failures, and successful 204 acknowledgement outcomes.
- Keep required input fields and unsupported optional inputs visible in wrapper metadata, consumer summaries, contract artifacts, and implementation docstrings so maintainers understand the abuse-reporting boundary before reuse.

### Design Artifacts

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/152-videos-report-abuse/data-model.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/152-videos-report-abuse/contracts/layer1-videos-report-abuse-wrapper-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/152-videos-report-abuse/contracts/layer1-videos-report-abuse-auth-payload-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/152-videos-report-abuse/quickstart.md`

### Phase 1 Red-Green-Refactor

- **Red**: Identify where the current repo artifacts do not yet describe `videos.reportAbuse` entities, required body fields, optional report details, OAuth-only access, 204-success acknowledgement, or failure boundaries clearly enough for implementation tasking.
- **Green**: Produce the data model, wrapper contract, auth-payload contract, and quickstart artifacts with enough detail to drive tests and implementation without leaking transport-specific code detail.
- **Refactor**: Remove duplicated wording across artifacts, keep the internal-only scope explicit, and re-check that the design remains the smallest change that satisfies the feature specification, official endpoint contract, and local tool inventory.

## Phase 2: Implementation Strategy

### User Story 1 - Submit a Video Abuse Report Through a Reusable Layer 1 Contract

- **Red**: Add failing unit and integration tests proving `videos.reportAbuse` is not yet available as a typed Layer 1 wrapper with explicit body validation, OAuth-only access, and normalized successful acknowledgement coverage.
- **Green**: Implement the minimum endpoint-specific wrapper behavior needed to define representative `videos.reportAbuse` metadata, validate required `body.videoId` and `body.reasonId`, execute through the existing shared executor path, and normalize a successful no-content response into a reviewable mutation acknowledgement.
- **Refactor**: Consolidate wrapper naming and mutation-result shaping so the new endpoint-specific behavior fits the current Layer 1 pattern, then rerun the targeted Layer 1 suites followed by the full repository suites.

### User Story 2 - Review Payload Expectations, Quota, and OAuth Rules Before Reuse

- **Red**: Add failing contract and integration checks proving higher-layer authors cannot yet determine that `videos.reportAbuse` requires authorized access, carries a 50-unit quota cost, requires `videoId` and `reasonId`, supports only documented optional body fields, or excludes delegated partner-only query parameters from this slice.
- **Green**: Implement the smallest metadata, consumer-summary, docstring, and contract changes needed to model `videos.reportAbuse` as `oauth_required` with clear maintainer-facing notes for body expectations, optional payload fields, unsupported query modifiers, and successful acknowledgement semantics.
- **Refactor**: Remove duplicated quota, access, and payload guidance across code docstrings and contract markdown, then rerun the targeted Layer 1 suites followed by the full repository suites.

### User Story 3 - Reject Invalid or Under-Authorized Abuse Reports Clearly

- **Red**: Add failing contract, integration, and transport checks proving the repository does not yet distinguish missing required body fields, invalid abuse-reason combinations, unsupported payload fields, missing OAuth access, upstream refusal failures, rate-limit failures, video-not-found failures, and successful report acknowledgements clearly enough for downstream abuse-reporting work.
- **Green**: Implement the minimum validation, transport, and contract-artifact updates needed to make the wrapper reviewable for invalid-shape handling, authorized-access requirements, optional-field boundaries, 204-success handling, and failure-boundary clarity.
- **Refactor**: Tighten contract language and test naming so YT-152 stays a single-endpoint Layer 1 slice rather than growing into broader moderation or abuse-reason discovery workflows, then rerun the targeted Layer 1 suites followed by the full repository suites.

### Regression Strategy

- Preserve the existing Layer 1 executor, auth-context handling, retry behavior, observability hooks, and transport helpers outside the intentional `videos.reportAbuse` additions.
- Preserve all public MCP behavior and hosted runtime behavior because YT-152 is internal-only.
- Re-run targeted Layer 1 unit, contract, integration, and transport coverage during Red-Green-Refactor, then run the full repository validation commands `python3 -m pytest` and `python3 -m ruff check .` before completion.
- Add regression protection for body validation, optional payload boundary visibility, 204-success acknowledgement handling, consumer-summary reviewability, quota visibility, and the `invalid_request` versus access-related versus normalized upstream refusal versus successful acknowledgement boundaries so later endpoint slices cannot silently blur `videos.reportAbuse` behavior.

### Rollback and Mitigation

- Keep the feature scoped to internal wrapper metadata, request validation, docstrings, feature-local contracts, consumer summaries, transport shaping, and Layer 1-focused tests so rollback can occur by reverting the endpoint-specific additions without affecting public MCP interfaces.
- Reuse the established `EndpointMetadata`, `EndpointRequestShape`, and `RepresentativeEndpointWrapper` patterns so a rollback does not require migrating consumers to a new abstraction.
- Avoid exposing secrets, OAuth tokens, delegated-owner context, or report submitter identity in any contract artifact, docstring, log expectation, or test fixture.

## Post-Design Constitution Check

- [x] Contracts defined or updated for all external/MCP-facing behavior changes
- [x] Plan includes explicit Red-Green-Refactor steps for each phase and user story
- [x] Red phase identifies failing tests before implementation tasks begin
- [x] Green phase limits implementation to minimum code required for passing tests
- [x] Refactor phase includes cleanup tasks with a full repository test-suite re-run
- [x] Integration and regression coverage strategy is documented
- [x] Plan names the command that proves the full repository test suite passes before completion
- [x] Plan defines how reStructuredText docstrings will be added or preserved for new and changed Python functions
- [x] Observability, security, and simplicity constraints are addressed

Post-design rationale:

- Design artifacts document no public MCP contract change while adding the internal Layer 1 contracts required for `videos.reportAbuse`.
- Red-Green-Refactor steps are explicit for research, design, and each user story.
- Full-suite verification remains `python3 -m pytest` and `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- The design preserves the simplest extension of the existing Layer 1 foundation and requires reStructuredText docstrings on changed Python functions.
- No constitution exceptions are required.

## Complexity Tracking

No constitution violations or justified exceptions are required for this plan.
