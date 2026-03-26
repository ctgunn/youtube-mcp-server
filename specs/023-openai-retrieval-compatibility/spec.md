# Feature Specification: OpenAI Retrieval Compatibility

**Feature Branch**: `023-openai-retrieval-compatibility`  
**Created**: 2026-03-25  
**Status**: Draft  
**Input**: User description: "Review requirements/PRD.md to get an overview of the project and its goals for context. Then, work on implementing the requirements for FND-023, as outlined in requirements/spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Use OpenAI-Compatible Retrieval Calls (Priority: P1)

An OpenAI-hosted retrieval integration needs to call `search` and `fetch` using the request and result shapes that OpenAI currently expects for ChatGPT apps, deep research, and company-knowledge-style retrieval flows.

**Why this priority**: FND-023 exists to make the foundational retrieval tools usable in OpenAI retrieval integrations without trial-and-error or tool-specific interpretation. If the OpenAI-compatible request and result contract is missing, the feature fails its primary purpose.

**Independent Test**: Can be fully tested by connecting an OpenAI-targeted MCP client, discovering `search` and `fetch`, issuing representative OpenAI-compatible calls, and confirming the responses match the published OpenAI-facing retrieval contract.

**Acceptance Scenarios**:

1. **Given** an OpenAI-targeted MCP client lists available tools, **When** it inspects `search` and `fetch`, **Then** it sees the input contract needed to construct retrieval calls for the supported OpenAI flow.
2. **Given** an OpenAI-targeted MCP client sends a valid `search` request using the supported OpenAI-compatible shape, **When** it calls the tool, **Then** it receives retrieval results in the documented OpenAI-compatible result structure.
3. **Given** an OpenAI-targeted MCP client sends a valid `fetch` request using the supported OpenAI-compatible shape, **When** it calls the tool, **Then** it receives the selected content in the documented OpenAI-compatible result structure.
4. **Given** an OpenAI-targeted MCP client sends a request that matches an older internal retrieval shape but not the supported OpenAI-compatible contract, **When** it calls `search` or `fetch`, **Then** the service either adapts the request through the documented compatibility path or rejects it with a stable structured error that points the client to the supported contract.

---

### User Story 2 - Follow OpenAI-Specific Examples Reliably (Priority: P2)

A developer or integrator needs OpenAI-specific discovery and invocation examples so they can configure and validate ChatGPT app or deep research retrieval flows without translating from generic MCP examples.

**Why this priority**: Even if the runtime behavior is correct, the feature remains hard to adopt if developers cannot see exactly how the OpenAI-targeted flow should look in discovery and invocation.

**Independent Test**: Can be fully tested by following the published OpenAI-specific examples from discovery through invocation and confirming a developer can complete the supported `search` and `fetch` flow without relying on undocumented assumptions.

**Acceptance Scenarios**:

1. **Given** an integrator reads the published retrieval documentation, **When** they follow the OpenAI-specific discovery example, **Then** they can identify the supported OpenAI retrieval flow without inferring missing contract details.
2. **Given** an integrator follows the OpenAI-specific invocation examples, **When** they execute the documented `search` and `fetch` calls, **Then** the observed request and response behavior matches the published examples.

---

### User Story 3 - Preserve Clarity Around Compatibility Boundaries (Priority: P3)

A maintainer or operator needs any intentional differences between the OpenAI-targeted retrieval flow and generic MCP-oriented retrieval behavior to be explicit so downstream consumers know which contract they are relying on.

**Why this priority**: Compatibility work often creates ambiguity between legacy behavior, generic behavior, and target-platform behavior. This feature needs a clear compatibility boundary so later retrieval changes do not silently break supported integrations.

**Independent Test**: Can be fully tested by reviewing the published contract and automated verification evidence to confirm supported OpenAI-compatible behavior, any preserved generic behavior, and any intentional divergence are all described consistently.

**Acceptance Scenarios**:

1. **Given** the service supports an OpenAI-targeted retrieval flow, **When** a maintainer reviews the feature documentation, **Then** they can distinguish supported OpenAI-compatible shapes from generic MCP-only or legacy retrieval shapes.
2. **Given** automated compatibility verification runs, **When** the tests complete, **Then** they prove the documented OpenAI-compatible retrieval flow works end to end and that any intentional divergence remains explicit.

### Edge Cases

- What happens when an OpenAI retrieval request is valid for generic MCP retrieval but omits a field required by the supported OpenAI-compatible flow?
- How does the service behave when a request matches a prior internal retrieval shape that is no longer the preferred OpenAI-compatible contract?
- What happens when `search` returns no results but the response still needs to remain valid for the OpenAI-targeted consumer?
- How does `fetch` respond when the requested source cannot be retrieved after a valid OpenAI-compatible request is accepted?
- How are documentation and runtime behavior kept aligned when OpenAI-targeted retrieval examples change or the supported contract evolves?

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Add failing contract and integration tests for OpenAI-compatible `search` and `fetch` discovery, request validation, result shaping, compatibility-adapter behavior if used, and documentation-backed end-to-end retrieval examples.
- **Green**: Implement the smallest retrieval-contract changes needed so `search` and `fetch` accept the supported OpenAI-compatible request shapes, return the documented OpenAI-compatible result structures, and provide stable outcomes for unsupported legacy or generic-only shapes.
- **Refactor**: Consolidate shared retrieval-contract definitions, remove drift between discovery metadata, runtime validation, documentation examples, and any compatibility adapter logic, then run the full repository verification flow to confirm existing MCP, hosted, and retrieval behaviors still pass.
- Required test levels: unit tests for request validation and result-shaping rules; integration tests for tool discovery and invocation behavior; contract tests for OpenAI-compatible schema and response alignment; hosted end-to-end verification for the documented OpenAI-specific `search` and `fetch` flow.
- Pull request evidence must include failing-to-passing compatibility coverage, one hosted or hosted-like verification transcript for the OpenAI-specific retrieval flow, and a passing full-suite run using `python3 -m pytest` plus `ruff check .`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The service MUST expose `search` and `fetch` in a discovery shape that allows OpenAI-targeted retrieval consumers to construct valid calls for the supported ChatGPT app, deep research, and company-knowledge-style retrieval flow.
- **FR-002**: The `search` tool MUST accept the supported OpenAI-compatible request shape for retrieval discovery.
- **FR-003**: The `fetch` tool MUST accept the supported OpenAI-compatible request shape for retrieval follow-up.
- **FR-004**: `search` responses MUST return retrieval results in the documented OpenAI-compatible result structure for the supported flow.
- **FR-005**: `fetch` responses MUST return fetched content in the documented OpenAI-compatible result structure for the supported flow.
- **FR-006**: If the service preserves an underlying generic retrieval shape that differs from the supported OpenAI-compatible flow, the service MUST provide a clear documented compatibility boundary between those shapes.
- **FR-007**: If the service uses a compatibility adapter instead of changing the foundational retrieval shape directly, the adapter MUST preserve the same user-visible OpenAI-compatible request and result contract described in discovery and documentation.
- **FR-008**: Unsupported retrieval calls that do not match the supported OpenAI-compatible contract MUST fail with a stable structured outcome unless they are explicitly supported through a documented compatibility path.
- **FR-009**: OpenAI-compatible retrieval behavior MUST be covered by automated verification for both `search` and `fetch`, including representative success and failure paths.
- **FR-010**: The published retrieval documentation MUST include OpenAI-specific discovery and invocation examples for the supported `search` and `fetch` flow.
- **FR-011**: The published retrieval documentation MUST identify any intentional divergence from prior internal retrieval shapes or from generic MCP-oriented retrieval expectations.
- **FR-012**: The completed compatibility work MUST preserve the ability of operators and integrators to verify the supported OpenAI retrieval flow end to end before release.
- **FR-013**: The completed compatibility work MUST preserve existing hosted authentication and transport expectations for retrieval calls.

### Key Entities *(include if feature involves data)*

- **OpenAI Retrieval Contract**: The published request and result shape for `search` and `fetch` that supported OpenAI-targeted consumers rely on.
- **Compatibility Boundary**: The documented distinction between the supported OpenAI retrieval contract and any generic or legacy retrieval shape the service may still expose internally or support conditionally.
- **Retrieval Example**: A published discovery or invocation example that demonstrates the supported OpenAI-compatible `search` or `fetch` flow.
- **Compatibility Verification Record**: The automated or hosted evidence showing the documented OpenAI retrieval flow works and unsupported shapes behave as documented.

### Assumptions

- FND-014 already introduced functional `search` and `fetch` retrieval tools for generic research workflows.
- FND-017 already improved the machine-readable completeness of retrieval discovery metadata.
- FND-021 already established that the hosted MCP service is publicly reachable in the way required for trusted remote MCP consumers while still enforcing MCP-layer authentication.
- The supported OpenAI retrieval flow is treated as the primary compatibility target for this feature, even if generic MCP retrieval behavior continues to exist for non-OpenAI consumers.
- The feature may satisfy compatibility either by aligning the foundational retrieval contract directly or by inserting a documented compatibility adapter, as long as the user-visible OpenAI contract is stable.

### Dependencies

- `FND-014` Deep research tool foundation (`search` + `fetch`)
- `FND-017` Retrieval tool contract completeness
- `FND-021` Cloud Run public reachability for remote MCP

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In automated compatibility verification, 100% of representative supported OpenAI-compatible `search` request shapes complete successfully with the documented result structure.
- **SC-002**: In automated compatibility verification, 100% of representative supported OpenAI-compatible `fetch` request shapes complete successfully with the documented result structure.
- **SC-003**: In automated failure-path verification, 100% of tested unsupported retrieval shapes that fall outside the documented OpenAI-compatible contract return the documented structured outcome.
- **SC-004**: An integrator can follow the published OpenAI-specific retrieval guidance and complete tool discovery plus one successful `search` call and one successful `fetch` call in under 15 minutes without undocumented steps.
- **SC-005**: Release evidence shows no mismatches between published OpenAI-specific retrieval examples and observed behavior for the representative success and failure scenarios defined for this feature.
