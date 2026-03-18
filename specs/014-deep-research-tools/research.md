# Research: FND-014 Deep Research Tool Foundation

## Phase 0 Research Summary

### Decision: Scope `search` and `fetch` as generic deep-research retrieval tools rather than early YouTube-specific wrappers
Rationale: The PRD and spec-kit seed place FND-014 before the YouTube domain slices and describe it as foundational retrieval capability for deep research consumers. Keeping the tools generic prevents this feature from pre-committing to YouTube-only request shapes before YT-101 and the later tool families land.
Alternatives considered:
- Make `search` a thin alias for a future YouTube search tool: rejected because it collapses the foundation slice into a later domain-specific feature and weakens the staged delivery model.
- Limit FND-014 to documentation-only placeholders: rejected because the acceptance criteria require real MCP registration, invocation, and test coverage.

### Decision: Use stateless retrieval references derived from the discovered source instead of persistent server-side search sessions
Rationale: The active architecture and feature spec both state that this slice uses in-memory runtime state only and does not add persistence. A stateless reference model lets `search` hand `fetch` a stable follow-up identifier without introducing durable storage, session coupling, or cache invalidation complexity.
Alternatives considered:
- Store search sessions in memory and require `fetch` to look up prior results: rejected because it introduces unnecessary lifecycle coupling and breaks hosted verification more easily across retries or horizontal scaling.
- Add persistent storage for search-result references: rejected because it directly violates the feature’s no-persistence constraint.

### Decision: Allow `fetch` to accept either the search-derived reference or the canonical source URI
Rationale: The feature spec requires a stable result reference or equivalent source identifier. Supporting both preserves the guided `search` -> `fetch` workflow while allowing deterministic testing and manual verification even when a client chooses to work directly from the discovered canonical URI.
Alternatives considered:
- Accept only opaque search-derived references: rejected because it makes manual verification and troubleshooting harder in a stateless system.
- Accept only raw URLs: rejected because the spec explicitly requires a stable follow-up reference from `search`, and downstream consumers benefit from a retrieval identifier that is not merely presentation data.

### Decision: Keep tool outputs within the existing MCP content-result contract established by FND-011
Rationale: The current protocol layer already serializes successful tool outputs into MCP content items with structured content. FND-014 should extend that aligned result model rather than inventing a retrieval-specific wrapper, which would add drift for downstream MCP consumers.
Alternatives considered:
- Return custom retrieval envelopes inside plain text only: rejected because it recreates the pre-FND-011 simplification and makes downstream agents parse more than necessary.
- Change the global result serializer as part of FND-014: rejected because the existing aligned MCP result contract is already sufficient and changing it would expand scope beyond the feature.

### Decision: Model `search` as paged discovery and `fetch` as one-source retrieval with explicit no-result and unavailable-source outcomes
Rationale: Deep research consumers need predictable discovery output and predictable follow-up retrieval behavior. Distinguishing empty discovery from retrieval failure keeps the contract testable and aligns with the feature spec’s requirement that no-results be distinct from errors.
Alternatives considered:
- Treat empty `search` responses as failures: rejected because no-match scenarios are normal search outcomes, not tool errors.
- Batch-fetch multiple results in one `fetch` call: rejected because the spec describes `fetch` as retrieving a selected result and the minimal viable contract should focus on one-source retrieval.

### Decision: Constrain implementation to the existing tool registry, protocol routing, and hosted verification paths
Rationale: The current codebase already has clear extension points in `src/mcp_server/tools/dispatcher.py`, `src/mcp_server/protocol/methods.py`, and the hosted integration/contract suites. Using those paths keeps the change surface small and satisfies the constitution’s simplicity requirement.
Alternatives considered:
- Introduce a new retrieval micro-layer or service abstraction before the tools exist: rejected because it adds architecture before the contract is proven.
- Change transport behavior while adding retrieval tools: rejected because FND-009, FND-010, and FND-013 already own transport, protocol, and hosted security responsibilities.

### Decision: Drive the slice with failing unit, contract, integration, and hosted-verification tests before implementation
Rationale: The constitution makes Red-Green-Refactor mandatory, and FND-014 changes an MCP-facing contract. The existing test layout already supports unit, integration, and contract validation, so the new feature should enter through failing tests at each boundary.
Alternatives considered:
- Rely only on manual hosted verification: rejected because the feature acceptance criteria explicitly require contract or integration tests.
- Limit coverage to unit tests around tool handlers: rejected because the public MCP contract and hosted invocation path must be proven end to end.

## Dependencies and Integration Patterns

- Dependency: Existing registry and dispatcher in `src/mcp_server/tools/dispatcher.py`.
  - Pattern: Register `search` and `fetch` through the same tool-definition path used by baseline tools so discovery stays deterministic.
- Dependency: Existing protocol method routing in `src/mcp_server/protocol/methods.py`.
  - Pattern: Reuse the current MCP request, response, and error flow while supplying retrieval-specific structured payloads through the aligned content serializer.
- Dependency: Existing hosted security enforcement in `src/mcp_server/security.py`.
  - Pattern: Keep all retrieval verification on the same protected `/mcp` route so FND-014 inherits the hardened access boundary instead of bypassing it.
- Dependency: Existing hosted verification and regression suites in `tests/unit`, `tests/integration`, and `tests/contract`.
  - Pattern: Add search/fetch coverage to the current suite structure rather than introducing a new verification mechanism.

## Red-Green-Refactor Plan

### Red

- Add failing discovery assertions proving `search` and `fetch` appear in `tools/list` with complete input metadata.
- Add failing unit and integration tests proving `search` distinguishes empty results from invalid requests.
- Add failing unit, integration, and contract tests proving `fetch` accepts a valid reference or URI and rejects malformed or unavailable retrieval targets with stable errors.
- Add failing hosted verification expectations for successful discovery, successful retrieval, and representative failure cases for both tools.

### Green

- Register `search` and `fetch` through the existing dispatcher with the minimum schemas and handlers needed to satisfy the failing tests.
- Shape discovery and retrieval payloads into the existing MCP-aligned result content structure.
- Extend hosted verification documentation and evidence requirements just enough to prove the new tool paths.

### Refactor

- Consolidate shared retrieval validation, content-shaping, and reference-normalization logic.
- Remove duplicate documentation or contract wording that describes the same discovery and retrieval rules in different terms.
- Re-run the full regression suite to confirm no drift in earlier foundation slices.

## Resolved Clarifications

No `NEEDS CLARIFICATION` markers remain. The repository architecture, constitution, and FND-014 feature specification are sufficient to close the design decisions for planning.
