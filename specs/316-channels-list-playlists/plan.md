# Implementation Plan: YT-316 Channel Playlist Listing

**Branch**: `316-channels-list-playlists` | **Date**: 2026-08-14 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/316-channels-list-playlists/spec.md`

## Summary

Deliver `channels_listPlaylists`, an additive higher-level MCP tool that returns a stable, bounded, source-ordered list of publicly accessible playlists for one channel. It will validate `channelId` and `maxResults`, verify the channel once, make one existing playlist-listing request, normalize useful playlist metadata and provenance, and translate lower-layer failures into safe public outcomes. It adds no persistence, source client, pagination traversal, ranking, transport, or authentication flow.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing MCP dispatcher and registry; `youtube_composed` conventions; existing `channels_list` and `playlists_list` handlers; standard-library JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A; request validation and result shaping are in-memory only  
**Testing**: Focused pytest unit, contract, integration, and protocol-routing tests; final `PYTHONPATH=src python3 -m pytest` and `PYTHONPATH=src python3 -m ruff check .`  
**Documentation Style**: reStructuredText docstrings for every new or changed Python function; feature-local Markdown contract documentation  
**Target Platform**: Local macOS/Linux development and the existing hosted Linux MCP service runtime  
**Project Type**: Python MCP service  
**Performance Goals**: At least 95% of representative valid requests for up to 50 playlists produce a structured outcome within 5 seconds; each request makes one bounded channel lookup and one bounded playlist listing  
**Constraints**: Preserve `channels_listPlaylists`; accept only `channelId` and optional `maxResults`; default to 25 and bound results to 1–50; preserve source order; omit unavailable optional metadata without fabrication; expose provenance, count, and safe errors; exclude credentials, owner context, raw source payloads, stack traces, signed URLs, and non-public data; add no dependencies, persistence, transport changes, scraping, pagination traversal, ranking, or cross-channel aggregation  
**Scale/Scope**: One concrete channel-family tool, two existing lower-layer dependencies, two bounded reads, four focused test areas plus registration/protocol regression coverage

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

- The feature contract defines the additive public schema, fixed two-read boundary, source order, normalized fields, provenance, empty-result semantics, and safe errors before code changes begin.
- Every phase and user-story strategy places failing tests before minimal code, then behavior-preserving cleanup. Completion requires `PYTHONPATH=src python3 -m pytest` and `PYTHONPATH=src python3 -m ruff check .` from the repository root.
- Every new or changed Python function, including validators, normalizers, error mappers, descriptor builders, and test doubles, must have a reStructuredText docstring covering purpose, inputs, outputs, raised errors where relevant, and side effects where relevant.
- The design reuses configured lower-layer observability, authentication, quota behavior, request context, and error sanitization. It introduces no new storage, client, transport, crawler, ranking component, or complexity exception.

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/316-channels-list-playlists/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── channels-list-playlists-contract.md
└── tasks.md                         # Created later by /speckit.tasks
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/
├── tools/
│   ├── dispatcher.py                # Default composed-tool registration and dependency injection
│   ├── youtube_common/
│   │   ├── channels.py              # Existing lower-level channels_list handler
│   │   └── playlists.py             # Existing lower-level playlists_list handler
│   └── youtube_composed/
│       ├── __init__.py              # Public composed-tool exports
│       └── channels.py              # Channel-playlist schema, handler, normalization, and errors
└── protocol/
    └── methods.py                   # Existing public error serialization regression coverage

/Users/ctgunn/Projects/youtube-mcp-server/tests/
├── unit/
│   ├── test_youtube_composed_channels.py
│   └── test_method_routing.py
├── contract/
│   └── test_youtube_composed_channels_contract.py
└── integration/
    ├── test_youtube_composed_tool_registration.py
    └── test_youtube_tool_registration.py
```

**Structure Decision**: Extend the existing composed channels family. The descriptor and handler will adapt `channels_list` for availability verification and `playlists_list` for the source collection rather than duplicate request execution or expose near-raw results. Keep playlist-record mapping and safe error translation local to the channels family; export and default-register through existing seams.

## Phase 0: Research and Open Questions

### Research Focus

- Confirm the catalog name, composed channel-family placement, lower-layer sources, descriptor/export/registration seams, test commands, and documentation rules.
- Resolve the exact lower-layer requests, default/bounds, two-read policy, source-order behavior, record-field mapping, successful empty result, safe error translation, and observability/security boundaries.
- Reconcile the feature-spec dependency label with the actual existing listing capability.

### Phase 0 Decisions

All research questions are resolved in [research.md](research.md). The actual lower-layer dependencies are existing YT-210 `channels.list` and YT-236 `playlists.list` capabilities; the YT-237 dependency label in the feature specification names playlist creation and is not used by this feature.

### Phase 0 Red-Green-Refactor

- **Red**: Record catalog placement, source request, input boundary, output mapping, empty versus error semantics, and dependency-label uncertainty as explicit research questions.
- **Green**: Resolve each question with a decision, rationale, and rejected alternatives in `research.md`.
- **Refactor**: Retain only decisions that shape the public contract and focused implementation; do not copy lower-layer transport internals into public artifacts.

## Phase 1: Design and Contracts

### Design Goals

- Define the precise request, normalized playlist record, successful listing, provenance context, and safe outcomes.
- Make fixed two-read boundedness, source ordering, request-time variability, default and bounds, no-ranking behavior, and empty-list semantics explicit.
- Define one independently testable public MCP contract that verifies one channel, then performs one channel-scoped playlist listing, with no continuation input.
- Keep the work additive: one concrete tool, no persistence, source client, traversal, enrichment, ranking, or multi-channel aggregation.

### Design Artifacts

- [data-model.md](data-model.md)
- [channels-list-playlists-contract.md](contracts/channels-list-playlists-contract.md)
- [quickstart.md](quickstart.md)

### Phase 1 Red-Green-Refactor

- **Red**: Identify tests required for validation, exact lower-layer request, defaults and bounds, source order, record normalization, sparse metadata, empty success, safe errors, discovery metadata, and default registration.
- **Green**: Produce the data model, contract, and quickstart with concrete schemas, field mappings, state transitions, boundedness, test evidence, and rollback expectations.
- **Refactor**: Reconcile field names, provenance categories, ordering and limit wording, safe error categories, and caller guidance across the artifacts; ensure every requirement traces to a contract clause and focused test.

## Phase 2: Implementation Strategy

### Shared Foundation - Descriptor Exposure, Registration, and Safe Delivery

- **Red**: Add failing contract, registration, and routing tests for `channels_listPlaylists` discovery, schema default/bounds, injected lower-layer dependency, safe category serialization, no `representativeOnly` marker, package export, and default dispatcher presence.
- **Green**: Add only the channel-family error class, schema, metadata, descriptor export, default registration, and safe category translation required to deliver the concrete tool.
- **Refactor**: Reuse centralized sanitization and request context; ensure all new or changed Python functions have reStructuredText docstrings; rerun focused registration and routing checks.

### User Story 1 - List a Channel's Playlists (P1)

- **Red**: Add failing unit and contract tests for required trimmed `channelId`, unknown-field rejection, exactly one `channels_list` verification and one `playlists_list` request using `snippet,contentDetails,status`, source-order preservation, normalized playlist identity/title and available optional fields, provenance, and returned count.
- **Green**: Add only the validator, channel-verification and channel-scoped-listing adapters, playlist normalizer, collection context, metadata, and handler behavior needed for successful retrieval.
- **Refactor**: Centralize safe field extraction and provenance mapping within the channels family, preserve source meaning without fabricating optional values, retain reStructuredText docstrings, and rerun focused unit and contract checks.

### User Story 2 - Bound a Playlist Listing (P2)

- **Red**: Add failing tests for omitted default 25, every 1–50 boundary, rejection of booleans/fractions/strings/out-of-range values, exact applied lower-layer limit, source order, one-page no-continuation behavior, and returned count.
- **Green**: Apply only the documented limit validation and collection context needed to expose the applied limit, no ranking, and request-time ordering semantics.
- **Refactor**: Consolidate repeated limit and ordering wording with Layer 3 conventions, retain reStructuredText docstrings for changed Python functions, and rerun focused contract and integration checks.

### User Story 3 - Receive Actionable Unavailable Outcomes (P3)

- **Red**: Add failing tests for non-object/missing/blank/non-text input, unavailable verified channels, successful empty items from an available channel, malformed source records, lower unavailable/access/capacity/source failures, and serialized errors without unsafe details.
- **Green**: Return an unavailable outcome when channel verification has no usable match and an empty successful result only when a verified channel's playlist listing succeeds with no items; omit malformed records that cannot satisfy the stable record contract; translate lower errors to documented safe categories without exposing sensitive details.
- **Refactor**: Keep lower-layer error translation local and sanitized, remove duplication with existing helpers, verify all modified Python functions retain reStructuredText docstrings, and rerun focused integration and protocol checks.

### Regression Strategy

- Preserve all existing public tools, shared catalog entries, and lower-layer `channels_list` and `playlists_list` contracts.
- Add focused coverage in `tests/unit/test_youtube_composed_channels.py`, `tests/contract/test_youtube_composed_channels_contract.py`, `tests/integration/test_youtube_composed_tool_registration.py`, `tests/integration/test_youtube_tool_registration.py`, and `tests/unit/test_method_routing.py`.
- During implementation run:

  ```bash
  PYTHONPATH=src python3 -m pytest \
    tests/unit/test_youtube_composed_channels.py \
    tests/contract/test_youtube_composed_channels_contract.py \
    tests/integration/test_youtube_composed_tool_registration.py \
    tests/integration/test_youtube_tool_registration.py \
    tests/unit/test_method_routing.py
  ```

- After the final code change require:

  ```bash
  PYTHONPATH=src python3 -m pytest
  PYTHONPATH=src python3 -m ruff check .
  ```

### Rollback and Mitigation

- Keep the tool additive. If a regression is found before release, remove only its default dispatcher registration and composed-package exports; the lower-layer playlist listing remains unchanged.
- Preserve lower-layer result and error contracts by adapting them at the new public boundary.
- Mitigate incorrect or sensitive output with pre-lookup validation, fixed two-read bounds, source-order preservation, public-only fields, explicit provenance, and existing sanitization.
- No migration, persistence rollback, or infrastructure rollback is required because no stored data or transport configuration changes.

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

Post-design rationale: The contract covers additive compatibility, one required input, bounded normalized retrieval, source-order and provenance semantics, safe errors, discovery, and rollback. All implementation phases specify Red before Green and Refactor after Green, including unit, contract, integration, routing, and full-suite verification. The design reuses lower-layer observability and configured dependencies without introducing a new client, persistence, transport behavior, OAuth flow, or ranking machinery.

## Complexity Tracking

No constitution violations or complexity exceptions require justification.
