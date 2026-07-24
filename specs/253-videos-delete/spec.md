# Feature Specification: Layer 2 Tool `videos_delete`

**Feature Branch**: `253-videos-delete`  
**Created**: 2026-07-24  
**Status**: Draft  
**Input**: User description: "Read the PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-253, as outlined in spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Delete a Video Through a Public Endpoint Tool (Priority: P1)

As a power user or agent workflow author, I can call the low-level `videos_delete` tool to delete an authorized target video while staying close to the upstream `videos.delete` behavior.

**Why this priority**: This is the core value of YT-253. Layer 2 must expose direct endpoint-backed video deletion for advanced client automation, debugging, and raw endpoint access without turning the tool into a higher-level content-management workflow.

**Independent Test**: Can be tested by invoking `videos_delete` with eligible OAuth authorization and a target video identity, then confirming the caller receives a structured deletion acknowledgment with mapped operation identity, quota context, access context, target context, and mutation outcome preserved.

**Acceptance Scenarios**:

1. **Given** a caller has eligible OAuth authorization and provides a valid target video identity for a deletable video, **When** they call `videos_delete`, **Then** the result confirms the delete operation was accepted or completed for that target.
2. **Given** a successful delete operation returns no refreshed video resource, **When** the caller inspects the result, **Then** the result still preserves enough request context to identify which video deletion was acknowledged.
3. **Given** the delete operation succeeds, **When** the caller inspects the result, **Then** the result includes the mapped `videos.delete` identity, official quota cost, OAuth requirement context, and mutation acknowledgment without returning unrelated video metadata.

---

### User Story 2 - Understand Quota, OAuth, and Destructive Semantics Before Calling (Priority: P2)

As a client developer, I can inspect `videos_delete` before invoking it and immediately understand that it maps to `videos.delete`, costs 50 official quota units per call, requires eligible OAuth authorization, requires a target video identity, and performs a destructive mutation.

**Why this priority**: Deletion is irreversible from the caller's perspective and has meaningful quota cost. Callers need quota, access, target-input, destructive-action, successful-acknowledgment, unsupported-behavior, and example guidance before they spend quota or delete content on behalf of an authorized user.

**Independent Test**: Can be tested by reviewing the tool discovery entry, description, usage notes, and examples to confirm the public name, upstream identity, quota cost of `50`, OAuth-required access mode, required target video identity, destructive-action warning, successful acknowledgment semantics, and unsupported behavior are visible before invocation.

**Acceptance Scenarios**:

1. **Given** a client developer discovers `videos_delete`, **When** they read the tool metadata and description, **Then** they can identify the public tool name, upstream resource and method, official quota-unit cost of `50`, OAuth requirement, destructive nature, required target video identity, and availability state.
2. **Given** an example request is shown for `videos_delete`, **When** a caller reads the example, **Then** the quota cost of `50`, required OAuth authorization, target video identity, destructive-action guidance, and expected acknowledgment result are visible alongside the request shape.
3. **Given** a caller expects video lookup, update, upload, rating, abuse reporting, caption, thumbnail, playlist, transcript, analytics, recommendation, or recovery behavior, **When** they inspect the tool contract, **Then** they can tell those workflows are outside this low-level endpoint tool or belong to separate endpoint or higher-level features.

---

### User Story 3 - Reject Invalid, Under-Authorized, or Unsupported Delete Requests Clearly (Priority: P3)

As a caller, I receive clear validation and failure feedback when my `videos_delete` request omits the required target video identity, includes unsupported request modifiers, lacks eligible OAuth authorization, targets a video I cannot delete, or asks for behavior outside the delete endpoint.

**Why this priority**: Video deletion is destructive and authorization-sensitive. Clients must not confuse malformed input, missing authorization, unavailable content, insufficient permissions, quota failures, unsupported behavior, upstream refusal, and successful deletion.

**Independent Test**: Can be tested by submitting representative invalid or unsupported requests, including missing target video identity, blank or malformed target identity, unsupported modifiers, API-key-only access, missing OAuth authorization, non-owned or unavailable target videos, quota failure, and out-of-scope workflow requests, then confirming each outcome is categorized with caller-facing guidance.

**Acceptance Scenarios**:

1. **Given** a caller omits the target video identity, **When** they call `videos_delete`, **Then** the request is rejected with guidance identifying the missing required input.
2. **Given** a caller supplies a blank, malformed, duplicate, unsupported, or otherwise unusable target video identity, **When** they call `videos_delete`, **Then** the request is rejected or categorized according to the documented target identity boundary with clear caller-facing guidance.
3. **Given** a caller lacks eligible OAuth authorization or permission to delete the target video, **When** they call `videos_delete`, **Then** the response clearly identifies the access or permission problem rather than presenting the request as a successful deletion.
4. **Given** a caller requests listing, metadata updates, rating, abuse reporting, upload replacement, captions, thumbnails, playlists, transcripts, analytics, recommendation, recovery, or policy-review behavior, **When** they call `videos_delete`, **Then** the request is rejected or clearly categorized as outside the low-level endpoint boundary.

### Edge Cases

- The caller omits the target video identity; the request must be rejected before it is treated as a delete operation.
- The caller provides a blank, malformed, duplicate, deprecated, unsupported, or otherwise unusable target video identity; the response must identify the supported target identity boundary.
- The caller attempts API-key-only access; the response must make clear that deletion requires eligible OAuth authorization.
- The caller has OAuth authorization but does not own, administer, or otherwise have permission to delete the target video; the response must distinguish permission failure from local validation, unavailable target, quota failure, upstream refusal, and successful deletion.
- The target video is private, removed, region-restricted, age-restricted, policy-restricted, already deleted, or otherwise unavailable to the caller; the caller-facing result or error must preserve enough context to identify the affected target according to shared Layer 2 conventions.
- The upstream service returns quota, authorization, forbidden, not-found, invalid request, policy, unavailable service, deprecated behavior, availability constraint, conflict, or unexpected failure; the caller-facing error must follow shared Layer 2 error conventions.
- The caller expects a returned refreshed video resource, video recovery, metadata lookup, rating, abuse reporting, uploads, media replacement, thumbnail management, caption management, playlist management, comment management, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, or policy review; the tool contract must keep those separate endpoint or higher-level behaviors out of scope.
- A successful delete operation returns an empty upstream response; the public result must still provide a structured acknowledgment without inventing a refreshed video resource.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing contract checks showing that `videos_delete` is absent from Layer 2 discovery and incomplete unless it exposes the mapped `videos.delete` identity, official quota-unit cost of `50`, OAuth-required access mode, destructive-action guidance, description-level quota visibility, and example-level quota visibility.
- **Red**: Add failing request-contract checks for missing target video identity, blank or malformed target identity, unsupported modifiers, missing OAuth authorization, API-key-only access, quota failure, unavailable target videos, insufficient permission, upstream refusals, and out-of-scope workflow requests.
- **Red**: Add failing result-contract checks proving that successful deletion acknowledgments, deleted target context, quota context, access context, mapped operation identity, credential-safe outcomes, and upstream error categories are represented according to shared Layer 2 conventions.
- **Green**: Deliver the smallest public `videos_delete` tool contract and behavior needed for callers to make supported low-level `videos.delete` requests and receive structured deletion acknowledgment results.
- **Green**: Include representative examples for successful authorized deletion, missing target validation failure, malformed target failure, unsupported modifier failure, missing OAuth failure, insufficient permission failure, quota or upstream failure, unavailable target failure, and out-of-scope workflow rejection.
- **Refactor**: Remove endpoint-specific duplication that belongs to YT-201/YT-202 shared contracts while keeping the `videos_delete` request, response, quota, access, destructive-action, validation, error, and example surfaces easy to review. Final review evidence must include a passing focused test run, a passing full repository behavior check, and a passing repository quality check.
- **Required test levels**: Contract tests for discovery metadata and request/result shape, unit tests for target video identity, OAuth, unsupported modifier, unavailable target, permission, credential-safe output, and out-of-scope behavior validation, integration-style checks for representative successful and failed video deletion paths, and documentation checks for quota/OAuth/destructive-action/example visibility.
- **Documentation work**: Every new or changed callable behavior in scope must include stakeholder-readable reference documentation that explains its `videos_delete` responsibility, inputs, outputs, quota cost, OAuth behavior, destructive-action semantics, unsupported behavior, failure categories, and result shape. Every new or changed Python function in scope must include a reStructuredText docstring describing purpose, required inputs, result meaning, and quota/access expectations where applicable.
- **Pull request evidence**: Review materials must show the matched seed slice `YT-253`, the dependency assumptions from YT-153/YT-201/YT-202, focused `videos_delete` test output, full-suite output, code-quality output, and any official-documentation or product-availability caveats recorded during the work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public Layer 2 MCP tool named `videos_delete`.
- **FR-002**: The `videos_delete` tool definition MUST identify its mapped upstream operation as YouTube resource `videos` and method `delete`.
- **FR-003**: The `videos_delete` tool metadata MUST record the official quota-unit cost of `50` per call.
- **FR-004**: The `videos_delete` tool description and usage examples MUST visibly state the official quota-unit cost of `50`.
- **FR-005**: The `videos_delete` tool metadata MUST state that the operation requires eligible OAuth authorization and MUST NOT present deletion as an API-key-only capability.
- **FR-006**: The `videos_delete` input contract MUST require a target video identity for each delete request.
- **FR-007**: The `videos_delete` input contract MUST document the supported target video identity boundary and any explicitly supported optional request modifiers.
- **FR-008**: The `videos_delete` input contract MUST reject missing target video identity with clear caller-facing validation feedback.
- **FR-009**: The `videos_delete` input contract MUST reject or clearly categorize blank, malformed, duplicate, deprecated, unsupported, or otherwise unusable target video identities according to the documented target identity boundary.
- **FR-010**: The `videos_delete` input contract MUST reject unsupported optional parameters, unsupported modifiers, incompatible access context, and out-of-scope workflow requests with clear caller-facing validation feedback.
- **FR-011**: The `videos_delete` tool MUST reject or clearly categorize missing, invalid, or insufficient OAuth authorization as an access failure rather than a successful deletion.
- **FR-012**: The `videos_delete` tool MUST document OAuth requirements clearly, including any supported account, channel, or delegated content-owner access expectations available through the shared contract.
- **FR-013**: The `videos_delete` contract MUST document that deletion is a destructive mutation and that successful completion is represented as a deletion acknowledgment rather than as a refreshed video resource.
- **FR-014**: The `videos_delete` contract MUST document applicable official limits and caveats, including quota cost, OAuth expectations, target video requirements, unsupported modifiers, destructive-action semantics, unavailable target behavior, availability state, and failure categories.
- **FR-015**: The `videos_delete` result MUST provide a structured deletion acknowledgment for successful requests.
- **FR-016**: The `videos_delete` result MUST preserve enough request and result context for callers to identify which target video, authorization context, quota cost, mapped operation identity, and outcome produced each deletion acknowledgment.
- **FR-017**: The `videos_delete` result MUST avoid exposing OAuth credentials, tokens, private authorization material, or sensitive access details in successful or failed deletion outcomes.
- **FR-018**: The `videos_delete` result MUST preserve the distinction between successful deletion acknowledgments and failures caused by validation, access, permission, quota, unavailable target, forbidden or policy constraints, invalid requests, conflict, service unavailability, deprecation, availability constraints, or unexpected upstream behavior.
- **FR-019**: The `videos_delete` tool MUST distinguish successful deletion acknowledgments from validation failures, access failures, permission failures, quota failures, not-found failures, forbidden or policy failures, invalid request failures, conflict responses, unavailable service responses, deprecated behavior, availability constraints, upstream refusals, and unexpected upstream failures.
- **FR-020**: The `videos_delete` tool MUST surface upstream quota, authorization, forbidden, not-found, policy, invalid request, conflict, unavailable service, deprecated behavior, availability constraint, upstream refusal, and unexpected upstream failures according to the shared Layer 2 error conventions.
- **FR-021**: The `videos_delete` contract MUST remain close to the upstream `videos.delete` endpoint and MUST NOT add video listing, metadata lookup, metadata update, media upload, media replacement, transcoding, automatic publishing workflow, rating mutation, rating lookup, abuse reporting, abuse-reason discovery, thumbnail management, caption management, playlist management, comment management, transcript retrieval, analytics, recommendation, ranking, summarization, enrichment, recovery, policy review, or automated content-management behavior.
- **FR-022**: The `videos_delete` tool MUST comply with the Layer 2 naming, metadata, quota, access, availability, response-shaping, mutation result, validation, error, and example standards established by YT-201 and YT-202.
- **FR-023**: The `videos_delete` tool MUST rely on the existing Layer 1 `videos.delete` capability from YT-153 for endpoint behavior rather than redefining a separate upstream contract.
- **FR-024**: The feature MUST include caller-facing examples for successful authorized deletion, missing target validation failure, malformed target validation failure, unsupported modifier failure, missing OAuth failure, insufficient permission failure, quota or upstream failure, unavailable target failure, and out-of-scope workflow request rejection.
- **FR-025**: The feature MUST include validation evidence that clients can discover, call, understand quota, OAuth, destructive-action semantics, unsupported behavior, successful acknowledgment behavior, and failure behavior for `videos_delete` without consulting implementation-only artifacts.

### Key Entities *(include if feature involves data)*

- **Videos Delete Tool**: The public Layer 2 MCP tool named `videos_delete`, representing one low-level endpoint-backed video deletion mutation operation.
- **Video Deletion Request**: The request shape that combines the required target video identity, any explicitly supported optional modifiers, and compatible access context.
- **Video Identity**: The caller-provided identifier for the video being deleted.
- **Access Context**: The caller access state required for OAuth-only video deletion without exposing credentials or sensitive access details.
- **Deletion Acknowledgment**: The structured successful outcome that preserves target video identity, quota, access, mapped operation context, and mutation outcome.
- **Deletion Outcome Classification**: The set of distinct outcome states that separate invalid requests, unsupported request shapes, missing authorization, insufficient permissions, quota failures, unavailable targets, upstream refusals, and successful deletion acknowledgments.
- **Quota Disclosure**: The caller-facing statement that each `videos_delete` invocation costs 50 official quota units.
- **Destructive-Action Guidance**: The caller-facing explanation that `videos_delete` deletes the target video when authorized and successful, and does not provide recovery, replacement, metadata lookup, or higher-level content-management behavior.
- **Unsupported Boundary Guidance**: The caller-facing explanation that video lookup, update, upload, replacement, rating, abuse reporting, captions, thumbnails, playlists, comments, transcripts, analytics, recommendation, recovery, summarization, enrichment, and policy review are outside this low-level video deletion tool.

### Assumptions

- YT-153 provides the Layer 1 `videos.delete` capability that this public Layer 2 tool exposes.
- YT-201 and YT-202 provide the shared Layer 2 naming, metadata, quota, auth, response-shaping, mutation result, validation, error, example, and documentation standards this feature must follow.
- `videos_delete` is a low-level endpoint-backed tool for direct deletion, debugging, and power-user workflows; video recovery, metadata lookup, content replacement, broader content management, analytics, ranking, recommendation, summarization, and research workflows belong to separate features.
- OAuth-based access is required for every supported `videos_delete` request, with requests outside that access mode rejected or categorized rather than silently downgraded.
- The only required caller-supplied business input is the target video identity, with unsupported modifiers rejected or clearly categorized unless the final shared contract explicitly documents them.
- A validly shaped authorized request can still receive an upstream refusal based on ownership, permissions, policy state, video availability, deletion eligibility, quota state, or service constraints, and that outcome should remain distinct from local validation failures and successful deletion.
- Successful deletion behavior for this slice is represented as a structured mutation acknowledgment rather than as a requirement to fetch and return a refreshed video resource.
- The official YouTube endpoint documentation and existing project inventory are the default sources for quota cost, access behavior, request boundaries, availability state, result behavior, and upstream error categories, with any discovered caveats recorded explicitly. The YT-253 seed identifies the official quota-unit cost as `50` for this public Layer 2 contract.

### Dependencies

- `YT-153` Layer 1 `videos.delete` wrapper is available for endpoint behavior.
- `YT-201` shared Layer 2 YouTube contracts are available for naming, request mapping, response, error, access, quota, layout, validation, mutation-result, and example conventions.
- `YT-202` Layer 2 metadata standards are available for public naming, quota, access, availability, description, example, and response-shaping rules.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `videos_delete` discovery metadata, descriptions, and examples produced by this feature display the mapped `videos.delete` identity and official quota-unit cost of `50`.
- **SC-002**: A client developer can determine in under 1 minute that `videos_delete` requires eligible OAuth authorization by reading the tool contract alone.
- **SC-003**: A client developer can identify the required target video input, destructive-action semantics, unsupported modifiers, and successful acknowledgment behavior in under 2 minutes by reading the tool contract alone.
- **SC-004**: A power user can discover `videos_delete`, understand quota and access impact, identify the required target input, and prepare a valid first delete request in under 3 minutes using only the public tool contract.
- **SC-005**: 100% of representative valid `videos_delete` requests return structured deletion acknowledgments with target video identity, quota context, access context, mapped operation identity, and outcome details preserved.
- **SC-006**: 100% of representative invalid delete requests that omit target video identity, use blank or malformed target identity, include unsupported modifiers, lack eligible OAuth authorization, use API-key-only access, include incompatible access context, target unavailable or non-owned videos, or request out-of-scope behavior are rejected or categorized with caller-facing feedback before being treated as successful deletions.
- **SC-007**: 100% of representative quota, authorization, permission, forbidden, not-found, policy, invalid-request, conflict, unavailable-service, deprecated-behavior, availability-constrained, upstream-refusal, and unexpected upstream scenarios are distinguishable from successful deletion acknowledgments and local validation failures.
- **SC-008**: Reviewers can verify in a single review pass that `videos_delete` complies with YT-201 and YT-202 Layer 2 naming, metadata, quota, OAuth, availability, mutation result, destructive-action, validation, error, and example standards.
- **SC-009**: Final review evidence includes passing focused `videos_delete` contract and validation checks, passing full repository behavior checks, and passing code-quality checks for the endpoint tool work.
