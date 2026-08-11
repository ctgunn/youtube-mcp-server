# Implementation Plan: Transcript Retrieval

**Branch**: `304-transcripts-get-transcript` | **Date**: 2026-08-11 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/304-transcripts-get-transcript/spec.md`

## Summary

Deliver `transcripts_getTranscript`, an additive Layer 3 MCP tool that retrieves complete plain transcript text for one video through the authorized official-caption path. The tool will resolve the language in the order explicit request, configured `YOUTUBE_TRANSCRIPT_LANG`, then `en`; compose existing caption discovery and download handlers; select an exact-language usable caption track deterministically; normalize VTT caption content to text; and return safe, provenance-aware results or safe MCP errors.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing FastAPI/Pydantic/Uvicorn MCP runtime; in-repository dispatcher, Layer 2 `captions_list` and `captions_download` handlers, Layer 3 conventions, and Python standard-library parsing utilities  
**Storage**: N/A; request, resolved-language, caption metadata, and downloaded text exist only for one invocation  
**Testing**: pytest for unit, contract, integration, and protocol regression coverage; Ruff for linting  
**Documentation Style**: reStructuredText docstrings for every new or changed Python function, including purpose, `:param:`, `:return:`, `:raises:` when relevant, and side effects when relevant  
**Target Platform**: Linux-hosted Cloud Run service and supported local development runtime  
**Project Type**: MCP-enabled web service  
**Performance Goals**: Under normal authorized source availability, at least 95% of representative requests return a structured result or safe structured error within 8 seconds  
**Constraints**: One video, one caption discovery call, and at most one caption download per invocation; exact requested-language matching only; no public fallback, translation, timing-data fabrication, persistence, credentials, stack traces, or raw source error bodies; normal success costs up to 250 documented caption quota units before retries  
**Scale/Scope**: One new public Layer 3 tool; extends the transcript-family module, its package exports, non-secret runtime settings, default dispatcher registration, and focused tests

## Constitution Check

*Pre-Phase 0 gate: PASS.*

- [x] Contracts are defined for all external/MCP-facing behavior changes in [contracts/transcripts-get-transcript-contract.md](./contracts/transcripts-get-transcript-contract.md).
- [x] The phase plan includes explicit Red-Green-Refactor steps for shared foundation work and all three user stories.
- [x] Each Red step defines failing tests before implementation work begins.
- [x] Each Green step limits code to the minimum needed to pass the corresponding tests.
- [x] Each Refactor step includes cleanup plus a full repository test-suite re-run.
- [x] Unit, contract, integration, and protocol regression coverage are documented.
- [x] The completion command is `python3 -m pytest`; lint evidence is `ruff check .`.
- [x] Every new or changed Python function is required to have a reStructuredText docstring.
- [x] Observability, security, boundedness, and simplest-architecture constraints are addressed below.

### Constitution-Driven Design Controls

- **Contract-first**: Publish the executable input schema, language priority, exact-match selection rule, success shape, provenance, composition boundary, quota/auth caveat, errors, and additive migration posture before registration.
- **Determinism**: Trim and case-normalize language tags only; select one exact BCP-47 match by usable status, caption kind, draft state, then identifier. Never rely on source ordering, base-language matching, or translation.
- **Observability**: Reuse dispatcher and lower-layer request lifecycle so request IDs, tool names, latency, and safe status events continue to be recorded. Do not log video IDs, caption text, authorization values, or raw source bodies beyond existing safe conventions.
- **Security**: Reuse configured OAuth dependencies, safe upstream messages, sanitized details, and public-metadata validation. A failed request exposes neither transcript content nor credentials.
- **Simplicity and boundedness**: Extend the existing transcript-family seam and compose existing handlers. Do not add a client, persistence, fallback provider, generic parser framework, or cross-family abstraction.
- **Rollback/mitigation**: This is additive. If it must be withdrawn, remove its default descriptor registration and package export while preserving the existing lower-level caption tools; no existing client migration is required.

## Research Decisions

All Phase 0 questions are resolved in [research.md](./research.md): use `captions.list` followed by `captions.download`, capture `YOUTUBE_TRANSCRIPT_LANG` in centralized non-secret runtime settings, use VTT only as the internal normalized download format, and parse it to complete plain text without exposing source content on failure.

## Phase Plan and Red-Green-Refactor Strategy

### Phase 0 - Research and Contract Decisions (complete)

- **Red**: Identify public-contract, configuration, caption access, language selection, download-format, error-mapping, registration, security, and verification gaps.
- **Green**: Record authoritative caption behavior, deterministic track selection, VTT normalization, safe error translation, and the central configuration path in `research.md` and the public contract.
- **Refactor**: Remove all unresolved markers, align terminology with YT-301 and the feature specification, and re-check the pre-design constitution gate.

### Phase 1 - Design and Contract Artifacts (complete)

- **Red**: Derive request/result entities, states, validation, field provenance, dependencies, failure outcomes, and operator verification flows from the specification and research.
- **Green**: Publish the data model, MCP contract, and quickstart verification path; update the Codex context using the repository script.
- **Refactor**: Reconcile duplicate policy text across artifacts, verify that the contract does not depend on representative-only metadata, and perform the post-design constitution check.

### Phase 2 - Implementation Planning (for `/speckit.tasks`; no tasks created here)

#### Shared Foundation - Configuration, Registration, and Safe MCP Error Delivery

- **Red**: Add failing configuration tests for unset, blank, valid, and malformed `YOUTUBE_TRANSCRIPT_LANG`; registration tests for the default descriptor; and protocol tests proving every new public category serializes to a stable MCP error category without unsafe details.
- **Green**: Add only the non-secret transcript-language setting, injection through the existing runtime/dispatcher path, transcript descriptor export and registration, and additive safe error mapping needed by the concrete tool.
- **Refactor**: Keep configuration parsing centralized, avoid direct process-environment reads in handlers, preserve lower-layer contracts, add reStructuredText docstrings to every changed Python function, and run focused coverage.

#### User Story 1 - Retrieve a Video Transcript (P1)

- **Red**: Add failing unit, contract, and integration tests for the concrete descriptor, required video validation, one discovery request followed by one download, VTT text normalization, source/raw versus normalized field provenance, successful empty text, and no representative-only marker.
- **Green**: Implement the transcript-family error type, schema, validator, metadata builder, caption-list adapter, selected-track download adapter, text normalizer, handler, descriptor, export, and default registration needed for the successful one-video flow.
- **Refactor**: Keep parsing and response helpers local to the transcript family; preserve complete-text behavior, safe diagnostics, and reStructuredText docstrings; rerun focused coverage.

#### User Story 2 - Control Transcript Language (P2)

- **Red**: Add failing unit tests for explicit language over configured default, configured default over English, `en` final fallback, whitespace/case normalization, malformed tags, exact-only matching, and deterministic selection among matching usable tracks.
- **Green**: Implement only the documented three-source resolver and exact-match selector. Prefer serving, standard, non-draft tracks before identifier tie-breaking; do not request translation or substitute any other language.
- **Refactor**: Simplify language normalization and selector keys without changing documented priority or selection behavior; retain reStructuredText docstrings and rerun focused coverage.

#### User Story 3 - Understand Unavailable Caption Access (P3)

- **Red**: Add failing tests for no exact matching track, stale selected track, missing authorization, quota exhaustion, temporary source failure, malformed download content, and detail sanitization.
- **Green**: Map only those lower-layer failures to `invalid_parameters`, `transcript_unavailable`, `authorization_sensitive_data`, `quota_exhaustion`, or `upstream_failure`; include resolved-language context only where safe and never return fallback or partially parsed content after failure.
- **Refactor**: Consolidate error translation within the transcript family, verify no category leaks lower-layer payloads, add or preserve reStructuredText docstrings, then run the full repository suite and lint after all changes.

### Required Verification Evidence

1. `python3 -m pytest tests/unit/test_youtube_composed_transcripts.py tests/contract/test_youtube_composed_transcripts_contract.py tests/integration/test_youtube_composed_tool_registration.py tests/integration/test_youtube_tool_registration.py tests/unit/test_runtime_config_validation.py`
2. `python3 -m pytest tests/unit/test_method_routing.py` (or the repository's final protocol-routing test location)
3. `python3 -m pytest`
4. `ruff check .`

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/304-transcripts-get-transcript/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── transcripts-get-transcript-contract.md
└── tasks.md                         # Created later by /speckit.tasks
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/
├── src/mcp_server/
│   ├── config.py                                      # Non-secret transcript-language setting
│   ├── tools/
│   │   ├── dispatcher.py                              # Default concrete tool registration
│   │   ├── youtube_common/
│   │   │   ├── captions.py                            # Existing authorized list/download dependencies
│   │   │   └── conventions.py                         # Safe error-detail utilities
│   │   └── youtube_composed/
│   │       ├── __init__.py                            # Public composed-tool exports
│   │       ├── conventions.py                         # Layer 3 provenance/category conventions
│   │       └── transcripts.py                         # Concrete transcript behavior
│   └── protocol/methods.py                            # Only if category serialization needs additive support
└── tests/
    ├── contract/test_youtube_composed_transcripts_contract.py
    ├── integration/test_youtube_composed_tool_registration.py
    ├── integration/test_youtube_tool_registration.py
    └── unit/
        ├── test_runtime_config_validation.py
        ├── test_method_routing.py
        └── test_youtube_composed_transcripts.py
```

**Structure Decision**: Extend the existing concrete Layer 3 transcript-family module and adjacent registration/configuration seams. Reuse the existing authorized caption handlers and request lifecycle; do not create a provider client, new persistent store, or generic parsing layer.

### Post-Design Constitution Check

*Post-Phase 1 gate: PASS.*

- [x] The concrete MCP contract covers schema, language resolution, deterministic selection, result provenance, bounded composition, safe errors, and additive migration posture.
- [x] The plan specifies Red before Green and Refactor after Green for foundation work and P1–P3.
- [x] Unit, contract, integration, and protocol regression coverage are identified, with full-suite and lint commands required before completion.
- [x] New or changed Python functions are required to retain or add reStructuredText docstrings.
- [x] Existing request observability is retained; logs, discovery metadata, and errors are constrained to safe diagnostic data.
- [x] The selected composition is bounded and uses existing handlers; no unjustified complexity exception is required.

## Complexity Tracking

No constitution exceptions are required.
