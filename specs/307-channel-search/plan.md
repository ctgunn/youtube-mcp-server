# Implementation Plan: Channel Search

**Branch**: `307-channel-search` | **Date**: 2026-08-11 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/307-channel-search/spec.md`

## Summary

Deliver `channels_searchChannels`, an additive Layer 3 MCP tool for public channel discovery by handle, name, or general query. It will compose the existing lower-level search, channel-details, and conditional uploads-playlist handlers; apply public-metadata refinement and deterministic ranking; and return a bounded, provenance-aware collection with safe partial-enrichment and error outcomes. The required `channelType` input needs a narrow supporting extension to the existing Layer 1/2 search contract so it can reach the configured search path without bypassing established boundaries.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing FastAPI/Pydantic/Uvicorn service runtime; in-repository MCP dispatcher; Layer 1 search request contract; Layer 2 `search_list`, `channels_list`, and `playlist_items_list` handlers; Layer 3 composed-tool conventions; Python standard-library date/time utilities  
**Storage**: N/A; request, candidate, enrichment, and ranking state exist only for one invocation  
**Testing**: pytest for unit, contract, integration, and protocol regression coverage; Ruff for linting  
**Documentation Style**: reStructuredText docstrings for every new or changed Python function, including purpose, `:param:`, `:return:`, `:raises:` when relevant, and side effects when relevant  
**Target Platform**: Linux-hosted Cloud Run service and supported local development runtime  
**Project Type**: MCP-enabled web service  
**Performance Goals**: Under normal public-source availability, at least 95% of representative searches return a complete, safely partial, or empty structured result within 5 seconds  
**Constraints**: Strict public schema; final result limit of 1–50 (default 10); base candidate and enrichment fan-out bounded to at most 50 distinct channels; public metadata, errors, and logs must not expose credentials, tokens, stack traces, raw request/response bodies, or private owner data; all new/changed Python functions require reStructuredText docstrings  
**Scale/Scope**: One new public Layer 3 tool plus a narrow additive Layer 1/2 search-field extension, package exports, dispatcher registration, and focused unit/contract/integration/protocol regression coverage

## Constitution Check

*Pre-Phase 0 gate: PASS.*

- [x] Contracts are defined for all external/MCP-facing behavior changes in [contracts/channels-search-channels-contract.md](./contracts/channels-search-channels-contract.md).
- [x] The phase plan includes explicit Red-Green-Refactor steps for shared foundation work and all three user stories.
- [x] Each Red step defines failing tests before implementation work begins.
- [x] Each Green step limits code to the minimum needed to pass the corresponding tests.
- [x] Each Refactor step includes cleanup plus a full repository test-suite re-run.
- [x] Unit, contract, integration, and protocol regression coverage are documented.
- [x] The completion command is `python3 -m pytest`; lint evidence is `python3 -m ruff check .`.
- [x] Every new or changed Python function is required to have a reStructuredText docstring.
- [x] Observability, security, and simplicity constraints are addressed below.

### Constitution-Driven Design Controls

- **Contract-first**: Publish the concrete input schema, response shape, provenance, composition boundary, safe errors, and additive compatibility posture before registration.
- **Determinism**: Normalize inputs, validate cross-field constraints, retain earliest base-search position for duplicate channel candidates and all ties, filter before ranking, then apply the final result cap.
- **Observability**: Reuse the existing dispatcher and lower-layer request lifecycle so tool-name request metrics and safe lower-layer operation/latency events continue to be produced. Do not add logging of query values, candidate payloads, or credentials.
- **Security**: Reuse safe lower-layer error mapping and detail sanitization; public discovery metadata must remain safe. Public search uses configured public capability only and never requests or returns owner-scoped data.
- **Simplicity and boundedness**: Extend the existing channels-family module and reuse injected handlers. Batch distinct channel metadata in one lookup when enrichment is required; read at most one public uploads-playlist item per distinct candidate only for an active latest-activity rule. Do not add a persistence layer, direct client, or generic cross-family abstraction.
- **Rollback/mitigation**: This is an additive tool and additive lower-level optional field. If the tool must be withdrawn, remove its descriptor from default registration while retaining existing tools and the independently backward-compatible lower-level `channelType` support; no existing client migration is required.

## Research Decisions

All Phase 0 questions are resolved in [research.md](./research.md). In particular, `channelType` is added narrowly through the existing search contracts; latest public activity is obtained only when required through the channel's public uploads playlist; and the existing channel-family public-signal classifier is reused to keep channel classification semantics consistent.

## Phase Plan and Red-Green-Refactor Strategy

### Phase 0 - Research and Contract Decisions (complete)

- **Red**: Identify contract, lower-layer composition, `channelType` pass-through, latest-activity, creator-heuristic, error-serialization, boundedness, security, and test-command gaps.
- **Green**: Record the selected composition, lower-layer extension, conservative classification, partial-result policy, safe error translation, and public contract in `research.md` and the contract artifact.
- **Refactor**: Remove all unresolved markers, align terminology with YT-301 and existing channel-family behavior, and re-check the pre-design constitution gate.

### Phase 1 - Design and Contract Artifacts (complete)

- **Red**: Derive missing entities, relationships, input validation, response provenance, failure states, compatibility posture, and verification flows from the specification and existing contracts.
- **Green**: Publish the data model, MCP contract, and quickstart verification path; update the Codex agent context with the current composed-tool technology context.
- **Refactor**: Reconcile duplicated validation, composition, and partial-result rules across the design artifacts; keep the contract concrete rather than representative-only; perform the post-design constitution check.

### Phase 2 - Implementation Planning (for `/speckit.tasks`; no tasks created here)

#### Shared Foundation - Search `channelType` Support

- **Red**: Add failing Layer 1/2 unit and contract tests showing that `channelType` accepts only `any` or `show`, is preserved in the safe search request shape, and rejects incompatible invalid values without unsafe detail exposure.
- **Green**: Add only the `channelType` optional-field declaration, validation, metadata/contract representation, and request shaping needed for the composed tool to request public channel searches. Preserve existing search behavior for callers that omit the field.
- **Refactor**: Keep validation at the existing lower-layer boundary; add or preserve reStructuredText docstrings for every changed Python function; run focused search tests.

#### User Story 1 - Search for Relevant Channels (P1)

- **Red**: Add failing unit tests for query trimming, allowed fields, default/bounded `maxResults`, `order` and `channelType` validation, base-search argument mapping with `type=channel`, candidate normalization from `id.channelId`, earliest-position de-duplication, empty success, source-continuation disclosure, and safe base-search error translation. Add contract and registration tests for the executable descriptor.
- **Green**: Add the concrete channels-family schema, error type, validator, base-search adapter, result normalizer, metadata builder, handler, package export, and dispatcher registration required to return normalized distinct channel results from `search_list`.
- **Refactor**: Reuse existing channel-profile normalization and provenance helpers where their semantics already match. Keep any new search-only helper local to the channels family unless a second concrete consumer proves a shared abstraction is justified; update reStructuredText docstrings and run focused unit/contract/integration tests.

#### User Story 2 - Refine Channels by Research Criteria (P2)

- **Red**: Add failing unit and integration tests for one batched public channel lookup, subscriber-range and latest-upload-window filters, `creatorOnly`, hidden or unavailable metadata, partial-enrichment disclosure, and all-unavailable required enrichment.
- **Green**: Invoke `channels_list` only when an active rule needs channel metadata, derive latest public upload activity only for an activity filter or `recent_activity`, reuse the conservative channel-family creator classifier, exclude only candidates that cannot satisfy an active data-dependent rule, and shape safe aggregate partial-enrichment information.
- **Refactor**: Preserve bounded fan-out, field provenance, safe error sanitization, and reStructuredText docstrings. Extract a reusable helper only after a second concrete tool needs the exact same semantics; rerun focused coverage.

#### User Story 3 - Rank Channels for a Research Goal (P3)

- **Red**: Add failing unit tests for all five `sortBy` modes, inclusive filters-before-rank behavior, earliest base-position ties, unknown-metadata exclusion for metadata-dependent ranks, de-duplication, and final result truncation.
- **Green**: Implement only the documented ranking keys and deterministic tie behavior; preserve filtered base relevance for `relevance` and apply the final cap after filtering, ranking, and de-duplication.
- **Refactor**: Simplify ranking-key construction without changing public semantics, document all changed functions with reStructuredText docstrings, run focused tests, then run the full suite and lint after all feature changes.

### Required Verification Evidence

1. `python3 -m pytest tests/unit/test_youtube_search.py tests/contract/test_youtube_search_contract.py tests/contract/test_layer1_search_contract.py`
2. `python3 -m pytest tests/unit/test_youtube_composed_channels.py tests/contract/test_youtube_composed_channels_contract.py tests/integration/test_youtube_composed_tool_registration.py tests/integration/test_youtube_tool_registration.py`
3. `python3 -m pytest tests/unit/test_method_routing.py`
4. `python3 -m pytest`
5. `python3 -m ruff check .`

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/307-channel-search/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── channels-search-channels-contract.md
└── tasks.md                         # Created later by /speckit.tasks
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/
├── src/mcp_server/
│   ├── integrations/resources/
│   │   ├── search.py                            # Layer 1 search request shape
│   │   └── validators/search.py                 # Search request validation
│   └── tools/
│       ├── dispatcher.py                        # Default concrete tool registration
│       ├── youtube_common/
│       │   ├── channels.py                      # Existing channels_list dependency
│       │   ├── conventions.py                   # Safe error-detail utilities
│       │   ├── playlist_items.py                # Existing playlist_items_list dependency
│       │   └── search.py                        # Layer 2 channelType pass-through and search dependency
│       └── youtube_composed/
│           ├── __init__.py                      # Public composed-tool exports
│           └── channels.py                      # channels_searchChannels behavior
└── tests/
    ├── contract/
    │   ├── test_layer1_search_contract.py
    │   ├── test_youtube_search_contract.py
    │   └── test_youtube_composed_channels_contract.py
    ├── integration/
    │   ├── test_youtube_search_registration.py
    │   ├── test_youtube_composed_tool_registration.py
    │   └── test_youtube_tool_registration.py
    └── unit/
        ├── test_method_routing.py
        ├── test_youtube_search.py
        └── test_youtube_composed_channels.py
```

**Structure Decision**: Extend the existing Layer 1/2 search request path only as needed for `channelType`, then implement the concrete public tool in the existing composed channels-family module. Reuse lower-layer search, channel, and playlist boundaries and the default dispatcher; do not introduce a new service, client, storage layer, or generic cross-family abstraction.

### Post-Design Constitution Check

*Post-Phase 1 gate: PASS.*

- [x] The concrete MCP contract covers schema, discovery metadata, response provenance, composition, boundedness, safe errors, and additive compatibility/rollback posture.
- [x] The plan specifies Red before Green and Refactor after Green for the `channelType` foundation work and P1–P3.
- [x] Unit, contract, integration, and protocol regression coverage are identified, with full-suite and lint commands required before completion.
- [x] New or changed Python functions, including the supporting search-contract change, are required to retain or add reStructuredText docstrings.
- [x] Existing request observability is retained; logs, public metadata, and errors are constrained to safe diagnostic data.
- [x] The selected composition is bounded and uses existing handlers; no unjustified complexity exception is required.

## Complexity Tracking

No constitution exceptions are required.
