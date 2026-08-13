# Implementation Plan: Transcript Language Discovery

**Branch**: `313-transcript-languages` | **Date**: 2026-08-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/313-transcript-languages/spec.md`

## Summary

Deliver `transcripts_listLanguages`, an additive Layer 3 MCP tool that lets a client discover the accessible caption-language tracks for one video before requesting transcript content. Extend the existing transcript-family module to validate one `videoId`, compose the existing authorized `captions.list` handler once, return a normalized language-option record for every returned track while preserving source-provided track metadata and provenance, and expose empty, authorization, quota, source-unavailable, and unexpected-source outcomes safely. The feature does not download or return caption text, add configuration, or change the transport.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: Existing FastAPI/Pydantic/Uvicorn MCP runtime; in-repository dispatcher; Layer 3 transcript-family and convention modules; Layer 2 `captions_list` handler; Python standard-library mappings; pytest; Ruff
**Storage**: N/A; the request, source caption records, and normalized language options exist only for one invocation
**Testing**: `PYTHONPATH=src python3 -m pytest` for full repository validation; focused unit, contract, integration, and protocol-routing regression tests during Red-Green-Refactor; `PYTHONPATH=src python3 -m ruff check .` for lint validation
**Documentation Style**: reStructuredText docstrings for every new or changed Python function, documenting purpose, `:param:`, `:return:`, `:raises:` where relevant, and observable side effects where relevant; feature-local Markdown contract documentation
**Target Platform**: Linux-hosted Cloud Run service and supported local macOS/Linux development runtime
**Project Type**: Python MCP web service
**Performance Goals**: Under normal authorized source availability, at least 95% of representative requests return a structured result or safe structured error within 5 seconds
**Constraints**: One video and one authorized `captions.list` composition per invocation; require only `videoId`; no caption download, caption text, timestamp segments, language selection or fallback, persistence, new provider client, direct environment reads, credentials, raw source bodies, stack traces, or transport changes; normal lookup consumes 50 documented caption quota units before retries; retain existing observability lifecycle and add reStructuredText docstrings to every changed Python function
**Scale/Scope**: One concrete public Layer 3 tool, its public exports and default dispatcher registration, one source dependency, safe metadata and error mapping, plus focused unit/contract/integration/regression coverage

## Constitution Check

*Pre-Phase 0 gate: PASS.*

- [x] Contracts are defined for all external/MCP-facing behavior changes in [contracts/transcripts-list-languages-contract.md](./contracts/transcripts-list-languages-contract.md).
- [x] The phase plan includes explicit Red-Green-Refactor steps for shared foundation work and all three user stories.
- [x] Each Red step defines failing tests before implementation work begins.
- [x] Each Green step limits code to the minimum needed to pass the corresponding tests.
- [x] Each Refactor step includes cleanup plus a full repository test-suite re-run.
- [x] Unit, contract, integration, and regression coverage are documented.
- [x] The completion command is `PYTHONPATH=src python3 -m pytest`; lint evidence is `PYTHONPATH=src python3 -m ruff check .`.
- [x] Every new or changed Python function is required to have a reStructuredText docstring.
- [x] Observability, security, and simplicity constraints are addressed below.

### Constitution-Driven Design Controls

- **Contract-first**: Publish the executable schema, result shape, provenance, bounded composition, OAuth/quota caveat, empty-result semantics, safe error outcomes, and additive compatibility posture before default registration.
- **Determinism**: Trim only the `videoId`. Preserve each returned caption track as a separate option in source order; do not deduplicate same-language tracks, rank them, infer missing values, translate, or select a default language.
- **Observability**: Reuse the dispatcher and `captions.list` request lifecycle so safe tool name, request correlation, latency, and status observability remains intact. Do not add logs containing video identifiers, caption text or metadata, authorization values, or raw source content.
- **Security**: Reuse configured OAuth, safe upstream messages, and detail sanitization. Only source-provided metadata explicitly allowed by the contract is returned; failures never disclose caption text, protected tracks, credentials, tokens, raw responses, signed URLs, or traces.
- **Simplicity and boundedness**: Add a sibling builder in the established transcript-family seam and call the existing caption-list handler exactly once. Do not create a service, provider client, persistence store, configuration setting, fallback, download flow, or cross-family abstraction.
- **Rollback/mitigation**: The addition is non-breaking. Remove its descriptor registration and package exports to withdraw it; `captions_list` and all existing public tools remain unchanged.

## Research Decisions

All Phase 0 questions are resolved in [research.md](./research.md): use the authorized `captions.list` Layer 2 path; surface one option per returned source track; make an empty completed listing a success; distinguish authorization, quota, source-unavailable, and unexpected failure safely; and reuse current registration, sanitization, test, and documentation conventions.

## Phase Plan and Red-Green-Refactor Strategy

### Phase 0 - Research and Contract Decisions (complete)

- **Red**: Identify unknowns around public output naming, source metadata, duplicate-language tracks, empty listing semantics, authorization limitations, lower-layer error mapping, registration, and validation evidence.
- **Green**: Resolve each topic in [research.md](./research.md), including the one-list-call boundary, source-field preservation, safe category mapping, and no-download scope.
- **Refactor**: Eliminate unresolved markers, align terminology with YT-301, YT-304, the PRD, and the accepted feature specification, and confirm that no new runtime dependency is needed.

### Phase 1 - Design and Contract Artifacts (complete)

- **Red**: Derive public request, language-option, result, provenance, state, validation, error, composition, and operator-verification requirements from the feature specification and research decisions.
- **Green**: Produce [data-model.md](./data-model.md), the executable MCP contract, and [quickstart.md](./quickstart.md); then update Codex context from the completed plan.
- **Refactor**: Remove duplicated policy wording, verify that the contract is executable rather than representative-only, and re-run the post-design Constitution Check.

### Phase 2 - Implementation Planning (for `/speckit.tasks`; no tasks created here)

#### Shared Foundation - Public Registration and Safe Error Delivery

- **Red**: Add failing registration and protocol-routing tests showing that `transcripts_listLanguages` is absent from the default catalog, that its descriptor is not executable, or that its safe categories cannot be rendered without unsafe details.
- **Green**: Add only the descriptor import, package exports, default dispatcher registration with the existing injected caption-list dependency, and the minimal safe error-category behavior required for the focused tests.
- **Refactor**: Keep all registration changes additive and local, preserve dispatcher observability and existing tool contracts, add or retain reStructuredText docstrings on changed Python functions, then run focused coverage.

#### User Story 1 - Discover Available Transcript Languages (P1)

- **Red**: Add failing unit, contract, and integration tests for the required-only schema; trimmed valid `videoId`; exactly one `captions.list` call with `part: snippet`; an option for each returned language track; source order; duplicate-language tracks; field provenance; and no representative-only marker.
- **Green**: Implement the transcript-family error type, validator, source-record normalizer, handler, metadata builder, descriptor, exports, and registration needed to return one normalized option per returned track.
- **Refactor**: Keep only source-field preservation and normalized output helpers in the transcript family, avoid generic abstractions, document changed functions with reStructuredText docstrings, and rerun focused coverage.

#### User Story 2 - Select a Suitable Transcript Track (P2)

- **Red**: Add failing tests for source-provided identifiers and caller-relevant metadata, missing optional identifiers and metadata, repeated languages, unknown track properties, and no fabricated values.
- **Green**: Return the source `language`, optional `captionTrackId`, and only approved supplied metadata such as name, status, track kind, draft state, or automatic-sync state; identify source-provided versus normalized fields in `fieldProvenance`.
- **Refactor**: Deduplicate source-record access without changing order or semantics, confirm raw metadata is never relabeled as inferred, retain reStructuredText docstrings, and rerun focused coverage.

#### User Story 3 - Understand Restricted or Missing Access (P3)

- **Red**: Add failing tests for valid empty source listings, invalid public arguments with no lower call, authentication and authorization denial, quota exhaustion, source endpoint unavailability, unexpected source failure, and error-detail sanitization.
- **Green**: Return an empty successful `no_accessible_languages` result only after a completed empty listing. Map validation to `invalid_parameters`, auth failures to `authorization_sensitive_data`, quota to `quota_exhaustion`, endpoint availability to `source_unavailable`, and other source failures to `upstream_failure`; never expose protected tracks or unsafe details.
- **Refactor**: Consolidate lower-caption error translation within the transcript family, retain the boundary between empty success and source failure, confirm reStructuredText docstrings, then run all focused tests, the complete repository suite, and lint after the final code change.

### Required Verification Evidence

1. `PYTHONPATH=src python3 -m pytest tests/unit/test_youtube_composed_transcripts.py tests/contract/test_youtube_composed_transcripts_contract.py tests/integration/test_youtube_composed_tool_registration.py tests/integration/test_youtube_tool_registration.py tests/unit/test_method_routing.py`
2. `PYTHONPATH=src python3 -m pytest`
3. `PYTHONPATH=src python3 -m ruff check .`

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/313-transcript-languages/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── transcripts-list-languages-contract.md
└── tasks.md                         # Created later by /speckit.tasks
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/
├── src/mcp_server/
│   ├── tools/
│   │   ├── dispatcher.py                           # Default concrete tool registration
│   │   ├── youtube_common/
│   │   │   ├── captions.py                         # Existing authorized captions.list dependency
│   │   │   └── conventions.py                      # Existing safe-error utilities
│   │   └── youtube_composed/
│   │       ├── __init__.py                         # Public composed-tool exports
│   │       ├── conventions.py                      # Shared provenance/category conventions
│   │       └── transcripts.py                      # Transcript-language discovery behavior
│   └── protocol/methods.py                         # Only if new category serialization requires additive support
└── tests/
    ├── contract/test_youtube_composed_transcripts_contract.py
    ├── integration/test_youtube_composed_tool_registration.py
    ├── integration/test_youtube_tool_registration.py
    └── unit/
        ├── test_method_routing.py
        └── test_youtube_composed_transcripts.py
```

**Structure Decision**: Extend the established Layer 3 transcript-family module and its adjacent export and registration seams. Reuse the authorized lower-layer caption listing and current request lifecycle; do not add a client, persistence, configuration, download parser, or generic transcript abstraction.

### Post-Design Constitution Check

*Post-Phase 1 gate: PASS.*

- [x] The concrete MCP contract covers schema, source metadata, provenance, one-call composition, empty-result behavior, safe errors, and additive compatibility.
- [x] The plan specifies Red before Green and Refactor after Green for foundation work and P1–P3.
- [x] Unit, contract, integration, and protocol regression coverage are identified, with full-suite and lint commands required before completion.
- [x] New or changed Python functions are required to retain or add reStructuredText docstrings.
- [x] Existing request observability is retained; logs, metadata, and errors are constrained to safe diagnostic data.
- [x] The selected composition is bounded, uses the existing handler, and introduces no unjustified complexity.

## Complexity Tracking

No constitution exceptions are required.
