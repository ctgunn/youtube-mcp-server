# Implementation Plan: YT-312 Video Statistics

**Branch**: `312-video-statistics` | **Date**: 2026-08-13 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/312-video-statistics/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/312-video-statistics/spec.md`

## Summary

Deliver `videos_getStatistics`, an additive MCP tool that returns normalized public counts for exactly one YouTube video. It will adapt one existing `videos_list` direct lookup using only the `statistics` source group, preserve source-provided non-negative decimal counts (including zero), represent absent expected metrics explicitly without inventing values, and translate lower-layer errors to safe Layer 3 outcomes. It adds no storage, new source client, transport behavior, pagination, enrichment, derived analytics, or new authentication flow.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing MCP tool registry and dispatcher; `src/mcp_server/tools/youtube_composed/` conventions; existing `videos_list` handler; Python standard-library JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A; request validation and result normalization are in-memory only  
**Testing**: Targeted pytest unit, contract, integration, and protocol-routing tests; final `PYTHONPATH=src python3 -m pytest`; final `PYTHONPATH=src python3 -m ruff check .`  
**Documentation Style**: reStructuredText docstrings for every new or changed Python function; feature-local Markdown contract documentation  
**Target Platform**: Local macOS/Linux development and the existing hosted Linux MCP service runtime  
**Project Type**: Python MCP service  
**Performance Goals**: At least 95% of representative valid requests produce a structured outcome within 3 seconds; each request makes exactly one bounded lower-layer video lookup  
**Constraints**: Preserve the public name `videos_getStatistics`; accept only `videoId`; request only `statistics`; return view, like, comment, and favorite counts when source-provided; retain a reported zero; represent absent expected counts as unavailable with no numeric value; exclude dislike counts, derived analytics, secrets, owner context, raw source payloads, stack traces, signed links, and media data; do not add dependencies, persistence, pagination, ranking, scraping, transport changes, or dispatcher rewrites  
**Scale/Scope**: One concrete videos-family tool, one existing lower-layer dependency, one direct lookup, four expected metric states plus safe failure handling, and focused unit, contract, integration, and protocol regression coverage

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

- The feature-local contract defines the external MCP input, the one-read normalized result, expected metrics, availability states, provenance, safe errors, additive compatibility, and rollback before implementation.
- Every phase and user-story plan below requires Red before Green and Refactor after Green. Completion requires `PYTHONPATH=src python3 -m pytest` and `PYTHONPATH=src python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Every new or changed Python function—including validators, count normalizers, error mappers, descriptor builders, default test fixtures, and test doubles—must have a reStructuredText docstring covering purpose, inputs, outputs, raised errors where relevant, and side effects where relevant.
- The design reuses configured runtime dependencies, request correlation, lower-layer observability, dependency injection, and centralized safe-detail sanitization. It adds no storage, source client, transport, authentication flow, crawler, or generalized analytics component.

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/312-video-statistics/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── videos-get-statistics-contract.md
└── tasks.md                         # Created later by /speckit.tasks
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/
├── tools/
│   ├── dispatcher.py                # Default composed-tool registration and dependency injection
│   ├── youtube_common/
│   │   └── videos.py                # Existing lower-level videos_list handler and default fixture
│   └── youtube_composed/
│       ├── __init__.py              # Public composed-tool exports
│       └── videos.py                # Video-statistics descriptor, validation, mapping, and errors
└── protocol/
    └── methods.py                   # Existing public error-category serialization regression coverage only

/Users/ctgunn/Projects/youtube-mcp-server/tests/
├── unit/
│   ├── test_youtube_composed_videos.py
│   └── test_method_routing.py
├── contract/
│   └── test_youtube_composed_videos_contract.py
└── integration/
    ├── test_youtube_composed_tool_registration.py
    └── test_youtube_tool_registration.py
```

**Structure Decision**: Extend the existing `youtube_composed` videos family. Its new descriptor and handler will adapt the existing lower-level `videos_list` handler rather than duplicate source request execution or expose the near-raw collection envelope. Export and default-register it through established package and dispatcher seams. Keep metric normalization and error translation local to the videos family unless later concrete video tools establish a shared helper need.

## Phase 0: Research and Open Questions

### Research Focus

- Confirm the reserved public catalog name, videos-family ownership, executable descriptor pattern, exports, and default registration seam.
- Resolve the direct-identifier lower-layer request, supported source statistics fields, count representation, zero versus missing semantics, public-read access, quota, and unavailable lookup behavior.
- Confirm result normalization, field provenance, disliked-count exclusion, sanitization, observability reuse, docstrings, test seams, and verification commands.

### Phase 0 Decisions

All research questions are resolved in [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/312-video-statistics/research.md). No `NEEDS CLARIFICATION` items remain.

### Phase 0 Red-Green-Refactor

- **Red**: Record catalog placement, source request, expected metric behavior, source-count representation, missingness, error, registration, and documentation uncertainties as explicit research questions.
- **Green**: Resolve every question with a decision, rationale, and rejected alternatives in `research.md`.
- **Refactor**: Retain only decisions that shape the public contract or focused implementation; do not copy source HTTP or credential internals into public artifacts.

## Phase 1: Design and Contracts

### Design Goals

- Define the exact request, normalized statistics result, per-metric availability state, provenance context, and safe outcome entities.
- Make reported zero, absent metric behavior, count representation, favorite-count caveat, and dislike-count exclusion explicit.
- Define one independently testable MCP contract using exactly one direct lookup with `statistics` and no pagination, fan-out, enrichment, or derived analytics.
- Keep the change additive: one concrete videos-family tool, no persistence, source client, transport, ranking, or analytics component.

### Design Artifacts

- [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/312-video-statistics/data-model.md)
- [videos-get-statistics-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/312-video-statistics/contracts/videos-get-statistics-contract.md)
- [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/312-video-statistics/quickstart.md)

### Phase 1 Red-Green-Refactor

- **Red**: Identify every rule that needs tests for input validation, exact lower-layer request, source count preservation, zero, absent expected metrics, unavailable video, safe errors, discovery metadata, and default registration.
- **Green**: Produce the data model, contract, and quickstart with concrete schema, metric mapping, state transitions, provenance, source caveats, test evidence, and rollback expectations.
- **Refactor**: Reconcile metric names, availability states, provenance categories, error categories, and caller guidance across artifacts; ensure every specification requirement traces to a contract clause and focused test.

## Phase 2: Implementation Strategy

### Shared Foundation - Descriptor Exposure, Registration, and Safe Delivery

- **Red**: Add failing contract, registration, and protocol tests for concrete `videos_getStatistics` discovery, schema, no representative-only marker, injected lower-layer dependency, safe serialized categories, and default dispatcher presence.
- **Green**: Add the smallest videos-family error class, public schema, descriptor export, default registration, and safe category translation required to deliver the concrete tool through the existing dispatcher. Update the lower-level default representative fixture only if required for default-registry successful invocation coverage.
- **Refactor**: Keep registration adjacent to `videos_getVideo`, reuse centralized sanitization and request context, ensure all new or changed Python functions have reStructuredText docstrings, and rerun focused registration and routing checks.

### User Story 1 - Retrieve Available Video Statistics (P1)

- **Red**: Add failing unit and contract tests for required trimmed `videoId`, unknown-field rejection, one `videos_list` request with `part=statistics`, all four expected metric mappings, source decimal-count preservation, source value zero, provenance, and successful normalized result shaping.
- **Green**: Add only the validator, one direct-identifier lookup adapter, metric normalizer, stable result fields, provenance metadata, and handler behavior needed for successful retrieval.
- **Refactor**: Centralize local safe metric extraction within the videos family, preserve source representation without numeric coercion or fabricated fields, retain reStructuredText docstrings, and rerun focused unit and contract checks.

### User Story 2 - Understand Hidden or Unavailable Counts (P2)

- **Red**: Add failing unit and contract tests for one or more absent expected source fields, an entirely absent source statistics object, a reported zero, no numeric `value` for unavailable metrics, favorite-count caveat, and absence of `dislikeCount` in both results and discovery metadata.
- **Green**: Add only explicit availability-state shaping and caller metadata needed to distinguish `available` reported counts from `unavailable` counts without revealing a speculative reason or deriving substitute values.
- **Refactor**: Consolidate the expected-metric list and availability construction in one local videos-family seam, verify metadata and result wording agree, retain reStructuredText docstrings, and rerun focused contract and integration checks.

### User Story 3 - Receive Actionable Lookup Outcomes (P3)

- **Red**: Add failing tests for non-object, missing, blank, non-text, and unknown input; empty lookup results; malformed source items; lower unavailable, authorization, quota, and source failures; and protocol serialization without unsafe details.
- **Green**: Map empty source collections and lower not-found or removed outcomes to generic `unavailable_resource`; map lower invalid, authorization, quota, and other failures to the documented safe categories without exposing sensitive detail.
- **Refactor**: Keep lower-layer error translation local and sanitized, remove duplication with existing safe-error utilities, verify all modified Python functions retain reStructuredText docstrings, then rerun focused integration and protocol checks.

### Regression Strategy

- Preserve existing public tools, the shared Layer 3 catalog, `videos_getVideo`, `videos_searchVideos`, `videos_list`, and lower-layer integration contracts.
- Add focused coverage at `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_videos.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_videos_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_method_routing.py`.
- Run focused checks during implementation:

  ```bash
  PYTHONPATH=src python3 -m pytest \
    tests/unit/test_youtube_composed_videos.py \
    tests/contract/test_youtube_composed_videos_contract.py \
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

- Keep the public tool additive. If a regression is found before release, remove only its default dispatcher registration and composed-package exports; the lower-level video lookup remains unchanged.
- Preserve lower-layer result and error contracts by adapting them at the new public boundary rather than modifying their request execution or source mapping.
- Mitigate incorrect or sensitive output through pre-lookup validation, a fixed one-read bound, count preservation, explicit availability and provenance context, documented source caveats, and existing safe-detail sanitization.
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

- The feature contract covers additive compatibility, one required input, one-read normalized retrieval, expected metric mapping, source-count preservation, zero versus unavailable states, source caveats, safe errors, discovery, and rollback.
- Each shared-foundation and user-story phase specifies Red before Green and Refactor after Green, along with unit, contract, integration, protocol, and final full-suite verification.
- The selected design reuses the configured lower-level video capability, safe category serialization, request context, and dispatcher registration. It introduces no new storage, source client, transport behavior, or analytics machinery.
- Every planned Python function change is subject to the constitution's reStructuredText docstring requirement; safe public diagnostic data and existing observability are preserved.

## Complexity Tracking

No constitution violations or complexity exceptions require justification.
