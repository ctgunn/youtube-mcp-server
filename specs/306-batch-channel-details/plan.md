# Implementation Plan: Batch Channel Details

**Branch**: `306-batch-channel-details` | **Date**: 2026-08-11 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/306-batch-channel-details/spec.md`

## Summary

Add the public Layer 3 `channels_getChannels` MCP tool. It validates a batch of 1–50 distinct channel IDs, uses one bounded channel lookup for the batch, restores caller order, and returns a normalized single-channel-compatible result or a safe outcome for every requested ID. It supports public response-detail selection and latest-upload enrichment that defaults to enabled, with at most one enrichment lookup per available channel. The design reuses the existing composed channels family, common single-channel normalization helpers, dispatcher registration, safe errors, and contract conventions.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: FastAPI, Pydantic v2, Uvicorn, existing in-repository MCP dispatcher, Layer 2 channel and playlist-item tool handlers, and Python standard-library dataclasses/JSON utilities  
**Storage**: N/A; request, normalization, and enrichment state exist only for the invocation  
**Testing**: pytest; focused unit, contract, and integration tests, followed by `python3 -m pytest` and `python3 -m ruff check .`  
**Documentation Style**: reStructuredText docstrings on every new or changed Python function, documenting purpose, `:param:`, `:return:`, `:raises:` where applicable, and relevant safe side effects/failure behavior  
**Target Platform**: Hosted Linux web service and local development runtime  
**Project Type**: MCP web service  
**Performance Goals**: At least 95% of representative batches of up to 50 IDs return complete or safely partial results within 15 seconds under normal source availability  
**Constraints**: One core channel-collection lookup per request; no more than one one-item latest-upload lookup per available channel; preserve request order; use public data only; never expose credentials, private owner context, stack traces, raw source payloads, signed links, or non-public contacts  
**Scale/Scope**: One additive public tool; 1–50 distinct IDs per invocation; no persistence, pagination, search, ranking, crawling, or change to existing Layer 1/Layer 2 contracts

## Constitution Check

*GATE: Passed before Phase 0 research and re-checked after Phase 1 design.*

- [x] Contracts are defined in `contracts/channels-get-channels-contract.md` for all MCP-facing behavior changes; the tool is additive and has a removal-only rollback path.
- [x] The plan specifies Red-Green-Refactor work for validation, bulk composition, enrichment, registration, and all three user stories.
- [x] Red work adds failing unit, contract, and integration tests before handler, descriptor, export, or registration changes.
- [x] Green work is limited to the composed channels family, its package export, and dispatcher registration needed to pass those tests.
- [x] Refactor consolidates shared single- and batch-channel helpers, keeps the public shape stable, and re-runs the full repository suite.
- [x] The coverage plan includes contract boundaries, injected dependency execution, discovery/registration, ordering, mixed outcomes, and regression coverage for YT-305.
- [x] Completion requires successful `python3 -m pytest` after final code changes; `python3 -m ruff check .` is also required.
- [x] All added or modified Python functions require reStructuredText docstrings with inputs, outputs, errors, and safe side effects documented.
- [x] The contract defines sanitized errors and partial results; implementation adds actionable structured failure context without secrets and uses the simplest existing composed-tool architecture.

## Implementation Phases

### Phase 0 — Research (complete)

- Confirm the single-channel result, provenance, heuristic, enrichment, and safe-error rules that batch items must preserve.
- Confirm that `channels_list` accepts a bounded comma-separated identifier collection and that its result order is not a safe public ordering guarantee.
- Confirm the existing bulk lookup pattern, dependency injection, test locations, registration boundary, and docstring conventions.
- Resolve response-detail selections as `snippet` and `contentDetails`, with `snippet` as the default. Internal retrieval still obtains data necessary for normalization and optional enrichment; unselected source-detail groups are not exposed or inferred.

### Phase 1 — Design and Contracts (complete)

- Define a public contract for request validation, response detail selection, ordered per-item outcomes, summary-count semantics, provenance, bounded enrichment, compatibility, security, and rollback.
- Define the batch request/result, item outcome, selected details, normalized metadata, enrichment, and state transitions in the data model.
- Define runnable request/response examples and verification commands in the quickstart.
- Update agent context with the new composed-tool technology and test surface only.

### Phase 2 — Implementation Planning (for `/speckit.tasks`)

1. **Shared foundation and P1 — Red**: Add failing unit tests for 1–50 trimmed unique `channelIds`, unknown fields, default detail selection, one bulk core lookup, item ordering, missing-ID unavailable items, normalized item compatibility, and summary counts. Add contract tests for schema and discovery metadata, and registration/invocation integration tests.
2. **Shared foundation and P1 — Green**: Add the `channels_getChannels` descriptor and handler in `src/mcp_server/tools/youtube_composed/channels.py`. Validate public arguments, make one bulk `channels_list` call, index its results by canonical ID, rebuild items in caller order, reuse/refactor common single-channel normalization safely, create summary counts, then export and register the additive descriptor.
3. **P2 — Red**: Add failing tests for accepted `parts`, omitted/default selection, selected-group omission, default `includeLatestUpload=true`, disabled enrichment with zero playlist-item calls, complete enrichment, no-upload unavailable enrichment, and field provenance restricted to returned paths.
4. **P2 — Green**: Implement detail-selection shaping, always retain identity/outcome/provenance, and perform at most one `playlist_items_list` request with one result for each available item only when enrichment is enabled.
5. **P3 — Red**: Add failing tests for an unavailable ID among successes, a per-item partial enrichment failure, a core request-wide authorization/quota/upstream failure, sanitized outcomes, and summary-count partitioning.
6. **P3 — Green**: Implement safe per-item unavailable and partial outcomes; retain request-wide errors only when the single bulk core dependency fails before any item can be resolved.
7. **Refactor and regression**: Extract only clearly shared helper behavior without changing YT-305 results; give every changed/new Python function a complete reStructuredText docstring; run focused tests, `python3 -m pytest`, and `python3 -m ruff check .`. A failing full suite blocks completion.

## Project Structure

### Documentation (this feature)

```text
specs/306-batch-channel-details/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── channels-get-channels-contract.md
└── tasks.md                         # Created later by /speckit.tasks
```

### Source Code (repository root)

```text
src/mcp_server/tools/
├── dispatcher.py                    # Default public tool registration
└── youtube_composed/
    ├── __init__.py                  # Public composed-tool exports
    └── channels.py                  # YT-305 shared helpers and YT-306 descriptor/handler

tests/
├── unit/test_youtube_composed_channels.py
├── contract/test_youtube_composed_channels_contract.py
├── integration/test_youtube_composed_tool_registration.py
└── integration/test_youtube_tool_registration.py
```

**Structure Decision**: Extend the existing composed `channels` family rather than introduce a service, data store, or new package. This keeps public batch normalization above Layer 2, preserves existing dependency injection and registration behavior, and makes YT-305 compatibility directly testable.
