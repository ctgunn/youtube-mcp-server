# Implementation Plan: YT-310 Playlist Details

**Branch**: `310-playlist-details` | **Date**: 2026-08-12 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/310-playlist-details/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/310-playlist-details/spec.md`

## Summary

Deliver `playlists_getPlaylist`, an additive MCP tool that returns normalized public details for one known YouTube playlist. The tool will adapt the existing `playlists_list` direct-identifier capability through one bounded lookup, map available playlist metadata into a stable result with provenance and playlist-item scope guidance, and translate lower-layer failures into safe public outcomes. It adds no storage, source client, transport behavior, ranking, playlist-item traversal, or new authentication flow.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing MCP tool registry and dispatcher; `src/mcp_server/tools/youtube_composed/` conventions; existing `playlists_list` handler; Python standard-library JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A; request normalization and response shaping are in-memory only  
**Testing**: Targeted pytest unit, contract, integration, and protocol-routing tests; final `PYTHONPATH=src python3 -m pytest`; final `PYTHONPATH=src python3 -m ruff check .`  
**Documentation Style**: reStructuredText docstrings for every new or changed Python function; feature-local Markdown contract documentation  
**Target Platform**: Local macOS/Linux development and the existing hosted Linux MCP service runtime  
**Project Type**: Python MCP service  
**Performance Goals**: At least 95% of representative single-playlist requests produce a structured outcome within 5 seconds; each request makes exactly one bounded lower-layer playlist lookup  
**Constraints**: Preserve the public name `playlists_getPlaylist`; accept only `playlistId`; make one public direct lookup using the required playlist detail groups; return only available public `playlistId`, title, description, channel attribution, publication time, thumbnails, privacy visibility, and item count; provide field provenance and explicit playlist-item exclusion guidance; expose only safe error categories; exclude credentials, private creator context, raw source payloads, stack traces, signed links, and non-public playlist data; do not add dependencies, persistence, pagination, playlist-item traversal, ranking, scraping, or broad dispatcher rewrites  
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

- The feature-local contract defines the MCP input, one-lookup boundary, normalized result, field provenance, playlist-item exclusion, public-content boundary, safe errors, additive compatibility, and rollback before implementation.
- Every Phase 0, Phase 1, shared-foundation, and user-story phase below puts Red before Green and Refactor after Green. Completion requires `PYTHONPATH=src python3 -m pytest` and `PYTHONPATH=src python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Every new or changed Python function, including validators, normalizers, error mappers, descriptor builders, and test doubles, must carry a reStructuredText docstring covering purpose, inputs, outputs, raised errors where relevant, side effects where relevant, and the public-content or safe-failure boundary where applicable.
- The design reuses request correlation, configured runtime dependencies, lower-layer observability, dependency injection, and centralized sanitization. It adds no storage, source client, transport, auth flow, crawler, or generalized enrichment component.

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/310-playlist-details/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── playlists-get-playlist-contract.md
└── tasks.md                         # Created later by /speckit.tasks
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/
├── tools/
│   ├── dispatcher.py                # Default composed-tool registration and dependency injection
│   ├── youtube_common/
│   │   └── playlists.py             # Existing lower-level playlists_list handler
│   └── youtube_composed/
│       ├── __init__.py              # Public composed-tool exports
│       └── playlists.py             # Playlist-detail descriptor, validation, mapping, and errors
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

**Structure Decision**: Extend the existing `youtube_composed` playlists family. Its new descriptor and handler will adapt the existing lower-level playlist lookup instead of duplicating request execution or exposing its near-raw envelope. Export and default-register the descriptor through established package and dispatcher seams. Keep playlist mapping and error translation local to the playlists family until another composed playlist tool demonstrates a shared helper need.

## Phase 0: Research and Open Questions

### Research Focus

- Confirm the reserved public catalog name, playlists-family ownership, executable descriptor pattern, exports, and default registration seam.
- Resolve the exact direct-identifier lower-layer request, required source groups, available playlist fields, one-lookup boundedness, and public-read capacity implications.
- Confirm normalization, field provenance, request-time variability, playlist-item exclusion guidance, unavailable versus safe source-failure behavior, sanitization, observability reuse, docstrings, tests, and verification commands.

### Phase 0 Decisions

All research questions are resolved in [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/310-playlist-details/research.md). No `NEEDS CLARIFICATION` items remain.

### Phase 0 Red-Green-Refactor

- **Red**: Record catalog placement, request-shape, result-mapping, safe-error, registration, and documentation uncertainties as explicit research questions.
- **Green**: Resolve every question with a decision, rationale, and rejected alternatives in `research.md`.
- **Refactor**: Retain only decisions that shape the public contract or focused implementation; do not copy lower-layer transport internals into public artifacts.

## Phase 1: Design and Contracts

### Design Goals

- Define the exact request, normalized playlist detail, provenance context, scope guidance, and safe-outcome entities.
- Make available public fields, source-preserved versus normalized values, request-time state, and playlist-item exclusion explicit.
- Define one independently testable public MCP contract with exactly one direct playlist lookup and no pagination, fan-out, ranking, or enrichment.
- Keep the work additive: one concrete playlists-family tool, no persistence, source client, crawler, playlist-item read, or transport change.

### Design Artifacts

- [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/310-playlist-details/data-model.md)
- [playlists-get-playlist-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/310-playlist-details/contracts/playlists-get-playlist-contract.md)
- [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/310-playlist-details/quickstart.md)

### Phase 1 Red-Green-Refactor

- **Red**: Identify every rule that needs tests for input validation, exact lower-layer request, complete and sparse result mapping, provenance, scope guidance, unavailable results, safe error translation, discovery metadata, and default registration.
- **Green**: Produce the data model, contract, and quickstart with concrete schema, field mapping, state transitions, boundedness, test evidence, and rollback expectations.
- **Refactor**: Reconcile result names, provenance categories, scope wording, error categories, and caller guidance across artifacts; ensure every specification requirement traces to a contract clause and focused test.

## Phase 2: Implementation Strategy

### Shared Foundation - Descriptor Exposure, Registration, and Safe Delivery

- **Red**: Add failing contract, registration, and protocol tests for concrete `playlists_getPlaylist` discovery, schema, no representative-only marker, injected lower-layer dependency, safe serialized categories, and default dispatcher presence.
- **Green**: Add the smallest playlists-family error class, public schema, descriptor export, default registration, and safe category translation required to deliver the concrete tool through the existing dispatcher.
- **Refactor**: Keep registration adjacent to existing composed descriptors, reuse centralized sanitization and request context, ensure all new or changed Python functions have reStructuredText docstrings, and rerun focused registration and routing checks.

### User Story 1 - Retrieve Playlist Details (P1)

- **Red**: Add failing unit and contract tests for required trimmed `playlistId`, unknown-field rejection, one `playlists_list` direct lookup with `snippet,contentDetails,status`, complete normalized field mapping, sparse public metadata, and successful result shaping.
- **Green**: Add only the validator, one direct-identifier lookup adapter, playlist-detail normalizer, stable result fields, field-provenance builder, metadata, and handler behavior needed for successful retrieval.
- **Refactor**: Centralize local safe field extraction and provenance mapping within the playlists family, preserve source meaning without fabricating optional fields, retain reStructuredText docstrings, and rerun focused unit and contract checks.

### User Story 2 - Interpret Playlist Details for Research (P2)

- **Red**: Add failing contract and handler tests that discovery and results identify the normalized one-playlist boundary, lower-layer dependency, field provenance, public-content boundary, request-time variability, and the explicit absence of playlist video entries.
- **Green**: Add only the caller-facing metadata and result context necessary to distinguish source-preserved playlist values from normalized contract values and to direct playlist-video requests to `playlists_getPlaylistItems`.
- **Refactor**: Consolidate repeated provenance and scope wording with existing Layer 3 conventions, retain reStructuredText docstrings for changed Python functions, and rerun focused contract and integration checks.

### User Story 3 - Receive Safe Outcomes for Unavailable Playlists (P3)

- **Red**: Add failing tests for non-object, missing, blank, non-text, and unknown input; empty or malformed lower-layer results; lower-layer unavailable, authorization, capacity, and source failures; and protocol serialization without unsafe details.
- **Green**: Map empty or malformed required lookup results to one unavailable-resource outcome. Translate lower-layer invalid input, access, capacity, and source failures to documented safe categories; expose only sanitized caller guidance.
- **Refactor**: Keep lower-layer error translation local and sanitized, remove duplication with existing safe-error utilities, verify all modified Python functions retain reStructuredText docstrings, then rerun focused integration and protocol checks.

### Regression Strategy

- Preserve existing public tools, the shared Layer 3 catalog, `playlists_list`, and lower-layer integration contracts.
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

- Keep the public tool additive. If a regression is found before release, remove only its default dispatcher registration and composed-package exports; the lower-level playlist capability remains unchanged.
- Preserve lower-layer result and error contracts by adapting them at the new public boundary rather than modifying them.
- Mitigate incorrect or sensitive output through pre-lookup validation, a fixed one-read bound, public-only source fields, explicit provenance and scope guidance, and existing safe-detail sanitization.
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

- The feature contract covers additive compatibility, one required input, one-read normalized retrieval, available-field mapping, provenance, playlist-item exclusion, safe errors, discovery, and rollback.
- Each shared-foundation and user-story phase specifies Red before Green and Refactor after Green, along with unit, contract, integration, protocol, and final full-suite verification.
- The selected design reuses the configured lower-level playlist capability, safe category serialization, request context, and dispatcher registration. It introduces no new storage, source client, transport behavior, ranking machinery, or playlist-item traversal.
- Every planned Python function change is subject to the constitution's reStructuredText docstring requirement; safe public diagnostic data and existing observability are preserved.

## Complexity Tracking

No constitution violations or complexity exceptions require justification.
