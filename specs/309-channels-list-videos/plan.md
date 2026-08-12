# Implementation Plan: YT-309 Channel Video Listing

**Branch**: `309-channels-list-videos` | **Date**: 2026-08-12 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/309-channels-list-videos/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/309-channels-list-videos/spec.md`

## Summary

Deliver `channels_listVideos`, an additive MCP tool that lets research clients list publicly available videos from one known channel through a stable, bounded contract. The tool will compose the existing public channel lookup with its uploads collection and the existing playlist-item listing capability, retain the source collection's observed order, de-duplicate by video identity, and return normalized collection context and field provenance. It will use neither query nor relevance ranking, storage, a new source client, or transport changes.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing MCP tool registry and dispatcher; `src/mcp_server/tools/youtube_composed/` conventions; existing `channels_list` and `playlist_items_list` handlers; Python standard-library JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A; request normalization and collection shaping are in-memory only  
**Testing**: Targeted pytest unit, contract, integration, and protocol-routing tests; final `PYTHONPATH=src python3 -m pytest`; final `PYTHONPATH=src python3 -m ruff check .`  
**Documentation Style**: reStructuredText docstrings for every new or changed Python function; feature-local Markdown contract documentation  
**Target Platform**: Local macOS/Linux development and the existing hosted Linux MCP service runtime  
**Project Type**: Python MCP service  
**Performance Goals**: At least 95% of representative requests for up to 50 videos produce a structured outcome within 5 seconds; each request makes one channel lookup and at most one uploads-collection listing  
**Constraints**: Preserve the public name `channels_listVideos`; accept only `channelId` and optional `maxResults`; default to 10 and bound results to 1–50; preserve observed uploads-collection order; never relevance-rank or keyword-filter; expose provenance and safe errors; exclude secrets, owner context, raw source payloads, stack traces, signed URLs, and non-public video data; do not add dependencies, persistence, transport changes, scraping, pagination traversal, or broad dispatcher rewrites  
**Scale/Scope**: One concrete channels-family tool, two existing lower-layer dependencies, one bounded two-read composition, four focused test areas plus registration/protocol regression coverage, and no changes to other public tool families

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

- The feature-local contract defines the MCP input, source-ordered result, provenance, bounded composition, public-content boundary, safe error behavior, and additive compatibility before implementation.
- Each shared-foundation and user-story phase below uses Red-Green-Refactor. Completion requires `PYTHONPATH=src python3 -m pytest` and `PYTHONPATH=src python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Every new or changed Python function, including validators, normalizers, item extractors, error mappers, descriptor builders, and test doubles, must carry a reStructuredText docstring covering purpose, inputs, outputs, raised errors where relevant, and side effects where relevant.
- The design retains request correlation, lower-layer observability, dependency injection, and sanitized error handling. It adds no storage, client, transport, authentication flow, crawler, or general ranking component.

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/309-channels-list-videos/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── channels-list-videos-contract.md
└── tasks.md                         # Created later by /speckit.tasks
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/
├── tools/
│   ├── dispatcher.py                # Default composed-tool registration and dependency injection
│   ├── youtube_common/
│   │   ├── channels.py              # Existing lower-level channels_list handler
│   │   └── playlist_items.py        # Existing lower-level playlist_items_list handler
│   └── youtube_composed/
│       ├── __init__.py              # Public composed-tool exports
│       └── channels.py              # Channel-list-videos descriptor, validation, composition, mapping, errors
└── protocol/
    └── methods.py                   # Existing public error-category serialization regression coverage only

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

**Structure Decision**: Extend the existing `youtube_composed` channels family. Its new descriptor and handler will adapt existing lower-level channel and playlist-item lookup capabilities rather than duplicate request execution or expose their near-raw envelopes. Export and default-register the descriptor through established package and dispatcher seams. Keep video-item normalization and error translation local to the channel family until a second composed tool demonstrates a shared use case.

## Phase 0: Research and Open Questions

### Research Focus

- Confirm the exact public catalog name, channel-family ownership, executable descriptor pattern, exports, and default registration seam.
- Resolve the deterministic, public uploads-collection path versus ranked search behavior, including the exact bounded lower-layer requests and quota/access implications.
- Confirm video-identity extraction, source-order preservation, de-duplication-before-cap behavior, available item fields, and empty-collection semantics.
- Resolve core-lookup versus collection-list failure categories, partial-availability boundaries, sanitization, discovery metadata, observability reuse, tests, docstrings, and verification commands.

### Phase 0 Decisions

All research questions are resolved in [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/309-channels-list-videos/research.md). No `NEEDS CLARIFICATION` items remain.

### Phase 0 Red-Green-Refactor

- **Red**: Record source-path, ordering, limit, item extraction, empty-versus-unavailable, partial-availability, lower-layer error, registration, and documentation uncertainties as explicit research questions.
- **Green**: Resolve every question with a decision, rationale, and rejected alternatives in `research.md`.
- **Refactor**: Retain only decisions that shape the public contract or focused implementation; do not copy lower-layer endpoint internals into the public contract.

## Phase 1: Design and Contracts

### Design Goals

- Define exact request, uploads-collection, channel video item, listing result, partial-availability, and safe-outcome entities.
- Make source-preserved item values, normalized collection context, field provenance, source ordering, and no-ranking semantics explicit.
- Define a single independently testable public MCP contract with exactly one channel lookup and at most one bounded uploads-collection listing.
- Keep the work additive: one concrete channel tool, no persistence, source client, crawler, pagination traversal, generic ranking, or new transport behavior.

### Design Artifacts

- [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/309-channels-list-videos/data-model.md)
- [channels-list-videos-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/309-channels-list-videos/contracts/channels-list-videos-contract.md)
- [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/309-channels-list-videos/quickstart.md)

### Phase 1 Red-Green-Refactor

- **Red**: Identify every rule that needs tests for input validation, source-order preservation, item normalization, de-duplication, final cap, empty collection, provenance, safe errors, and discovery metadata.
- **Green**: Produce the data model, contract, and quickstart with concrete schemas, state transitions, field mappings, boundedness, test evidence, and rollback expectations.
- **Refactor**: Reconcile field names, provenance categories, ordering language, partial-availability conditions, error categories, and caller guidance across artifacts; ensure every specification requirement traces to a contract clause and focused test.

## Phase 2: Implementation Strategy

### Shared Foundation - Descriptor Exposure, Registration, and Safe Delivery

- **Red**: Add failing contract, registration, and protocol tests for concrete `channels_listVideos` discovery, schema defaults and bounds, no representative-only marker, injected dependencies, safe serialized categories, and default dispatcher presence.
- **Green**: Add the smallest channel-family error class, public schema, descriptor export, default registration, and safe category translation required to deliver the concrete tool through the existing dispatcher.
- **Refactor**: Keep registration adjacent to existing composed channel descriptors, reuse centralized sanitization and request context, ensure all new or changed Python functions have reStructuredText docstrings, and rerun focused registration and routing checks.

### User Story 1 - List a Channel's Videos (P1)

- **Red**: Add failing unit and contract tests for required `channelId`, unknown-field rejection, `maxResults` default and every boundary, one `channels_list` request for the public uploads collection, one `playlist_items_list` request with the applied limit, successful item mapping, source-order preservation, de-duplication by video identifier, final cap, and an accessible empty collection.
- **Green**: Add only the validator, one-channel uploads-collection lookup adapter, bounded playlist-item adapter, video-item normalizer, ordered de-duplication/cap behavior, stable response fields, provenance builder, descriptor metadata, and handler behavior needed for successful listing.
- **Refactor**: Centralize local safe extraction and provenance mapping within the channels family, preserve source meaning without fabricating optional fields, retain reStructuredText docstrings, and rerun focused unit and contract checks.

### User Story 2 - Understand Result Meaning and Ordering (P2)

- **Red**: Add failing contract and handler tests that discovery and results identify the uploads-collection path, publicly observed source order, applied limit, no relevance ranking, request-time collection variability, field provenance, and public-content boundaries.
- **Green**: Add only the caller-facing metadata and result context necessary to distinguish source-preserved video values from normalized collection values and to direct ranked or keyword discovery to a search-oriented tool.
- **Refactor**: Consolidate repeated ordering and provenance wording with existing Layer 3 conventions, retain reStructuredText docstrings for changed Python functions, and rerun focused contract and integration checks.

### User Story 3 - Receive Safe Outcomes for Unavailable Content (P3)

- **Red**: Add failing tests for missing or malformed requests, empty/malformed core channel results, missing uploads-collection identity, empty uploads collection, core unavailable/access/capacity/source errors, collection access/capacity/source errors, and any known individual omission partial-availability disclosure without unsafe details.
- **Green**: Map core failure and missing-channel cases to whole-request safe categories; map missing uploads identity and empty collection to a successful empty result; map a failed required collection read to a whole-request safe category; omit any known inaccessible individual item and expose only safe aggregate partial-availability context.
- **Refactor**: Keep lower-layer error translation local and sanitized, remove duplication with existing safe error utilities, verify all modified Python functions retain reStructuredText docstrings, then rerun focused integration and protocol checks.

### Regression Strategy

- Preserve existing public tools, the shared Layer 3 catalog, `channels_list`, `playlist_items_list`, and lower-layer integration contracts.
- Add focused coverage at `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`.
- Run focused checks during implementation:

  ```bash
  PYTHONPATH=src python3 -m pytest \
    tests/unit/test_youtube_composed_channels.py \
    tests/contract/test_youtube_composed_channels_contract.py \
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

- Keep the public tool additive. If a regression is found before release, remove only its default dispatcher registration and composed-package exports; lower-level channel and playlist-item capabilities remain unchanged.
- Preserve lower-layer result and error contracts by adapting them at the new public boundary rather than modifying them.
- Mitigate incorrect or sensitive output through pre-lookup validation, a fixed one-channel/two-read bound, public-only source material, de-duplication by stable identifier, explicit provenance and ordering disclosure, and existing safe-detail sanitization.
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

- The feature contract covers additive compatibility, input, source-order semantics, no-ranking behavior, response provenance, bounded composition, empty and partial-availability results, safe errors, discovery, and rollback.
- Each shared-foundation and user-story phase specifies Red before Green and Refactor after Green, along with unit, contract, integration, protocol, and final full-suite verification.
- The selected design reuses existing configured channel and playlist-item capabilities, safe category serialization, request context, and dispatcher registration. It introduces no new storage, source client, transport behavior, or generalized ranking machinery.
- Every planned Python function change is subject to the constitution's reStructuredText docstring requirement; safe public diagnostic data and existing observability are preserved.

## Complexity Tracking

No constitution violations or complexity exceptions require justification.
