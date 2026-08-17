# Implementation Plan: YT-320 Playlist Video Transcript Aggregation

**Branch**: `320-playlist-transcripts` | **Date**: 2026-08-17 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/320-playlist-transcripts/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/320-playlist-transcripts/spec.md`

## Summary

Deliver `playlists_getVideoTranscripts`, an additive Layer 3 MCP tool that returns timestamped transcript outcomes for a bounded, source-ordered set of videos in one playlist. The implementation will make one bounded playlist-item lookup, resolve a single request language using explicit input, configured default, then English, and fan out to the existing timestamped-caption capability only for eligible videos. It will preserve successful per-video results when other videos have unavailable or restricted captions, return a caller-safe fan-out summary, and introduce no persistence, transport, source client, or pagination traversal.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing MCP tool registry and dispatcher; `src/mcp_server/tools/youtube_composed/` Layer 3 conventions; existing `playlistItems.list` handler; existing timestamped-caption handler; Python standard-library JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A; request, language resolution, transcript outcomes, and summary are in-memory only  
**Testing**: Targeted pytest unit, contract, integration, and protocol-routing tests; final `PYTHONPATH=src python3 -m pytest`; final `PYTHONPATH=src python3 -m ruff check .`  
**Documentation Style**: reStructuredText docstrings for every new or changed Python function and test helper; feature-local Markdown contract documentation  
**Target Platform**: Local macOS/Linux development and the existing hosted Linux MCP service runtime  
**Project Type**: Python MCP service  
**Performance Goals**: At least 95% of representative requests processing 10 or fewer eligible videos return a structured outcome within 15 seconds; one bounded playlist listing and at most the applied-limit number of caption retrieval attempts per request  
**Constraints**: Preserve the public name `playlists_getVideoTranscripts`; accept only `playlistId`, optional `language`, and optional `maxResults`; default `maxResults` to 10 and bound it to 1–50; preserve source order; resolve language explicit → configured `YOUTUBE_TRANSCRIPT_LANG` → `en`; return timestamped segments; never silently substitute another language; retain safe per-video partial results; never log or expose transcript content on failed outcomes, credentials, raw source payloads, signed URLs, or traces; do not alter the existing timestamped-caption tool's public fallback policy  
**Scale/Scope**: One concrete playlists-family tool, one playlist listing, zero through 50 timestamped transcript attempts, three existing lower-layer operations, four focused test areas plus protocol regression coverage, and no change to other public tool families

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

- The feature-local contract specifies the additive public schema, timestamped result model, language resolution, one-listing and bounded-fan-out behavior, per-video partial outcomes, safe errors, and rollback boundary before implementation.
- Each shared-foundation and user-story phase below specifies Red before Green and Refactor after Green. Completion requires `PYTHONPATH=src python3 -m pytest` and `PYTHONPATH=src python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Every new or changed Python function and test helper must have a reStructuredText docstring describing purpose, inputs, outputs, raised errors where relevant, and side effects where relevant.
- The design reuses configured credential paths, injected handlers, request correlation, centralized sanitization, and existing MCP observability. It adds no store, source client, background queue, transport feature, pagination traversal, fallback provider, or generic fan-out framework.

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/320-playlist-transcripts/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── playlists-get-video-transcripts-contract.md
└── tasks.md                         # Created later by /speckit.tasks
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/
├── src/mcp_server/
│   ├── tools/
│   │   ├── dispatcher.py                         # Default descriptor registration and dependency injection
│   │   ├── youtube_common/
│   │   │   ├── captions.py                       # Authorized caption list/download handlers
│   │   │   ├── conventions.py                    # Safe error-detail utilities
│   │   │   └── playlist_items.py                 # Bounded playlistItems.list handler
│   │   └── youtube_composed/
│   │       ├── __init__.py                       # Public composed-tool exports
│   │       ├── playlists.py                      # Playlist fan-out validation, mapping, metadata, and handler
│   │       └── transcripts.py                    # Existing timestamped-caption dependency
│   └── protocol/methods.py                       # Regression-only safe error serialization checks
└── tests/
    ├── unit/
    │   ├── test_youtube_composed_playlists.py
    │   ├── test_youtube_composed_transcripts.py
    │   └── test_method_routing.py
    ├── contract/
    │   ├── test_youtube_composed_playlists_contract.py
    │   └── test_youtube_composed_transcripts_contract.py
    └── integration/
        ├── test_youtube_composed_tool_registration.py
        └── test_youtube_tool_registration.py
```

**Structure Decision**: Extend the existing concrete Layer 3 playlists-family module. It will inject the established lower-layer playlist listing and timestamped-caption handlers rather than duplicate source calls, authentication, VTT parsing, error sanitization, or transport behavior. Language resolution belongs at the new playlist boundary so that it satisfies YT-320 without changing the established public behavior of `transcripts_getTimestampedCaptions`.

## Phase 0: Research and Open Questions

### Research Focus

- Confirm the reserved public catalog name, playlists-family ownership, exports, executable descriptor pattern, and default registration seam.
- Resolve the exact one-page playlist request, source-order and unavailable-item treatment, `maxResults` default and bounds, and the only reliable indicator that additional playlist items were not attempted.
- Reconcile YT-320's configured-language fallback with the timestamped-caption dependency's source-default fallback without breaking the dependency's existing contract.
- Confirm safe partial-result categories, mixed API-key/OAuth dependency injection, metadata, observability, docstrings, tests, rollback, and verification commands.

### Phase 0 Decisions

All research questions are resolved in [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/320-playlist-transcripts/research.md). No `NEEDS CLARIFICATION` items remain.

### Phase 0 Red-Green-Refactor

- **Red**: Record catalog placement, bounded enumeration, language-resolution compatibility, segment representation, partial-result, credential-boundary, error, registration, and documentation uncertainties as explicit research questions.
- **Green**: Resolve every question with a repository-compatible decision, rationale, and rejected alternatives in `research.md`.
- **Refactor**: Retain only decisions that shape the public contract and focused implementation; avoid copying lower-layer endpoint details or creating a generic abstraction for one bounded workflow.

## Phase 1: Design and Contracts

### Design Goals

- Define the exact request, resolved language, ordered per-video outcome, timestamped segment, fan-out summary, and safe whole-request error entities.
- Make it explicit that `maxResults` limits both playlist items considered and the number of transcript attempts; additional items are disclosed only when the source signals a further page.
- Define a concrete public MCP contract with one playlist listing, no continuation input, exact requested-language matching, configured-default-to-English fallback when language is omitted, and per-video partial-result preservation.
- Keep the work additive: one playlists-family tool, reuse of existing caption and playlist handlers, no persistence, provider fallback, raw result passthrough, or source traversal beyond the bounded page.

### Design Artifacts

- [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/320-playlist-transcripts/data-model.md)
- [playlists-get-video-transcripts-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/320-playlist-transcripts/contracts/playlists-get-video-transcripts-contract.md)
- [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/320-playlist-transcripts/quickstart.md)

### Phase 1 Red-Green-Refactor

- **Red**: Identify testable rules for strict input validation, limit default/bounds, request-level language resolution, exact one playlist lookup, maximum attempt count, source order, empty success, no-attempt unavailable videos, segment mapping, per-video failures, fan-out summary, metadata, and default registration.
- **Green**: Produce the data model, contract, and quickstart with concrete field definitions, state transitions, lower-layer boundaries, language compatibility, safe outcomes, test evidence, and rollback expectations.
- **Refactor**: Reconcile field names, availability statuses, language-source labels, result/provenance wording, error categories, and caller guidance across the design artifacts; ensure every requirement traces to a contract clause and focused test.

## Phase 2: Implementation Strategy

### Shared Foundation - Descriptor Exposure, Language Resolution, and Safe Delivery

- **Red**: Add failing contract, registration, and routing tests for concrete `playlists_getVideoTranscripts` discovery, strict schema, default and bounds, no representative-only marker, injected playlist and timestamped-caption dependencies, configured-default language forwarding, and safe serialized categories.
- **Green**: Add the smallest playlists-family constants, error class, validator, language resolver, metadata builder, descriptor export, and default dispatcher registration needed to make the tool callable. Inject the configured transcript language/error and pass the resolved language explicitly to the timestamped-caption handler; do not change that handler's public fallback behavior.
- **Refactor**: Keep registration beside existing playlists descriptors, reuse centralized sanitization and request context, preserve all reStructuredText docstrings, and rerun focused registration and routing checks.

### User Story 1 - Retrieve a Playlist's Available Transcripts (P1)

- **Red**: Add failing unit and contract tests for trimmed `playlistId`, omitted limit default of 10, limits 1 and 50, one `playlistItems.list` request using `snippet,contentDetails,status`, source-order preservation, timestamped segments, empty playlists, unavailable playlist items, one attempt per eligible video, and no more attempts than the applied limit.
- **Green**: Add only the one bounded playlist lookup, eligible-video mapping, injected timestamped-caption calls, ordered transcript outcome construction, fan-out summary, provenance, metadata, and handler behavior necessary for successful retrieval.
- **Refactor**: Consolidate local playlist-item and transcript-outcome mapping without duplicating caption parsing or playlist normalization, retain reStructuredText docstrings, and rerun focused unit and contract checks.

### User Story 2 - Request a Preferred Transcript Language (P2)

- **Red**: Add failing tests for valid language normalization, explicit language forwarding, configured default when omitted, English fallback when no configured default exists, exact-language unavailable outcomes, and the absence of another-language substitution.
- **Green**: Resolve one request language at the playlist boundary using explicit → configured default → English and pass it to every eligible timestamped-caption retrieval. Return the actual selected source language and request-level language source with successful outcomes.
- **Refactor**: Reuse the established language-tag validation and error-sanitization rules where practical, retain reStructuredText docstrings, and rerun transcript and playlist focused tests without changing the timestamped-caption tool's independent no-language semantics.

### User Story 3 - Understand Incomplete Caption Access (P3)

- **Red**: Add failing tests for non-object, missing, blank, non-text, unknown-field, boolean, fractional, zero, negative, and out-of-range inputs; captionless videos; requested-language absence; authorization, quota, source-unavailable, and upstream caption failures; playlist lookup failures; successful empty playlists; missing video identifiers; no leaked sensitive details; counts by outcome; and next-page limited indication.
- **Green**: Translate playlist-listing failures to safe whole-request errors. For each considered item, return a safe source-ordered outcome; map captionless and requested-language failures to `transcript_unavailable`, preserve authorization, quota, source-unavailable, and upstream categories per item, and continue after any individual transcript failure.
- **Refactor**: Keep lower-layer error translation local and sanitized, remove duplicated safe-detail handling, confirm new and changed Python functions retain reStructuredText docstrings, and rerun focused integration and protocol checks.

### Regression Strategy

- Preserve existing public tools, the shared Layer 3 catalog, `playlists_getPlaylistItems`, `transcripts_getTimestampedCaptions`, and lower-layer caption and playlist-item contracts.
- Add focused coverage at `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_playlists.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_transcripts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_playlists_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_transcripts_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`.
- Run focused checks during implementation:

  ```bash
  PYTHONPATH=src python3 -m pytest \
    tests/unit/test_youtube_composed_playlists.py \
    tests/unit/test_youtube_composed_transcripts.py \
    tests/contract/test_youtube_composed_playlists_contract.py \
    tests/contract/test_youtube_composed_transcripts_contract.py \
    tests/integration/test_youtube_composed_tool_registration.py \
    tests/integration/test_youtube_tool_registration.py \
    tests/unit/test_method_routing.py
  ```

- After the final code change, require:

  ```bash
  PYTHONPATH=src python3 -m pytest
  PYTHONPATH=src python3 -m ruff check .
  ```

### Rollback and Mitigation

- Keep the public tool additive. If a regression is found before release, remove only its default dispatcher registration and composed-package exports; existing playlist and transcript tools remain unchanged.
- Preserve lower-layer result, credential, and error contracts by adapting them at the new public boundary rather than modifying them. In particular, do not change `transcripts_getTimestampedCaptions` language fallback semantics.
- Mitigate cost, latency, and sensitive-output risks through pre-lookup validation, a fixed one-page listing bound, at-most-one caption workflow per eligible item, source-order preservation, explicit per-video status, request-level fan-out accounting, and existing safe-detail sanitization.
- No migration, persistence rollback, or infrastructure rollback is needed because this feature introduces neither stored data nor transport configuration.

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

- The feature contract covers additive compatibility, strict inputs, configured language resolution, timestamped segments, one bounded listing, capped per-video fan-out, source order, empty success, partial results, safe errors, discovery metadata, and rollback.
- Each shared-foundation and user-story phase specifies Red before Green and Refactor after Green, with unit, contract, integration, protocol, and final full-suite verification.
- The design reuses injected lower-layer playlist and caption capabilities, mixed existing credential modes, safe category serialization, request context, and dispatcher registration. It introduces no new storage, client, transport behavior, pagination traversal, or generalized asynchronous fan-out system.
- Every planned Python change is subject to the constitution's reStructuredText-docstring requirement. Existing request observability is retained, and errors and metadata are constrained to safe diagnostics.

## Complexity Tracking

No constitution violations or complexity exceptions require justification.
