# Implementation Plan: YT-318 Channel Content Search

**Branch**: `318-channels-search-content` | **Date**: 2026-08-16 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/318-channels-search-content/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/318-channels-search-content/spec.md`

## Summary

Deliver `channels_searchContent`, an additive Layer 3 MCP tool for finding publicly searchable video content within one known channel. The tool will validate a bounded channel-and-query request, make exactly one channel-constrained call through the existing `search_list` tool, normalize usable public video results and response context, and disclose direct-search semantics without enrichment, local filtering, or re-ranking. It will reuse the existing composed channels family, dispatcher, error sanitization, and observability path; it adds no storage, transport, source client, or pagination traversal.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing MCP tool registry and dispatcher; Layer 2 `search_list` handler; `youtube_composed` channel-family conventions; Python standard-library dictionaries and regular expressions; pytest; Ruff  
**Storage**: N/A; request validation, search candidates, and normalized results exist only for one invocation  
**Testing**: Targeted pytest unit, contract, integration, and protocol-routing coverage; final `PYTHONPATH=src python3 -m pytest`; final `PYTHONPATH=src python3 -m ruff check .`  
**Documentation Style**: reStructuredText docstrings for every new or changed Python function, covering purpose, parameters, return value, raised errors where relevant, and side effects; feature-local Markdown contract documentation  
**Target Platform**: Local macOS/Linux development and the existing hosted Linux MCP service runtime  
**Project Type**: Python MCP service  
**Performance Goals**: At least 95% of representative valid requests produce a complete structured result, empty result, or safe actionable error within 5 seconds; each request performs exactly one bounded public search  
**Constraints**: Preserve the additive public name `channels_searchContent`; require `channelId` and `query`; default `maxResults` to 10 and bound it to 1–50; allow only `relevance`, `date`, or `viewCount` ordering; accept an optional BCP 47 language preference only as a relevance hint; constrain the lower-layer request to public videos in the requested channel; do not expose a continuation input; never enrich, locally rank, or claim to filter source results; omit malformed, duplicate, or out-of-scope source records with safe aggregate disclosure; never expose secrets, tokens, raw upstream payloads, stack traces, owner data, or restricted content  
**Scale/Scope**: One concrete channels-family tool; one injected lower-layer dependency; one bounded search request; descriptor export and default dispatcher registration; focused unit, contract, integration, and routing regression coverage

## Constitution Check

*GATE: Passed before Phase 0 research. Re-checked after Phase 1 design.*

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

- The feature-local [contract](contracts/channels-search-content-contract.md) defines the additive MCP schema, direct-search boundary, normalized result, provenance, empty and partial-result handling, safe error taxonomy, and rollback posture before implementation.
- Every Phase 0–2 activity and each user story below has explicit Red, Green, and Refactor work. Completion requires `PYTHONPATH=src python3 -m pytest` and `PYTHONPATH=src python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- All new or changed Python functions—including the public validator, lower-layer argument builder, candidate normalizer, result builder, error mapper, metadata builder, handler, descriptor, and any local language helper—must have complete reStructuredText docstrings.
- The plan keeps request correlation and safe lower-layer error behavior by injecting `search_list` through the existing dispatcher. It logs no query, raw candidate, credential, or restricted-content data, and it adds no persistence, direct HTTP path, source client, or generalized search abstraction.

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/318-channels-search-content/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── channels-search-content-contract.md
└── tasks.md                         # Created later by /speckit.tasks
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/
├── tools/
│   ├── dispatcher.py                # Default composed-tool registration and injected lower-layer handler
│   ├── youtube_common/
│   │   ├── conventions.py           # Existing safe detail sanitization and upstream error messaging
│   │   └── search.py                # Existing Layer 2 public search_list boundary
│   └── youtube_composed/
│       ├── __init__.py              # Public composed-tool exports
│       └── channels.py              # Channel-content-search schema, validation, mapping, metadata, and descriptor

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

**Structure Decision**: Extend the existing `youtube_composed` channels family. Adapt the existing `search_list` handler through its injected public interface and register one additive descriptor through the established package and dispatcher seams. Keep validation, source-item normalization, direct-search context, and error translation local to the channels family until a second concrete consumer demonstrates the same precise semantics.

## Phase 0: Research and Open Questions

### Research Focus

- Confirm the declared catalog name, concrete channels-family ownership, export seam, default registration seam, and existing direct-search handler pattern.
- Resolve the exact bounded Layer 2 request, public result type, ordering policy, language-preference mapping, no-pagination decision, and direct-search versus local-shaping disclosure.
- Resolve source candidate identity, channel-association defense, duplicate and malformed-record handling, successful-empty semantics, safe lower-layer error translation, discovery metadata, observability reuse, test seams, docstrings, and verification commands.

### Phase 0 Decisions

All research questions are resolved in [research.md](research.md). No open questions remain.

### Phase 0 Red-Green-Refactor

- **Red**: Record source-path, request shape, result identity, association, ordering, language, error, registration, and documentation uncertainties as explicit research questions.
- **Green**: Resolve each question with a selected decision, rationale, and rejected alternatives in `research.md`.
- **Refactor**: Keep only decisions that affect the public contract or focused implementation, reconcile names with the feature specification, and avoid copying lower-layer endpoint internals into the user-facing contract.

## Phase 1: Design and Contracts

### Design Goals

- Define one exact request, one channel-scoped video-search request, normalized search item, successful collection, partial-availability summary, and safe outcome.
- Make direct channel-constrained matching, upstream ordering, no local enrichment/filtering/re-ranking, language-hint limitations, channel-association defense, and public-only scope explicit.
- Publish one independently testable MCP contract with exactly one bounded lower-layer search and no caller-controlled continuation.
- Keep the change additive: one channels-family descriptor with no new storage, client, transport behavior, pagination traversal, generic search service, or cross-family abstraction.

### Design Artifacts

- [data-model.md](data-model.md)
- [channels-search-content-contract.md](contracts/channels-search-content-contract.md)
- [quickstart.md](quickstart.md)

### Phase 1 Red-Green-Refactor

- **Red**: Identify every rule requiring tests for input validation, direct base-request construction, source association, item normalization, duplicate/malformed omission, cap, empty result, language handling, provenance, safe errors, discovery metadata, and registration.
- **Green**: Produce the data model, contract, and quickstart with concrete schemas, source mapping, boundedness, state transitions, test evidence, and rollback expectations.
- **Refactor**: Reconcile field names, result context, source-order wording, aggregate partial-availability rules, error categories, and caller guidance across all artifacts; ensure every feature requirement traces to a contract clause and focused test.

## Phase 2: Implementation Strategy

### Shared Foundation - Descriptor Exposure, Registration, and Safe Delivery

- **Red**: Add failing contract, registration, and routing tests for the concrete `channels_searchContent` descriptor, its schema defaults and bounds, its direct-search metadata, injected `search_list` dependency, safe serialized error categories, absence of a representative-only marker, and default dispatcher presence.
- **Green**: Add only the channels-family error subtype, public schema, descriptor export, default registration, and safe category translation needed to deliver the new tool through the existing dispatcher.
- **Refactor**: Keep registration beside the existing composed channel descriptors, reuse central sanitization and request context, ensure every new or changed Python function has a reStructuredText docstring, and rerun focused registration and routing checks.

### User Story 1 - Search a Channel's Content (P1)

- **Red**: Add failing unit and contract tests for non-object input; missing, blank, non-text, and unknown fields; trimming; exact one-call `search_list` request with the requested channel, query, `part=snippet`, and `type=video`; normalized public video fields; channel association; upstream-order preservation; duplicate/malformed/out-of-scope omissions; final cap; complete response context; successful empty results; and safe lower-layer error translation.
- **Green**: Add only the validator, base-request builder, direct-search candidate normalizer, association/duplicate defense, result/context/provenance builder, error mapper, metadata builder, handler, and descriptor needed to return bounded public video results from the existing search boundary.
- **Refactor**: Centralize local safe extraction and omission accounting in the channels family; preserve available source values without fabricating optional fields; do not introduce local ranking, enrichment, or filtering; preserve reStructuredText docstrings and rerun focused unit and contract checks.

### User Story 2 - Control Search Results (P2)

- **Red**: Add failing unit and contract tests for the default, minimum, maximum, and invalid `maxResults` values; every supported `order`; exact forwarding of the effective cap and order; cap-after-normalization behavior; and discovery/result context identifying direct upstream ordering rather than local ranking.
- **Green**: Add only the bounded integer and order validation, forwarding, metadata, and response context required to honor the selected ordering and applied limit.
- **Refactor**: Consolidate constants and direct-order wording with existing composed-search conventions, retain reStructuredText docstrings for changed Python functions, and rerun focused unit, contract, and integration checks.

### User Story 3 - Refine Search by Language (P3)

- **Red**: Add failing unit and contract tests for valid and invalid BCP 47 language tags, trimming, omission when unspecified, forwarding the normalized optional value as the lower-layer relevance-language hint, response-context disclosure, and the absence of any guarantee that returned videos are in the preferred language.
- **Green**: Add only a scoped language validator, optional lower-layer argument mapping, applied-input context, and metadata language caveat needed to implement relevance refinement without changing matching, ranking, or public-content scope.
- **Refactor**: Keep language validation and request mapping local; preserve safe errors, no query logging, and reStructuredText docstrings; then rerun focused coverage followed by the required full suite and lint checks after the final code change.

### Regression Strategy

- Preserve the existing public tools, Layer 3 catalog, `search_list` request/response contract, dispatcher behavior, and existing channels-family semantics.
- Add focused coverage at `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_channels.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_channels_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py` if its routing matrix requires the newly registered name.
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

- Keep the public tool additive. If a regression is found before release, remove only its default dispatcher registration and composed-package exports; existing public and lower-layer search tools remain unchanged.
- Preserve lower-layer request, response, auth, quota, and error contracts by adapting them only at the new public boundary.
- Mitigate incorrect or sensitive output through pre-call validation, fixed one-search boundedness, `type=video` and requested-channel constraints, defensive source association, aggregate-only omission disclosure, direct-search/no-enrichment metadata, and existing safe-detail sanitization.
- No migration, persistence rollback, or infrastructure rollback is needed because the feature introduces neither stored data nor transport configuration.

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

- The contract covers additive compatibility, request schema, direct channel-scoped video search, source/item normalization, context, provenance, empty and aggregate partial results, safe errors, discovery, and rollback.
- Phase 0, Phase 1, shared foundation, and every user story specify Red before Green and Refactor after Green, with unit, contract, integration, routing, full-suite, and lint verification.
- The design retains configured public search capability, centralized sanitization, request lifecycle observability, and default dispatcher registration. It introduces no new storage, source client, transport behavior, authorization flow, crawler, pagination traversal, enrichment, or ranking machinery.
- Every planned Python function change is subject to the constitution's reStructuredText docstring requirement; public metadata, errors, and logs remain limited to safe diagnostic data.

## Complexity Tracking

No constitution violations or complexity exceptions require justification.
