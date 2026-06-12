# Feature Specification: Layer 2 Tool `channelSections_update`

**Feature Branch**: `214-channel-sections-update`  
**Created**: 2026-06-12  
**Status**: Draft  
**Input**: User description: "Read the PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-214, as outlined in spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Update Channel Sections Through a Public Tool (Priority: P1)

As a power user, I can call the low-level `channelSections_update` tool to update an existing channel section for an authorized channel while staying close to the upstream `channelSections.update` write behavior and returned channel-section resource.

**Why this priority**: This is the core value of YT-214. Layer 2 must expose endpoint-backed channel-section updates for direct channel layout maintenance, debugging, and later composition without turning the tool into a higher-level playlist curation, video enrichment, channel branding, or layout recommendation workflow.

**Independent Test**: Can be tested by invoking `channelSections_update` with eligible authorization, a supported part selection, and a valid channel-section resource containing an existing section identifier, then confirming the caller receives the updated channel-section resource in a near-raw endpoint-backed shape with metadata identifying the mapped upstream operation.

**Acceptance Scenarios**:

1. **Given** a caller has eligible authorization for a channel and an existing channel section, **When** they call `channelSections_update` with a valid section resource and supported part selection, **Then** the result includes the updated channel-section resource and preserves the requested operation context.
2. **Given** a caller updates the title, position, type, or content references allowed by the selected channel-section structure, **When** they call `channelSections_update`, **Then** the request succeeds or returns an upstream-supported update failure without inventing higher-level layout repair behavior.
3. **Given** a caller updates playlist-backed or channel-backed section content, **When** the submitted content matches the selected section type, **Then** the result preserves the returned channel-section fields without adding unrelated playlist, video, or channel metadata.
4. **Given** a caller wants direct access to channel-section update behavior, **When** they use `channelSections_update`, **Then** the tool performs only the section update operation and is not presented as section reordering automation, playlist creation, layout optimization, or content recommendation.

---

### User Story 2 - Understand Cost, OAuth, and Writable Fields Before Calling (Priority: P2)

As a client developer, I can inspect `channelSections_update` before invoking it and immediately understand that it maps to `channelSections.update`, costs 50 official quota units per call, requires eligible OAuth authorization, and requires a valid channel-section body with supported writable fields.

**Why this priority**: Channel-section updates are quota-bearing and permission-sensitive, and update requests can accidentally omit or overwrite important channel-section fields. Callers need quota, OAuth, part-selection, writable-field, partner-context, and content-structure visibility in discovery, descriptions, and examples before they spend quota or attempt a channel write.

**Independent Test**: Can be tested by reviewing the tool discovery entry, description, usage notes, and examples to confirm the public name, upstream identity, quota cost of `50`, OAuth-required access mode, required existing section identifier, supported part names, supported writable fields, optional partner delegation context, and availability or limit caveats are visible before invocation.

**Acceptance Scenarios**:

1. **Given** a client developer discovers `channelSections_update`, **When** they read the tool metadata and description, **Then** they can identify the public tool name, upstream resource and method, official quota-unit cost of `50`, OAuth-required access mode, and supported part-selection behavior.
2. **Given** an example request is shown for `channelSections_update`, **When** a caller reads the example, **Then** the quota cost of `50`, eligible OAuth requirement, existing section identifier requirement, and writable-field expectations are visible alongside the request shape.
3. **Given** a caller wants to update a channel section using partner or delegated-channel context, **When** they inspect the tool contract, **Then** the supported partner context, required authorization, and relationship between owner and channel context are clear before invocation.
4. **Given** a caller needs to update playlist-backed or channel-backed section content, **When** they inspect the tool contract, **Then** the required match between section type and writable content-detail fields is clear before invocation.

---

### User Story 3 - Reject Unsupported Update Requests Clearly (Priority: P3)

As a caller, I receive clear validation feedback when my `channelSections_update` request lacks eligible OAuth authorization, omits the target section identifier, omits required section details, or uses unsupported writable fields, so I can correct the request without guessing which channel-section rule was violated.

**Why this priority**: `channelSections.update` combines write authorization, required target identity, part selection, partner-only optional parameters, and section-body rules. Clear validation protects callers from confusing write failures while keeping the tool faithful to the endpoint instead of inventing fallback section layouts, partial-update semantics, or content repair.

**Independent Test**: Can be tested by submitting representative invalid requests, including missing OAuth, missing part selection, missing section identifier, missing `snippet.type` when required for the update shape, unsupported writable fields, invalid content-structure combinations, duplicate references, unsupported partner context, and unavailable target sections, then confirming each failure is categorized with caller-facing guidance.

**Acceptance Scenarios**:

1. **Given** a caller provides no eligible OAuth authorization, **When** they call `channelSections_update`, **Then** the response clearly identifies the authorization requirement rather than presenting the request as a content-format failure.
2. **Given** a caller omits the existing channel-section identifier from the update resource, **When** they call `channelSections_update`, **Then** the request is rejected with guidance that the target section identifier is required.
3. **Given** a caller provides playlist content for a section type that does not accept playlists, **When** they call `channelSections_update`, **Then** the request is rejected or clearly flagged with the supported writable-field and content-structure rule.
4. **Given** a caller provides partner delegation context without the required paired channel context or eligible partner authorization, **When** they call `channelSections_update`, **Then** the response identifies the partner-context requirement.

### Edge Cases

- The caller omits required part selection; the request must be rejected before it is treated as a supported update attempt.
- The caller omits the channel-section identifier, supplies a malformed identifier, or targets a section that does not exist or is not editable by the authorized caller; the response must distinguish missing identity, invalid identity, missing resource, and access failure.
- The caller omits required writable fields for the selected update shape, including `snippet.type` or content details where the submitted section type requires them.
- The caller supplies `contentDetails.playlists[]` for a section type that does not accept playlists, or `contentDetails.channels[]` for a section type that does not accept channels; the response must identify the mismatch.
- The caller supplies duplicate playlist or channel references, private or missing playlist references, inactive or missing channel references, too many playlist or channel references, or the authorized channel's own ID where that is not allowed.
- The caller submits a section title that is missing when required, too long, or inconsistent with the selected section type.
- The caller supplies read-only fields, unsupported writable fields, unsupported part names, unsupported optional parameters, layout automation instructions, playlist creation instructions, or unrelated channel update fields; the request must be rejected or clearly flagged as outside the endpoint contract.
- The caller has OAuth authorization but lacks rights for the target channel section, delegated owner, or partner context; the response must distinguish access failure from invalid section content.
- The update would effectively replace or clear fields the caller did not intend to manage; the tool contract must make writable-field and full-resource expectations clear before invocation.
- The channel has already reached or violates a supported channel-section layout limit after the update; the response must preserve the limit failure rather than presenting the request as malformed.
- The upstream service returns quota, authorization, invalid request, content-structure, missing resource, unavailable service, deprecated behavior, or unexpected upstream failure; the caller-facing error must follow the shared Layer 2 error conventions.
- The upstream success response omits optional fields; the result must preserve returned fields without fabricating missing channel-section data.
- The caller expects section sorting, section patching, section replacement across multiple sections, playlist creation, video metadata expansion, channel analytics, layout recommendations, or bulk channel layout editing; the tool contract must keep those separate endpoint or higher-level behaviors out of scope.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing contract checks showing that `channelSections_update` is absent from Layer 2 discovery and incomplete unless it exposes the mapped `channelSections.update` identity, official quota-unit cost of `50`, OAuth-required auth mode, supported part names, writable-field expectations, availability or limit caveats, description-level quota visibility, and example-level quota visibility.
- **Red**: Add failing request-contract checks for required OAuth guidance, required part selection, required existing section identifier, required channel-section body, supported writable body fields, partner-context pairing rules, invalid content-structure combinations, duplicate references, unsupported fields, missing target sections, and channel-section availability or limit guidance.
- **Red**: Add failing result-contract checks proving that updated channel-section resource fields, selected part context, delegated or partner context when present, and upstream error categories are represented according to the shared Layer 2 conventions.
- **Green**: Deliver the smallest public `channelSections_update` tool contract and behavior needed for callers to make supported low-level `channelSections.update` requests and receive near-raw channel-section update results.
- **Green**: Include representative examples for authorized title or position update, authorized playlist-backed content update, authorized channel-backed content update, partner or delegated-channel context where supported, missing OAuth authorization, missing section identifier, invalid writable field, invalid content structure, duplicate references, unavailable target section, and unsupported option validation failure.
- **Refactor**: Remove endpoint-specific duplication that belongs to YT-201/YT-202 shared contracts while keeping the `channelSections_update` request, response, quota, auth, part-selection, partner-context, writable-field expectations, caveats, and examples easy to review. Final review evidence must include `pytest` with a passing result and `ruff check .` with a passing result.
- **Required test levels**: Contract tests for discovery metadata and request/result shape, unit tests for section-body and partner-context validation, integration-style checks for representative successful and failed channel-section update paths, and documentation checks for quota/auth/writable-field/example visibility.
- **Docstring work**: Every new or changed Python function in scope must include a reStructuredText docstring that explains its `channelSections_update` responsibility, inputs, outputs, quota cost, OAuth behavior, part-selection behavior, partner-context constraints, writable-field rules, content-structure rules, and update result.
- **Pull request evidence**: Review materials must show the matched seed slice `YT-214`, the dependency assumptions from YT-114/YT-201/YT-202, focused `channelSections_update` test output, full-suite command output, lint output, and any official-documentation caveats recorded during the work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public Layer 2 MCP tool named `channelSections_update`.
- **FR-002**: The `channelSections_update` tool definition MUST identify its mapped upstream operation as YouTube resource `channelSections` and method `update`.
- **FR-003**: The `channelSections_update` tool metadata MUST record the official quota-unit cost of `50` per call.
- **FR-004**: The `channelSections_update` tool description and usage examples MUST visibly state the official quota-unit cost of `50`.
- **FR-005**: The `channelSections_update` tool metadata MUST state that the operation requires eligible OAuth authorization and MUST NOT present channel-section updates as an API-key-only capability.
- **FR-006**: The `channelSections_update` input contract MUST preserve the upstream concepts of required part selection, existing channel-section resource identity, channel-section request body, supported writable body fields, and optional partner or delegated-channel context where those concepts are supported.
- **FR-007**: The `channelSections_update` input contract MUST require supported part selection for each update request and MUST document that part selection determines both the properties being updated and the properties returned.
- **FR-008**: The `channelSections_update` input contract MUST require an existing channel-section identifier in the submitted channel-section resource.
- **FR-009**: The `channelSections_update` input contract MUST document supported writable body fields, including section type, title, position, playlist references, and channel references where supported by the selected section type.
- **FR-010**: The `channelSections_update` input contract MUST make full-resource or overwrite-sensitive update expectations visible so callers understand which submitted writable fields can replace existing section values.
- **FR-011**: The `channelSections_update` tool MUST support valid authorized update requests with no optional partner context when the caller's OAuth authorization is sufficient for the target channel section.
- **FR-012**: The `channelSections_update` tool MUST support valid authorized update requests that include supported partner or delegated-channel context when the paired context and authorization requirements are satisfied.
- **FR-013**: The `channelSections_update` tool MUST reject requests that require OAuth, partner, or delegated-channel access when no eligible authorization is available, using the shared Layer 2 auth error convention.
- **FR-014**: The `channelSections_update` tool MUST reject missing, empty, malformed, unsupported, or conflicting part selections with clear caller-facing validation feedback.
- **FR-015**: The `channelSections_update` tool MUST reject missing channel-section identifiers, malformed identifiers, missing update bodies, unsupported body fields, unsupported part names, unsupported optional parameters, and unsupported layout or automation instructions with clear caller-facing validation feedback.
- **FR-016**: The `channelSections_update` tool MUST reject or clearly flag content-structure mismatches, including playlist references for non-playlist section types, channel references for non-channel section types, missing playlist references for playlist section types, and missing channel references for channel section types.
- **FR-017**: The `channelSections_update` tool MUST reject or clearly flag duplicate references, unavailable referenced playlists or channels, private playlist references, too many references, missing required titles, invalid positions, missing target sections, and channel-section layout limits according to the shared Layer 2 error conventions.
- **FR-018**: The `channelSections_update` result MUST preserve updated channel-section resource fields, selected part context, relevant authorization or partner context, and returned upstream fields in a near-raw endpoint-backed shape.
- **FR-019**: The `channelSections_update` tool MUST surface upstream quota, authorization, invalid request, content-structure, missing resource, unavailable service, deprecated behavior, and unexpected upstream failures according to the shared Layer 2 error conventions.
- **FR-020**: The `channelSections_update` contract MUST document applicable official limits and caveats, including the OAuth requirement, supported scopes or equivalent access expectations, partner-only optional context, required target section identity, supported part names, writable body fields, update replacement expectations, and maximum channel-section behavior.
- **FR-021**: The `channelSections_update` contract MUST remain close to the upstream `channelSections.update` endpoint and MUST NOT add higher-level section sorting, multi-section replacement, playlist creation, video metadata expansion, channel analytics, layout recommendation, channel branding, bulk editing, enrichment, or heuristic interpretation.
- **FR-022**: The `channelSections_update` tool MUST comply with the Layer 2 naming, metadata, quota, auth, availability, response-shaping, mutation result, partner-context, writable-field, content-structure, error, and example standards established by YT-201 and YT-202.
- **FR-023**: The `channelSections_update` tool MUST rely on the existing Layer 1 `channelSections.update` capability from YT-114 for endpoint behavior rather than redefining a separate upstream contract.
- **FR-024**: The feature MUST include caller-facing examples for at least one authorized title or position update, one authorized playlist-backed content update, one authorized channel-backed content update, one supported partner or delegated-channel scenario, one missing-OAuth failure, one missing-section-identifier failure, one invalid-writable-field failure, one invalid-content-structure failure, one duplicate-reference failure, one missing-target-section failure, and one unsupported option failure.
- **FR-025**: The feature MUST include validation evidence that clients can discover, call, understand OAuth and writable-field requirements, interpret channel-section update results, and handle failures for `channelSections_update` without consulting implementation-only artifacts.

### Key Entities

- **Channel Sections Update Tool**: The public Layer 2 MCP tool named `channelSections_update`, representing one low-level endpoint-backed channel-section update operation.
- **Channel Section Update Request**: The request shape that combines required part selection, an existing channel-section resource identifier, writable channel-section body fields, and any supported partner or delegated-channel context for one update attempt.
- **Target Channel Section Identifier**: The caller-provided identity of the existing channel section that should be updated.
- **Part Selection**: The caller-selected resource sections that determine which channel-section properties are updated and returned.
- **Writable Channel Section Body**: The caller-provided channel-section resource content, including supported section type, title, position, playlist references, channel references, and related writable fields.
- **Writable Field Rule**: The distinction between fields callers may update, fields that are read-only, and submitted fields that can replace existing values.
- **Section Content Rule**: The relationship between the selected section type and the required or forbidden playlist and channel references.
- **Partner or Delegated-Channel Context**: Optional caller-provided context used when an authorized YouTube content partner flow is supported for the update request.
- **Channel Section Update Result**: The returned channel-section resource fields and operation context produced by a successful `channelSections_update` call.
- **Quota Disclosure**: The caller-facing statement that each `channelSections_update` invocation costs 50 official quota units.
- **OAuth Requirement Disclosure**: The caller-facing indication that channel-section updates require eligible OAuth authorization and may require valid partner context for delegated-channel requests.
- **Writable-Field Disclosure**: The caller-facing explanation of required target identity, supported writable fields, section-type-specific content details, overwrite-sensitive update behavior, reference limits, and relevant update failures.

### Assumptions

- YT-114 provides the Layer 1 `channelSections.update` capability that this public Layer 2 tool exposes.
- YT-201 and YT-202 provide the shared Layer 2 naming, metadata, quota, auth, response-shaping, mutation result, partner-context, error, example, and validation standards this feature must follow.
- `channelSections_update` is a low-level endpoint-backed tool for direct channel-section updates, debugging, and power-user workflows; higher-level layout design, multi-section ordering, playlist creation, video enrichment, channel branding, analytics, ranking, recommendation, or bulk editing workflows belong to separate endpoint or Layer 3 features.
- The official YouTube Data API documentation is the default source for `channelSections.update` quota cost, OAuth behavior, part-selection rules, writable body fields, partner-context behavior, update replacement expectations, content-structure rules, availability state, limit behavior, and upstream error categories, with any discovered caveats recorded explicitly.
- Representative coverage of authorized title or position update, playlist-backed content update, channel-backed content update, partner or delegated-channel context, missing authorization, missing section identity, invalid writable fields, invalid content structure, duplicate references, missing target sections, unsupported options, and updated-resource results is sufficient for this slice.

### Dependencies

- `YT-114` Layer 1 `channelSections.update` wrapper is available for endpoint behavior.
- `YT-201` shared Layer 2 YouTube contracts are available for naming, request mapping, response, error, auth, quota, layout, and validation conventions.
- `YT-202` Layer 2 metadata standards are available for public naming, quota, auth, availability, description, example, and response-shaping rules.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `channelSections_update` discovery metadata, descriptions, and examples produced by this feature display the mapped `channelSections.update` identity and official quota-unit cost of `50`.
- **SC-002**: A client developer can determine in under 1 minute that `channelSections_update` requires eligible OAuth authorization and can identify supported partner or delegated-channel context by reading the tool contract alone.
- **SC-003**: A client developer can identify the required target section identifier, supported part names, writable body fields, update replacement expectations, and section-type-specific content rules in under 2 minutes by reading the tool contract alone.
- **SC-004**: 100% of representative valid `channelSections_update` requests return updated channel-section results with selected part context, relevant authorization or partner context, and returned upstream fields preserved.
- **SC-005**: 100% of representative invalid update requests that omit OAuth, omit part selection, omit the target section identifier, use invalid writable fields, use invalid content structure, use duplicate or unavailable references, target unavailable sections, or use unsupported options are rejected with caller-facing feedback before being treated as successful endpoint requests.
- **SC-006**: Reviewers can verify in a single review pass that `channelSections_update` complies with YT-201 and YT-202 Layer 2 naming, metadata, quota, auth, mutation result, partner-context, writable-field, content-structure, error, and example standards.
- **SC-007**: A power user can discover `channelSections_update`, identify the OAuth requirement, identify the required target section identifier, choose valid writable fields, and prepare a valid first request in under 3 minutes using only the public tool contract.
- **SC-008**: Final review evidence includes passing focused `channelSections_update` contract and validation checks, passing full repository behavior checks, and passing code-quality checks for the endpoint tool work.
