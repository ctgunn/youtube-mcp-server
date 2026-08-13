# Implementation Plan: Timestamped Caption Retrieval

**Branch**: `314-timestamped-captions` | **Date**: 2026-08-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/314-timestamped-captions/spec.md`

## Summary

Deliver `transcripts_getTimestampedCaptions`, an additive Layer 3 MCP tool that retrieves one authorized caption track for one video and returns each source VTT cue as a separately timed caption segment. Extend the existing transcript-family seam to validate `videoId` and optional `language`, make one authorized `captions.list` request and at most one authorized `captions.download` request, select one usable track deterministically, parse VTT timing into elapsed seconds, preserve cue order and boundaries, and expose safe access and source-failure outcomes. The tool reuses current caption integrations, dispatcher lifecycle, and safe-error behavior; it adds no persistence, provider, transport, or configuration setting.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing FastAPI/Pydantic/Uvicorn MCP runtime; in-repository dispatcher; Layer 3 transcript-family and convention modules; Layer 2 `captions_list` and `captions_download` handlers; Python standard-library text/HTML/regular-expression utilities; pytest; Ruff  
**Storage**: N/A; request, caption-track data, downloaded content, and normalized segments exist only for one invocation  
**Testing**: `PYTHONPATH=src python3 -m pytest` for final repository validation; focused unit, contract, integration, and protocol-routing regression tests during Red-Green-Refactor; `PYTHONPATH=src python3 -m ruff check .` for lint validation  
**Documentation Style**: reStructuredText docstrings for every new or changed Python function, documenting purpose, `:param:`, `:return:`, `:raises:` where relevant, and observable side effects where relevant; feature-local Markdown contract documentation  
**Target Platform**: Linux-hosted Cloud Run service and supported local macOS/Linux development runtime  
**Project Type**: Python MCP web service  
**Performance Goals**: Under normal authorized source availability, at least 95% of representative requests return a structured result or safe structured error within 5 seconds  
**Constraints**: One video, one authorized caption discovery, and at most one authorized VTT download per invocation; require `videoId`; accept optional exact-match `language`; preserve each valid source cue's timing and order; no merging, splitting, translating, generating, or returning other-language captions; no persistence, new client/provider, direct environment reads, credentials, raw source bodies, stack traces, or transport changes; normal successful retrieval consumes 50 caption-list plus 200 caption-download quota units before retries; retain existing observability lifecycle and add reStructuredText docstrings to every changed Python function  
**Scale/Scope**: One concrete public Layer 3 tool, its public exports and default dispatcher registration, one bounded two-step caption composition, safe VTT segment parsing, metadata/error mapping, and focused unit/contract/integration/regression coverage

## Constitution Check

*Pre-Phase 0 gate: PASS.*

- [x] Contracts are defined for all external/MCP-facing behavior changes in [contracts/transcripts-get-timestamped-captions-contract.md](./contracts/transcripts-get-timestamped-captions-contract.md).
- [x] The phase plan includes explicit Red-Green-Refactor steps for shared foundation work and all three user stories.
- [x] Each Red step defines failing tests before implementation work begins.
- [x] Each Green step limits code to the minimum needed to pass the corresponding tests.
- [x] Each Refactor step includes cleanup plus a full repository test-suite re-run.
- [x] Unit, contract, integration, and regression coverage are documented.
- [x] The completion command is `PYTHONPATH=src python3 -m pytest`; lint evidence is `PYTHONPATH=src python3 -m ruff check .`.
- [x] Every new or changed Python function is required to have a reStructuredText docstring.
- [x] Observability, security, and simplicity constraints are addressed below.

### Constitution-Driven Design Controls

- **Contract-first**: Publish the executable schema, selection policy, segment shape and timing semantics, provenance, bounded composition, OAuth/quota caveats, safe outcomes, and additive compatibility posture before default registration.
- **Determinism**: Match a supplied language exactly after language-tag normalization. With no language, select a source-designated default usable track if the source supplies a documented default indicator; otherwise select the first usable track in completed source order. Exclude failed tracks. Preserve the selected source's cue order and boundaries; do not deduplicate, merge, split, sort, translate, or substitute captions.
- **Observability**: Reuse dispatcher and lower-layer caption request lifecycles so safe tool name, request correlation, latency, and status observability remains intact. Do not log caption text, VTT content, video identifiers, track metadata, authorization values, or raw source responses.
- **Security**: Reuse configured OAuth, safe upstream messages, and detail sanitization. The public result may contain caption text only after successful authorized retrieval. Errors never disclose caption text, VTT/raw payloads, credentials, tokens, protected track details, signed URLs, or traces.
- **Simplicity and boundedness**: Add a sibling descriptor and parser helper in the established transcript-family module. Reuse current list/download handlers and existing language validation where its semantics match this contract. Do not create a service, provider client, persistence store, configuration setting, cross-family abstraction, or fallback source.
- **Rollback/mitigation**: The addition is non-breaking. Withdraw the feature by removing its descriptor registration and package exports; existing caption and transcript tools remain unchanged.

## Research Decisions

All Phase 0 questions are resolved in [research.md](./research.md): use the authorized official caption list/download flow; parse VTT into source-cue segments; preserve source timing; select a track deterministically without another-language substitution; distinguish empty, access, quota, unavailable-source, and unexpected-failure outcomes safely; and reuse existing registration, sanitization, test, and documentation conventions.

## Phase Plan and Red-Green-Refactor Strategy

### Phase 0 - Research and Contract Decisions (complete)

- **Red**: Identify unknowns around official caption authorization, quota, track availability, default selection, VTT timing grammar, source-cue granularity, malformed content, error serialization, registration, and test evidence.
- **Green**: Resolve each topic in [research.md](./research.md), including the one-list/at-most-one-download boundary, default selection, VTT parsing rules, safe public categories, and no-fallback scope.
- **Refactor**: Eliminate unresolved markers, align terminology with YT-301, YT-304, YT-313, the PRD, and the accepted feature specification, and confirm that no runtime dependency or configuration is needed.

### Phase 1 - Design and Contract Artifacts (complete)

- **Red**: Derive public request, track-selection, segment, result, provenance, timing, state, validation, error, composition, and operator-verification requirements from the feature specification and research decisions.
- **Green**: Produce [data-model.md](./data-model.md), the executable MCP contract, and [quickstart.md](./quickstart.md); then update Codex context from the completed plan.
- **Refactor**: Remove duplicate selection and failure wording, verify the contract is executable rather than representative-only, and re-run the post-design Constitution Check.

### Phase 2 - Implementation Planning (for `/speckit.tasks`; no tasks created here)

#### Shared Foundation - Public Registration and Safe Error Delivery

- **Red**: Add failing registration and protocol-routing tests showing that `transcripts_getTimestampedCaptions` is absent from the default catalog, cannot be invoked through its descriptor, or cannot serialize its documented safe categories.
- **Green**: Add only the descriptor import, package exports, default dispatcher registration with existing injected OAuth caption handlers, and any minimal additive protocol category mapping required by the focused tests.
- **Refactor**: Keep registration additive and local, preserve dispatcher observability and existing tool contracts, add or retain reStructuredText docstrings on changed Python functions, then run focused coverage.

#### User Story 1 - Retrieve Timed Caption Segments (P1)

- **Red**: Add failing unit, contract, and integration tests for the required-only schema; trimmed valid `videoId`; one `captions.list` call with `part: snippet`; at most one `captions.download` call with `tfmt: vtt`; a VTT cue with hours and decimals; adjacent and overlapping cues; blank cue text; text-markup stripping; exact elapsed-second values; source ordering; provenance; and no representative-only marker.
- **Green**: Implement the timestamped-caption error type, validator, selected-track composition, bounded VTT cue parser, result builder, metadata builder, descriptor, package exports, and default registration needed to return one segment per valid source cue.
- **Refactor**: Keep VTT parsing and timing normalization confined to the transcript family, reuse safe caption error utilities, avoid a generic media parser, document every new or changed Python function with reStructuredText docstrings, and rerun focused coverage.

#### User Story 2 - Retrieve a Requested Language (P2)

- **Red**: Add failing tests for valid explicit language selection, malformed language, a requested language with no usable exact match, multiple usable same-language tracks, no-language source default, no-language first-usable source-order fallback, failed-track exclusion, and no cross-language substitution.
- **Green**: Normalize and exactly match an explicit language. When omitted, select a documented source-designated default usable track when present, otherwise the first usable source-order track; identify the selected language and selection source. Return `language_unavailable` for a supplied language without an accessible exact match and never download another language.
- **Refactor**: Consolidate only shared track-selection logic that retains the tool's source-order default policy, preserve clear provenance, retain reStructuredText docstrings, and rerun focused coverage.

#### User Story 3 - Understand Unavailable or Restricted Captions (P3)

- **Red**: Add failing tests for valid empty completed listings, unavailable video/track, invalid public arguments with no lower-layer call, authentication and authorization denial, quota exhaustion, endpoint unavailability, malformed/undecodable VTT, unexpected lower-layer failures, and error-detail sanitization.
- **Green**: Return a successful `no_accessible_captions` result only after a completed empty listing with no explicit language; map a supplied-but-unmatched language to `language_unavailable`; map input to `invalid_parameters`, access failures to `authorization_sensitive_data`, quota to `quota_exhaustion`, endpoint availability to `source_unavailable`, and malformed/unexpected source outcomes to `upstream_failure`. Do not return partial segments after a malformed download.
- **Refactor**: Consolidate lower-caption error translation and parser failure handling within the transcript family, preserve the boundary between completed absence and source failure, confirm reStructuredText docstrings, then run all focused tests, the complete repository suite, and lint after the final code change.

### Required Verification Evidence

1. `PYTHONPATH=src python3 -m pytest tests/unit/test_youtube_composed_transcripts.py tests/contract/test_youtube_composed_transcripts_contract.py tests/integration/test_youtube_composed_tool_registration.py tests/integration/test_youtube_tool_registration.py tests/unit/test_method_routing.py`
2. `PYTHONPATH=src python3 -m pytest`
3. `PYTHONPATH=src python3 -m ruff check .`

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/314-timestamped-captions/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── transcripts-get-timestamped-captions-contract.md
└── tasks.md                         # Created later by /speckit.tasks
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/
├── src/mcp_server/
│   ├── tools/
│   │   ├── dispatcher.py                           # Default concrete tool registration
│   │   ├── youtube_common/
│   │   │   ├── captions.py                         # Existing authorized list/download dependencies
│   │   │   └── conventions.py                      # Existing safe-error utilities
│   │   └── youtube_composed/
│   │       ├── __init__.py                         # Public composed-tool exports
│   │       ├── conventions.py                      # Shared provenance/category conventions
│   │       └── transcripts.py                      # Timestamped caption composition and VTT parsing
│   └── protocol/methods.py                         # Only if a documented category needs additive serialization
└── tests/
    ├── contract/test_youtube_composed_transcripts_contract.py
    ├── integration/test_youtube_composed_tool_registration.py
    ├── integration/test_youtube_tool_registration.py
    └── unit/
        ├── test_method_routing.py
        └── test_youtube_composed_transcripts.py
```

**Structure Decision**: Extend the established Layer 3 transcript-family module and its adjacent export and registration seams. Reuse authorized lower-layer caption listing and download plus the current request lifecycle; do not add a client, persistence, configuration, or generic media/transcript abstraction.

### Post-Design Constitution Check

*Post-Phase 1 gate: PASS.*

- [x] The concrete MCP contract covers schema, bounded two-step composition, track selection, VTT timing/segment semantics, provenance, OAuth/quota caveats, safe failures, and additive compatibility.
- [x] The plan specifies Red before Green and Refactor after Green for foundation work and P1–P3.
- [x] Unit, contract, integration, and protocol regression coverage are identified, with full-suite and lint commands required before completion.
- [x] New or changed Python functions are required to retain or add reStructuredText docstrings.
- [x] Existing request observability is retained; logs, metadata, and errors are constrained to safe diagnostic data.
- [x] The selected composition is bounded, uses existing handlers, and introduces no unjustified complexity.

## Complexity Tracking

No constitution exceptions are required.
