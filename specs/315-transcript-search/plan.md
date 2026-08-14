# Implementation Plan: Transcript Search

**Branch**: `315-transcript-search` | **Date**: 2026-08-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/315-transcript-search/spec.md`

## Summary

Deliver `transcripts_searchTranscript`, an additive Layer 3 MCP tool that retrieves normalized timestamped caption segments for one authorized video and performs a case-insensitive literal search within each segment. The tool will return chronological, bounded contextual matches with source timestamps; distinguish a valid no-match result from unavailable captions; and reuse the existing YT-314 timestamped-caption handler, transcript-family descriptor pattern, dispatcher lifecycle, and safe error mapping. It adds no persistence, provider, client, configuration setting, transport, or generic search framework.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: Existing FastAPI/Pydantic/Uvicorn MCP runtime; in-repository dispatcher; Layer 3 transcript-family module; concrete `transcripts_getTimestampedCaptions` handler from YT-314; Python standard-library text utilities; pytest; Ruff  
**Storage**: N/A; request, retrieved segments, and search matches exist in memory for one invocation only  
**Testing**: Focused unit, contract, integration, and protocol-routing regression tests with `PYTHONPATH=src python3 -m pytest`; final repository validation with `PYTHONPATH=src python3 -m pytest`; lint with `PYTHONPATH=src python3 -m ruff check .`  
**Documentation Style**: reStructuredText docstrings for every new or changed Python function, documenting purpose, `:param:`, `:return:`, `:raises:` where relevant, and observable side effects where relevant; feature-local Markdown contract documentation  
**Target Platform**: Linux-hosted Cloud Run service and supported local macOS/Linux development runtime  
**Project Type**: Python MCP web service  
**Performance Goals**: For representative transcripts of up to 10,000 segments, at least 95% of valid searches return an ordered result or safe error within 3 seconds after timestamped segments are available  
**Constraints**: One video; one invocation of the timestamped-caption dependency, which remains bounded to one authorized caption discovery and at most one VTT download; exact requested-language matching; case-insensitive literal matching only within individual segments; 1–50 `maxMatches`, default 10; no fallback language, semantic/fuzzy search, cross-segment matching, persistence, direct environment reads, credentials, raw caption/VTT content in errors or logs, stack traces, or transport changes  
**Scale/Scope**: One new public Layer 3 tool; a bounded local search over one normalized segment collection; transcript-family exports and default registration; focused unit, contract, integration, and protocol regression tests

## Constitution Check

*Pre-Phase 0 gate: PASS.*

- [x] Contracts are defined for all external/MCP-facing behavior changes in [contracts/transcripts-search-transcript-contract.md](./contracts/transcripts-search-transcript-contract.md).
- [x] The phase plan includes explicit Red-Green-Refactor steps for shared foundation work and all three user stories.
- [x] Each Red step defines failing tests before implementation work begins.
- [x] Each Green step limits code to the minimum needed to pass the corresponding tests.
- [x] Each Refactor step includes cleanup plus a full repository test-suite re-run.
- [x] Unit, contract, integration, and regression coverage are documented.
- [x] The completion command is `PYTHONPATH=src python3 -m pytest`; lint evidence is `PYTHONPATH=src python3 -m ruff check .`.
- [x] Every new or changed Python function is required to have a reStructuredText docstring.
- [x] Observability, security, and simplicity constraints are addressed below.

### Constitution-Driven Design Controls

- **Contract-first**: Publish the executable schema, deterministic literal-match and snippet rules, timestamps, provenance, composition boundary, safe outcomes, and additive compatibility posture before default registration.
- **Determinism**: Trim public text inputs; use Unicode case-folded literal matching within each segment; produce at most one match per segment; sort by ascending segment start time while retaining source order for equal starts; then apply the requested limit. A snippet is a deterministic window centered on the first match in that segment.
- **Observability**: Reuse the dispatcher and timestamped-caption request lifecycle so request correlation, tool name, latency, and status observability remain intact. Do not log video IDs, queries, caption text, snippets, timing, track metadata, authorization values, raw source responses, or traces.
- **Security**: Reuse authorized retrieval and error-detail sanitization. Return caption-derived text only after successful authorized retrieval; never disclose caption content, VTT bytes, credentials, tokens, protected track details, signed URLs, raw source bodies, or stack traces in failures.
- **Simplicity and boundedness**: Inject and compose the existing timestamped-caption handler rather than calling the public dispatcher recursively or repeating caption-list, download, VTT parsing, language selection, or upstream error logic. Do not add a provider, client, service, store, configuration setting, or generic cross-family search abstraction.
- **Rollback/mitigation**: The public tool is additive. If it must be withdrawn, remove its default descriptor registration and package export; existing caption and transcript tools remain unchanged and no client migration is needed.

## Research Decisions

All Phase 0 decisions are recorded in [research.md](./research.md). In particular, YT-315 composes YT-314 timestamped retrieval rather than YT-304 plain-text retrieval because the public result requires timestamps; it uses a bounded deterministic snippet rule, chronological ordering, and the existing safe error taxonomy.

## Phase Plan and Red-Green-Refactor Strategy

### Phase 0 - Research and Contract Decisions (complete)

- **Red**: Identify public-contract, dependency, timestamp, matching, snippet, error-serialization, registration, security, and verification gaps, including the difference between YT-304 plain-text output and YT-314 timed segments.
- **Green**: Record the selected timestamped dependency, literal matching policy, bounded snippet policy, deterministic ordering, no-match outcome, safe error translation, and contract shape in `research.md` and the public contract.
- **Refactor**: Remove all unresolved clarifications, align terminology with YT-301, YT-304, YT-314, the PRD, and the accepted feature specification, then re-check the pre-design constitution gate.

### Phase 1 - Design and Contract Artifacts (complete)

- **Red**: Derive the request, normalized segment, match, result, provenance, validation, state, dependency, failure, and operator-verification requirements from the specification and research.
- **Green**: Publish the data model, executable MCP contract, and quickstart verification path; update Codex context from the completed plan.
- **Refactor**: Reconcile matching, ordering, and failure wording across design artifacts; ensure the concrete contract does not inherit obsolete representative `matchScore` or `no_matching_results` behavior; perform the post-design constitution check.

### Phase 2 - Implementation Planning (for `/speckit.tasks`; no tasks created here)

#### Shared Foundation - Registration, Composition, and Safe Error Delivery

- **Red**: Add failing descriptor, registration, and protocol-routing tests proving the new concrete tool is discoverable, composes exactly one injected timestamped-caption handler, and serializes each documented safe category without raw details.
- **Green**: Add only the search-tool constants, error type, descriptor export, default dispatcher registration, and category propagation needed for the concrete tool. The dispatcher constructs an injected timestamped-caption handler with its existing OAuth-backed caption dependencies; it does not invoke a nested MCP descriptor or dispatcher.
- **Refactor**: Keep composition in the transcript family, preserve existing category mappings, request lifecycle, and tool contracts, add or retain reStructuredText docstrings on every changed Python function, and run focused coverage.

#### User Story 1 - Find Relevant Transcript Moments (P1)

- **Red**: Add failing unit, contract, and integration tests for required `videoId` and `query`; whitespace trimming; case-insensitive literal matching; one result per matching segment; source-preserving matched text; deterministic snippets; returned elapsed-second timestamps; chronological ordering; equal-timestamp source-order ties; one dependency call; metadata; provenance; and absence of `representativeOnly`.
- **Green**: Implement the validator, local matching and snippet helpers, result builder, handler, metadata builder, descriptor, package export, and registration required to search the injected timestamped segment result. Return only the minimum concrete result shape described by the contract.
- **Refactor**: Keep literal-search and snippet helpers private to the transcript family, avoid a generic search layer, preserve safe details and reStructuredText docstrings, and rerun focused unit, contract, and integration coverage.

#### User Story 2 - Search a Requested Language (P2)

- **Red**: Add failing tests proving that explicit `language` is forwarded unchanged after public validation to the timestamped dependency; exact-language success remains identified in the result; unavailable requested language remains a safe `language_unavailable` error; and no different-language or translated content is returned.
- **Green**: Reuse the timestamped dependency's exact requested-language policy and selected-language metadata. Do not add another language resolver, caption selector, fallback, or translation path.
- **Refactor**: Remove duplicate language-selection logic, retain dependency injection and reStructuredText docstrings, and rerun focused coverage.

#### User Story 3 - Handle Empty and Bounded Searches (P3)

- **Red**: Add failing tests for `maxMatches` default, lower and upper bounds, wrong types, unsupported fields, truncation after ordering, no source-accessible captions, empty successful segment collections, valid no-match result, authorization, quota, unavailable-source, malformed upstream segments, and error-detail sanitization.
- **Green**: Enforce the documented 1–50 bound with default 10; return `availability: no_matches` with empty `matches` only after a successfully retrieved selected transcript has no literal match; convert no accessible captions to `transcript_unavailable`; preserve the timestamped dependency's language, authorization, quota, source, and upstream categories.
- **Refactor**: Consolidate outcome mapping and result construction within the transcript family without changing any predecessor tool; verify all changed functions have reStructuredText docstrings; run focused coverage, then the full suite and lint after final code changes.

### Required Verification Evidence

1. `PYTHONPATH=src python3 -m pytest tests/unit/test_youtube_composed_transcripts.py tests/contract/test_youtube_composed_transcripts_contract.py tests/integration/test_youtube_composed_tool_registration.py tests/integration/test_youtube_tool_registration.py tests/unit/test_method_routing.py`
2. `PYTHONPATH=src python3 -m pytest`
3. `PYTHONPATH=src python3 -m ruff check .`

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/315-transcript-search/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── transcripts-search-transcript-contract.md
└── tasks.md                         # Created later by /speckit.tasks
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/
├── src/mcp_server/
│   ├── tools/
│   │   ├── dispatcher.py                           # Default concrete tool registration
│   │   └── youtube_composed/
│   │       ├── __init__.py                         # Public composed-tool exports
│   │       └── transcripts.py                      # Timed retrieval composition and local search
│   └── protocol/methods.py                         # Existing safe category mapping; change only if tests prove needed
└── tests/
    ├── contract/test_youtube_composed_transcripts_contract.py
    ├── integration/test_youtube_composed_tool_registration.py
    ├── integration/test_youtube_tool_registration.py
    └── unit/
        ├── test_method_routing.py
        └── test_youtube_composed_transcripts.py
```

**Structure Decision**: Extend the established Layer 3 transcript-family module and its adjacent export and registration seams. Reuse the concrete timestamped-caption handler and existing dispatcher lifecycle; do not create a client, persistence store, configuration setting, provider, or generic search abstraction.

### Post-Design Constitution Check

*Post-Phase 1 gate: PASS.*

- [x] The concrete MCP contract covers schema, deterministic matching and snippet rules, timestamps, provenance, bounded composition, safe errors, and additive migration posture.
- [x] The plan specifies Red before Green and Refactor after Green for foundation work and P1–P3.
- [x] Unit, contract, integration, and protocol regression coverage are identified, with full-suite and lint commands required before completion.
- [x] New or changed Python functions are required to retain or add reStructuredText docstrings.
- [x] Existing request observability is retained; logs, metadata, and errors are constrained to safe diagnostic data.
- [x] The selected composition is bounded, uses existing timed-segment behavior, and introduces no unjustified complexity.

## Complexity Tracking

No constitution exceptions are required.
