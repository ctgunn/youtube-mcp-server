# Feature Specification: Layer 2 Tool `videos_update`

**Feature Branch**: `249-videos-update`  
**Created**: 2026-07-21  
**Status**: Draft  
**Input**: User description: "Read the PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-249, as outlined in spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Update Video Resources Through a Public Endpoint Tool (Priority: P1)

As a power user or agent workflow author, I can call the low-level `videos_update` tool to update supported writable sections of an existing YouTube video resource while staying close to the upstream `videos.update` mutation behavior.

**Why this priority**: This is the core value of YT-249. Layer 2 must expose direct endpoint-backed `videos.update` behavior for raw endpoint access, debugging, and controlled video metadata/status workflows without turning the tool into a higher-level publishing, editing, or enrichment assistant.

**Independent Test**: Can be tested by invoking `videos_update` with eligible OAuth authorization, valid video identity, supported writable part selection, and a compatible video resource body, then confirming the caller receives an updated video result with mapped operation identity, quota context, access context, writable-part context, update body context, mutation outcome details, and returned video resource data preserved.

**Acceptance Scenarios**:

1. **Given** a caller has eligible OAuth authorization and provides a valid video identity, supported writable part selection, and compatible update body, **When** they call `videos_update`, **Then** the result includes the updated video resource in a near-raw endpoint-backed shape.
2. **Given** a caller provides optional supported delegation context for an eligible content owner, **When** the update succeeds, **Then** the result preserves the requested operation context, delegation context, quota context, access context, writable-part context, and returned video fields.
3. **Given** the update succeeds and the upstream operation returns a single video resource, **When** the caller inspects the result, **Then** the single-resource mutation outcome is clear and is not presented as a list, search, ranking, recommendation, analytics, upload, or transcript workflow.
4. **Given** a caller updates only explicitly supported writable parts, **When** the returned video resource contains a subset of requested or expected fields, **Then** the tool preserves returned fields without fabricating unchanged, omitted, or non-writable video data.

---

### User Story 2 - Understand Cost, OAuth, Writable Parts, and Update Semantics Before Calling (Priority: P2)

As a client developer, I can inspect `videos_update` before invoking it and immediately understand that it maps to `videos.update`, costs 50 official quota units per call, requires eligible OAuth authorization, updates only supported writable parts, and follows replacement-oriented endpoint semantics for included parts.

**Why this priority**: Video updates are quota-bearing, permission-sensitive mutations. Callers need quota, OAuth, writable-part, update body, examples, destructive-update caveats, and out-of-scope guidance before they spend quota or modify video resources.

**Independent Test**: Can be tested by reviewing the tool discovery entry, description, usage notes, and examples to confirm the public name, upstream identity, quota cost of `50`, OAuth-required access mode, supported writable parts, update body expectations, mutation semantics, delegation context, expected updated-resource result, and unsupported behavior are visible before invocation.

**Acceptance Scenarios**:

1. **Given** a client developer discovers `videos_update`, **When** they read the tool metadata and description, **Then** they can identify the public tool name, upstream resource and method, official quota-unit cost of `50`, OAuth requirement, supported writable parts, update body expectations, and availability state.
2. **Given** an example request is shown for `videos_update`, **When** a caller reads the example, **Then** the quota cost of `50`, required OAuth authorization, selected writable parts, update body shape, mutation semantics, and expected updated-video result are visible alongside the request shape.
3. **Given** a caller needs to update only selected mutable video fields, **When** they inspect the tool contract, **Then** they can tell which parts and fields are writable through this low-level tool and which requested parts may replace existing data for those included sections.
4. **Given** a caller expects media upload, transcoding, deletion, rating changes, thumbnails, captions, playlists, comments, analytics, recommendations, ranking, transcript extraction, summarization, or research enrichment, **When** they inspect the tool contract, **Then** they can tell those workflows are outside this low-level video update tool or belong to separate endpoint or higher-level features.

---

### User Story 3 - Reject Invalid or Unsupported Video Update Requests Clearly (Priority: P3)

As a caller, I receive clear validation and failure feedback when my `videos_update` request omits required identity, omits writable part selection, lacks eligible OAuth authorization, includes read-only or unsupported fields, or asks for behavior outside the update endpoint.

**Why this priority**: A malformed update can be expensive and can unintentionally replace video resource sections. Clear request boundaries help callers distinguish malformed input, insufficient access, unsupported writable-part requests, quota failures, upstream failures, and successful mutation outcomes.

**Independent Test**: Can be tested by submitting representative invalid or unsupported requests, including missing video identity, missing part selection, read-only parts, unsupported fields, incompatible update body, API-key-only access, missing OAuth authorization, incompatible delegation context, quota failures, and out-of-scope video workflows, then confirming each outcome is categorized with caller-facing guidance.

**Acceptance Scenarios**:

1. **Given** a caller omits the video identity or update body, **When** they call `videos_update`, **Then** the request is rejected with guidance identifying the missing required update input.
2. **Given** a caller omits part selection or includes non-writable, duplicate, conflicting, unknown, or unsupported parts, **When** they call `videos_update`, **Then** the request is rejected with guidance explaining the part-selection issue.
3. **Given** a caller lacks eligible OAuth authorization for the target video or delegated content-owner context, **When** they call `videos_update`, **Then** the response clearly identifies the access requirement rather than presenting the request as a missing resource or successful update.
4. **Given** a caller requests media upload, deletion, rating mutation, thumbnail management, caption management, playlist management, comment management, transcript retrieval, analytics, ranking, recommendation, summarization, or enrichment behavior, **When** they call `videos_update`, **Then** the request is rejected or clearly categorized as outside the low-level endpoint boundary.

### Edge Cases

- The caller omits video identity; the request must be rejected before it is treated as a supported video update attempt.
- The caller omits the update body or provides an update body that does not identify a supported video resource; the response must identify the missing update input.
- The caller omits required writable part selection; the request must be rejected before mutation behavior is attempted.
- The caller supplies empty, malformed, duplicate, conflicting, unknown, read-only, or unsupported part selections; the response must identify invalid part input.
- The caller supplies read-only fields, unsupported fields, malformed nested fields, or fields incompatible with the selected writable parts; the response must identify the update-body issue.
- The caller selects writable parts that are not represented by compatible fields in the update body; the response must identify the mismatch before treating the request as successful.
- The caller attempts API-key-only access; the response must make clear that video updates require eligible OAuth authorization.
- The caller has OAuth authorization but lacks permission to update the selected video, account, channel, or delegated owner; the response must distinguish access failure from missing resource, invalid body, and quota failure.
- The caller provides delegated content-owner context without eligible authorization or with incompatible target video ownership; the response must surface the delegation access requirement.
- The upstream service returns quota, authorization, forbidden, not-found, invalid request, policy, unavailable service, deprecated behavior, availability constraint, or unexpected failure; the caller-facing error must follow the shared Layer 2 error conventions.
- The updated video resource is returned with only a subset of requested or expected fields; the result must preserve returned fields without fabricating missing video metadata.
- The caller expects media upload, media replacement, transcoding, automatic publishing workflow, video deletion, rating mutation, thumbnail management, caption management, playlist management, comment management, transcript retrieval, analytics, recommendation, ranking, summarization, or enrichment; the tool contract must keep those separate endpoint or higher-level behaviors out of scope.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing contract checks showing that `videos_update` is absent from Layer 2 discovery and incomplete unless it exposes the mapped `videos.update` identity, official quota-unit cost of `50`, OAuth-required access mode, writable-part guidance, update semantics, description-level quota visibility, and example-level quota visibility.
- **Red**: Add failing request-contract checks for missing video identity, missing update body, missing part selection, read-only or unsupported parts, malformed part selection, selected parts missing from the update body, unsupported fields, missing OAuth authorization, incompatible delegation context, quota failure, and out-of-scope workflow requests.
- **Red**: Add failing result-contract checks proving that updated video resources, requested operation context, writable-part context, update body context, quota context, access context, delegation context where provided, mutation outcome details, and upstream error categories are represented according to the shared Layer 2 conventions.
- **Green**: Deliver the smallest public `videos_update` tool contract and behavior needed for callers to make supported low-level `videos.update` requests and receive near-raw updated video resource results.
- **Green**: Include representative examples for authorized metadata/status updates, delegated content-owner context where supported, missing identity validation failure, missing part validation failure, read-only part validation failure, incompatible update body failure, missing OAuth failure, quota or upstream failure, and out-of-scope workflow rejection.
- **Refactor**: Remove endpoint-specific duplication that belongs to YT-201/YT-202 shared contracts while keeping the `videos_update` request, response, quota, access, writable-part, update semantics, validation, error, and example surfaces easy to review. Final review evidence must include a passing focused test run, a passing full repository behavior check, and a passing repository quality check.
- **Required test levels**: Contract tests for discovery metadata and request/result shape, unit tests for video identity, part-selection, writable-field, update-body, OAuth, delegation, unsupported-option, and out-of-scope behavior validation, integration-style checks for representative successful and failed video update paths, and documentation checks for quota/OAuth/writable-part/example visibility.
- **Documentation work**: Every new or changed callable behavior in scope must include stakeholder-readable reference documentation that explains its `videos_update` responsibility, inputs, outputs, quota cost, OAuth behavior, writable-part constraints, update semantics, unsupported behavior, failure categories, and result shape.
- **Pull request evidence**: Review materials must show the matched seed slice `YT-249`, the dependency assumptions from YT-149/YT-201/YT-202, focused `videos_update` test output, full-suite output, code-quality output, and any official-documentation or product-availability caveats recorded during the work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public Layer 2 MCP tool named `videos_update`.
- **FR-002**: The `videos_update` tool definition MUST identify its mapped upstream operation as YouTube resource `videos` and method `update`.
- **FR-003**: The `videos_update` tool metadata MUST record the official quota-unit cost of `50` per call.
- **FR-004**: The `videos_update` tool description and usage examples MUST visibly state the official quota-unit cost of `50`.
- **FR-005**: The `videos_update` tool metadata MUST state that the operation requires eligible OAuth authorization and MUST NOT present video updates as an API-key-only capability.
- **FR-006**: The `videos_update` input contract MUST preserve the upstream concepts of required video identity, required writable part selection, compatible video resource body, supported update options, and supported delegation context where those concepts are available through the Layer 1 dependency.
- **FR-007**: The `videos_update` input contract MUST require video identity, supported writable part selection, and a compatible update body for each update request.
- **FR-008**: The `videos_update` input contract MUST document which video parts and fields are writable for this low-level tool and which requested parts may replace existing data within those included sections.
- **FR-009**: The `videos_update` input contract MUST document update semantics clearly enough that callers understand the effect of including, omitting, or mismatching writable parts and update body fields.
- **FR-010**: The `videos_update` input contract MUST reject missing video identity with clear caller-facing validation feedback.
- **FR-011**: The `videos_update` input contract MUST reject missing, empty, malformed, duplicate, unsupported, read-only, ambiguous, or conflicting part selections with clear caller-facing validation feedback.
- **FR-012**: The `videos_update` input contract MUST reject missing, empty, malformed, unsupported, read-only, or part-incompatible update body fields with clear caller-facing validation feedback.
- **FR-013**: The `videos_update` input contract MUST reject unsupported optional parameters, unsupported modifiers, incompatible delegation context, and out-of-scope workflow requests with clear caller-facing validation feedback.
- **FR-014**: The `videos_update` tool MUST reject or clearly categorize missing, invalid, or insufficient OAuth authorization as an access failure rather than a successful or public video update result.
- **FR-015**: The `videos_update` tool MUST document OAuth requirements clearly, including any supported account, channel, or delegated content-owner access expectations.
- **FR-016**: The `videos_update` contract MUST document applicable official limits and caveats, including quota cost, OAuth expectations, writable-part rules, replacement-oriented update semantics for included parts, unsupported field behavior, availability state, and failure categories.
- **FR-017**: The `videos_update` result MUST preserve the updated video resource, requested part context, update body context, quota context, access context, delegation context where applicable, mapped operation identity, mutation outcome details, and returned upstream fields in a near-raw endpoint-backed shape.
- **FR-018**: The `videos_update` result MUST preserve enough request and result context for callers to identify which video identity, part selection, update body, authorization context, and optional supported settings produced the update outcome.
- **FR-019**: The `videos_update` result MUST NOT fabricate video metadata, media state, upload state, publication workflow state, thumbnails, captions, playlists, transcript text, analytics, recommendations, ranking, summaries, enrichment details, or fields that are not returned by the video update operation.
- **FR-020**: The `videos_update` tool MUST distinguish successful video updates from validation failures, access failures, quota failures, not-found failures, forbidden or policy failures, invalid request failures, unavailable service responses, deprecated behavior, availability constraints, and unexpected upstream failures.
- **FR-021**: The `videos_update` tool MUST surface upstream quota, authorization, forbidden, not-found, policy, invalid request, unavailable service, deprecated behavior, availability constraint, and unexpected upstream failures according to the shared Layer 2 error conventions.
- **FR-022**: The `videos_update` contract MUST remain close to the upstream `videos.update` endpoint and MUST NOT add media upload, media replacement, transcoding, automatic publishing workflow, video creation, deletion, rating mutation, thumbnail management, caption management, playlist management, comment management, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, automated research synthesis, or heuristic classification.
- **FR-023**: The `videos_update` tool MUST comply with the Layer 2 naming, metadata, quota, access, availability, response-shaping, mutation result, writable-part, validation, error, and example standards established by YT-201 and YT-202.
- **FR-024**: The `videos_update` tool MUST rely on the existing Layer 1 `videos.update` capability from YT-149 for endpoint behavior rather than redefining a separate upstream contract.
- **FR-025**: The feature MUST include caller-facing examples for authorized metadata/status update, delegated content-owner context where supported, missing identity validation failure, missing part validation failure, read-only part validation failure, incompatible update body failure, missing OAuth failure, quota or upstream failure, and out-of-scope workflow request rejection.
- **FR-026**: The feature MUST include validation evidence that clients can discover, call, understand quota, OAuth, writable-part requirements, update semantics, unsupported behavior, updated-resource results, and failure behavior for `videos_update` without consulting implementation-only artifacts.

### Key Entities

- **Videos Update Tool**: The public Layer 2 MCP tool named `videos_update`, representing one low-level endpoint-backed video update operation.
- **Video Update Request**: The request shape that combines video identity, supported writable part selection, compatible video resource body, and any compatible optional update or delegation settings.
- **Video Identity**: The caller-provided identifier for the existing video resource targeted by the update.
- **Writable Part Selection**: The caller-selected video resource sections eligible for update through this contract.
- **Update Body**: The caller-provided video resource fields intended to update the selected writable parts.
- **Update Body Context**: The caller-facing record of which supported fields and selected writable parts shaped the update attempt.
- **Access Context**: The caller access state required for OAuth-only video updates without exposing credentials or sensitive access details.
- **Updated Video Resource Result**: The returned video resource and operation context produced by a successful `videos_update` call.
- **Quota Disclosure**: The caller-facing statement that each `videos_update` invocation costs 50 official quota units.
- **OAuth Requirement Disclosure**: The caller-facing indication that video updates require eligible OAuth authorization and may require valid delegated content-owner context for some requests.
- **Unsupported Boundary Guidance**: The caller-facing explanation that upload, creation, deletion, rating, thumbnails, captions, playlists, comments, transcripts, analytics, ranking, summarization, recommendations, and enrichment are outside this low-level video update tool.

### Assumptions

- YT-149 provides the Layer 1 `videos.update` capability that this public Layer 2 tool exposes.
- YT-201 and YT-202 provide the shared Layer 2 naming, metadata, quota, auth, response-shaping, mutation result, validation, error, example, and documentation standards this feature must follow.
- `videos_update` is a low-level endpoint-backed tool for direct video metadata/status mutation, debugging, and power-user workflows; media upload, publishing workflows, transcript retrieval, analytics, ranking, summarization, recommendation, and other higher-level research workflows belong to separate endpoint or Layer 3 features.
- OAuth-based access is required for every supported `videos_update` request, with requests outside that access mode rejected or categorized rather than silently downgraded.
- Supported behavior for this slice centers on updating only video resource parts and fields allowed by the Layer 1 `videos.update` dependency and the official endpoint contract.
- Callers need clear replacement-oriented update semantics for included writable parts so they do not unintentionally remove or overwrite fields by sending incomplete update bodies.
- The official YouTube endpoint documentation and existing project inventory are the default sources for quota cost, access behavior, writable-part rules, update semantics, availability state, mutation result behavior, and upstream error categories, with any discovered caveats recorded explicitly. The YT-249 seed identifies the official quota-unit cost as `50` for this public Layer 2 contract.

### Dependencies

- `YT-149` Layer 1 `videos.update` wrapper is available for endpoint behavior.
- `YT-201` shared Layer 2 YouTube contracts are available for naming, request mapping, response, error, access, quota, layout, validation, mutation, and example conventions.
- `YT-202` Layer 2 metadata standards are available for public naming, quota, access, availability, description, example, and response-shaping rules.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `videos_update` discovery metadata, descriptions, and examples produced by this feature display the mapped `videos.update` identity and official quota-unit cost of `50`.
- **SC-002**: A client developer can determine in under 1 minute that `videos_update` requires eligible OAuth authorization by reading the tool contract alone.
- **SC-003**: A client developer can identify required video identity, writable part selection, update body expectations, update semantics, unsupported field boundaries, and failure categories in under 2 minutes by reading the tool contract alone.
- **SC-004**: A power user can discover `videos_update`, understand quota and access impact, identify required update inputs, and prepare a valid first video update request in under 3 minutes using only the public tool contract.
- **SC-005**: 100% of representative valid `videos_update` requests return updated-video results with requested part context, update body context, quota context, access context, mapped operation identity, mutation outcome details, and returned upstream fields preserved.
- **SC-006**: 100% of representative invalid video update requests that omit video identity, omit update body, omit part selection, use invalid or read-only part selection, include unsupported fields, mismatch selected parts and update body, lack eligible OAuth authorization, include incompatible delegation context, or request out-of-scope behavior are rejected or categorized with caller-facing feedback before being treated as successful endpoint requests.
- **SC-007**: 100% of representative quota, authorization, forbidden, not-found, policy, invalid-request, unavailable-service, deprecated-behavior, availability-constrained, and unexpected upstream scenarios are distinguishable from successful video updates and local validation failures.
- **SC-008**: Reviewers can verify in a single review pass that `videos_update` complies with YT-201 and YT-202 Layer 2 naming, metadata, quota, OAuth, availability, mutation result, writable-part, validation, error, and example standards.
- **SC-009**: Final review evidence includes passing focused `videos_update` contract and validation checks, passing full repository behavior checks, and passing code-quality checks for the endpoint tool work.
