# Feature Specification: Layer 2 Tool `watermarks_set`

**Feature Branch**: `254-watermarks-set`  
**Created**: 2026-07-24  
**Status**: Draft  
**Input**: User description: "Read the PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-254, as outlined in spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Set a Channel Watermark Through a Public Endpoint Tool (Priority: P1)

As a power user or agent workflow author, I can call the low-level `watermarks_set` tool to set an authorized channel watermark while staying close to the upstream `watermarks.set` upload behavior.

**Why this priority**: This is the core value of YT-254. Layer 2 must expose direct endpoint-backed channel watermark updates for advanced client automation, debugging, and raw endpoint access without turning the tool into a broader channel-branding workflow.

**Independent Test**: Can be tested by invoking `watermarks_set` with eligible OAuth authorization, a supported channel identity, watermark placement metadata, and supported watermark upload content, then confirming the caller receives a structured watermark-update acknowledgment with mapped operation identity, quota context, access context, upload context, and outcome details preserved.

**Acceptance Scenarios**:

1. **Given** a caller has eligible OAuth authorization and provides a supported channel identity, watermark metadata, and upload content, **When** they call `watermarks_set`, **Then** the result confirms that the watermark update was accepted or completed for that channel.
2. **Given** a successful watermark update returns no refreshed channel resource, **When** the caller inspects the result, **Then** the result still preserves enough request context to identify which channel and watermark settings were acknowledged.
3. **Given** the watermark update succeeds, **When** the caller inspects the result, **Then** the result includes the mapped `watermarks.set` identity, official quota cost, OAuth requirement context, media-upload context, and mutation acknowledgment without returning unrelated channel branding metadata.

---

### User Story 2 - Understand Quota, OAuth, and Upload Requirements Before Calling (Priority: P2)

As a client developer, I can inspect `watermarks_set` before invoking it and immediately understand that it maps to `watermarks.set`, costs 50 official quota units per call, requires eligible OAuth authorization, and requires both watermark metadata and media-upload content.

**Why this priority**: Watermark updates change channel branding, require authorized access, include media upload, and consume meaningful quota. Callers need quota, access, input, media boundary, example, and unsupported-behavior guidance before they spend quota or alter channel branding on behalf of an authorized user.

**Independent Test**: Can be tested by reviewing the tool discovery entry, description, usage notes, and examples to confirm the public name, upstream identity, quota cost of `50`, OAuth-required access mode, required channel identity, watermark metadata, required upload content, supported upload boundaries, expected acknowledgment result, and unsupported behavior are visible before invocation.

**Acceptance Scenarios**:

1. **Given** a client developer discovers `watermarks_set`, **When** they read the tool metadata and description, **Then** they can identify the public tool name, upstream resource and method, official quota-unit cost of `50`, OAuth requirement, required channel identity, required watermark metadata, required media upload, and availability state.
2. **Given** an example request is shown for `watermarks_set`, **When** a caller reads the example, **Then** the quota cost of `50`, required OAuth authorization, required watermark metadata, required upload content, supported upload boundary, and expected acknowledgment result are visible alongside the request shape.
3. **Given** a caller expects watermark removal, channel branding lookup, banner upload, channel metadata updates, thumbnail changes, video operations, analytics, recommendation, or research enrichment, **When** they inspect the tool contract, **Then** they can tell those workflows are outside this low-level endpoint tool or belong to separate endpoint or higher-level features.

---

### User Story 3 - Reject Invalid, Under-Authorized, or Unsupported Watermark Requests Clearly (Priority: P3)

As a caller, I receive clear validation and failure feedback when my `watermarks_set` request omits required channel context, omits watermark metadata, omits upload content, provides unsupported media, lacks eligible OAuth authorization, targets a channel I cannot administer, or asks for behavior outside the set endpoint.

**Why this priority**: Watermark updates are upload-sensitive and authorization-sensitive mutations. Clients must not confuse malformed input, missing authorization, unsupported media, unavailable channel context, insufficient permissions, quota failures, upstream refusal, and successful watermark updates.

**Independent Test**: Can be tested by submitting representative invalid or unsupported requests, including missing channel identity, blank or malformed channel identity, missing watermark metadata, incomplete timing or position metadata, missing upload content, unsupported upload content, API-key-only access, missing OAuth authorization, unauthorized channel context, quota failure, upstream refusal, and out-of-scope workflow requests, then confirming each outcome is categorized with caller-facing guidance.

**Acceptance Scenarios**:

1. **Given** a caller omits the required channel identity, watermark metadata, or upload content, **When** they call `watermarks_set`, **Then** the request is rejected with guidance identifying the missing required input.
2. **Given** a caller supplies blank, malformed, incomplete, incompatible, unsupported, or otherwise unusable channel, watermark metadata, or upload input, **When** they call `watermarks_set`, **Then** the request is rejected or categorized according to the documented request boundary with clear caller-facing guidance.
3. **Given** a caller lacks eligible OAuth authorization or permission to update the target channel watermark, **When** they call `watermarks_set`, **Then** the response clearly identifies the access or permission problem rather than presenting the request as a successful watermark update.
4. **Given** a caller requests watermark removal, channel lookup, channel metadata update, banner upload, thumbnail upload, video management, captions, playlists, comments, transcripts, analytics, recommendation, ranking, summarization, or enrichment behavior, **When** they call `watermarks_set`, **Then** the request is rejected or clearly categorized as outside the low-level endpoint boundary.

### Edge Cases

- The caller omits channel identity; the request must be rejected before it is treated as a watermark update.
- The caller provides a blank, malformed, ambiguous, duplicate, deprecated, unsupported, or otherwise unusable channel identity; the response must identify the supported channel identity boundary.
- The caller omits watermark placement or display metadata, or provides metadata with missing, inconsistent, deprecated, unsupported, or incompatible timing and position values; the response must identify the supported watermark metadata boundary.
- The caller provides watermark metadata without upload content, or upload content without watermark metadata; the response must distinguish metadata-only and media-only requests from supported watermark-set requests.
- The caller provides upload content whose format, size, media type, or representation falls outside the supported upload boundary; the response must identify the media-upload problem without exposing private media data.
- The caller attempts API-key-only access; the response must make clear that setting a watermark requires eligible OAuth authorization.
- The caller has OAuth authorization but does not own, administer, or otherwise have permission to update the target channel watermark; the response must distinguish permission failure from local validation, unavailable channel context, quota failure, upstream refusal, and successful update.
- The target channel is unavailable, policy-restricted, not eligible for watermark updates, or otherwise unavailable to the caller; the caller-facing result or error must preserve enough context to identify the affected channel according to shared Layer 2 conventions.
- The upstream service returns quota, authorization, forbidden, not-found, invalid request, policy, unsupported media, upload, unavailable service, deprecated behavior, availability constraint, conflict, or unexpected failure; the caller-facing error must follow shared Layer 2 error conventions.
- A successful watermark-set operation returns an empty upstream response; the public result must still provide a structured acknowledgment without inventing refreshed channel, branding, or media metadata.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing contract checks showing that `watermarks_set` is absent from Layer 2 discovery and incomplete unless it exposes the mapped `watermarks.set` identity, official quota-unit cost of `50`, OAuth-required access mode, media-upload requirement, watermark metadata requirement, description-level quota visibility, and example-level quota visibility.
- **Red**: Add failing request-contract checks for missing channel identity, blank or malformed channel identity, missing watermark metadata, incomplete or unsupported timing and position metadata, missing media upload, unsupported media upload, unsupported modifiers, missing OAuth authorization, API-key-only access, quota failure, unavailable or unauthorized channel context, upstream refusals, and out-of-scope workflow requests.
- **Red**: Add failing result-contract checks proving that successful watermark-update acknowledgments, target channel context, watermark metadata context, media-upload context, quota context, access context, mapped operation identity, credential-safe outcomes, and upstream error categories are represented according to shared Layer 2 conventions.
- **Green**: Deliver the smallest public `watermarks_set` tool contract and behavior needed for callers to make supported low-level `watermarks.set` requests and receive structured watermark-update acknowledgments.
- **Green**: Include representative examples for successful authorized watermark update, missing channel validation failure, malformed channel validation failure, missing metadata failure, unsupported metadata failure, missing upload failure, unsupported upload failure, unsupported modifier failure, missing OAuth failure, insufficient permission failure, quota or upstream failure, unavailable channel failure, and out-of-scope workflow rejection.
- **Refactor**: Remove endpoint-specific duplication that belongs to YT-201/YT-202 shared contracts while keeping the `watermarks_set` request, response, quota, access, upload, metadata, validation, error, and example surfaces easy to review. Final review evidence must include a passing focused test run, a passing full repository behavior check, and a passing repository quality check.
- **Required test levels**: Contract tests for discovery metadata and request/result shape, unit tests for channel identity, watermark metadata, media-upload boundary, OAuth, unsupported modifier, unavailable channel, permission, credential-safe output, and out-of-scope behavior validation, integration-style checks for representative successful and failed watermark update paths, and documentation checks for quota/OAuth/media-upload/example visibility.
- **Documentation work**: Every new or changed callable behavior in scope must include stakeholder-readable reference documentation that explains its `watermarks_set` responsibility, inputs, outputs, quota cost, OAuth behavior, media-upload expectations, unsupported behavior, failure categories, and result shape. Every new or changed Python function in scope must include a reStructuredText docstring describing purpose, required inputs, result meaning, and quota/access expectations where applicable.
- **Pull request evidence**: Review materials must show the matched seed slice `YT-254`, the dependency assumptions from YT-154/YT-201/YT-202, focused `watermarks_set` test output, full-suite output, code-quality output, and any official-documentation or product-availability caveats recorded during the work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public Layer 2 MCP tool named `watermarks_set`.
- **FR-002**: The `watermarks_set` tool definition MUST identify its mapped upstream operation as YouTube resource `watermarks` and method `set`.
- **FR-003**: The `watermarks_set` tool metadata MUST record the official quota-unit cost of `50` per call.
- **FR-004**: The `watermarks_set` tool description and usage examples MUST visibly state the official quota-unit cost of `50`.
- **FR-005**: The `watermarks_set` tool metadata MUST state that the operation requires eligible OAuth authorization and MUST NOT present watermark updates as an API-key-only capability.
- **FR-006**: The `watermarks_set` input contract MUST preserve the upstream concepts of target channel identity, watermark metadata, media-upload content, and supported access context where those concepts are available through the Layer 1 dependency.
- **FR-007**: The `watermarks_set` input contract MUST require channel identity, watermark metadata, and one supported media upload for each watermark-set request.
- **FR-008**: The `watermarks_set` input contract MUST document the supported channel identity boundary and any explicitly supported optional request modifiers.
- **FR-009**: The `watermarks_set` input contract MUST document the supported watermark metadata boundary, including the timing, position, and display fields that callers may provide.
- **FR-010**: The `watermarks_set` input contract MUST document the supported media-upload boundary, including accepted upload representation, media-type expectations, size expectations, and unsupported upload shapes.
- **FR-011**: The `watermarks_set` input contract MUST reject missing channel identity with clear caller-facing validation feedback.
- **FR-012**: The `watermarks_set` input contract MUST reject missing watermark metadata, incomplete watermark metadata, unsupported watermark timing, unsupported watermark position, or incompatible display metadata with clear caller-facing validation feedback.
- **FR-013**: The `watermarks_set` input contract MUST reject missing media upload, unsupported media type, oversized media, unreadable media, duplicate media, media-only requests, metadata-only requests, or otherwise unsupported media-upload shapes with clear caller-facing validation feedback.
- **FR-014**: The `watermarks_set` input contract MUST reject unsupported optional parameters, unsupported modifiers, incompatible access context, and out-of-scope workflow requests with clear caller-facing validation feedback.
- **FR-015**: The `watermarks_set` tool MUST reject or clearly categorize missing, invalid, or insufficient OAuth authorization as an access failure rather than a successful watermark update.
- **FR-016**: The `watermarks_set` tool MUST document OAuth requirements clearly, including any supported account, channel, or delegated content-owner access expectations available through the shared contract.
- **FR-017**: The `watermarks_set` contract MUST document applicable official limits and caveats, including quota cost, OAuth expectations, target channel requirements, watermark metadata requirements, media-upload requirements, unsupported modifiers, unavailable channel behavior, availability state, and failure categories.
- **FR-018**: The `watermarks_set` result MUST provide a structured watermark-update acknowledgment for successful requests.
- **FR-019**: The `watermarks_set` result MUST preserve enough request and result context for callers to identify which channel identity, watermark metadata, media-upload descriptor, authorization context, quota cost, mapped operation identity, and outcome produced each watermark-update acknowledgment.
- **FR-020**: The `watermarks_set` result MUST avoid exposing OAuth credentials, tokens, private authorization material, raw private media data, upload secrets, or sensitive access details in successful or failed watermark outcomes.
- **FR-021**: The `watermarks_set` result MUST NOT fabricate refreshed channel branding metadata, watermark lookup results, banner state, media hosting URLs, analytics, recommendations, rankings, summaries, transcript text, enrichment details, or fields that are not returned by the watermark-set operation or shared mutation acknowledgment contract.
- **FR-022**: The `watermarks_set` tool MUST distinguish successful watermark-update acknowledgments from validation failures, access failures, permission failures, quota failures, not-found failures, forbidden or policy failures, invalid request failures, unsupported-media failures, upload failures, conflict responses, unavailable service responses, deprecated behavior, availability constraints, upstream refusals, and unexpected upstream failures.
- **FR-023**: The `watermarks_set` tool MUST surface upstream quota, authorization, forbidden, not-found, policy, invalid request, unsupported media, upload, conflict, unavailable service, deprecated behavior, availability constraint, upstream refusal, and unexpected upstream failures according to the shared Layer 2 error conventions.
- **FR-024**: The `watermarks_set` contract MUST remain close to the upstream `watermarks.set` endpoint and MUST NOT add watermark removal, watermark lookup, channel lookup, channel metadata update, banner upload, thumbnail upload, video creation, video update, deletion, caption management, playlist management, comment management, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, automated branding workflows, or heuristic classification.
- **FR-025**: The `watermarks_set` tool MUST comply with the Layer 2 naming, metadata, quota, access, availability, response-shaping, mutation result, upload result, validation, error, and example standards established by YT-201 and YT-202.
- **FR-026**: The `watermarks_set` tool MUST rely on the existing Layer 1 `watermarks.set` capability from YT-154 for endpoint behavior rather than redefining a separate upstream contract.
- **FR-027**: The feature MUST include caller-facing examples for successful authorized watermark update, missing channel validation failure, malformed channel validation failure, missing metadata failure, unsupported metadata failure, missing upload failure, unsupported upload failure, unsupported modifier failure, missing OAuth failure, insufficient permission failure, quota or upstream failure, unavailable channel failure, and out-of-scope workflow request rejection.
- **FR-028**: The feature MUST include validation evidence that clients can discover, call, understand quota, OAuth, media-upload requirements, watermark metadata requirements, unsupported behavior, successful acknowledgment behavior, and failure behavior for `watermarks_set` without consulting implementation-only artifacts.

### Key Entities

- **Watermarks Set Tool**: The public Layer 2 MCP tool named `watermarks_set`, representing one low-level endpoint-backed channel watermark update operation.
- **Watermark Set Request**: The request shape that combines target channel identity, watermark metadata, media-upload content, and any compatible access or delegation context.
- **Channel Identity**: The caller-provided identifier for the channel whose watermark is being updated.
- **Watermark Metadata**: The caller-provided timing, position, and display information used to describe how the uploaded watermark should appear.
- **Watermark Upload Payload**: The upload-specific content supplied for the watermark image, including enough safe descriptor information for validation and result context without exposing private media content.
- **Access Context**: The caller access state required for OAuth-only watermark updates without exposing credentials or sensitive access details.
- **Watermark Update Acknowledgment**: The structured successful outcome that preserves channel identity, watermark metadata context, upload descriptor context, quota, access, mapped operation context, and mutation outcome.
- **Watermark Outcome Classification**: The set of distinct outcome states that separate invalid requests, unsupported metadata, unsupported upload content, missing authorization, insufficient permissions, quota failures, unavailable channel context, upstream refusals, and successful watermark updates.
- **Quota Disclosure**: The caller-facing statement that each `watermarks_set` invocation costs 50 official quota units.
- **Media-Upload Guidance**: The caller-facing explanation of required upload content, supported media boundaries, and unsupported media-only or metadata-only request shapes.
- **Unsupported Boundary Guidance**: The caller-facing explanation that watermark removal, channel lookup, channel metadata updates, banner uploads, thumbnail updates, video workflows, captions, playlists, comments, transcripts, analytics, ranking, summarization, recommendations, and enrichment are outside this low-level watermark-set tool.

### Assumptions

- YT-154 provides the Layer 1 `watermarks.set` capability that this public Layer 2 tool exposes.
- YT-201 and YT-202 provide the shared Layer 2 naming, metadata, quota, auth, response-shaping, mutation result, upload result, validation, error, example, and documentation standards this feature must follow.
- `watermarks_set` is a low-level endpoint-backed tool for direct watermark upload and update, debugging, and power-user workflows; watermark removal belongs to `watermarks_unset`, and broader branding, lookup, analytics, summarization, recommendation, and research workflows belong to separate features.
- OAuth-based access is required for every supported `watermarks_set` request, with requests outside that access mode rejected or categorized rather than silently downgraded.
- Supported behavior for this slice centers on one target channel identity, one watermark metadata payload, and one media-upload payload per request. Unsupported modifiers are rejected or clearly categorized unless the final shared contract explicitly documents them.
- A validly shaped authorized request can still receive an upstream refusal based on channel ownership, permissions, branding eligibility, upload eligibility, policy state, quota state, service constraints, or resource availability, and that outcome should remain distinct from local validation failures and successful watermark updates.
- Successful watermark-set behavior for this slice is represented as a structured mutation or upload acknowledgment rather than as a requirement to fetch and return full channel branding state.
- The official YouTube endpoint documentation and existing project inventory are the default sources for quota cost, access behavior, media-upload boundaries, watermark metadata boundaries, availability state, result behavior, and upstream error categories, with any discovered caveats recorded explicitly. The YT-254 seed identifies the official quota-unit cost as `50` for this public Layer 2 contract.

### Dependencies

- `YT-154` Layer 1 `watermarks.set` wrapper is available for endpoint behavior.
- `YT-201` shared Layer 2 YouTube contracts are available for naming, request mapping, response, error, access, quota, layout, validation, mutation-result, upload-result, and example conventions.
- `YT-202` Layer 2 metadata standards are available for public naming, quota, access, availability, description, example, and response-shaping rules.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `watermarks_set` discovery metadata, descriptions, and examples produced by this feature display the mapped `watermarks.set` identity and official quota-unit cost of `50`.
- **SC-002**: A client developer can determine in under 1 minute that `watermarks_set` requires eligible OAuth authorization by reading the tool contract alone.
- **SC-003**: A client developer can identify the required channel identity, watermark metadata, required media upload, supported upload boundary, unsupported modifiers, and successful acknowledgment behavior in under 2 minutes by reading the tool contract alone.
- **SC-004**: A power user can discover `watermarks_set`, understand quota and access impact, identify required watermark inputs, and prepare a valid first watermark-set request in under 3 minutes using only the public tool contract.
- **SC-005**: 100% of representative valid `watermarks_set` requests return structured watermark-update acknowledgments with channel identity, watermark metadata context, upload descriptor context, quota context, access context, mapped operation identity, and outcome details preserved.
- **SC-006**: 100% of representative invalid watermark-set requests that omit channel identity, use blank or malformed channel identity, omit watermark metadata, use unsupported watermark metadata, omit media upload, use unsupported media upload, lack eligible OAuth authorization, use API-key-only access, include incompatible access context, target unavailable or unauthorized channels, or request out-of-scope behavior are rejected or categorized with caller-facing feedback before being treated as successful updates.
- **SC-007**: 100% of representative quota, authorization, permission, forbidden, not-found, policy, invalid-request, unsupported-media, upload-failure, conflict, unavailable-service, deprecated-behavior, availability-constrained, upstream-refusal, and unexpected upstream scenarios are distinguishable from successful watermark-update acknowledgments and local validation failures.
- **SC-008**: Reviewers can verify in a single review pass that `watermarks_set` complies with YT-201 and YT-202 Layer 2 naming, metadata, quota, OAuth, availability, upload result, mutation result, validation, error, and example standards.
- **SC-009**: Final review evidence includes passing focused `watermarks_set` contract and validation checks, passing full repository behavior checks, and passing code-quality checks for the endpoint tool work.
