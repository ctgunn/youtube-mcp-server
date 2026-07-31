# Implementation Plan: YT-302 Video Details

**Branch**: `302-video-details` | **Date**: 2026-07-30 | **Spec**: [/Users/ctgunn/Projects/youtube-mcp-server/specs/302-video-details/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/302-video-details/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/302-video-details/spec.md`

## Summary

Deliver `videos_getVideo`, a public MCP tool that retrieves exactly one video through the existing `videos.list` capability and returns a stable normalized detail object. The tool always provides core metadata, expands only the caller-selected optional groups, and converts unavailable, access, quota, and source failures into safe caller-facing outcomes. It reuses the existing videos family, tool registry, lower-level lookup, and error-sanitization boundaries without adding persistence, endpoints, or fan-out.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing MCP tool registry and dispatcher; `src/mcp_server/tools/youtube_composed/` public-tool conventions; existing `videos_list` descriptor and `videos.list` integration wrapper; Python standard-library dataclasses and JSON-compatible dictionaries; pytest; Ruff  
**Storage**: N/A; request handling and normalization are in-memory only  
**Testing**: Targeted pytest unit, contract, and integration tests; final `python3 -m pytest`; final `python3 -m ruff check .`  
**Documentation Style**: reStructuredText docstrings for every new or changed Python function; feature-local Markdown contract documentation  
**Target Platform**: Local macOS/Linux development and the existing hosted Linux MCP service runtime  
**Project Type**: Python MCP service  
**Performance Goals**: One invocation accepts one video identifier, makes no more than one lower-level video lookup, and returns a bounded single-video result with no enrichment or fan-out  
**Constraints**: Preserve the existing public name `videos_getVideo`; accept only `videoId` and optional `parts`; use the five specified part values; always retrieve default core fields; do not expose lower-level collection envelopes, secrets, headers, tokens, traces, signed links, raw request bodies, or media; do not add dependencies, persistence, transport changes, or broad dispatcher rewrites  
**Scale/Scope**: One concrete video-family tool, five optional detail groups, one lower-level dependency (`videos.list`), four focused test areas, and no changes to other public tool families

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

- The feature-local contract documents the public input, response, provenance, optional-group, metadata, and error behavior before implementation.
- Each user story below is organized as Red, Green, and Refactor work. Final verification is `python3 -m pytest` and `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- Any added or modified Python function, including descriptor builders, validation helpers, normalization helpers, error mappers, and test doubles, must include a reStructuredText docstring covering purpose, inputs, outputs, raised errors where relevant, and side effects where relevant.
- The plan reuses the existing registry, videos lookup, lower-level error sanitization, and request context. It adds structured safe errors at the public boundary and no new logging, persistence, or infrastructure path is required for the bounded single lookup.

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/302-video-details/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── videos-get-video-contract.md
└── tasks.md                         # Created later by /speckit.tasks
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/
├── tools/
│   ├── dispatcher.py                # Default public-tool registration
│   ├── youtube_common/
│   │   └── videos.py                # Existing lower-level videos_list descriptor
│   └── youtube_composed/
│       ├── __init__.py              # Public exports
│       └── videos.py                # Video-detail descriptor, handler, validation, mapping
└── integrations/resources/
    └── videos.py                    # Existing videos.list wrapper dependency

/Users/ctgunn/Projects/youtube-mcp-server/tests/
├── unit/
│   └── test_youtube_composed_videos.py
├── contract/
│   └── test_youtube_composed_videos_contract.py
└── integration/
    ├── test_youtube_composed_tool_registration.py
    └── test_youtube_tool_registration.py
```

**Structure Decision**: Extend the existing `youtube_composed` videos family. Its new concrete descriptor and handler will call the existing `videos_list` capability rather than duplicating request execution or exposing its near-raw collection response. Export and default-register the descriptor through the existing package and dispatcher seams. New paths, symbols, and test names follow the established composed-family convention.

## Phase 0: Research and Open Questions

### Research Focus

- Confirm the existing public-tool family and exact catalog name for single-video details.
- Confirm how the existing `videos_list` lookup obtains one item, validates its lower-level request, and sanitizes failures.
- Resolve default versus optional part selection, normalized field provenance, sparse-data behavior, and unavailable-video translation.
- Confirm descriptor registration, discovery metadata, test locations, docstring requirements, and final validation commands.

### Phase 0 Red-Green-Refactor

- **Red**: Record every potentially ambiguous behavior—default parts, optional part union, source absence, error translation, and registration—as a research question before design.
- **Green**: Resolve every question in [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/302-video-details/research.md) with a decision, rationale, and rejected alternatives.
- **Refactor**: Remove copied lower-level endpoint details and retain only the decisions necessary to implement and test the public video-details contract.

## Phase 1: Design and Contracts

### Design Goals

- Define the exact request and result entities, including all default fields and the five supported optional detail groups.
- Make field provenance and sparse/unavailable values explicit without inventing source values or adding heuristic fields.
- Define a public MCP contract that is independently testable through discovery and invocation.
- Keep the implementation to a single normalized retrieval through `videos.list`; do not introduce enrichment, fan-out, persistence, or a new upstream integration.

### Design Artifacts

- [/Users/ctgunn/Projects/youtube-mcp-server/specs/302-video-details/data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/302-video-details/data-model.md)
- [/Users/ctgunn/Projects/youtube-mcp-server/specs/302-video-details/contracts/videos-get-video-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/302-video-details/contracts/videos-get-video-contract.md)
- [/Users/ctgunn/Projects/youtube-mcp-server/specs/302-video-details/quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/302-video-details/quickstart.md)

### Phase 1 Red-Green-Refactor

- **Red**: Identify any missing rule needed to test the input schema, default result, each part mapping, sparse values, safe error category, or discovery metadata.
- **Green**: Produce the data model, contract, and quickstart with concrete mappings and test evidence expectations.
- **Refactor**: Deduplicate field names and error terminology across the artifacts; verify every requirement traces to a testable contract clause and all new names follow the established composed-family convention.

## Phase 2: Implementation Strategy

### User Story 1 - Retrieve a Video's Core Details (P1)

- **Red**: Add failing unit and contract tests for required `videoId`, rejection of unsupported inputs, a single lower-level call requesting `snippet,contentDetails`, and the normalized default result for one available video.
- **Green**: Add the smallest descriptor, validation, lower-level adapter, and core-field mapper in the existing video family; register its public name through the default dispatcher.
- **Refactor**: Consolidate repeated field extraction and validation helpers, preserve the existing lower-level boundary, add or update reStructuredText docstrings, and run the focused P1 checks.

### User Story 2 - Request Additional Detail Groups (P2)

- **Red**: Add failing tests for every allowed `parts` value, empty selection, duplicate/unsupported/wrongly typed selections, union of requested parts with core parts, and exact optional-field mappings.
- **Green**: Add only the optional-part validator, part union, and conditional group mapper needed to make the requested field groups available with the default result.
- **Refactor**: Centralize the part-to-field mapping, retain source values without fabrication, confirm unrequested optional groups are absent, and rerun focused unit and contract checks.

### User Story 3 - Understand Unavailable and Failed Lookups (P3)

- **Red**: Add failing tests showing that an empty lower-level result and not-found/removed result become one `unavailable_resource` outcome, while access, quota, and other source failures become their distinct safe categories with unsafe details removed.
- **Green**: Add the minimum error translation and safe-detail propagation needed for the documented categories; do not expose the lower-level collection envelope or distinguish private, deleted, restricted, and not-found videos.
- **Refactor**: Reuse existing sanitization logic where possible, remove duplicated error handling, confirm every changed Python function has a reStructuredText docstring, and rerun focused integration checks.

### Regression Strategy

- Preserve all existing public tools, the existing `videos_list` behavior, lower-level `videos.list` wrapper semantics, and the shared catalog validation rules.
- Add focused tests at `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_composed_videos.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_youtube_composed_videos_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_composed_tool_registration.py`, and `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_youtube_tool_registration.py`.
- Run focused checks before final validation:

  ```bash
  python3 -m pytest tests/unit/test_youtube_composed_videos.py tests/contract/test_youtube_composed_videos_contract.py tests/integration/test_youtube_composed_tool_registration.py tests/integration/test_youtube_tool_registration.py
  ```

- After the final code change, require:

  ```bash
  python3 -m pytest
  python3 -m ruff check .
  ```

### Rollback and Mitigation

- Keep the public tool additive. If a regression is found before release, remove only its default dispatcher registration and exports; existing lower-level video tools remain unchanged.
- Preserve the lower-level result and error contracts by adapting them at the new public boundary rather than modifying them.
- Mitigate incorrect or sensitive responses through pre-lookup validation, a fixed single-item result shape, explicit unavailable handling, and existing safe-detail sanitization.
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

- The feature contract is complete and directly maps every input, output group, error category, and metadata disclosure to tests.
- The plan uses one existing lower-level dependency and one existing registration seam; no constitution exception or additional architecture is required.
- Every phase and user story has an explicit Red-Green-Refactor sequence, including focused and full-suite verification.
- The documented safe error mapping, bounded result, existing request context, and no-persistence scope satisfy observability, security, and simplicity requirements.

## Complexity Tracking

No constitution violations or complexity exceptions require justification.
