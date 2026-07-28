# Feature Specification: Layer 2 Tool `watermarks_unset`

**Feature Branch**: `255-watermarks-unset`  
**Created**: 2026-07-27  
**Status**: Draft  
**Input**: User description: "Read the PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-255, as outlined in spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Remove a Channel Watermark Through a Public Endpoint Tool (Priority: P1)

As a power user or agent workflow author, I can call the low-level `watermarks_unset` tool to remove an authorized channel watermark while staying close to the upstream `watermarks.unset` behavior.

**Why this priority**: This is the core value of YT-255. Layer 2 must expose direct endpoint-backed channel watermark removal for advanced client automation, debugging, and raw endpoint access without turning the tool into a broader channel-branding workflow.

**Independent Test**: Can be tested by invoking `watermarks_unset` with eligible OAuth authorization and supported channel context, then confirming the caller receives a structured watermark-removal acknowledgment with mapped operation identity, quota context, access context, target channel context, and mutation outcome preserved.

**Acceptance Scenarios**:

1. **Given** a caller has eligible OAuth authorization and provides supported channel context for a channel whose watermark can be removed, **When** they call `watermarks_unset`, **Then** the result confirms that the watermark removal was accepted or completed for that channel.
2. **Given** a successful watermark removal returns no refreshed channel resource, **When** the caller inspects the result, **Then** the result still preserves enough request context to identify which channel watermark removal was acknowledged.
3. **Given** the watermark removal succeeds, **When** the caller inspects the result, **Then** the result includes the mapped `watermarks.unset` identity, official quota cost, OAuth requirement context, channel context, and mutation acknowledgment without returning unrelated channel branding metadata.

---

### User Story 2 - Understand Quota, OAuth, and Removal Semantics Before Calling (Priority: P2)

As a client developer, I can inspect `watermarks_unset` before invoking it and immediately understand that it maps to `watermarks.unset`, costs 50 official quota units per call, requires eligible OAuth authorization, requires channel context, does not require media upload content, and removes an existing channel watermark when authorized and successful.

**Why this priority**: Watermark removal changes channel branding and consumes meaningful quota. Callers need quota, access, target-channel, no-upload, successful-acknowledgment, unsupported-behavior, and example guidance before they spend quota or remove branding on behalf of an authorized user.

**Independent Test**: Can be tested by reviewing the tool discovery entry, description, usage notes, and examples to confirm the public name, upstream identity, quota cost of `50`, OAuth-required access mode, required channel context, no-upload boundary, successful acknowledgment semantics, and unsupported behavior are visible before invocation.

**Acceptance Scenarios**:

1. **Given** a client developer discovers `watermarks_unset`, **When** they read the tool metadata and description, **Then** they can identify the public tool name, upstream resource and method, official quota-unit cost of `50`, OAuth requirement, removal behavior, required channel context, no-upload boundary, and availability state.
2. **Given** an example request is shown for `watermarks_unset`, **When** a caller reads the example, **Then** the quota cost of `50`, required OAuth authorization, required channel context, no-upload boundary, and expected acknowledgment result are visible alongside the request shape.
3. **Given** a caller expects watermark upload, watermark placement changes, channel branding lookup, banner upload, channel metadata updates, thumbnail changes, video operations, analytics, recommendation, or research enrichment, **When** they inspect the tool contract, **Then** they can tell those workflows are outside this low-level endpoint tool or belong to separate endpoint or higher-level features.

---

### User Story 3 - Reject Invalid, Under-Authorized, or Unsupported Removal Requests Clearly (Priority: P3)

As a caller, I receive clear validation and failure feedback when my `watermarks_unset` request omits required channel context, includes unsupported watermark-setting or upload payloads, lacks eligible OAuth authorization, targets a channel I cannot administer, targets a channel whose watermark cannot be removed, or asks for behavior outside the unset endpoint.

**Why this priority**: Watermark removal is mutation-oriented and authorization-sensitive. Clients must not confuse malformed input, missing authorization, unavailable channel context, insufficient permissions, quota failures, no-removal-possible outcomes, upstream refusal, and successful watermark removal.

**Independent Test**: Can be tested by submitting representative invalid or unsupported requests, including missing channel context, blank or malformed channel context, unsupported modifiers, watermark metadata, upload content, API-key-only access, missing OAuth authorization, unauthorized channel context, no-removal-possible outcomes, quota failure, upstream refusal, and out-of-scope workflow requests, then confirming each outcome is categorized with caller-facing guidance.

**Acceptance Scenarios**:

1. **Given** a caller omits required channel context, **When** they call `watermarks_unset`, **Then** the request is rejected with guidance identifying the missing required input.
2. **Given** a caller supplies blank, malformed, ambiguous, duplicate, unsupported, or otherwise unusable channel context, **When** they call `watermarks_unset`, **Then** the request is rejected or categorized according to the documented channel-context boundary with clear caller-facing guidance.
3. **Given** a caller includes watermark metadata, media upload content, or unsupported modifiers that belong to setting a watermark rather than removing one, **When** they call `watermarks_unset`, **Then** the request is rejected or clearly categorized as outside the unset contract.
4. **Given** a caller lacks eligible OAuth authorization or permission to administer the target channel, **When** they call `watermarks_unset`, **Then** the response clearly identifies the access or permission problem rather than presenting the request as a successful watermark removal.
5. **Given** a caller requests watermark upload, watermark metadata updates, channel lookup, channel metadata update, banner upload, thumbnail upload, video management, captions, playlists, comments, transcripts, analytics, recommendation, ranking, summarization, or enrichment behavior, **When** they call `watermarks_unset`, **Then** the request is rejected or clearly categorized as outside the low-level endpoint boundary.

### Edge Cases

- The caller omits channel context; the request must be rejected before it is treated as a watermark-removal operation.
- The caller provides blank, malformed, ambiguous, duplicate, deprecated, unsupported, or otherwise unusable channel context; the response must identify the supported channel-context boundary.
- The caller includes watermark placement metadata, display metadata, media-upload content, duplicate upload content, media-only content, or metadata-only content; the response must identify that upload and setting payloads are outside the unset request boundary.
- The caller attempts API-key-only access; the response must make clear that watermark removal requires eligible OAuth authorization.
- The caller has OAuth authorization but does not own, administer, or otherwise have permission to remove the target channel watermark; the response must distinguish permission failure from local validation, unavailable channel context, quota failure, upstream refusal, no-removal-possible outcomes, and successful removal.
- The target channel has no current watermark, is unavailable, policy-restricted, not eligible for watermark changes, or otherwise unavailable to the caller; the caller-facing result or error must preserve enough context to identify the affected channel according to shared Layer 2 conventions.
- The upstream service returns quota, authorization, forbidden, not-found, invalid request, policy, unavailable service, deprecated behavior, availability constraint, conflict, no-removal-possible, or unexpected failure; the caller-facing error must follow shared Layer 2 error conventions.
- A successful watermark-unset operation returns an empty upstream response; the public result must still provide a structured acknowledgment without inventing refreshed channel, branding, upload, or media metadata.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing contract checks showing that `watermarks_unset` is absent from Layer 2 discovery and incomplete unless it exposes the mapped `watermarks.unset` identity, official quota-unit cost of `50`, OAuth-required access mode, no-upload boundary, description-level quota visibility, and example-level quota visibility.
- **Red**: Add failing request-contract checks for missing channel context, blank or malformed channel context, ambiguous channel context, unsupported modifiers, watermark metadata payloads, media-upload payloads, missing OAuth authorization, API-key-only access, quota failure, unavailable or unauthorized channel context, no-removal-possible outcomes, upstream refusals, and out-of-scope workflow requests.
- **Red**: Add failing result-contract checks proving that successful watermark-removal acknowledgments, target channel context, quota context, access context, mapped operation identity, credential-safe outcomes, no-upload boundaries, and upstream error categories are represented according to shared Layer 2 conventions.
- **Green**: Deliver the smallest public `watermarks_unset` tool contract and behavior needed for callers to make supported low-level `watermarks.unset` requests and receive structured watermark-removal acknowledgments.
- **Green**: Include representative examples for successful authorized watermark removal, missing channel validation failure, malformed channel validation failure, unsupported modifier failure, unsupported metadata or upload failure, missing OAuth failure, insufficient permission failure, quota or upstream failure, unavailable channel failure, no-removal-possible outcome, and out-of-scope workflow rejection.
- **Refactor**: Remove endpoint-specific duplication that belongs to YT-201/YT-202 shared contracts while keeping the `watermarks_unset` request, response, quota, access, removal, no-upload, validation, error, and example surfaces easy to review. Final review evidence must include a passing focused test run, a passing full repository behavior check, and a passing repository quality check.
- **Required test levels**: Contract tests for discovery metadata and request/result shape, unit tests for channel context, OAuth, unsupported modifier, unsupported metadata and upload payloads, unavailable channel, permission, credential-safe output, no-removal-possible outcomes, and out-of-scope behavior validation, integration-style checks for representative successful and failed watermark removal paths, and documentation checks for quota/OAuth/no-upload/example visibility.
- **Documentation work**: Every new or changed callable behavior in scope must include stakeholder-readable reference documentation that explains its `watermarks_unset` responsibility, inputs, outputs, quota cost, OAuth behavior, removal semantics, no-upload boundary, unsupported behavior, failure categories, and result shape. Every new or changed Python function in scope must include a reStructuredText docstring describing purpose, required inputs, result meaning, and quota/access expectations where applicable.
- **Pull request evidence**: Review materials must show the matched seed slice `YT-255`, the dependency assumptions from YT-155/YT-201/YT-202, focused `watermarks_unset` test output, full-suite output, code-quality output, and any official-documentation or product-availability caveats recorded during the work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public Layer 2 MCP tool named `watermarks_unset`.
- **FR-002**: The `watermarks_unset` tool definition MUST identify its mapped upstream operation as YouTube resource `watermarks` and method `unset`.
- **FR-003**: The `watermarks_unset` tool metadata MUST record the official quota-unit cost of `50` per call.
- **FR-004**: The `watermarks_unset` tool description and usage examples MUST visibly state the official quota-unit cost of `50`.
- **FR-005**: The `watermarks_unset` tool metadata MUST state that the operation requires eligible OAuth authorization and MUST NOT present watermark removal as an API-key-only capability.
- **FR-006**: The `watermarks_unset` input contract MUST require supported channel context for each watermark-removal request.
- **FR-007**: The `watermarks_unset` input contract MUST document the supported channel-context boundary and any explicitly supported optional request modifiers.
- **FR-008**: The `watermarks_unset` input contract MUST document that media upload content, watermark placement metadata, and watermark display metadata are not required and are outside the supported unset request boundary.
- **FR-009**: The `watermarks_unset` input contract MUST reject missing channel context with clear caller-facing validation feedback.
- **FR-010**: The `watermarks_unset` input contract MUST reject or clearly categorize blank, malformed, ambiguous, duplicate, deprecated, unsupported, or otherwise unusable channel context according to the documented channel-context boundary.
- **FR-011**: The `watermarks_unset` input contract MUST reject unsupported optional parameters, unsupported modifiers, incompatible access context, watermark-setting payloads, media-upload payloads, and out-of-scope workflow requests with clear caller-facing validation feedback.
- **FR-012**: The `watermarks_unset` tool MUST reject or clearly categorize missing, invalid, or insufficient OAuth authorization as an access failure rather than a successful watermark removal.
- **FR-013**: The `watermarks_unset` tool MUST document OAuth requirements clearly, including any supported account, channel, or delegated content-owner access expectations available through the shared contract.
- **FR-014**: The `watermarks_unset` contract MUST document that successful completion is represented as a watermark-removal acknowledgment rather than as a refreshed channel resource, branding object, media record, or watermark lookup result.
- **FR-015**: The `watermarks_unset` contract MUST document applicable official limits and caveats, including quota cost, OAuth expectations, channel-context requirements, no-upload boundary, unsupported modifiers, unavailable channel behavior, no-removal-possible behavior, availability state, and failure categories.
- **FR-016**: The `watermarks_unset` result MUST provide a structured watermark-removal acknowledgment for successful requests.
- **FR-017**: The `watermarks_unset` result MUST preserve enough request and result context for callers to identify which channel context, authorization context, quota cost, mapped operation identity, and outcome produced each watermark-removal acknowledgment.
- **FR-018**: The `watermarks_unset` result MUST avoid exposing OAuth credentials, tokens, private authorization material, upload content, private media data, or sensitive access details in successful or failed watermark outcomes.
- **FR-019**: The `watermarks_unset` result MUST NOT fabricate refreshed channel branding metadata, watermark lookup results, banner state, media hosting URLs, analytics, recommendations, rankings, summaries, transcript text, enrichment details, or fields that are not returned by the watermark-unset operation or shared mutation acknowledgment contract.
- **FR-020**: The `watermarks_unset` result MUST preserve the distinction between successful watermark-removal acknowledgments and failures caused by validation, access, permission, quota, unavailable channel context, no-removal-possible outcomes, forbidden or policy constraints, invalid requests, conflict, service unavailability, deprecation, availability constraints, or unexpected upstream behavior.
- **FR-021**: The `watermarks_unset` tool MUST distinguish successful watermark-removal acknowledgments from validation failures, access failures, permission failures, quota failures, not-found failures, forbidden or policy failures, invalid request failures, conflict responses, unavailable service responses, no-removal-possible outcomes, deprecated behavior, availability constraints, upstream refusals, and unexpected upstream failures.
- **FR-022**: The `watermarks_unset` tool MUST surface upstream quota, authorization, forbidden, not-found, policy, invalid request, conflict, unavailable service, no-removal-possible, deprecated behavior, availability constraint, upstream refusal, and unexpected upstream failures according to the shared Layer 2 error conventions.
- **FR-023**: The `watermarks_unset` contract MUST remain close to the upstream `watermarks.unset` endpoint and MUST NOT add watermark upload, watermark placement updates, watermark display updates, channel lookup, channel metadata update, banner upload, thumbnail upload, video creation, video update, deletion, caption management, playlist management, comment management, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, automated branding workflows, or heuristic classification.
- **FR-024**: The `watermarks_unset` tool MUST comply with the Layer 2 naming, metadata, quota, access, availability, response-shaping, mutation result, validation, error, and example standards established by YT-201 and YT-202.
- **FR-025**: The `watermarks_unset` tool MUST rely on the existing Layer 1 `watermarks.unset` capability from YT-155 for endpoint behavior rather than redefining a separate upstream contract.
- **FR-026**: The feature MUST include caller-facing examples for successful authorized watermark removal, missing channel validation failure, malformed channel validation failure, ambiguous channel-context failure, unsupported modifier failure, unsupported metadata or upload failure, missing OAuth failure, insufficient permission failure, quota or upstream failure, unavailable channel failure, no-removal-possible outcome, and out-of-scope workflow request rejection.
- **FR-027**: The feature MUST include validation evidence that clients can discover, call, understand quota, OAuth, channel-context requirements, no-upload boundary, unsupported behavior, successful acknowledgment behavior, and failure behavior for `watermarks_unset` without consulting implementation-only artifacts.

### Key Entities

- **Watermarks Unset Tool**: The public Layer 2 MCP tool named `watermarks_unset`, representing one low-level endpoint-backed channel watermark removal mutation.
- **Watermark Removal Request**: The request shape that combines supported channel context and compatible access context for one watermark-removal attempt.
- **Channel Context**: The caller-provided or authorization-derived channel information needed to identify the channel whose watermark should be removed.
- **Access Context**: The caller access state required for OAuth-only watermark removal without exposing credentials or sensitive access details.
- **Watermark Removal Acknowledgment**: The structured successful outcome that preserves channel context, quota, access, mapped operation context, and mutation outcome.
- **Watermark Removal Outcome Classification**: The set of distinct outcome states that separate invalid requests, unsupported request shapes, unsupported setting or upload payloads, missing authorization, insufficient permissions, quota failures, unavailable channel context, no-removal-possible outcomes, upstream refusals, and successful removal acknowledgments.
- **Quota Disclosure**: The caller-facing statement that each `watermarks_unset` invocation costs 50 official quota units.
- **No-Upload Guidance**: The caller-facing explanation that `watermarks_unset` removes a watermark without accepting watermark image upload content, placement metadata, or display metadata.
- **Unsupported Boundary Guidance**: The caller-facing explanation that watermark upload, watermark placement changes, channel lookup, channel metadata updates, banner uploads, thumbnail updates, video workflows, captions, playlists, comments, transcripts, analytics, ranking, summarization, recommendations, and enrichment are outside this low-level watermark removal tool.

### Assumptions

- YT-155 provides the Layer 1 `watermarks.unset` capability that this public Layer 2 tool exposes.
- YT-201 and YT-202 provide the shared Layer 2 naming, metadata, quota, auth, response-shaping, mutation result, validation, error, example, and documentation standards this feature must follow.
- `watermarks_unset` is a low-level endpoint-backed tool for direct watermark removal, debugging, and power-user workflows; watermark upload belongs to `watermarks_set`, and broader branding, lookup, analytics, summarization, recommendation, and research workflows belong to separate features.
- OAuth-based access is required for every supported `watermarks_unset` request, with requests outside that access mode rejected or categorized rather than silently downgraded.
- The only required caller-supplied business input is supported channel context, with unsupported modifiers, watermark-setting metadata, and media-upload content rejected or clearly categorized unless the final shared contract explicitly documents them.
- A validly shaped authorized request can still receive an upstream refusal based on channel ownership, permissions, branding eligibility, current watermark state, policy state, quota state, service constraints, or resource availability, and that outcome should remain distinct from local validation failures and successful removal.
- Successful watermark-unset behavior for this slice is represented as a structured mutation acknowledgment rather than as a requirement to fetch and return full channel branding state.
- The official YouTube endpoint documentation and existing project inventory are the default sources for quota cost, access behavior, request boundaries, availability state, result behavior, and upstream error categories, with any discovered caveats recorded explicitly. The YT-255 seed identifies the official quota-unit cost as `50` for this public Layer 2 contract.

### Dependencies

- `YT-155` Layer 1 `watermarks.unset` wrapper is available for endpoint behavior.
- `YT-201` shared Layer 2 YouTube contracts are available for naming, request mapping, response, error, access, quota, layout, validation, mutation-result, and example conventions.
- `YT-202` Layer 2 metadata standards are available for public naming, quota, access, availability, description, example, and response-shaping rules.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `watermarks_unset` discovery metadata, descriptions, and examples produced by this feature display the mapped `watermarks.unset` identity and official quota-unit cost of `50`.
- **SC-002**: A client developer can determine in under 1 minute that `watermarks_unset` requires eligible OAuth authorization by reading the tool contract alone.
- **SC-003**: A client developer can identify the required channel context, no-upload boundary, unsupported modifiers, and successful acknowledgment behavior in under 2 minutes by reading the tool contract alone.
- **SC-004**: A power user can discover `watermarks_unset`, understand quota and access impact, identify the required channel context, and prepare a valid first watermark-removal request in under 3 minutes using only the public tool contract.
- **SC-005**: 100% of representative valid `watermarks_unset` requests return structured watermark-removal acknowledgments with channel context, quota context, access context, mapped operation identity, and outcome details preserved.
- **SC-006**: 100% of representative invalid watermark-removal requests that omit channel context, use blank or malformed channel context, include unsupported modifiers, include watermark metadata or upload content, lack eligible OAuth authorization, use API-key-only access, include incompatible access context, target unavailable or unauthorized channels, produce no-removal-possible outcomes, or request out-of-scope behavior are rejected or categorized with caller-facing feedback before being treated as successful removals.
- **SC-007**: 100% of representative quota, authorization, permission, forbidden, not-found, policy, invalid-request, conflict, unavailable-service, no-removal-possible, deprecated-behavior, availability-constrained, upstream-refusal, and unexpected upstream scenarios are distinguishable from successful watermark-removal acknowledgments and local validation failures.
- **SC-008**: Reviewers can verify in a single review pass that `watermarks_unset` complies with YT-201 and YT-202 Layer 2 naming, metadata, quota, OAuth, availability, mutation result, removal semantics, no-upload boundary, validation, error, and example standards.
- **SC-009**: Final review evidence includes passing focused `watermarks_unset` contract and validation checks, passing full repository behavior checks, and passing code-quality checks for the endpoint tool work.
