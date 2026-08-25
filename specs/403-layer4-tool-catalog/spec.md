# Feature Specification: Layer 4 Default MCP Tool-Catalog Integration Coverage

**Feature Branch**: `403-layer4-tool-catalog`  
**Created**: 2026-08-25  
**Status**: Draft  
**Input**: User description: "Work on the requirements for OPS-403, as outlined in `requirements/spec-kit-seed.md`."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Verify the Default Tool Catalog (Priority: P1)

As a maintainer, I can run a focused verification command that discovers the default MCP tool catalog and reports an individual integration result for every discovered tool.

**Why this priority**: Complete coverage of the actual public catalog is the release gate; without it, a catalog or dispatch regression can reach users unnoticed.

**Independent Test**: Run the focused catalog verification against the default registry and confirm that every discovered tool has exactly one reported route-invocation outcome.

**Acceptance Scenarios**:

1. **Given** the default tool registry is available, **When** catalog verification starts, **Then** it obtains the inventory through the public tool-discovery route rather than a separately maintained list of tool names.
2. **Given** a tool is returned by discovery and has a safe fixture, **When** verification runs, **Then** it invokes that tool through the public tool-invocation route and reports its result separately.
3. **Given** a fixture represents a successful call, **When** the route returns its result, **Then** verification confirms a non-error MCP result with structured content.

---

### User Story 2 - Keep Tool Coverage Complete (Priority: P2)

As a tool author, I cannot add a default tool without documenting a safe invocation fixture and expected outcome, and I cannot leave a fixture for a tool that is no longer in the default catalog.

**Why this priority**: This makes coverage durable as the catalog changes and prevents false confidence from stale or incomplete fixtures.

**Independent Test**: Add a catalog entry without a fixture, and separately add a fixture without a matching catalog entry; each condition causes the focused verification to fail with the uncovered or stale item identified.

**Acceptance Scenarios**:

1. **Given** a discovered default tool has no documented safe fixture or explicit expected-error fixture, **When** verification checks completeness, **Then** it fails and identifies that tool.
2. **Given** a documented fixture does not correspond to a discovered default tool, **When** verification checks completeness, **Then** it fails and identifies the stale fixture.
3. **Given** a successful endpoint-backed result includes an endpoint identifier, **When** verification compares it with the registered tool metadata, **Then** the identifiers agree.

---

### User Story 3 - Operate Verification Safely (Priority: P3)

As an operator, I can distinguish deterministic catalog verification from credential-gated live YouTube verification and know that catalog verification performs neither outbound requests nor destructive mutations.

**Why this priority**: The verification must be safe and repeatable in ordinary development and release workflows without credentials or risk to external data.

**Independent Test**: Run catalog verification with no real credentials and observe that it completes using safe fixtures, makes no outbound YouTube request, and performs no destructive action.

**Acceptance Scenarios**:

1. **Given** a deterministic fixture represents an unavailable remote-data outcome, **When** the public route handles the call, **Then** verification confirms the documented safe MCP error category and confirms that no process-level exception escapes.
2. **Given** a maintainer follows the project documentation, **When** they select a verification command, **Then** they can distinguish the focused catalog command, the complete test command, and credential-gated live verification.

### Edge Cases

- A discovered tool is missing a fixture, or a fixture remains after its tool is removed; verification fails with the specific unmatched name rather than silently skipping it.
- A fixture intentionally has no deterministic data available; verification accepts only its documented safe MCP error category and rejects an unhandled exception.
- A successful fixture returns malformed, unstructured, or error content; verification fails that individual tool case.
- A result includes an endpoint identifier that differs from its registered upstream operation identifier; verification fails the individual tool case.
- The default catalog is empty or discovery fails; verification fails clearly because complete catalog coverage cannot be demonstrated.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Add focused integration tests that first fail for catalog discovery through the public route, missing and stale fixtures, one invocation per discovered tool, successful structured results, expected-error results, and endpoint-to-metadata agreement.
- **Green**: Add only the catalog-fixture inventory and verification behavior needed for the focused tests to pass; retain deterministic fixtures and route-level invocation as the boundary under test.
- **Refactor**: Consolidate repeated fixture and result assertions while preserving per-tool reporting. Run the full repository test suite after the focused suite passes.
- **Required test levels**: Focused deterministic integration verification for catalog discovery and invocation; catalog/fixture contract checks; complete repository regression testing. Live YouTube verification is explicitly outside this suite and remains separately credential-gated.
- **Documentation and docstrings**: Any new or changed Python function in scope must have a reStructuredText docstring describing its purpose, arguments, return value, and safe error behavior. Project documentation must state how to run the focused `make test-tools` command and the complete `make test` command, plus their boundary relative to live verification.
- **Pull-request evidence**: Include a passing focused catalog result showing one case for every discovered default tool and a passing `make test` result. If source-level test commands are used, include passing results for `PYTHONPATH=src python3 -m pytest tests/integration/test_mcp_tool_catalog_endpoints.py` and `PYTHONPATH=src python3 -m pytest`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST discover the default MCP tool inventory through the public `tools/list` route at verification time and MUST NOT use a duplicated hard-coded list of default tool names as the inventory source.
- **FR-002**: The system MUST create and report one deterministic integration case for every tool returned by the discovered default inventory.
- **FR-003**: The system MUST invoke each discovered tool through the public `tools/call` route using its documented safe fixture.
- **FR-004**: For every fixture expected to succeed, the system MUST verify that the route returns a non-error MCP result containing structured content.
- **FR-005**: When a successful endpoint-backed result exposes an `endpoint` value, the system MUST verify that value matches the registered tool metadata's `upstream.operationKey` value.
- **FR-006**: For every deterministic fixture expected to have no data, the system MUST verify the documented safe MCP error category and MUST verify that the route does not allow a process-level exception to escape.
- **FR-007**: The system MUST fail catalog verification and identify every discovered default tool that has neither a documented safe success fixture nor an explicit expected-error fixture.
- **FR-008**: The system MUST fail catalog verification and identify every documented fixture that does not correspond to a currently discovered default tool.
- **FR-009**: Catalog verification MUST run without real credentials, outbound YouTube requests, or destructive external mutations.
- **FR-010**: The project MUST provide a documented focused `make test-tools` command for catalog verification and a documented `make test` command for the complete test suite.
- **FR-011**: The project documentation MUST explain that deterministic catalog verification is distinct from credential-gated, read-only live YouTube verification.

### Key Entities

- **Discovered Tool**: A default public MCP tool returned by the public discovery route; its name and registered metadata determine required coverage.
- **Invocation Fixture**: A documented deterministic input and expected result category for one discovered tool, classified as a safe success or an explicit expected error.
- **Integration Result**: The individually reported outcome of invoking one discovered tool through the public route, including whether its response satisfies the fixture's expected category.
- **Catalog Coverage Report**: The verification output that maps each discovered tool to one integration result and exposes missing or stale fixture names.

### Assumptions

- The default registry is the catalog in scope; non-default, experimental, or credential-gated live-only tools are outside this deterministic suite unless they become part of that registry.
- A safe fixture may model an expected no-data condition when returning representative remote data would be misleading; such a fixture must declare the safe MCP error category it expects.
- Existing project conventions define the precise MCP error categories and structured-content shape used by the verification.

### Scope Boundaries

- This feature is a release-verification layer only. It does not add, remove, or expose client-facing MCP tools.
- This feature does not replace Layer 1's live execution path and does not prove real YouTube credentials or remote behavior.
- Live verification remains credential-gated, read-only, and outside the focused catalog suite.

### Dependencies

- Foundational MCP registry, discovery, dispatch, and result-contract capabilities from `FND-002`, `FND-010`, and `FND-011`.
- The default Layer 2 and Layer 3 tool catalog delivered by `YT-203` through `YT-255` and `YT-302` through `YT-320`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A focused catalog-verification run reports exactly one route-invocation result for 100% of tools discovered from the default catalog.
- **SC-002**: A run with any missing or stale fixture fails before release and identifies 100% of the unmatched tool or fixture names.
- **SC-003**: 100% of successful fixtures verify a non-error structured MCP result, and 100% of expected-error fixtures verify their documented safe error category without an escaped process-level exception.
- **SC-004**: 100% of successful endpoint-backed results that expose an endpoint identifier match their registered upstream operation identifier.
- **SC-005**: Maintainers can run the focused verification with no real credentials, no outbound YouTube request, and zero destructive external mutations.
- **SC-006**: Project documentation enables a maintainer to identify and run both the focused and complete verification commands on the first attempt, and clearly distinguishes them from opt-in live verification.
