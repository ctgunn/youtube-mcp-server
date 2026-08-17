# Implementation Plan: Search Playlist Items

**Branch**: `[319-playlist-item-search]` | **Date**: 2026-08-17 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/319-playlist-item-search/spec.md`

## Summary

Add the public higher-level MCP tool `playlists_searchItems`. It validates a playlist identifier and literal query, confirms the playlist is accessible, then composes bounded playlist-item retrieval with in-server matching. The tool examines up to 500 playlist entries in source order (ten pages of 50), returns at most 25 matches by default or 50 when requested, and makes result limits, search coverage, matching fields, and safe failures explicit. No semantic, transcript, fuzzy, or continuation-token interface is introduced.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing in-repo MCP dispatcher and tool registry; Layer 2 YouTube resource wrappers; Python standard library  
**Storage**: In-memory request and result state only; no persistent storage  
**Testing**: pytest and Ruff; focused unit, contract, integration, and protocol-routing tests followed by `python3 -m pytest` and `python3 -m ruff check .`  
**Documentation Style**: Python reStructuredText docstrings for every new or changed function, class, and test helper; docstrings must state purpose, inputs, return value, raised errors where relevant, and side effects where relevant  
**Target Platform**: Hosted MCP service and local development runtime  
**Project Type**: Python MCP web service  
**Performance Goals**: At least 95% of representative searches inspecting at most 500 accessible playlist entries complete with a structured outcome within 10 seconds under normal source availability  
**Constraints**: Exact case-insensitive literal phrase matching only; 1-50 returned matches (default 25); at most 500 inspected entries; at most ten item-list pages; preserve source order; never expose continuation tokens, credentials, raw source payloads, private values, or internal traces  
**Scale/Scope**: One playlist per request; one playlist availability lookup; zero to ten playlist-item reads; no pagination input, persistence, enrichment, or UI changes

## Constitution Check

*GATE: Passed before Phase 0 research. Re-checked after Phase 1 design: passed.*

- [x] Contracts are defined for the MCP-facing `playlists_searchItems` request, response, discovery metadata, composition boundary, and safe error behavior in [contracts/playlists-search-items-contract.md](./contracts/playlists-search-items-contract.md).
- [x] The plan defines explicit Red-Green-Refactor steps for each user story and shared pagination foundation.
- [x] Red work adds failing unit, contract, integration, and routing tests before production behavior is added.
- [x] Green work is limited to the smallest family-local validation, bounded traversal, matching, normalization, descriptor export, and registry wiring needed to pass those tests.
- [x] Refactor work consolidates only duplicated playlist-search helpers, preserves behavior, and re-runs the full repository suite.
- [x] Integration coverage includes the public MCP registry, descriptor discovery, injected lower-layer dependencies, multi-page traversal, and safe error serialization; regression coverage protects pagination and availability distinctions.
- [x] The completion gate requires successful `python3 -m pytest` and `python3 -m ruff check .` after all final changes.
- [x] Every new or changed Python function, class, and test helper will have a reStructuredText docstring covering purpose, inputs, outputs, errors, and relevant side effects.
- [x] Observability records only safe search outcome metrics; error mapping strips credentials, raw payloads, continuation tokens, and traces; the simplest family-local composition is used without new services or storage.

## Research Decisions

### Phase 0 - Research and Contract Decisions

1. **Pagination and coverage — Red**: Add failing tests that prove one-page `playlists_getPlaylistItems` behavior is insufficient for a 500-entry search and that traversal stops at the terminal page or inspection cap without leaking page tokens. **Green**: Add a private playlist-family traversal helper that requests 50 entries at a time, follows only private continuation state, stops after ten pages/500 entries, and fails safely on a repeated token. **Refactor**: Reuse existing safe lower-layer error mapping where its semantics remain identical; do not change YT-311's one-page public contract.
2. **Availability distinction — Red**: Add failing tests distinguishing an accessible empty playlist from an unavailable playlist. **Green**: Use the existing direct playlist lookup before item traversal to establish availability, and map lower-layer errors to the public safe taxonomy. **Refactor**: Keep availability logic local to the composed playlist family and share only existing error sanitation.
3. **Literal matching and shaping — Red**: Add failing tests for whitespace normalization, Unicode case-folded literal comparison, deterministic matching-field order, unavailable values, source order, result limits, and coverage semantics. **Green**: Match only exposed title, description, channel title, and video identifier values; return concise normalized items and result context. **Refactor**: Extract a small private matching helper only if it removes duplicated behavior without obscuring the public contract.
4. **MCP exposure — Red**: Add failing contract, registry, and protocol-routing tests for discovery metadata, strict input schema, safe errors, and descriptor registration. **Green**: Add the descriptor to the playlists family exports and default dispatcher using existing injected Layer 2 handlers. **Refactor**: Keep catalog scaffolding unchanged because the planned tool name is already present there.

## Project Structure

### Documentation (this feature)

```text
specs/319-playlist-item-search/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── playlists-search-items-contract.md
└── tasks.md                         # Created later by /speckit.tasks
```

### Source Code (repository root)

```text
src/mcp_server/tools/
├── dispatcher.py                    # Default public MCP tool registration
└── youtube_composed/
    ├── __init__.py                  # Public package exports
    └── playlists.py                 # Playlist search contract, handler, normalization, errors

tests/
├── unit/
│   ├── test_youtube_composed_playlists.py
│   └── test_method_routing.py
├── contract/
│   └── test_youtube_composed_playlists_contract.py
└── integration/
    ├── test_youtube_composed_tool_registration.py
    └── test_youtube_tool_registration.py
```

**Structure Decision**: Extend the existing `youtube_composed` playlist family. It already owns the adjacent YT-311 public contract and safely injected Layer 2 dependencies. The search needs direct private page traversal rather than the YT-311 public handler, which deliberately performs one page only and omits descriptions.

## Phase 1 Design Deliverables

- [research.md](./research.md) resolves the pagination, availability, matching, error, and registration decisions.
- [data-model.md](./data-model.md) defines request validation, source item, returned match, coverage, and outcome fields.
- [contracts/playlists-search-items-contract.md](./contracts/playlists-search-items-contract.md) is the authoritative external MCP contract, including discovery metadata and safe errors.
- [quickstart.md](./quickstart.md) defines expected behavior and the required Red-Green-Refactor verification path.
- The agent context is updated with the current plan after these artifacts are written.

## Complexity Tracking

No constitution violations or complexity exceptions. The ten-page internal traversal is required to meet the specified 500-entry inspection bound and is kept within the existing playlist tool family, Layer 2 wrappers, and dispatcher.
