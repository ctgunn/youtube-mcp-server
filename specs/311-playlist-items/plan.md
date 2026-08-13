# Implementation Plan: YT-311 Playlist Items

**Branch**: `311-playlist-items` | **Date**: 2026-08-13 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/311-playlist-items/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/311-playlist-items/spec.md`

## Summary

Deliver `playlists_getPlaylistItems`, an additive MCP tool that returns a concise, source-ordered collection of videos and unavailable entries exposed by one playlist. The tool will compose one existing public `playlistItems.list` capability, validate a playlist identifier and bounded result limit, normalize available item details with explicit availability and provenance, and map lower-layer failures to safe Layer 3 outcomes. It adds no storage, enrichment, pagination traversal, source client, authentication flow, or transport change.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: Existing MCP tool registry and dispatcher; `src/mcp_server/tools/youtube_composed/` conventions; existing `playlistItems_list` handler; Python standard-library JSON-compatible dictionaries; pytest; Ruff
**Storage**: N/A; request normalization and collection shaping are in-memory only
**Testing**: Targeted pytest unit, contract, integration, and protocol-routing tests; final `PYTHONPATH=src python3 -m pytest`; final `PYTHONPATH=src python3 -m ruff check .`
**Documentation Style**: reStructuredText docstrings for every new or changed Python function; feature-local Markdown contract documentation
**Target Platform**: Local macOS/Linux development and the existing hosted Linux MCP service runtime
**Project Type**: Python MCP service
**Performance Goals**: At least 95% of representative requests for up to 50 playlist entries produce a structured outcome within 5 seconds; each request makes exactly one bounded lower-layer playlist-item lookup
**Constraints**: Preserve the public name `playlists_getPlaylistItems`; accept only `playlistId` and optional `maxResults`; default to 25 and bound results to 1–50; preserve exposed source order; retain unavailable exposed entries without fabricating details; expose provenance, applied limit, and safe errors; exclude secrets, owner context, raw source payloads, stack traces, signed URLs, and non-public video data; do not add dependencies, persistence, transport changes, scraping, pagination traversal, ranking, search, or per-video enrichment
**Scale/Scope**: One concrete playlists-family tool, one existing lower-layer dependency, one bounded lookup, four focused test areas plus registration/protocol regression coverage, and no changes to other public tool families

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

- The feature-local contract defines the MCP input, normalized collection, source-order and availability semantics, one-read bound, safe errors, additive compatibility, and rollback before implementation.
- Every Phase 0, Phase 1, shared-foundation, and user-story phase below puts Red before Green and Refactor after Green. Completion requires `PYTHONPATH=src python3 -m pytest` and `PYTHONPATH=src python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Every new or changed Python function, including validators, item normalizers, error mappers, descriptor builders, and test doubles, must carry a reStructuredText docstring covering purpose, inputs, outputs, raised errors where relevant, and side effects where relevant.
- The design reuses configured runtime dependencies, request correlation, lower-layer observability, dependency injection, and centralized sanitization. It introduces no storage, client, transport, auth flow, crawler, ranking, or generalized enrichment component.

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/311-playlist-items/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── playlists-get-playlist-items-contract.md
└── tasks.md                         # Created later by /speckit.tasks
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/
├── tools/
│   ├── dispatcher.py                # Default composed-tool registration and dependency injection
│   ├── youtube_common/
│   │   └── playlist_items.py        # Existing lower-level playlistItems_list handler
│   └── youtube_composed/
│       ├── __init__.py              # Public composed-tool exports
│       └── playlists.py             # Playlist-item descriptor, validation, mapping, and errors
└── protocol/
    └── methods.py                   # Existing public error-category serialization regression coverage only

/Users/ctgunn/Projects/youtube-mcp-server/tests/
├── unit/
│   ├── test_youtube_composed_playlists.py
│   └── test_method_routing.py
├── contract/
│   └── test_youtube_composed_playlists_contract.py
└── integration/
    ├── test_youtube_composed_tool_registration.py
    └── test_youtube_tool_registration.py
```

**Structure Decision**: Extend the existing `youtube_composed` playlists family. Its descriptor and handler will adapt the existing lower-level playlist-item listing capability rather than duplicate request execution or expose its near-raw envelope. Export and default-register it through established package and dispatcher seams. Keep playlist-entry mapping and error translation local to the playlists family until another concrete composed playlist tool establishes a shared helper need.

## Phase 0: Research and Open Questions

### Research Focus

- Confirm the reserved public catalog name, playlists-family ownership, executable descriptor pattern, exports, and default registration seam.
- Resolve the exact playlist-scoped lower-layer request, default and maximum bounds, public-read capacity behavior, source ordering, and first-page-only scope.
- Confirm item identity and availability mapping, successful empty collection behavior, lower-layer safe-error translation, sanitization, observability reuse, docstrings, tests, and verification commands.

### Phase 0 Decisions

All research questions are resolved in [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/311-playlist-items/research.md).

### Phase 0 Red-Green-Refactor

- **Red**: Record catalog placement, source request, default/boundary validation, ordering, availability, error, registration, and documentation uncertainties as explicit research questions.
- **Green**: Resolve every question with a decision, rationale, and rejected alternatives in `research.md`.
- **Refactor**: Retain only decisions that shape the public contract or focused implementation; do not copy lower-layer endpoint internals into public artifacts.

## Phase 1: Design and Contracts

### Design Goals

- Define the exact request, normalized playlist item, successful collection, provenance context, and safe outcome entities.
- Make source ordering, applied limit, incomplete-result indicator, available versus unavailable item details, and request-time variability explicit.
- Define one independently testable public MCP contract using exactly one bounded playlist-item lookup and no continuation input.
- Keep the work additive: one concrete playlists-family tool, no persistence, source client, crawler, pagination traversal, ranking, or video enrichment.

### Design Artifacts

- [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/311-playlist-items/data-model.md)
- [playlists-get-playlist-items-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/311-playlist-items/contracts/playlists-get-playlist-items-contract.md)
- [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/311-playlist-items/quickstart.md)

### Phase 1 Red-Green-Refactor

- **Red**: Identify every rule that needs tests for input validation, exact lower-layer request, default and explicit limits, source-order preservation, complete and sparse item mapping, unavailable entry retention, empty success, safe errors, discovery metadata, and default registration.
- **Green**: Produce the data model, contract, and quickstart with concrete schemas, field mappings, state transitions, boundedness, test evidence, and rollback expectations.
- **Refactor**: Reconcile field names, availability states, provenance categories, ordering and limit wording, error categories, and caller guidance across artifacts; ensure every specification requirement traces to a contract clause and focused test.

## Phase 2: Implementation Strategy

### Shared Foundation - Descriptor Exposure, Registration, and Safe Delivery

- **Red**: Add failing contract, registration, and protocol tests for concrete `playlists_getPlaylistItems` discovery, schema defaults and bounds, no representative-only marker, injected lower-layer dependency, safe serialized categories, and default dispatcher presence.
- **Green**: Add the smallest playlists-family error class, public schema, descriptor export, default registration, and safe category translation required to deliver the concrete tool through the existing dispatcher.
- **Refactor**: Keep registration adjacent to the existing playlist-detail descriptor, reuse centralized sanitization and request context, ensure all new or changed Python functions have reStructuredText docstrings, and rerun focused registration and routing checks.

### User Story 1 - Retrieve Videos in a Playlist (P1)

- **Red**: Add failing unit and contract tests for required trimmed `playlistId`, unknown-field rejection, omitted limit default, every limit boundary, one `playlistItems_list` request with `snippet,contentDetails,status`, exact applied limit, ordered complete result mapping, and returned-count context.
- **Green**: Add only the validator, one playlist-scoped lookup adapter, item normalizer, stable collection fields, provenance builder, metadata, and handler behavior needed for successful retrieval.
- **Refactor**: Centralize local safe field extraction and provenance mapping within the playlists family, preserve source meaning without fabricating optional fields, retain reStructuredText docstrings, and rerun focused unit and contract checks.

### User Story 2 - Bound Playlist Research (P2)

- **Red**: Add failing contract and handler tests that discovery and results identify the default of 25, 1–50 bounds, one-page no-continuation limit, source order, absence of ranking, request-time variability, applied limit, returned count, and limited-result semantics.
- **Green**: Add only the caller-facing metadata and collection context needed to distinguish a complete observed page from a response where the source signals additional entries beyond the applied limit.
- **Refactor**: Consolidate repeated limit and ordering wording with existing Layer 3 conventions, retain reStructuredText docstrings for changed Python functions, and rerun focused contract and integration checks.

### User Story 3 - Understand Unavailable Results (P3)

- **Red**: Add failing tests for non-object, missing, blank, non-text, out-of-range, boolean, fractional, and unknown input; successful empty collections; malformed returned entries; unavailable entry mapping and retention; lower unavailable, access, capacity, and source failures; and protocol serialization without unsafe details.
- **Green**: Map successful empty `items` collections to a successful empty result, retain every exposed item in source order, label entries without usable public video details as unavailable, and translate lower-layer invalid input, unavailable, access, capacity, and source failures to documented safe categories without exposing sensitive detail.
- **Refactor**: Keep lower-layer error translation local and sanitized, remove duplication with existing safe-error utilities, verify all modified Python functions retain reStructuredText docstrings, then rerun focused integration and protocol checks.

### Regression Strategy

- Preserve existing public tools, the shared Layer 3 catalog, `playlists_getPlaylist`, `playlistItems_list`, and lower-layer integration contracts.
- Add focused coverage at `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_playlists.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_playlists_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`.
- Run focused checks during implementation:

  ```bash
  PYTHONPATH=src python3 -m pytest \
    tests/unit/test_youtube_composed_playlists.py \
    tests/contract/test_youtube_composed_playlists_contract.py \
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

- Keep the public tool additive. If a regression is found before release, remove only its default dispatcher registration and composed-package exports; the lower-level playlist-item capability remains unchanged.
- Preserve lower-layer result and error contracts by adapting them at the new public boundary rather than modifying them.
- Mitigate incorrect or sensitive output through pre-lookup validation, a fixed one-read bound, public-only source fields, source-order preservation, explicit availability and provenance context, and existing safe-detail sanitization.
- No migration, persistence rollback, or infrastructure rollback is needed because this feature adds neither stored data nor transport configuration.

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

- The feature contract covers additive compatibility, input, source order, applied limit, normalized available and unavailable entries, successful empty collections, safe errors, discovery, and rollback.
- Each shared-foundation and user-story phase specifies Red before Green and Refactor after Green, along with unit, contract, integration, protocol, and final full-suite verification.
- The selected design reuses the configured lower-level playlist-item capability, safe category serialization, request context, and dispatcher registration. It introduces no new storage, source client, transport behavior, or ranking machinery.
- Every planned Python function change is subject to the constitution's reStructuredText docstring requirement; safe public diagnostic data and existing observability are preserved.

## Complexity Tracking

No constitution violations or complexity exceptions require justification.
