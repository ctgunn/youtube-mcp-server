# Feature Specification: Layer 2 Tool Metadata, Naming, and Quota Standards

**Feature Branch**: `202-layer2-metadata-standards`  
**Created**: 2026-05-24  
**Status**: Draft  
**Input**: User description: "Read the PRD to get an overview of the project and its goals for context. Then, work on the requirements for YT-202, as outlined in requirements/spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Inspect Tool Identity and Cost (Priority: P1)

As a client developer, I can inspect any Layer 2 endpoint-backed tool and immediately understand its public name, mapped YouTube resource method, official quota cost, authentication mode, and availability caveats before I call it.

**Why this priority**: Layer 2 tools expose low-level endpoint operations for power users and direct API-style workflows. Their value depends on discovery metadata and public descriptions being clear enough that callers can reason about cost, access, and endpoint identity without trial-and-error.

**Independent Test**: Can be tested by reviewing representative Layer 2 tool definitions and confirming that each definition exposes name, upstream identity, quota cost, auth mode, and deprecation or availability state in a consistent caller-facing contract.

**Acceptance Scenarios**:

1. **Given** a client developer is inspecting a Layer 2 tool, **When** they read the tool definition, **Then** they can identify the public MCP tool name, mapped YouTube resource and method, official quota-unit cost, auth mode, and any deprecation or availability caveat.
2. **Given** a tool has OAuth-only or mixed authentication behavior, **When** the caller reviews the tool description and usage notes, **Then** the required access mode is explicit before invocation.
3. **Given** a tool maps to an expensive upstream method, **When** the caller reviews the tool contract, **Then** the official quota cost is visible in both the tool definition and example usage notes.

---

### User Story 2 - Derive Names Consistently (Priority: P2)

As a maintainer, I can derive every Layer 2 public tool name from its YouTube resource-method pair using one documented standard, so endpoint-backed tools remain predictable across resource families.

**Why this priority**: Later Layer 2 slices from YT-203 through YT-255 depend on consistent naming. Naming drift would make the public catalog harder for MCP clients, authors, and reviewers to navigate.

**Independent Test**: Can be tested by applying the documented naming standard to representative resource-method pairs such as `videos.list`, `playlists.insert`, `comments.setModerationStatus`, and `videos.getRating`.

**Acceptance Scenarios**:

1. **Given** a YouTube resource-method pair, **When** the naming standard is applied, **Then** the resulting public name follows the resource-method pattern without a redundant provider prefix.
2. **Given** an upstream method uses meaningful camelCase, **When** the naming standard is applied, **Then** the method suffix remains recognizable in the public tool name.
3. **Given** a later endpoint slice proposes a tool name, **When** reviewers compare it with the naming standard, **Then** they can approve or reject the name without redefining the rule in that slice.

---

### User Story 3 - Preserve Raw Endpoint Semantics With Clear Boundaries (Priority: P3)

As a future Layer 3 author, I can compose lower-level Layer 2 tools while knowing when each result is near-raw upstream data, when it includes light MCP-oriented reshaping, and what quota and auth costs composition will accumulate.

**Why this priority**: Layer 3 tools may combine multiple lower-level endpoint calls. Authors need Layer 2 contracts to distinguish raw upstream fields from light reshaping and to expose quota/auth implications before composition decisions are made.

**Independent Test**: Can be tested by reviewing representative Layer 2 contract examples and confirming that response-shaping allowances, raw-field preservation expectations, quota cost, and auth requirements are clear enough to support safe composition.

**Acceptance Scenarios**:

1. **Given** a Layer 2 tool returns upstream resource data, **When** a future Layer 3 author reviews its contract, **Then** they can identify which fields are near-raw upstream values and whether any light wrapper fields are present for MCP clarity.
2. **Given** a composed workflow would call multiple Layer 2 tools, **When** the author reviews each tool's metadata, **Then** they can estimate the total official quota-unit impact from the documented per-call costs.
3. **Given** a Layer 2 response is lightly reshaped, **When** the caller reviews usage notes, **Then** the reshaping is described as a clarity aid and not as a higher-level heuristic or composite result.

### Edge Cases

- Some upstream method names use camelCase suffixes such as `setModerationStatus`, `getRating`, or `reportAbuse`; the naming standard must keep those suffixes recognizable while preserving the resource-method naming pattern.
- Some endpoint operations have conditional auth behavior where public reads may work with an API key but private filters or mutation paths require OAuth; the metadata standard must support mixed or conditional auth without hiding the distinction.
- Some upstream methods have high quota costs, including caption, search, and video upload-related operations; the metadata standard must make high-cost calls prominent before invocation.
- Some endpoints are deprecated, unavailable, region-constrained, owner-only, media-upload oriented, or otherwise constrained; tool metadata and descriptions must surface those caveats consistently.
- Some endpoints return empty or acknowledgment-style responses rather than item lists; the response-shaping standard must still preserve endpoint identity, requested operation context, and quota/auth metadata.
- Some later endpoint slices may discover official documentation inconsistencies around quota, availability, or auth; the standard must define how those caveats are represented instead of allowing silent divergence.
- Some examples may be referenced before their endpoint implementation exists; examples must demonstrate contract standards without implying that this slice delivers individual endpoint tool behavior.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing contract checks that reject Layer 2 tool definitions missing public tool name, upstream resource and method, official quota-unit cost, auth mode, deprecation or availability state, description-level quota visibility, or example-level quota visibility.
- **Red**: Add failing naming examples for representative methods including `videos.list`, `playlists.insert`, `comments.setModerationStatus`, `videos.getRating`, and at least one mutation or media-related endpoint.
- **Red**: Add failing checks or review fixtures that distinguish near-raw responses from lightly reshaped responses and reject examples that present Layer 2 tools as higher-level composed tools.
- **Green**: Define the minimum shared metadata, naming, quota, auth, availability, description, usage-note, and response-shaping standards needed for later Layer 2 endpoint tool slices to comply.
- **Green**: Provide representative examples that prove the standard covers read endpoints, mutation endpoints, high-quota endpoints, camelCase method names, mixed-auth endpoints, constrained endpoints, and response shapes that are not simple lists.
- **Refactor**: Remove duplicate wording with YT-201 shared scaffolding where possible while keeping YT-202-specific metadata and quota standards easy to discover. Final review evidence must include `pytest` with a passing result and `ruff check .` with a passing result.
- **Required test levels**: Contract tests for metadata completeness and naming derivation, unit tests for representative metadata examples, integration-style checks for discovery-visible tool definition fields where applicable, and documentation checks for quota/auth/availability visibility.
- **Docstring work**: Every new or changed Python function in scope must include a reStructuredText docstring that explains its Layer 2 metadata, naming, quota, auth, availability, or response-standard responsibility.
- **Pull request evidence**: Review materials must show the matched seed slice `YT-202`, the representative resource-method examples used for validation, focused test command output, full-suite command output, lint output, and any official-documentation caveats recorded during the work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST define the required metadata fields for every Layer 2 endpoint-backed tool definition: public MCP tool name, mapped YouTube resource name, mapped YouTube method name, official quota-unit cost, auth mode, and deprecation or availability state.
- **FR-002**: The system MUST require every Layer 2 tool description to include the official quota-unit cost for the mapped endpoint.
- **FR-003**: The system MUST require example usage notes for every Layer 2 tool to include the official quota-unit cost or an explicit quota warning when the endpoint is especially expensive.
- **FR-004**: The system MUST define the allowed Layer 2 auth-mode values as API-key access, OAuth-required access, and mixed or conditional access, with caller-facing wording for each.
- **FR-005**: The system MUST define how deprecated, unavailable, constrained, or availability-limited endpoint behavior is represented in Layer 2 tool metadata and descriptions.
- **FR-006**: The system MUST define how public Layer 2 tool names are derived from YouTube resource-method pairs using the resource-method pattern without a redundant provider prefix.
- **FR-007**: The system MUST include naming examples for at least `videos.list`, `playlists.insert`, `comments.setModerationStatus`, and `videos.getRating`.
- **FR-008**: The system MUST preserve recognizable upstream method casing in public names when lowercasing would obscure the official method identity.
- **FR-009**: The system MUST define how metadata standards apply to read, mutation, media-upload, owner-only, high-quota, and availability-constrained endpoint shapes.
- **FR-010**: The system MUST define when a Layer 2 response may be lightly reshaped for MCP clarity while remaining traceable to a single upstream endpoint.
- **FR-011**: The system MUST define when a Layer 2 response must remain near-raw and must not be presented as a higher-level composed, enriched, ranked, or heuristic result.
- **FR-012**: The system MUST require Layer 2 tool contracts to preserve upstream-visible pagination, part selection, filters, request identifiers, mutation acknowledgments, and returned resource fields when those concepts exist upstream.
- **FR-013**: The system MUST define how official documentation inconsistencies for quota, auth, deprecation, or availability are recorded in tool metadata or adjacent contract notes.
- **FR-014**: The system MUST provide representative metadata examples for at least 10 Layer 2 resource-method pairs covering simple reads, paginated reads, camelCase method names, OAuth-only operations, mixed-auth operations, mutations, media operations, and high-quota operations.
- **FR-015**: The system MUST provide validation expectations so later Layer 2 endpoint slices can be rejected when required metadata, quota visibility, auth visibility, naming compliance, or response-shaping boundaries are missing.
- **FR-016**: The system MUST keep this feature limited to standards, shared metadata expectations, examples, and validation expectations; it MUST NOT deliver individual endpoint-backed public tool behavior beyond representative contract examples.
- **FR-017**: The system MUST remain compatible with the YT-201 shared Layer 2 scaffolding and avoid redefining broad input mapping, layout, or error conventions except where necessary for metadata, naming, quota, auth, availability, and response-shaping standards.
- **FR-018**: The system MUST allow later Layer 2 endpoint tool specs from YT-203 through YT-255 to depend on YT-202 for metadata, naming, quota, auth, availability, description, example, and response-shaping rules.

### Key Entities

- **Layer 2 Tool Definition**: The public discovery-facing definition for one endpoint-backed MCP tool, including its name, description, input contract, result expectations, and required metadata.
- **Tool Metadata Record**: The required identity and operational fields for a Layer 2 tool: public name, upstream resource, upstream method, quota cost, auth mode, and availability state.
- **Resource-Method Pair**: The official YouTube resource and method identity, such as `videos.list` or `comments.setModerationStatus`, used to derive the public Layer 2 tool name.
- **Quota Disclosure**: Caller-facing quota cost information shown in tool metadata, descriptions, and usage notes before invocation.
- **Auth Mode Disclosure**: Caller-facing indication of whether the tool supports API-key access, requires OAuth, or has mixed or conditional access behavior.
- **Availability State**: The caller-facing status of an endpoint, including active, deprecated, unavailable, region-constrained, owner-only, or otherwise constrained behavior.
- **Response-Shaping Boundary**: The rule that distinguishes near-raw endpoint payloads and light MCP clarity wrappers from higher-level enrichment, ranking, or composition.
- **Contract Example**: A representative resource-method example used to prove the standards work before individual endpoint tools are implemented.

### Assumptions

- YT-201 provides the shared Layer 2 scaffolding and broad endpoint-tool conventions that this feature extends with metadata, naming, quota, auth, availability, description, example, and response-shaping standards.
- Layer 2 tools are low-level, endpoint-backed tools for direct access, debugging, and power-user workflows; higher-level composition remains Layer 3 responsibility.
- The official YouTube Data API documentation is the default source for quota cost, auth requirements, deprecation state, and endpoint availability, with any discovered inconsistencies recorded explicitly.
- Representative examples are enough for this slice when they validate the standards across major endpoint shapes; individual endpoint implementation starts in YT-203 and later slices.
- Future Layer 3 authors will use Layer 2 metadata to reason about composition cost and access requirements, but this slice does not define Layer 3 tool behavior.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of representative Layer 2 metadata examples include public tool name, upstream resource, upstream method, official quota-unit cost, auth mode, and availability state.
- **SC-002**: A maintainer can derive the correct public tool name for at least 10 representative YouTube resource-method pairs in under 5 minutes using only the documented naming standard.
- **SC-003**: 100% of representative tool descriptions and usage-note examples include quota cost or an explicit high-quota warning before invocation.
- **SC-004**: Reviewers can identify whether a representative response is near-raw, lightly reshaped, or out of Layer 2 scope for at least six endpoint shapes without asking for clarification.
- **SC-005**: Later Layer 2 endpoint slices can reference YT-202 for metadata, naming, quota, auth, availability, and response-shaping standards with zero unresolved clarification markers.
- **SC-006**: A future Layer 3 author can estimate the official quota-unit cost and auth requirements of a three-tool Layer 2 composition in under 3 minutes using only the published Layer 2 metadata.
- **SC-007**: Final review evidence includes passing focused metadata/naming checks, passing full repository behavior checks, and passing code-quality checks for the standards work.
