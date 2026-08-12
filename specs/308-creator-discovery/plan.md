# Implementation Plan: Creator Discovery

**Branch**: `308-creator-discovery` | **Date**: 2026-08-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/308-creator-discovery/spec.md`

## Summary

Deliver `channels_findCreators`, an additive Layer 3 MCP tool that discovers distinct public channel candidates from topic-matching videos. The tool will compose existing lower-level video search, channel lookup, and conditional uploads-playlist handlers; preserve earliest matched-video position; optionally enrich/filter/rank candidates; return bounded matching-video samples; and safely disclose provenance, partial enrichment, and error outcomes.

## Technical Context

**Language/Version**: Python 3.11

**Primary Dependencies**: Existing FastAPI/Pydantic/Uvicorn service runtime; in-repository MCP dispatcher; Layer 2 `search_list`, `channels_list`, and `playlist_items_list` handlers; Layer 3 composed-tool conventions; Python standard-library date/time utilities

**Storage**: N/A; request, matched-video, candidate, enrichment, sample, and ranking state exist only for one invocation

**Testing**: pytest for unit, contract, integration, and protocol regression coverage; Ruff for linting

**Documentation Style**: reStructuredText docstrings for every new or changed Python function, including purpose, `:param:`, `:return:`, `:raises:` when relevant, and side effects when relevant

**Target Platform**: Linux-hosted Cloud Run service and supported local development runtime

**Project Type**: MCP-enabled web service

**Performance Goals**: Under normal public-source availability, at least 95% of representative creator-discovery requests return a complete, safely partial, or empty structured result within 5 seconds

**Constraints**: Strict public schema; final result limit of 1–50 (default 10); base video retrieval and distinct-channel enrichment bounded to 50 candidates; per-channel samples bounded to 0–10 (default 0); public metadata, errors, and logs must not expose credentials, tokens, stack traces, raw request/response bodies, or private owner data; all new/changed Python functions require reStructuredText docstrings

**Scale/Scope**: One new public Layer 3 tool, composed-channel package exports, dispatcher registration, and focused unit/contract/integration/protocol regression coverage; no new persistence, upstream client, or endpoint wrapper

## Constitution Check

*Pre-Phase 0 gate: PASS.*

- [x] Contracts are defined for all external/MCP-facing behavior changes in [contracts/channels-find-creators-contract.md](./contracts/channels-find-creators-contract.md).
- [x] The phase plan includes explicit Red-Green-Refactor steps for shared foundation work and all three user stories.
- [x] Each Red step defines failing tests before implementation work begins.
- [x] Each Green step limits code to the minimum needed to pass the corresponding tests.
- [x] Each Refactor step includes cleanup plus a full repository test-suite re-run.
- [x] Unit, contract, integration, and protocol regression coverage are documented.
- [x] The completion command is `python3 -m pytest`; lint evidence is `python3 -m ruff check .`.
- [x] Every new or changed Python function is required to have a reStructuredText docstring.
- [x] Observability, security, and simplicity constraints are addressed below.

### Constitution-Driven Design Controls

- **Contract-first**: Publish the concrete input schema, response shape, provenance, composition boundary, sample semantics, safe errors, and additive compatibility posture before registration.
- **Determinism**: Normalize inputs; retain each channel's earliest matching-video position; retain per-channel matching-video order; filter before ranking; preserve base position for all ties; then apply the final result cap.
- **Observability**: Reuse the existing dispatcher and lower-layer request lifecycle so tool-name request metrics and safe lower-layer operation/latency events continue to be produced. Do not add logging of query values, candidate payloads, samples, or credentials.
- **Security**: Reuse safe lower-layer error mapping and detail sanitization. Public discovery metadata must remain safe. The workflow requests public data only and never requests or returns owner-scoped context.
- **Simplicity and boundedness**: Extend the existing composed channels-family module and reuse injected handlers. Retrieve at most 50 base videos, enrich at most 50 distinct channels in one batch when needed, read at most one public uploads-playlist item per enriched candidate only for an active activity rule, and include at most 10 samples per final candidate. Do not add persistence, a direct client, or a generic cross-family abstraction.
- **Rollback/mitigation**: This is an additive tool with no existing schema or result changes. If it must be withdrawn, remove only its default descriptor registration and preserve all existing tools; no client migration is required.

## Research Decisions

All Phase 0 questions are resolved in [research.md](./research.md). The selected design calls `search_list` directly with `type=video`, deliberately retrieves a bounded 50-video candidate set separately from the final channel cap, groups candidates by public channel identifier, and reuses the existing public-only enrichment, ranking, safe-error, and creator-classification behavior.

## Phase Plan and Red-Green-Refactor Strategy

### Phase 0 - Research and Contract Decisions (complete)

- **Red**: Identify contract, candidate-window, sample-ordering, lower-layer composition, enrichment, ranking, error-serialization, boundedness, security, and test-command questions.
- **Green**: Record the selected 50-video candidate bound, per-channel sample bound, direct lower-layer composition, conservative creator heuristic, partial-result policy, safe error translation, and public contract in `research.md` and the contract artifact.
- **Refactor**: Remove all unresolved markers, align terminology with YT-301/YT-303/YT-307 and existing channels-family behavior, and re-check the pre-design constitution gate.

### Phase 1 - Design and Contract Artifacts (complete)

- **Red**: Derive missing entities, relationships, input validation, response provenance, sample selection, failure states, compatibility posture, and verification flows from the specification and existing contracts.
- **Green**: Publish the data model, MCP contract, and quickstart verification path; update the Codex agent context with the current composed-tool technology context.
- **Refactor**: Reconcile duplicated validation, composition, ranking, sampling, and partial-result rules across design artifacts; keep the contract concrete rather than representative-only; perform the post-design constitution check.

### Phase 2 - Implementation Planning (for `/speckit.tasks`; no tasks created here)

#### Shared Foundation - Creator-Discovery Contract Surface

- **Red**: Add failing contract tests for the exact schema, defaults, bounds, public metadata, composition boundary, lower-layer dependencies, provenance, heuristic disclosure, continuation caveat, safe error categories, and absence of representative-only or unsafe metadata.
- **Green**: Add only the constants, public schema, safe error type, metadata builder, package exports, and default dispatcher registration required for the executable tool contract.
- **Refactor**: Keep public contract construction in the existing channels family; add or preserve reStructuredText docstrings on every changed Python function and run focused contract/registration tests.

#### User Story 1 - Discover Creators from Relevant Videos (P1)

- **Red**: Add failing unit and integration tests for query trimming, allowed fields, default/bounded `maxResults`, base-video `order` and publication windows, a `type=video` base request bounded at 50, matched-video normalization, distinct-channel grouping, earliest-position stability, empty success, base-only continuation disclosure, and safe base-search failure translation.
- **Green**: Add the validator, base-video request adapter, matched-video normalizer, candidate-grouping helper, result shaper, handler, descriptor, export, and registration required to return distinct public channel candidates from `search_list`.
- **Refactor**: Reuse existing timestamp parsing, source-field copying, provenance, and safe error mapping where their semantics match. Keep creator-discovery-only helpers local to the channels family unless a second concrete consumer proves a shared abstraction is justified; update reStructuredText docstrings and run focused unit/contract/integration tests.

#### User Story 2 - Refine Creators by Audience and Activity (P2)

- **Red**: Add failing unit and integration tests for one batched public channel lookup, inclusive subscriber and latest-upload filters, `creatorOnly`, hidden or unavailable metadata, partial-enrichment disclosure, and all-candidates-unavailable required enrichment.
- **Green**: Invoke `channels_list` only when an active rule needs channel metadata, derive latest public upload activity only for an activity filter or `recent_activity`, reuse the conservative channel-family creator classifier, exclude only candidates that cannot satisfy an active data-dependent rule, and shape safe aggregate partial-enrichment information.
- **Refactor**: Preserve bounded fan-out, field provenance, safe error sanitization, and reStructuredText docstrings. Extract a reusable helper only after a second concrete tool needs the exact same semantics; rerun focused coverage.

#### User Story 3 - Prioritize and Inspect Creator Candidates (P3)

- **Red**: Add failing unit tests for all five `sortBy` modes, filters-before-ranking, earliest-base-position ties, unknown-metadata exclusion for metadata-dependent ranks, final result truncation, sample limit zero, positive per-channel sample caps, and base-order samples after final filtering/ranking.
- **Green**: Implement only the documented ranking keys, deterministic tie behavior, and sample selection from the grouped base videos. Preserve filtered base-video relevance for `relevance`, apply samples only to final candidates, and apply the final cap after filtering and ranking.
- **Refactor**: Simplify ranking and sample-selection helpers without changing public semantics, document all changed functions with reStructuredText docstrings, run focused tests, then run the full suite and lint after all feature changes.

### Required Verification Evidence

1. `python3 -m pytest tests/unit/test_youtube_composed_channels.py tests/contract/test_youtube_composed_channels_contract.py tests/integration/test_youtube_composed_tool_registration.py tests/integration/test_youtube_tool_registration.py`
2. `python3 -m pytest tests/unit/test_method_routing.py`
3. `python3 -m pytest`
4. `python3 -m ruff check .`

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/308-creator-discovery/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── channels-find-creators-contract.md
└── tasks.md                         # Created later by /speckit.tasks
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/
├── src/mcp_server/tools/
│   ├── dispatcher.py                        # Default concrete tool registration
│   ├── youtube_common/
│   │   ├── channels.py                      # Existing channels_list dependency
│   │   ├── conventions.py                   # Safe error-detail utilities
│   │   ├── playlist_items.py                # Existing playlist_items_list dependency
│   │   └── search.py                        # Existing search_list dependency
│   └── youtube_composed/
│       ├── __init__.py                      # Public composed-tool exports
│       └── channels.py                      # channels_findCreators behavior
└── tests/
    ├── contract/
    │   └── test_youtube_composed_channels_contract.py
    ├── integration/
    │   ├── test_youtube_composed_tool_registration.py
    │   └── test_youtube_tool_registration.py
    └── unit/
        ├── test_method_routing.py
        └── test_youtube_composed_channels.py
```

**Structure Decision**: Implement the concrete public tool in the existing composed channels-family module, then expose and register it through existing package and dispatcher boundaries. Reuse lower-layer search, channel, and playlist handlers; do not add a service, client, storage layer, or generic cross-family abstraction.

### Post-Design Constitution Check

*Post-Phase 1 gate: PASS.*

- [x] The concrete MCP contract covers schema, discovery metadata, response provenance, composition, boundedness, sampling, safe errors, and additive compatibility/rollback posture.
- [x] The plan specifies Red before Green and Refactor after Green for contract work and P1–P3.
- [x] Unit, contract, integration, and protocol regression coverage are identified, with full-suite and lint commands required before completion.
- [x] New or changed Python functions are required to retain or add reStructuredText docstrings.
- [x] Existing request observability is retained; logs, public metadata, and errors are constrained to safe diagnostic data.
- [x] The selected composition is bounded and uses existing handlers; no unjustified complexity exception is required.

## Complexity Tracking

No constitution exceptions are required.
