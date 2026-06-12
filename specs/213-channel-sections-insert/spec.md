# Feature Specification: Layer 2 Tool `channelSections_insert`

**Feature Branch**: `213-channel-sections-insert`  
**Created**: 2026-06-11  
**Status**: Draft  
**Input**: User description: "Read the PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-213, as outlined in spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create Channel Sections Through a Public Tool (Priority: P1)

As a power user, I can call the low-level `channelSections_insert` tool to add a channel section to an authorized channel while staying close to the upstream `channelSections.insert` write behavior and returned channel-section resource.

**Why this priority**: This is the core value of YT-213. Layer 2 must expose endpoint-backed channel-section creation for direct channel layout management, debugging, and later composition without turning the tool into a higher-level playlist curation, video enrichment, channel branding, or layout recommendation workflow.

**Independent Test**: Can be tested by invoking `channelSections_insert` with eligible authorization, a supported part selection, and a valid channel-section definition, then confirming the caller receives the created channel-section resource in a near-raw endpoint-backed shape with metadata identifying the mapped upstream operation.

**Acceptance Scenarios**:

1. **Given** a caller has eligible authorization for a channel, **When** they call `channelSections_insert` with a valid section definition and supported part selection, **Then** the result includes the created channel-section resource and preserves the requested operation context.
2. **Given** a caller creates a section populated by playlist references, **When** they call `channelSections_insert` with content that matches the selected section type, **Then** the request succeeds or returns an upstream-supported creation failure without inventing higher-level playlist expansion behavior.
3. **Given** a caller creates a section populated by channel references, **When** they call `channelSections_insert` with content that matches the selected section type, **Then** the result preserves the returned channel-section fields without adding unrelated channel metadata.
4. **Given** a caller wants direct access to channel-section creation behavior, **When** they use `channelSections_insert`, **Then** the tool performs only the section creation operation and is not presented as channel layout optimization, section ordering automation, playlist creation, or content recommendation.

---

### User Story 2 - Understand Cost, OAuth, and Content Rules Before Calling (Priority: P2)

As a client developer, I can inspect `channelSections_insert` before invoking it and immediately understand that it maps to `channelSections.insert`, costs 50 official quota units per call, requires eligible OAuth authorization, and requires a valid channel-section body with supported section type and content details.

**Why this priority**: Channel-section creation is quota-bearing and permission-sensitive, and invalid section body combinations are easy to construct. Callers need quota, OAuth, partner-context, part-selection, and content-structure visibility in discovery, descriptions, and examples before they spend quota or attempt a channel write.

**Independent Test**: Can be tested by reviewing the tool discovery entry, description, usage notes, and examples to confirm the public name, upstream identity, quota cost of `50`, OAuth-required access mode, supported request body fields, required `snippet.type`, supported part names, optional partner delegation context, and availability or limit caveats are visible before invocation.

**Acceptance Scenarios**:

1. **Given** a client developer discovers `channelSections_insert`, **When** they read the tool metadata and description, **Then** they can identify the public tool name, upstream resource and method, official quota-unit cost of `50`, OAuth-required access mode, and supported part-selection behavior.
2. **Given** an example request is shown for `channelSections_insert`, **When** a caller reads the example, **Then** the quota cost of `50` and the need for eligible OAuth authorization plus a valid section body are visible alongside the request shape.
3. **Given** a caller wants to create a channel section using partner or delegated-channel context, **When** they inspect the tool contract, **Then** the supported partner context, required authorization, and relationship between owner and channel context are clear before invocation.
4. **Given** a caller needs to choose between playlist-backed and channel-backed section content, **When** they inspect the tool contract, **Then** the required match between section type and `contentDetails` fields is clear before invocation.

---

### User Story 3 - Reject Unsupported Create Requests Clearly (Priority: P3)

As a caller, I receive clear validation feedback when my `channelSections_insert` request lacks eligible OAuth authorization, omits required section details, or uses unsupported section content, so I can correct the request without guessing which channel-section rule was violated.

**Why this priority**: `channelSections.insert` combines write authorization, part selection, partner-only optional parameters, and section-body rules. Clear validation protects callers from confusing write failures while keeping the tool faithful to the endpoint instead of inventing fallback section layouts or content repair.

**Independent Test**: Can be tested by submitting representative invalid requests, including missing OAuth, missing part selection, missing `snippet.type`, missing required content details, duplicate content references, unsupported fields, invalid partner context, and unavailable channel-section capacity, then confirming each failure is categorized with caller-facing guidance.

**Acceptance Scenarios**:

1. **Given** a caller provides no eligible OAuth authorization, **When** they call `channelSections_insert`, **Then** the response clearly identifies the authorization requirement rather than presenting the request as a content-format failure.
2. **Given** a caller omits `snippet.type` from the section body, **When** they call `channelSections_insert`, **Then** the request is rejected with guidance that the section type is required.
3. **Given** a caller provides playlist content for a section type that does not accept playlists, **When** they call `channelSections_insert`, **Then** the request is rejected or clearly flagged with the supported content-structure rule.
4. **Given** a caller provides partner delegation context without the required paired channel context or eligible partner authorization, **When** they call `channelSections_insert`, **Then** the response identifies the partner-context requirement.

### Edge Cases

- The caller omits required part selection; the request must be rejected before it is treated as a supported create attempt.
- The caller omits `snippet.type`; the request must identify that the section type is required.
- The caller omits `contentDetails` for a section type that requires referenced playlists or channels; the response must identify the missing content structure.
- The caller supplies `contentDetails.playlists[]` for a section type that does not accept playlists, or `contentDetails.channels[]` for a section type that does not accept channels; the response must identify the mismatch.
- The caller supplies duplicate playlist or channel references, private or missing playlist references, inactive or missing channel references, too many playlist or channel references, or the authorized channel's own ID where that is not allowed.
- The caller submits a section title that is missing when required, too long, or inconsistent with the selected section type.
- The caller supplies read-only fields, unsupported section body fields, unsupported part names, unsupported optional parameters, layout automation instructions, playlist creation instructions, or channel update fields; the request must be rejected or clearly flagged as outside the endpoint contract.
- The caller has OAuth authorization but lacks rights for the target channel, delegated owner, or partner context; the response must distinguish access failure from invalid section content.
- The channel has already reached the maximum supported number of sections; the response must preserve the capacity failure rather than presenting the request as malformed.
- The upstream service returns quota, authorization, invalid request, content-structure, missing resource, unavailable service, deprecated behavior, or unexpected upstream failure; the caller-facing error must follow the shared Layer 2 error conventions.
- The upstream success response omits optional fields; the result must preserve returned fields without fabricating missing channel-section data.
- The caller expects section sorting, section replacement, playlist creation, video metadata expansion, channel analytics, layout recommendations, or bulk channel layout editing; the tool contract must keep those separate endpoint or higher-level behaviors out of scope.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing contract checks showing that `channelSections_insert` is absent from Layer 2 discovery and incomplete unless it exposes the mapped `channelSections.insert` identity, official quota-unit cost of `50`, OAuth-required auth mode, supported part names, content-structure requirements, availability or limit caveats, description-level quota visibility, and example-level quota visibility.
- **Red**: Add failing request-contract checks for required OAuth guidance, required part selection, required section body, required `snippet.type`, supported writable body fields, partner-context pairing rules, invalid content-structure combinations, duplicate references, unsupported fields, and channel-section capacity or availability guidance.
- **Red**: Add failing result-contract checks proving that created channel-section resource fields, selected part context, delegated or partner context when present, and upstream error categories are represented according to the shared Layer 2 conventions.
- **Green**: Deliver the smallest public `channelSections_insert` tool contract and behavior needed for callers to make supported low-level `channelSections.insert` requests and receive near-raw channel-section creation results.
- **Green**: Include representative examples for authorized playlist-backed creation, authorized channel-backed creation, partner or delegated-channel context where supported, missing OAuth authorization, missing section type, invalid content structure, duplicate references, capacity failure, and unsupported option validation failure.
- **Refactor**: Remove endpoint-specific duplication that belongs to YT-201/YT-202 shared contracts while keeping the `channelSections_insert` request, response, quota, auth, part-selection, partner-context, content-structure, caveats, and examples easy to review. Final review evidence must include `pytest` with a passing result and `ruff check .` with a passing result.
- **Required test levels**: Contract tests for discovery metadata and request/result shape, unit tests for section-body and partner-context validation, integration-style checks for representative successful and failed channel-section creation paths, and documentation checks for quota/auth/content/example visibility.
- **Docstring work**: Every new or changed Python function in scope must include a reStructuredText docstring that explains its `channelSections_insert` responsibility, inputs, outputs, quota cost, OAuth behavior, part-selection behavior, partner-context constraints, content-structure rules, and creation result.
- **Pull request evidence**: Review materials must show the matched seed slice `YT-213`, the dependency assumptions from YT-113/YT-201/YT-202, focused `channelSections_insert` test output, full-suite command output, lint output, and any official-documentation caveats recorded during the work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public Layer 2 MCP tool named `channelSections_insert`.
- **FR-002**: The `channelSections_insert` tool definition MUST identify its mapped upstream operation as YouTube resource `channelSections` and method `insert`.
- **FR-003**: The `channelSections_insert` tool metadata MUST record the official quota-unit cost of `50` per call.
- **FR-004**: The `channelSections_insert` tool description and usage examples MUST visibly state the official quota-unit cost of `50`.
- **FR-005**: The `channelSections_insert` tool metadata MUST state that the operation requires eligible OAuth authorization and MUST NOT present channel-section creation as an API-key-only capability.
- **FR-006**: The `channelSections_insert` input contract MUST preserve the upstream concepts of required part selection, channel-section request body, supported writable body fields, and optional partner or delegated-channel context where those concepts are supported.
- **FR-007**: The `channelSections_insert` input contract MUST require supported part selection for each create request and MUST document that part selection determines both the properties being written and the properties returned.
- **FR-008**: The `channelSections_insert` input contract MUST require a channel-section body that includes `snippet.type`.
- **FR-009**: The `channelSections_insert` input contract MUST document supported writable body fields, including section type, title, position, playlist references, and channel references where supported by the selected section type.
- **FR-010**: The `channelSections_insert` tool MUST support valid authorized creation requests with no optional partner context when the caller's OAuth authorization is sufficient for the target channel.
- **FR-011**: The `channelSections_insert` tool MUST support valid authorized creation requests that include supported partner or delegated-channel context when the paired context and authorization requirements are satisfied.
- **FR-012**: The `channelSections_insert` tool MUST reject requests that require OAuth, partner, or delegated-channel access when no eligible authorization is available, using the shared Layer 2 auth error convention.
- **FR-013**: The `channelSections_insert` tool MUST reject missing, empty, malformed, unsupported, or conflicting part selections with clear caller-facing validation feedback.
- **FR-014**: The `channelSections_insert` tool MUST reject missing `snippet.type`, missing required section content, unsupported body fields, unsupported part names, unsupported optional parameters, and unsupported layout or automation instructions with clear caller-facing validation feedback.
- **FR-015**: The `channelSections_insert` tool MUST reject or clearly flag content-structure mismatches, including playlist references for non-playlist section types, channel references for non-channel section types, missing playlist references for playlist section types, and missing channel references for channel section types.
- **FR-016**: The `channelSections_insert` tool MUST reject or clearly flag duplicate references, unavailable referenced playlists or channels, private playlist references, too many references, missing required titles, invalid positions, and channel-section capacity limits according to the shared Layer 2 error conventions.
- **FR-017**: The `channelSections_insert` result MUST preserve created channel-section resource fields, selected part context, relevant authorization or partner context, and returned upstream fields in a near-raw endpoint-backed shape.
- **FR-018**: The `channelSections_insert` tool MUST surface upstream quota, authorization, invalid request, content-structure, missing resource, unavailable service, deprecated behavior, and unexpected upstream failures according to the shared Layer 2 error conventions.
- **FR-019**: The `channelSections_insert` contract MUST document applicable official limits and caveats, including the OAuth requirement, supported scopes or equivalent access expectations, partner-only optional context, required `snippet.type`, supported part names, writable body fields, and maximum channel-section behavior.
- **FR-020**: The `channelSections_insert` contract MUST remain close to the upstream `channelSections.insert` endpoint and MUST NOT add higher-level section sorting, section replacement, playlist creation, video metadata expansion, channel analytics, layout recommendation, channel branding, bulk editing, enrichment, or heuristic interpretation.
- **FR-021**: The `channelSections_insert` tool MUST comply with the Layer 2 naming, metadata, quota, auth, availability, response-shaping, mutation result, partner-context, content-structure, error, and example standards established by YT-201 and YT-202.
- **FR-022**: The `channelSections_insert` tool MUST rely on the existing Layer 1 `channelSections.insert` capability from YT-113 for endpoint behavior rather than redefining a separate upstream contract.
- **FR-023**: The feature MUST include caller-facing examples for at least one authorized playlist-backed section creation request, one authorized channel-backed section creation request, one supported partner or delegated-channel scenario, one missing-OAuth failure, one missing-section-type failure, one invalid-content-structure failure, one duplicate-reference failure, one capacity-limit failure, and one unsupported option failure.
- **FR-024**: The feature MUST include validation evidence that clients can discover, call, understand OAuth and content-structure requirements, interpret channel-section creation results, and handle failures for `channelSections_insert` without consulting implementation-only artifacts.

### Key Entities

- **Channel Sections Insert Tool**: The public Layer 2 MCP tool named `channelSections_insert`, representing one low-level endpoint-backed channel-section creation operation.
- **Channel Section Create Request**: The request shape that combines required part selection, a channel-section body, and any supported partner or delegated-channel context for one create attempt.
- **Part Selection**: The caller-selected resource sections that determine which channel-section properties are written and returned.
- **Channel Section Body**: The caller-provided channel-section resource content, including the required section type and any supported title, position, playlist references, or channel references.
- **Section Content Rule**: The relationship between the selected section type and the required or forbidden playlist and channel references.
- **Partner or Delegated-Channel Context**: Optional caller-provided context used when an authorized YouTube content partner flow is supported for the create request.
- **Channel Section Create Result**: The returned channel-section resource fields and operation context produced by a successful `channelSections_insert` call.
- **Quota Disclosure**: The caller-facing statement that each `channelSections_insert` invocation costs 50 official quota units.
- **OAuth Requirement Disclosure**: The caller-facing indication that channel-section creation requires eligible OAuth authorization and may require valid partner context for delegated-channel requests.
- **Content-Structure Disclosure**: The caller-facing explanation of required `snippet.type`, supported writable fields, section-type-specific content details, reference limits, and relevant create failures.

### Assumptions

- YT-113 provides the Layer 1 `channelSections.insert` capability that this public Layer 2 tool exposes.
- YT-201 and YT-202 provide the shared Layer 2 naming, metadata, quota, auth, response-shaping, mutation result, partner-context, error, example, and validation standards this feature must follow.
- `channelSections_insert` is a low-level endpoint-backed tool for direct channel-section creation, debugging, and power-user workflows; higher-level layout design, section ordering, playlist creation, video enrichment, channel branding, analytics, ranking, recommendation, or bulk editing workflows belong to separate endpoint or Layer 3 features.
- The official YouTube Data API documentation is the default source for `channelSections.insert` quota cost, OAuth behavior, part-selection rules, writable body fields, partner-context behavior, content-structure rules, availability state, limit behavior, and upstream error categories, with any discovered caveats recorded explicitly.
- Representative coverage of authorized playlist-backed creation, authorized channel-backed creation, partner or delegated-channel context, missing authorization, missing section type, invalid content structure, duplicate references, capacity limits, unsupported options, and created-resource results is sufficient for this slice.

### Dependencies

- `YT-113` Layer 1 `channelSections.insert` wrapper is available for endpoint behavior.
- `YT-201` shared Layer 2 YouTube contracts are available for naming, request mapping, response, error, auth, quota, layout, and validation conventions.
- `YT-202` Layer 2 metadata standards are available for public naming, quota, auth, availability, description, example, and response-shaping rules.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `channelSections_insert` discovery metadata, descriptions, and examples produced by this feature display the mapped `channelSections.insert` identity and official quota-unit cost of `50`.
- **SC-002**: A client developer can determine in under 1 minute that `channelSections_insert` requires eligible OAuth authorization and can identify supported partner or delegated-channel context by reading the tool contract alone.
- **SC-003**: A client developer can identify the required section body, required `snippet.type`, supported part names, writable body fields, and section-type-specific content rules in under 2 minutes by reading the tool contract alone.
- **SC-004**: 100% of representative valid `channelSections_insert` requests return created channel-section results with selected part context, relevant authorization or partner context, and returned upstream fields preserved.
- **SC-005**: 100% of representative invalid create requests that omit OAuth, omit part selection, omit `snippet.type`, use invalid content structure, use duplicate or unavailable references, use unsupported options, or exceed channel-section capacity are rejected with caller-facing feedback before being treated as successful endpoint requests.
- **SC-006**: Reviewers can verify in a single review pass that `channelSections_insert` complies with YT-201 and YT-202 Layer 2 naming, metadata, quota, auth, mutation result, partner-context, content-structure, error, and example standards.
- **SC-007**: A power user can discover `channelSections_insert`, identify the OAuth requirement, choose a valid section type and content structure, and prepare a valid first request in under 3 minutes using only the public tool contract.
- **SC-008**: Final review evidence includes passing focused `channelSections_insert` contract and validation checks, passing full repository behavior checks, and passing code-quality checks for the endpoint tool work.
