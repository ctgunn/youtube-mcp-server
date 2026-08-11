# Implementation Plan: YT-305 Channel Details

**Branch**: `305-channels-get-channel` | **Date**: 2026-08-11 | **Spec**: [/Users/ctgunn/Projects/youtube-mcp-server/specs/305-channels-get-channel/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/305-channels-get-channel/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/305-channels-get-channel/spec.md`

## Summary

Deliver `channels_getChannel`, an additive MCP tool that returns one normalized public channel profile, cautiously derived public contact and creator-versus-brand information, and a bounded latest-video publication enrichment. The implementation will reuse the existing channel and playlist-item lookup capabilities, compose at most two lower-layer requests, preserve explicit field provenance, and return a usable profile when the optional latest-video enrichment is unavailable or fails safely.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: Existing MCP tool registry and dispatcher; `src/mcp_server/tools/youtube_composed/` conventions; existing `channels_list` and `playlist_items_list` handlers; Python standard-library dataclasses and JSON-compatible dictionaries; pytest; Ruff
**Storage**: N/A; request handling, normalization, and enrichment state are in-memory only
**Testing**: Targeted pytest unit, contract, integration, and protocol-routing tests; final `PYTHONPATH=src python3 -m pytest`; final `PYTHONPATH=src python3 -m ruff check .`
**Documentation Style**: reStructuredText docstrings for every new or changed Python function; feature-local Markdown contract documentation
**Target Platform**: Local macOS/Linux development and the existing hosted Linux MCP service runtime
**Project Type**: Python MCP service
**Performance Goals**: At least 95% of representative single-channel requests yield a complete or safely partial result within 5 seconds; each request performs one core channel lookup and at most one latest-upload lookup
**Constraints**: Preserve the public name `channels_getChannel`; accept only `channelId`; return one result only; use only public channel material for contact and heuristic values; classify uncertain or conflicting channel type as `unknown`; expose provenance and safe partial-enrichment state; exclude secrets, owner context, raw source payloads, stack traces, signed URLs, and non-public contact data; do not add dependencies, persistence, transport changes, scraping, or broad dispatcher rewrites
**Scale/Scope**: One concrete channel-family tool, two lower-layer dependencies, one bounded optional enrichment, three focused test areas plus registration/protocol regression coverage, and no changes to other public tool families

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

- The feature-local contract defines the MCP input, result, provenance, heuristic disclosures, bounded composition, partial-enrichment state, and error behavior before implementation.
- Each shared-foundation and user-story phase below uses Red-Green-Refactor. Completion requires `PYTHONPATH=src python3 -m pytest` and `PYTHONPATH=src python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Every new or changed Python function, including validators, normalizers, contact and heuristic helpers, error mappers, descriptor builders, and test doubles, must carry a reStructuredText docstring that covers purpose, inputs, outputs, raised errors where relevant, and side effects where relevant.
- The design preserves request context and existing safe error/logging behavior. It adds no storage, client, transport, or authentication flow, and it limits enrichment to a public uploads playlist and one item.

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/305-channels-get-channel/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── channels-get-channel-contract.md
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
│       └── channels.py              # Channel-detail descriptor, validation, normalization, heuristics, enrichment
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

**Structure Decision**: Extend the existing `youtube_composed` channels family. Its descriptor and handler will adapt existing lower-level lookup capabilities rather than duplicate request execution or expose their near-raw collection envelopes. Export and default-register the descriptor through the established package and dispatcher seams. Keep contact and tri-state classification helpers within the channel family because no second composed family uses them yet.

## Phase 0: Research and Open Questions

### Research Focus

- Confirm the exact public catalog name, channel-family ownership, and concrete-descriptor pattern.
- Confirm the one-channel lookup parameters, public source fields, authentication/quota facts, and safe lower-layer error categories.
- Resolve the deterministic, bounded latest-video enrichment path and distinguish unavailable enrichment from failed enrichment.
- Resolve public-contact extraction and creator-versus-brand disclosure without treating derived values as verified identity claims.
- Confirm discovery metadata, default registration, test locations, reStructuredText docstring work, existing protocol support, and final verification commands.

### Phase 0 Decisions

All research questions are resolved in [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/305-channels-get-channel/research.md). No `NEEDS CLARIFICATION` items remain.

### Phase 0 Red-Green-Refactor

- **Red**: Record ambiguous behavior—source/provenance mapping, public-contact scope, tri-state classification, uploads-playlist selection, missing-versus-failed enrichment, error mapping, and registration—as explicit research questions.
- **Green**: Resolve every question with a decision, rationale, and rejected alternatives in `research.md`.
- **Refactor**: Retain only decisions that shape the public contract or focused implementation; do not copy lower-layer endpoint internals into the public contract.

## Phase 1: Design and Contracts

### Design Goals

- Define the exact request, core profile, normalized metadata, public-contact, heuristic, enrichment, provenance, and lookup-outcome entities.
- Make contact extraction and creator-versus-brand classification visibly heuristic, public-only, deterministic, and non-canonical.
- Make the core-profile success, no-visible-upload success, and partial-enrichment success distinguishable.
- Define an independently testable public MCP contract with a maximum of two lower-layer reads.
- Keep the work additive: one concrete channel tool, no persistence, no source client, no general crawler, and no new transport behavior.

### Design Artifacts

- [/Users/ctgunn/Projects/youtube-mcp-server/specs/305-channels-get-channel/data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/305-channels-get-channel/data-model.md)
- [/Users/ctgunn/Projects/youtube-mcp-server/specs/305-channels-get-channel/contracts/channels-get-channel-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/305-channels-get-channel/contracts/channels-get-channel-contract.md)
- [/Users/ctgunn/Projects/youtube-mcp-server/specs/305-channels-get-channel/quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/305-channels-get-channel/quickstart.md)

### Phase 1 Red-Green-Refactor

- **Red**: Identify every rule needed to test input validation, source and derived field provenance, public-contact safety, tri-state classification, bounded enrichment, partial state, safe errors, and discovery metadata.
- **Green**: Produce the data model, contract, and quickstart with concrete schemas, state transitions, field mappings, boundedness, test evidence, and rollback expectations.
- **Refactor**: Reconcile field names, provenance categories, enrichment statuses, error categories, and caller guidance across all artifacts; ensure every specification requirement traces to a contract clause and focused test.

## Phase 2: Implementation Strategy

### Shared Foundation - Descriptor Exposure, Registration, and Safe Delivery

- **Red**: Add failing contract, registration, and protocol tests for concrete `channels_getChannel` discovery, no representative-only marker, injected dependencies, safe serialized categories, and default dispatcher presence.
- **Green**: Add the smallest channel-family error class, public schema, descriptor export, default registration, and safe category translation required to deliver the concrete tool through the existing dispatcher.
- **Refactor**: Keep registration adjacent to existing composed descriptors, reuse centralized sanitization and request context, ensure all new or changed Python functions have reStructuredText docstrings, and rerun focused registration and routing checks.

### User Story 1 - Retrieve One Channel's Details (P1)

- **Red**: Add failing unit and contract tests for required `channelId`, unknown-field rejection, a single `channels_list` call using the core public profile parts, normalized core and metadata mapping, sparse public values, and complete field provenance.
- **Green**: Add only the validator, one-channel lookup adapter, core-profile normalizer, metadata mapper, provenance builder, descriptor metadata, and handler behavior needed for a successful single-channel result.
- **Refactor**: Centralize repeated safe extraction and provenance mapping within the channel family, preserve source meaning without fabricating absent values, retain reStructuredText docstrings, and rerun focused unit and contract checks.

### User Story 2 - Assess Channel Type With Appropriate Caution (P2)

- **Red**: Add failing unit and contract tests for deterministic de-duplication of valid public email addresses and links; malformed, duplicate, unsupported, and private-value omission; positive creator signals; positive brand signals; conflicting or insufficient signals yielding `unknown`; and heuristic disclosure metadata.
- **Green**: Add only channel-family helpers that derive contact values from returned public channel material and produce a positive-evidence-only `creator`, `brand`, or `unknown` classification with signal identifiers and limitations. Do not crawl pages, access owner data, or introduce a generic cross-family helper.
- **Refactor**: Consolidate normalization and classifier token handling, ensure contact and heuristic fields remain `heuristic_inferred`, retain reStructuredText docstrings, and rerun focused unit and contract checks.

### User Story 3 - Handle Missing Channels and Incomplete Enrichment Safely (P3)

- **Red**: Add failing tests for empty core results, core not-found/access/quota/upstream failures, no uploads-playlist identifier, empty or malformed latest-item data, exactly one playlist-item read, and playlist access/quota/upstream failures after core success.
- **Green**: Add the minimum bounded latest-upload enrichment using the existing uploads-playlist path; map absent latest data to successful `unavailable` enrichment; map a post-profile dependency failure to `partial` enrichment with `partial_enrichment_failure` and a safe cause category; map core failures to whole-request safe categories.
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

- Keep the public tool additive. If a regression is found before release, remove only its default dispatcher registration and composed-package exports; the lower-level channel and playlist-item capabilities remain unchanged.
- Preserve lower-layer result and error contracts by adapting them at the new public boundary rather than modifying them.
- Mitigate incorrect or sensitive output through pre-lookup validation, a fixed one-channel/two-read bound, public-only contact extraction, explicit provenance, conservative `unknown` classification, safe partial-state disclosure, and existing safe-detail sanitization.
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

- The feature contract covers schema, additive compatibility, response provenance, public-contact limits, heuristic uncertainty, bounded composition, partial-enrichment state, safe errors, discovery, and rollback.
- Each shared-foundation and user-story phase specifies Red before Green and Refactor after Green, along with unit, contract, integration, protocol, and final full-suite verification.
- The selected design reuses two existing lower-layer capabilities, default registration, safe category serialization, and request context. It introduces no new storage, source client, transport behavior, or generalized scraping.
- Every planned Python function change is subject to the constitution's reStructuredText docstring requirement, and observability/error details remain restricted to safe public diagnostic data.

## Complexity Tracking

No constitution violations or complexity exceptions require justification.
