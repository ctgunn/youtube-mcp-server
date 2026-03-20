# Feature Specification: Retrieval Tool Contract Completeness

**Feature Branch**: `017-retrieval-tool-contract`  
**Created**: 2026-03-19  
**Status**: Draft  
**Input**: User description: "Review the requirements/PRD.md to get an overview of the project and its goals for your context. Then, work on implementing the requirements for FND-017, as outlined in requirements/spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Discover a Valid Fetch Shape (Priority: P1)

An MCP client needs tool discovery to describe the `fetch` request contract clearly enough that it can build a valid request without probing the server through failed calls.

**Why this priority**: FND-017 exists to remove trial-and-error from retrieval-tool invocation. If discovery does not describe the valid `fetch` request shapes, the retrieval contract is still incomplete even if the tool works at runtime.

**Independent Test**: Can be fully tested by listing tools from an MCP client, using only the published `fetch` metadata to construct valid requests for each supported input pattern, and confirming those requests succeed without relying on separate documentation or undocumented retries.

**Acceptance Scenarios**:

1. **Given** an MCP client lists available tools, **When** it inspects the `fetch` tool metadata, **Then** it can determine which identifiers are accepted, which combinations are valid, and which combinations are invalid.
2. **Given** an MCP client constructs a `fetch` request using one supported identifier pattern published in discovery, **When** it calls the tool, **Then** the request is accepted and returns the requested source content.
3. **Given** an MCP client constructs a `fetch` request using a disallowed identifier combination that discovery marks as invalid, **When** it calls the tool, **Then** the service rejects the request with a stable structured error that matches the published contract.

---

### User Story 2 - Trust Discovery for Search Inputs (Priority: P2)

An MCP client needs the `search` tool metadata to describe required and optional inputs precisely so it can issue valid discovery calls without guessing which fields are required or tolerated.

**Why this priority**: `search` is the starting point for retrieval workflows. If its machine-readable contract is incomplete or inaccurate, clients cannot reliably begin the discover-then-fetch flow.

**Independent Test**: Can be fully tested by building a `search` request solely from tool discovery, confirming required inputs are obvious, optional controls are understandable, and invalid request shapes fail exactly where the published contract says they should.

**Acceptance Scenarios**:

1. **Given** an MCP client lists tools, **When** it inspects the `search` tool metadata, **Then** it can identify the required query input and the supported optional controls from machine-readable discovery output alone.
2. **Given** an MCP client sends a `search` request that matches the discovered contract, **When** it calls the tool, **Then** it receives a structured result set or an explicit no-results outcome.
3. **Given** an MCP client sends a `search` request that violates the discovered contract, **When** it calls the tool, **Then** it receives a stable structured validation failure instead of ambiguous runtime behavior.

---

### User Story 3 - Verify Contract and Runtime Stay Aligned (Priority: P3)

A developer or operator needs automated and hosted verification evidence showing that the published retrieval schemas and the live validation behavior remain in sync as the service evolves.

**Why this priority**: A machine-readable contract loses value quickly if later changes make discovery and runtime behavior drift apart. This feature must lock the published schema and live validation together.

**Independent Test**: Can be fully tested by running automated contract coverage plus a hosted verification flow that lists tools, builds representative `search` and `fetch` calls from discovery output, and confirms both successful and failing calls match the documented contract.

**Acceptance Scenarios**:

1. **Given** automated verification is run, **When** retrieval-tool contract tests execute, **Then** they prove that the discovered schemas match the runtime acceptance and rejection behavior for representative `search` and `fetch` calls.
2. **Given** an operator follows the hosted verification guidance, **When** they perform discovery and retrieval checks, **Then** they can demonstrate that valid retrieval calls can be constructed from discovery output alone.

### Edge Cases

- How does discovery represent `fetch` when more than one identifier can be used to target the same source?
- What happens when a client supplies both supported `fetch` identifiers but they point to different sources?
- What happens when a client omits all accepted `fetch` identifiers?
- How does the service distinguish a no-results `search` outcome from an invalid `search` request?
- What happens when optional retrieval controls are omitted and the service must apply defaults?
- How is contract behavior preserved when the hosted verification examples and the discovered schemas disagree?

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Add failing contract and integration tests that prove the discovered `search` and `fetch` schemas are sufficient to construct valid calls, including supported `fetch` identifier patterns, invalid combination failures, required-input failures, and hosted discovery-driven verification.
- **Green**: Update the retrieval-tool contract so discovery fully describes accepted request shapes and the runtime validation behavior matches the published metadata for both successful and failing calls.
- **Refactor**: Consolidate shared retrieval-contract definitions, remove duplicated rule descriptions between discovery and validation paths, and rerun the broader MCP regression suite to confirm existing initialize, tool listing, hosted access, and retrieval behaviors still hold.
- Required test levels: unit tests for schema and validation rules; integration tests for dispatcher and invocation behavior; contract tests for discovery metadata and result/error alignment; hosted end-to-end verification for discovery-driven `search` and `fetch` calls.
- Pull request evidence must include failing-to-passing retrieval contract tests, one hosted verification transcript showing tool discovery plus successful `search` and `fetch` calls built from that discovery, and at least one failing-call example proving invalid request shapes are rejected as documented.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The service MUST expose `search` and `fetch` discovery metadata that fully describes the accepted request contract for each tool in machine-readable form.
- **FR-002**: The `search` discovery contract MUST identify which input is required and which inputs are optional so a client can build a valid `search` call from discovery output alone.
- **FR-003**: The `search` discovery contract MUST describe any supported input restrictions that determine whether a request is accepted or rejected.
- **FR-004**: The `fetch` discovery contract MUST describe every supported way a client may identify the source to retrieve.
- **FR-005**: The `fetch` discovery contract MUST describe the valid required-input combinations, including when exactly one identifier is sufficient and when multiple identifiers may be provided together.
- **FR-006**: The `fetch` discovery contract MUST make it possible for a client to infer which requests are invalid before sending them, including the case where no supported identifier is supplied.
- **FR-007**: Runtime validation for `search` and `fetch` MUST accept every request shape described as valid by discovery metadata.
- **FR-008**: Runtime validation for `search` and `fetch` MUST reject every request shape described as invalid by discovery metadata with a stable structured error.
- **FR-009**: The service MUST keep discovery metadata and runtime validation aligned for both successful and failing retrieval calls across local and hosted flows.
- **FR-010**: The published retrieval contract MUST include representative examples showing how a client can construct valid `search` and `fetch` calls from discovery output alone.
- **FR-011**: Hosted verification guidance MUST demonstrate at least one valid `search` call and all supported valid `fetch` request patterns derived from discovery output.
- **FR-012**: Automated verification MUST cover the primary valid and invalid request shapes for `search` and `fetch`, including unsupported `fetch` identifier combinations.
- **FR-013**: The completed retrieval contract MUST preserve the existing discoverability and invocation behavior of the foundational retrieval tools for supported clients.

### Key Entities *(include if feature involves data)*

- **Tool Discovery Contract**: The machine-readable metadata a client receives for `search` and `fetch`, including accepted inputs, required fields, optional fields, allowed combinations, and disallowed shapes.
- **Search Request Shape**: A valid or invalid pattern of inputs a client may attempt when calling `search`.
- **Fetch Request Shape**: A valid or invalid pattern of identifiers a client may attempt when calling `fetch` to retrieve a source.
- **Verification Example**: A documented discovery-driven retrieval example used to prove that a client can construct valid calls from published tool metadata alone.

### Assumptions

- FND-014 already introduced the foundational `search` and `fetch` tools and established their role in deep research-style workflows.
- FND-011 already established that tool discovery exposes machine-readable metadata; FND-017 strengthens the completeness of that metadata for retrieval tools.
- Supported MCP clients are expected to rely on tool discovery first rather than separate product-specific retrieval documentation.
- The retrieval tools continue to use the same user-facing tool names, result concepts, and protected hosted access model established by earlier foundation work.

### Dependencies

- `FND-011` Tool metadata and invocation result alignment
- `FND-014` Deep research tool foundation (`search` + `fetch`)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In automated contract verification, 100% of supported `search` request shapes can be constructed and invoked successfully using discovery output alone.
- **SC-002**: In automated contract verification, 100% of supported `fetch` request patterns can be constructed and invoked successfully using discovery output alone.
- **SC-003**: In automated failure-path verification, 100% of tested invalid retrieval request shapes that discovery marks as disallowed are rejected with the documented structured error behavior.
- **SC-004**: In hosted verification, an operator can complete discovery plus one valid `search` call and every supported valid `fetch` call pattern in under 15 minutes without consulting undocumented guidance.
- **SC-005**: Release evidence shows no mismatches between published retrieval-tool discovery metadata and runtime validation behavior for the representative success and failure scenarios defined for this feature.
