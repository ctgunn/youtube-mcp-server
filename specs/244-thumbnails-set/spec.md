# Feature Specification: Layer 2 Thumbnails Set Tool

**Feature Branch**: `244-thumbnails-set`  
**Created**: 2026-07-20  
**Status**: Draft  
**Input**: User description: "Read the PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-244, as outlined in spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Set a Video Thumbnail Through a Public Tool (Priority: P1)

As a power user or agent workflow author with eligible authorization, I can call the low-level `thumbnails_set` tool with a video identifier and thumbnail upload content so I can replace a video's custom thumbnail while staying close to the upstream `thumbnails.set` behavior.

**Why this priority**: This is the core value of YT-244. Layer 2 must expose endpoint-backed thumbnail setting for direct media-upload workflows, debugging, and later composition without turning the tool into video editing, thumbnail generation, image transformation, analytics, recommendation, ranking, summarization, or enrichment behavior.

**Independent Test**: Can be tested by invoking `thumbnails_set` with a valid video identifier, supported thumbnail upload content, and eligible OAuth-backed access, then confirming the caller receives a successful thumbnail-set result with request context, upload context, quota context, access context, and returned upstream context.

**Acceptance Scenarios**:

1. **Given** a caller provides a valid video identifier, supported thumbnail upload content, and eligible OAuth-backed access, **When** they call `thumbnails_set`, **Then** the system sets the custom thumbnail for the targeted video and returns a successful endpoint-backed result.
2. **Given** a thumbnail update succeeds, **When** the caller inspects the result, **Then** they can identify which video was targeted, that upload content was used, the mapped operation identity, and the quota context for the operation.
3. **Given** a caller wants low-level endpoint access, **When** they use `thumbnails_set`, **Then** the tool performs only the thumbnail setting operation and is not presented as thumbnail generation, image editing, video metadata update, video upload, analytics, recommendation, ranking, summarization, or research enrichment behavior.

---

### User Story 2 - Understand Cost, OAuth, and Upload Requirements Before Calling (Priority: P2)

As a client developer, I can inspect `thumbnails_set` before invoking it and immediately understand that it maps to `thumbnails.set`, costs 50 official quota units per call, requires OAuth-backed authorization, requires a video identifier, and requires supported media-upload content.

**Why this priority**: Thumbnail setting is an authorized media-upload operation with significant quota impact. Callers need cost, access, upload expectations, examples, and out-of-scope guidance before they spend quota or build automated workflows around custom thumbnail changes.

**Independent Test**: Can be tested by reviewing the tool discovery entry, description, usage notes, and examples to confirm the public name, upstream identity, quota cost of `50`, OAuth-backed access requirement, required video identifier, required upload content, supported upload boundary, expected result shape, and unsupported behavior are visible before invocation.

**Acceptance Scenarios**:

1. **Given** a client developer discovers `thumbnails_set`, **When** they read the tool metadata and description, **Then** they can identify the public tool name, upstream resource and method, official quota-unit cost of `50`, OAuth-backed authorization requirement, media-upload requirement, and availability state.
2. **Given** an example request is shown for `thumbnails_set`, **When** a caller reads the example, **Then** the quota cost of `50`, target video identifier, upload content expectation, OAuth-backed access expectation, and expected thumbnail-set result are visible alongside the request shape.
3. **Given** a caller needs thumbnail generation, image transformation, video metadata editing, video upload, channel branding, analytics, ranking, summarization, or enrichment, **When** they inspect the tool contract, **Then** they can tell those workflows are outside this low-level thumbnail-setting tool or belong to separate endpoint or higher-level features.

---

### User Story 3 - Reject Invalid or Under-Authorized Thumbnail Requests Clearly (Priority: P3)

As a caller, I receive clear validation and access feedback when my `thumbnails_set` request omits the video identifier, omits upload content, supplies unsupported upload content, lacks OAuth-backed access, targets an ineligible video, or asks for behavior outside the thumbnail-setting endpoint.

**Why this priority**: `thumbnails.set` mutates video presentation, uploads media, and consumes quota. Clear boundaries help callers distinguish malformed requests, unsupported uploads, access failures, target-video restrictions, quota failures, upstream rejections, and successful thumbnail updates without guessing which rule was violated.

**Independent Test**: Can be tested by submitting representative invalid or ineligible requests, including missing video identifier, missing upload content, unsupported upload content, missing OAuth-backed access, insufficient access to the target video, ineligible target video, quota or upstream rejection, and out-of-scope thumbnail-management requests, then confirming each failure is categorized with caller-facing guidance.

**Acceptance Scenarios**:

1. **Given** a caller omits the required video identifier or upload content, **When** they call `thumbnails_set`, **Then** the request is rejected with guidance identifying the missing required input.
2. **Given** a caller supplies malformed, empty, unsupported, or conflicting video identifier or upload inputs, **When** they call `thumbnails_set`, **Then** the request is rejected with guidance identifying the invalid or unsupported input.
3. **Given** a caller submits a validly shaped request without eligible OAuth-backed access, **When** they call `thumbnails_set`, **Then** the response distinguishes access failure from malformed input and from upstream thumbnail-update failure.
4. **Given** a valid OAuth-backed thumbnail request is rejected because the target video is missing, unavailable, not writable, ineligible for custom thumbnails, quota-limited, or otherwise rejected upstream, **When** the caller receives the response, **Then** the failure category is distinguishable from local validation failures and successful thumbnail-set outcomes.

### Edge Cases

- The caller provides a video identifier without thumbnail upload content, or upload content without a video identifier; the request must identify the missing required counterpart.
- The caller provides an empty, malformed, duplicate, conflicting, or unsupported video identifier; the response must identify invalid target input.
- The upload content is present but empty, malformed, unsupported, too ambiguous to classify, or outside the documented media-upload boundary; the response must identify the upload problem before treating the request as supported.
- The caller supplies video metadata changes, image transformation instructions, thumbnail generation prompts, paging controls, listing selectors, or other optional inputs that do not belong to thumbnail setting; the response must identify unsupported input rather than silently ignoring request ambiguity.
- The caller submits a validly shaped request without OAuth-backed access or with insufficient authorization for the target video; the response must identify access failure rather than reporting a successful thumbnail update.
- The target video no longer exists, is unavailable, is not writable by the authorized caller, or is not eligible for custom thumbnails.
- The upstream service accepts the thumbnail update but returns a sparse response; the result must preserve enough context for the caller to identify the target video and operation without fabricating missing thumbnail details.
- The upstream service returns quota, authorization, invalid request, upload rejection, missing resource, unavailable service, deprecated behavior, or unexpected failure; the caller-facing error must follow the shared Layer 2 error conventions.
- The caller expects thumbnail generation, image editing, video upload, video metadata updates, channel branding, analytics, recommendation, ranking, summarization, enrichment, or heuristic classification; the tool contract must keep those separate endpoint or higher-level behaviors out of scope.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing contract checks showing that `thumbnails_set` is absent from Layer 2 discovery and incomplete unless it exposes the mapped `thumbnails.set` identity, official quota-unit cost of `50`, OAuth-backed access disclosure, required video identifier, required media-upload guidance, description-level quota visibility, and example-level quota visibility.
- **Red**: Add failing request-contract checks for missing video identifier, invalid video identifier, missing upload content, unsupported upload content, unsupported optional inputs, missing or insufficient OAuth-backed access, target-video ineligibility, upload rejection categorization, and out-of-scope thumbnail or video-management requests.
- **Red**: Add failing result-contract checks proving that successful thumbnail-set results, target video context, upload context, quota context, access failures, validation failures, target-video failures, upload failures, and upstream error categories are represented according to the shared Layer 2 conventions.
- **Green**: Deliver the smallest public `thumbnails_set` tool contract and behavior needed for callers to make supported low-level `thumbnails.set` requests and receive clear thumbnail-set results.
- **Green**: Include representative examples for OAuth-backed thumbnail setting, successful sparse thumbnail-set results, missing video identifier validation failure, missing upload validation failure, invalid identifier validation failure, unsupported upload validation failure, authorization failure, target-video failure, quota or upstream upload failure, and out-of-scope thumbnail-management request rejection.
- **Refactor**: Remove endpoint-specific duplication that belongs to YT-201/YT-202 shared contracts while keeping the `thumbnails_set` request, response, quota, access, upload, validation, error, and example surfaces easy to review. Final review evidence must include a passing focused test run, a passing full repository behavior check, and a passing repository quality check.
- **Required test levels**: Contract tests for discovery metadata and request/result shape, unit tests for video identifier, upload requirement, unsupported-option, media-upload boundary, target-video, and access-boundary validation, integration-style checks for representative successful and failed thumbnail-setting paths, and documentation checks for quota/access/upload/example visibility.
- **Documentation work**: Every new or changed callable behavior in scope must include stakeholder-readable reference documentation that explains its `thumbnails_set` responsibility, inputs, outputs, quota cost, OAuth requirement, media-upload boundary, target-video behavior, unsupported behavior, result shape, and failure categories.
- **Pull request evidence**: Review materials must show the matched seed slice `YT-244`, the dependency assumptions from YT-144/YT-201/YT-202, focused `thumbnails_set` test output, full-suite output, code-quality output, and any official-documentation caveats recorded during the work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public Layer 2 MCP tool named `thumbnails_set`.
- **FR-002**: The `thumbnails_set` tool definition MUST identify its mapped upstream operation as YouTube resource `thumbnails` and method `set`.
- **FR-003**: The `thumbnails_set` tool metadata MUST record the official quota-unit cost of `50` per call.
- **FR-004**: The `thumbnails_set` tool description and usage examples MUST visibly state the official quota-unit cost of `50`.
- **FR-005**: The `thumbnails_set` tool metadata MUST state that the operation requires OAuth-backed authorization and MUST make that access requirement visible to callers before invocation.
- **FR-006**: The `thumbnails_set` input contract MUST require a video identifier for each thumbnail-setting request.
- **FR-007**: The `thumbnails_set` input contract MUST require supported thumbnail media-upload content for each thumbnail-setting request.
- **FR-008**: The `thumbnails_set` input contract MUST document which video identifier and upload inputs are supported, which upload expectations apply, and which request fields or modifiers are outside this tool's public contract.
- **FR-009**: The `thumbnails_set` input contract MUST reject missing, empty, malformed, ambiguous, duplicate, unsupported, or conflicting video identifier inputs with clear caller-facing validation feedback.
- **FR-010**: The `thumbnails_set` input contract MUST reject missing, empty, malformed, unsupported, ambiguous, or conflicting media-upload inputs with clear caller-facing validation feedback.
- **FR-011**: The `thumbnails_set` input contract MUST reject unsupported optional parameters, video metadata changes, thumbnail generation instructions, image transformation instructions, listing selectors, paging controls, and other out-of-scope modifiers with clear caller-facing validation feedback.
- **FR-012**: The `thumbnails_set` tool MUST reject or clearly categorize missing, invalid, expired, or insufficient OAuth-backed authorization as an access failure rather than a successful thumbnail-set result.
- **FR-013**: The `thumbnails_set` tool MUST reject or clearly categorize missing, unavailable, unwritable, custom-thumbnail-ineligible, or otherwise invalid target videos when determinable from validation or normalized upstream feedback.
- **FR-014**: The `thumbnails_set` result MUST preserve the thumbnail-set outcome, target video context, upload context, quota context, access context, mapped operation identity, and returned upstream context in a near-raw endpoint-backed shape.
- **FR-015**: The `thumbnails_set` result MUST preserve enough request and result context for callers to identify the video whose thumbnail was targeted even when the upstream response is sparse.
- **FR-016**: The `thumbnails_set` result MUST NOT fabricate thumbnail image details, video metadata, channel details, analytics, recommendation, ranking, summarization, or enrichment details that are not returned by the thumbnail-setting operation.
- **FR-017**: The `thumbnails_set` tool MUST distinguish successful thumbnail-set results from validation failures, access failures, target-video failures, unsupported upload failures, upstream upload rejections, quota failures, invalid request failures, unavailable service responses, deprecated behavior, and unexpected upstream failures.
- **FR-018**: The `thumbnails_set` tool MUST surface upstream quota, authorization, invalid request, upload rejection, missing resource, unavailable service, deprecated behavior, and unexpected upstream failures according to the shared Layer 2 error conventions.
- **FR-019**: The `thumbnails_set` contract MUST document applicable official limits and caveats, including quota cost, OAuth requirement, required video identifier, media-upload requirement, upload boundaries, target-video eligibility, unsupported modifier behavior, sparse-response behavior, and availability state.
- **FR-020**: The `thumbnails_set` contract MUST remain close to the upstream `thumbnails.set` endpoint and MUST NOT add thumbnail generation, image editing or transformation, video upload, video metadata updates, channel branding, analytics, recommendation, ranking, summarization, enrichment, or heuristic classification.
- **FR-021**: The `thumbnails_set` tool MUST comply with the Layer 2 naming, metadata, quota, access, availability, response-shaping, media-upload, mutation result, validation, error, and example standards established by YT-201 and YT-202.
- **FR-022**: The `thumbnails_set` tool MUST rely on the existing Layer 1 `thumbnails.set` capability from YT-144 for endpoint behavior rather than redefining a separate upstream contract.
- **FR-023**: The feature MUST include caller-facing examples for successful OAuth-backed thumbnail setting, sparse successful result handling, missing video identifier validation failure, missing upload validation failure, invalid video identifier validation failure, unsupported upload validation failure, missing authorization failure, target-video or quota upstream failure, and out-of-scope thumbnail-management request rejection.
- **FR-024**: The feature MUST include validation evidence that clients can discover, call, understand quota, OAuth, upload requirements, target-video boundaries, unsupported behavior, failure behavior, and thumbnail-set results for `thumbnails_set` without consulting implementation-only artifacts.

### Key Entities

- **Thumbnails Set Tool**: The public Layer 2 MCP tool named `thumbnails_set`, representing one low-level endpoint-backed thumbnail-setting operation.
- **Thumbnails Set Request**: The request shape centered on the required video identifier, required upload content, and any explicitly supported thumbnail-setting context.
- **Video Identifier**: The caller-supplied target identifier that selects the video whose custom thumbnail should be set.
- **Thumbnail Upload Content**: The caller-supplied media content used for the thumbnail-setting operation and constrained by the documented upload boundary.
- **Access Context**: The caller access state required to set custom thumbnails without exposing credentials or sensitive authorization details.
- **Target Video Eligibility**: The caller-facing classification of whether the selected video can receive a custom thumbnail through this operation.
- **Thumbnails Set Result**: The thumbnail-set outcome, target video context, upload context, quota context, access context, mapped operation identity, and returned upstream context produced by a successful `thumbnails_set` call.
- **Quota Disclosure**: The caller-facing statement that each `thumbnails_set` invocation costs 50 official quota units.
- **Unsupported Boundary Guidance**: The caller-facing explanation that thumbnail generation, image editing, video upload, video metadata updates, channel branding, analytics, ranking, summarization, and enrichment are outside this low-level thumbnail-setting tool.

### Assumptions

- YT-144 provides the Layer 1 `thumbnails.set` capability that this public Layer 2 tool exposes.
- YT-201 and YT-202 provide the shared Layer 2 naming, metadata, quota, access, response-shaping, media-upload, mutation result, validation, error, example, and documentation standards this feature must follow.
- `thumbnails_set` is a low-level endpoint-backed tool for direct custom thumbnail setting, debugging, and power-user workflows; thumbnail generation, image transformation, video upload, video metadata editing, channel branding, analytics, ranking, summarization, enrichment, and other higher-level workflows belong to separate endpoint or Layer 3 features.
- Thumbnail setting requires eligible OAuth-backed authorization because it mutates video presentation and uses media upload content.
- Supported behavior for this slice centers on one required video identifier plus one required thumbnail upload payload supplied on an authorized request.
- Optional upload modifiers are in scope only when the public tool contract explicitly documents them as supported; otherwise they remain outside the public boundary for this slice.
- A validly shaped authorized request can still receive an upstream rejection based on video ownership, video availability, custom-thumbnail eligibility, upload acceptability, quota state, or other resource-specific constraints, and that outcome should remain distinct from local validation failures.
- Successful thumbnail-set responses may be sparse and may not include a full thumbnail or video resource; the Layer 2 result preserves returned context without inventing missing details.
- The official YouTube endpoint documentation and existing project inventory are the default sources for `thumbnails.set` quota cost, OAuth behavior, identifier rules, upload requirements, availability state, and upstream error categories, with any discovered caveats recorded explicitly. The YT-244 seed identifies the official quota-unit cost as `50` for this public Layer 2 contract.

### Dependencies

- `YT-144` Layer 1 `thumbnails.set` wrapper is available for endpoint behavior.
- `YT-201` shared Layer 2 YouTube contracts are available for naming, request mapping, response, error, access, quota, layout, media-upload, and validation conventions.
- `YT-202` Layer 2 metadata standards are available for public naming, quota, access, availability, description, example, and response-shaping rules.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `thumbnails_set` discovery metadata, descriptions, and examples produced by this feature display the mapped `thumbnails.set` identity and official quota-unit cost of `50`.
- **SC-002**: A client developer can determine in under 1 minute that `thumbnails_set` requires OAuth-backed authorization and media-upload content by reading the tool contract alone.
- **SC-003**: A client developer can identify the required video identifier, required upload content, upload boundaries, target-video eligibility considerations, sparse-response behavior, and out-of-scope behaviors in under 2 minutes by reading the tool contract alone.
- **SC-004**: A power user can discover `thumbnails_set`, choose valid inputs, understand the quota and access impact, and prepare a valid first thumbnail-setting request in under 3 minutes using only the public tool contract.
- **SC-005**: 100% of representative valid `thumbnails_set` requests return thumbnail-set results with target video context, upload context, quota context, access context, mapped operation identity, and returned upstream context preserved.
- **SC-006**: 100% of representative invalid thumbnail-setting requests that omit the video identifier, omit upload content, use invalid identifiers, use unsupported upload content, include unsupported optional inputs, lack eligible OAuth-backed access, or request out-of-scope behavior are rejected or categorized with caller-facing feedback before being treated as successful endpoint requests.
- **SC-007**: 100% of representative target-video, upload rejection, quota, authorization, invalid-request, unavailable-service, deprecated-behavior, and unexpected upstream scenarios are distinguishable from successful thumbnail-set results and local validation failures.
- **SC-008**: Reviewers can verify in a single review pass that `thumbnails_set` complies with YT-201 and YT-202 Layer 2 naming, metadata, quota, access, availability, media-upload, mutation result, validation, error, and example standards.
- **SC-009**: Final review evidence includes passing focused `thumbnails_set` contract and validation checks, passing full repository behavior checks, and passing code-quality checks for the endpoint tool work.
