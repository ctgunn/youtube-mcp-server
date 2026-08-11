# Implementation Plan: Video Search with Channel Refinement

**Branch**: `[303-videos-search]` | **Date**: 2026-08-10 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/303-videos-search/spec.md`

## Summary

Deliver `videos_searchVideos`, a concrete Layer 3 MCP tool that searches public videos and conditionally enriches candidates with public channel data before applying channel-oriented filters, ranking, and optional one-result-per-channel selection. The tool will compose the existing Layer 2 `search_list`, `channels_list`, and conditional `playlist_items_list` handlers, preserve the existing video-family descriptor and registration pattern, expose a non-representative discovery contract, and map all failures to safe MCP outcomes.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: Existing FastAPI/Pydantic/Uvicorn runtime; in-repository MCP dispatcher, Layer 2 `search_list`, `channels_list`, and `playlist_items_list` handlers, Layer 3 contract conventions, and Python standard library date/time utilities
**Storage**: N/A; request, candidate, enrichment, and ranking state are in-memory for one invocation
**Testing**: pytest for unit, contract, integration, and protocol regression coverage; Ruff for linting
**Documentation Style**: reStructuredText docstrings for every new or changed Python function, including purpose, `:param:`, `:return:`, `:raises:` when relevant, and side effects when relevant
**Target Platform**: Linux-hosted Cloud Run service and supported local development runtime
**Project Type**: MCP-enabled web service
**Performance Goals**: Under normal upstream availability, at least 95% of representative searches return a structured result or safe structured error within 5 seconds
**Constraints**: Public input is limited to the specified schema; final results are bounded to 1–50 (default 10); enrichment fan-out is bounded by distinct base-result channels (at most 50); public metadata, errors, and logs must not expose credentials, tokens, stack traces, or raw request bodies; all new/changed Python functions require reStructuredText docstrings
**Scale/Scope**: One new public Layer 3 tool; extends the existing videos family, package exports, dispatcher registration, protocol error-category mapping, and focused unit/contract/integration/protocol tests

## Constitution Check

*Pre-Phase 0 gate: PASS.*

- [x] Contracts are defined for all external/MCP-facing behavior changes in [contracts/videos-search-videos.md](./contracts/videos-search-videos.md).
- [x] The phase plan includes explicit Red-Green-Refactor steps for shared foundation work and all three user stories.
- [x] Each Red step defines failing tests before implementation work begins.
- [x] Each Green step limits code to the minimum needed to pass the corresponding tests.
- [x] Each Refactor step includes cleanup plus a full repository test-suite re-run.
- [x] Unit, contract, integration, and protocol regression coverage are documented.
- [x] The completion command is `python3 -m pytest`; lint evidence is `ruff check .`.
- [x] Every new or changed Python function is required to have a reStructuredText docstring.
- [x] Observability, security, boundedness, and simplest-architecture constraints are addressed below.

### Constitution-Driven Design Controls

- **Contract-first**: Publish the concrete input schema, response shape, provenance, composition boundary, errors, and migration posture before registration.
- **Determinism**: Normalize inputs, validate cross-field constraints in the handler, filter before ranking, preserve base-search position for all ties, de-duplicate only after ranking, then apply the final result cap.
- **Observability**: Reuse the existing dispatcher and Layer 1/Layer 2 request lifecycle so tool-name request metrics and safe lower-layer operation/latency events continue to be produced. Do not add request-value logging.
- **Security**: Reuse safe lower-layer error mapping and detail sanitization; metadata must pass the public-metadata safety validation. Public search uses configured API-key capability only and never returns credential material.
- **Simplicity and boundedness**: Reuse injected lower-layer handlers rather than introducing a new client or persistence layer. Batch channel metadata lookup by distinct channel ID where supported. Only read each candidate channel's uploads playlist when a latest-upload filter or `recent_activity` ranking requires it.
- **Rollback/mitigation**: This is an additive tool and additive error-category mapping. If production behavior must be withdrawn, remove the descriptor from default registration while leaving existing Layer 2 tools unaffected; no caller migration is required because no existing public tool contract changes.

## Research Decisions

All Phase 0 questions are resolved in [research.md](./research.md). In particular, latest public upload activity uses a bounded read of each enriched channel's public uploads playlist only when needed; it is disclosed as derived public activity rather than a field returned by `channels.list`.

## Phase Plan and Red-Green-Refactor Strategy

### Phase 0 - Research and Contract Decisions (complete)

- **Red**: Identify contract, lower-layer composition, latest-upload, heuristic, error-serialization, boundedness, security, and test-command gaps.
- **Green**: Record the selected composition, conservative creator-classification behavior, partial-result policy, safe error translation, and contract shape in `research.md` and the public contract artifact.
- **Refactor**: Remove unresolved markers, align terminology with YT-301/302 and the feature specification, and re-check the pre-design constitution gate.

### Phase 1 - Design and Contract Artifacts (complete)

- **Red**: Derive missing entities, relationships, input validation, response provenance, failure states, and verification flows from the specification.
- **Green**: Publish the data model, MCP contract, and quickstart verification path; update the agent context with the existing composed-tool and contract technology context.
- **Refactor**: Reconcile duplicated rule descriptions across the design artifacts, ensure the contract does not rely on representative-only metadata, and perform the post-design constitution check.

### Phase 2 - Implementation Planning (for `/speckit.tasks`; no tasks created here)

#### Shared Foundation - Safe Layer 3 Error Delivery

- **Red**: Add protocol-level failing tests proving each public Layer 3 error category used by this tool serializes to a numeric MCP error response with stable `error.data.category`, rather than raising an unmapped-category failure.
- **Green**: Add only the additive category mappings and safe message/detail handling needed by `invalid_parameters`, `unavailable_resource`, `authorization_sensitive_data`, `quota_exhaustion`, `upstream_failure`, `partial_enrichment_failure`, and `unsupported_filter_or_sort`.
- **Refactor**: Consolidate category mapping without changing existing Layer 2 outcomes; update reStructuredText docstrings for changed Python functions; run affected protocol tests.

#### User Story 1 - Search for Relevant Videos (P1)

- **Red**: Add failing unit tests for query trimming, allowed fields, default/bounded `maxResults`, order/date/channel validation, date-window ordering, base video-search argument mapping, candidate normalization, empty success, continuation data, and safe base-search error translation. Add contract and registration tests for the executable descriptor.
- **Green**: Add the concrete schema, error type, validator, base-search adapter, result normalizer, metadata builder, handler, package export, and dispatcher registration required to return normalized video results from `search_list` with `type=video`.
- **Refactor**: Keep common video normalization helpers local to the videos family unless another concrete tool demonstrably needs them; add or preserve reStructuredText docstrings; run focused unit/contract/integration tests.

#### User Story 2 - Find Videos from Suitable Channels (P2)

- **Red**: Add failing unit and integration tests for batched channel lookup, subscriber-range and latest-upload-window filters, `creatorOnly`, missing/hidden channel data, partial-enrichment disclosure, all-unavailable enrichment, and one-result-per-channel behavior after ranking.
- **Green**: Inject and call `channels_list` only when a requested rule needs channel data, derive latest public upload activity only for latest-upload rules, classify conservatively from public channel metadata, exclude only candidates that cannot satisfy an active metadata-dependent rule, and shape safe partial-enrichment information.
- **Refactor**: Extract a reusable helper only if its use is already shared with another concrete Layer 3 tool; preserve bounded fan-out, field provenance, safe error sanitization, and reStructuredText docstrings; rerun focused coverage.

#### User Story 3 - Rank Results for a Research Goal (P3)

- **Red**: Add failing unit tests for all five `sortBy` modes, filter-before-rank ordering, stable base-position ties, unknown-metadata exclusion for metadata-dependent ranks, unique-channel selection after ranking, and final result truncation.
- **Green**: Implement only the documented ranking keys and deterministic tie behavior; retain relevance order when requested and use the final candidate cap after filtering, ranking, and de-duplication.
- **Refactor**: Simplify ranking-key construction without changing public semantics, document all changed functions with reStructuredText docstrings, run focused tests, then run `python3 -m pytest` and `ruff check .` after all feature changes.

### Required Verification Evidence

1. `python3 -m pytest tests/unit/test_youtube_composed_videos.py tests/contract/test_youtube_composed_videos_contract.py tests/integration/test_youtube_composed_tool_registration.py tests/integration/test_youtube_tool_registration.py`
2. `python3 -m pytest tests/unit/test_method_routing.py` (or the repository's replacement protocol-routing test if the final location changes)
3. `python3 -m pytest`
4. `ruff check .`

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/303-videos-search/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── videos-search-videos.md
└── tasks.md                         # Created later by /speckit.tasks
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/
├── src/mcp_server/
│   ├── protocol/methods.py                          # Safe MCP error serialization
│   └── tools/
│       ├── dispatcher.py                            # Default concrete tool registration
│       ├── youtube_common/
│       │   ├── channels.py                          # Existing channels_list dependency
│       │   ├── conventions.py                       # Safe error-detail utilities
│       │   ├── playlist_items.py                    # Existing playlist_items_list dependency
│       │   └── search.py                            # Existing search_list dependency
│       └── youtube_composed/
│           ├── __init__.py                          # Public composed-tool exports
│           ├── conventions.py                       # Layer 3 category/provenance conventions
│           └── videos.py                            # Concrete videos_searchVideos behavior
└── tests/
    ├── contract/test_youtube_composed_videos_contract.py
    ├── integration/test_youtube_composed_tool_registration.py
    ├── integration/test_youtube_tool_registration.py
    └── unit/
        ├── test_method_routing.py
        └── test_youtube_composed_videos.py
```

**Structure Decision**: Extend the existing concrete Layer 3 videos-family module and its adjacent tests. Reuse existing lower-layer search/channel boundaries and default dispatcher registration; do not introduce a new service, client, persistence store, or generic cross-family abstraction for this one tool.

### Post-Design Constitution Check

*Post-Phase 1 gate: PASS.*

- [x] The concrete MCP contract covers schema, discovery metadata, response provenance, composition, boundedness, safe errors, and additive migration posture.
- [x] The plan specifies Red before Green and Refactor after Green for foundation work and P1–P3.
- [x] Unit, contract, integration, and protocol regression coverage are identified, with full-suite and lint commands required before completion.
- [x] New or changed Python functions are required to retain or add reStructuredText docstrings.
- [x] Existing request observability is retained; logs/metadata/errors are constrained to safe diagnostic data.
- [x] The selected composition is bounded and uses existing handlers; no unjustified complexity exception is required.
