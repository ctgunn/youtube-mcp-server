# Feature Specification: Layer 2 Tool `channels_update`

**Feature Branch**: `211-channels-update`  
**Created**: 2026-06-09  
**Status**: Draft  
**Input**: User description: "Read the PRD.md to get an overview of the project and its goals for context. Then, work on the requirements for YT-211, as outlined in spec-kit-seed.md."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Update Supported Channel Settings Through a Public Tool (Priority: P1)

As a power user, I can call the low-level `channels_update` tool to update supported writable channel settings while staying close to the upstream `channels.update` operation and receiving the updated channel resource outcome.

**Why this priority**: This is the core value of YT-211. Layer 2 must expose direct endpoint-backed channel updates for power users, debugging, and channel-management workflows without turning the tool into a higher-level branding wizard, analytics workflow, or composed channel-management tool.

**Independent Test**: Can be tested by invoking `channels_update` with eligible authorization, a supported writable part, and an aligned channel resource body, then confirming the result preserves the updated channel resource, selected writable part, quota context, and mapped endpoint identity.

**Acceptance Scenarios**:

1. **Given** a caller has eligible channel-management authorization and provides a valid channel update for `brandingSettings`, **When** they call `channels_update`, **Then** the system applies the update and returns an updated channel resource result.
2. **Given** a caller has eligible channel-management authorization and provides a valid channel update for `localizations`, **When** they call `channels_update`, **Then** the system applies the update and returns an updated channel resource result.
3. **Given** a caller provides a valid `brandingSettings.image.bannerExternalUrl` value obtained from a prior banner upload flow, **When** they call `channels_update`, **Then** the system treats it as a channel update request and does not imply that banner upload itself happened in this tool.

---

### User Story 2 - Understand Cost, Access, and Writable Boundaries Before Calling (Priority: P2)

As a client developer, I can inspect `channels_update` before invoking it and immediately understand that it maps to `channels.update`, costs 50 official quota units per call, requires eligible OAuth authorization, and only supports documented writable channel parts for this slice.

**Why this priority**: Channel updates are quota-sensitive and modify live channel configuration. Callers need cost, access, and writable-part visibility before they attempt a mutation.

**Independent Test**: Can be tested by reviewing the tool discovery entry, description, usage notes, and examples to confirm the public name, upstream identity, quota cost of `50`, OAuth-required access, supported writable parts, read-only exclusions, and availability state are visible before invocation.

**Acceptance Scenarios**:

1. **Given** a client developer discovers `channels_update`, **When** they read the tool metadata and description, **Then** they can identify the public tool name, upstream resource and method, official quota-unit cost of `50`, OAuth-required auth mode, availability state, and supported writable parts.
2. **Given** an example request is shown for `channels_update`, **When** a caller reads the example, **Then** the quota cost of `50`, OAuth requirement, selected writable part, and required channel body alignment are visible alongside the request shape.
3. **Given** a caller wants to update a read-only channel field or unsupported resource part, **When** they inspect the tool contract, **Then** they can tell that request is outside the supported `channels_update` boundary.

---

### User Story 3 - Reject Unsupported or Ineligible Channel Updates Clearly (Priority: P3)

As a caller, I receive clear validation or access feedback when my `channels_update` request lacks eligible authorization, omits required update content, selects unsupported writable parts, or attempts read-only channel changes.

**Why this priority**: Mutation tools need clear failure boundaries so callers do not accidentally retry invalid writes, confuse access failures with malformed update bodies, or assume unsupported fields were partially applied.

**Independent Test**: Can be tested by submitting representative invalid requests, including missing authorization, missing `part`, missing channel body, part-to-body mismatches, unsupported parts, read-only fields, and ineligible channel access, then confirming each failure is categorized with caller-facing guidance.

**Acceptance Scenarios**:

1. **Given** a caller lacks eligible OAuth authorization, **When** they call `channels_update`, **Then** the request is rejected with an access-related response rather than being treated as a public channel operation.
2. **Given** a caller selects `brandingSettings` but omits matching `brandingSettings` content from the channel body, **When** they call `channels_update`, **Then** the request is rejected with guidance that selected parts must align with body content.
3. **Given** a caller includes read-only or unsupported channel fields in the update body, **When** they call `channels_update`, **Then** the request is rejected or clearly flagged before it is treated as a supported update.

### Edge Cases

- A caller provides no `part`, no channel body, an empty channel body, or no target channel identifier; the request must be rejected before it is treated as a supported update.
- A caller selects a writable part that is not supported by this slice; the response must identify the unsupported writable boundary.
- A caller selects `brandingSettings` or `localizations` but the channel body omits the matching field; the response must identify the part-to-body mismatch.
- A caller mixes supported writable fields with read-only or unrelated channel fields; the request must not silently drop unsupported data.
- A caller has valid OAuth credentials but lacks permission to update the targeted channel; the response must distinguish channel-management ineligibility from invalid request shape.
- A caller attempts to use `channels_update` for channel lookup, channel search, channel analytics, banner upload, playlist expansion, video expansion, or multi-step branding orchestration; the tool contract must keep those behaviors out of scope.
- The upstream service returns quota, authorization, invalid request, missing channel, unavailable service, or unexpected upstream failure; the caller-facing result must follow the shared Layer 2 error conventions.

## Test Strategy (Red-Green-Refactor) *(mandatory)*

- **Red**: Start with failing contract checks showing that `channels_update` is absent from Layer 2 discovery and incomplete unless it exposes the mapped `channels.update` identity, official quota-unit cost of `50`, OAuth-required auth mode, active availability state, description-level quota visibility, example-level quota visibility, and writable-part guidance.
- **Red**: Add failing request-contract checks for required `part`, required channel body, target channel identity, supported writable parts, part-to-body alignment, unsupported parts, read-only fields, missing authorization, and ineligible channel-management access.
- **Red**: Add failing result-contract checks proving that updated channel resource content, selected writable parts, mutation context, quota context, and shared Layer 2 error categories are represented according to the endpoint-backed response convention.
- **Green**: Deliver the smallest public `channels_update` tool contract and behavior needed for callers to make supported low-level `channels.update` requests and receive near-raw updated channel outcomes.
- **Green**: Include representative examples for a `brandingSettings` update, a `localizations` update, a banner URL activation update, a missing authorization failure, a part-to-body mismatch, and a read-only field rejection.
- **Refactor**: Remove endpoint-specific duplication that belongs to YT-201/YT-202 shared contracts while keeping the `channels_update` request, response, quota, auth, writable-part, and example expectations easy to review. Final review evidence must include `pytest` with a passing result and `ruff check .` with a passing result.
- **Required test levels**: Contract tests for discovery metadata and request/result shape, unit tests for writable-part and body validation, integration-style checks for representative successful and failed channel update paths, and documentation checks for quota/auth/writable-part/example visibility.
- **Docstring work**: Every new or changed Python function in scope must include a reStructuredText docstring that explains its `channels_update` responsibility, inputs, outputs, quota cost, OAuth behavior, writable-part constraints, and failure-boundary behavior.
- **Pull request evidence**: Review materials must show the matched seed slice `YT-211`, the dependency assumptions from YT-111/YT-201/YT-202, focused `channels_update` test output, full-suite command output, lint output, and any official-documentation caveats recorded during the work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST expose a public Layer 2 MCP tool named `channels_update`.
- **FR-002**: The `channels_update` tool definition MUST identify its mapped upstream operation as YouTube resource `channels` and method `update`.
- **FR-003**: The `channels_update` tool metadata MUST record the official quota-unit cost of `50` per call.
- **FR-004**: The `channels_update` tool description and usage examples MUST visibly state the official quota-unit cost of `50`.
- **FR-005**: The `channels_update` tool metadata MUST state OAuth-required auth mode and make clear that public-only access is unsupported for channel updates.
- **FR-006**: The `channels_update` input contract MUST require the caller to provide a selected writable resource part and an aligned channel resource body for one update attempt.
- **FR-007**: The `channels_update` input contract MUST document supported writable parts for this slice, including `brandingSettings` and `localizations`.
- **FR-008**: The `channels_update` input contract MUST require enough channel body context to identify the targeted channel and the writable fields being changed.
- **FR-009**: The `channels_update` tool MUST reject missing, empty, unsupported, malformed, or read-only update shapes with clear caller-facing validation feedback.
- **FR-010**: The `channels_update` tool MUST reject selected writable parts that do not align with the channel body fields supplied by the caller.
- **FR-011**: The `channels_update` tool MUST reject requests when eligible OAuth authorization or channel-management access is unavailable, using the shared Layer 2 auth error convention.
- **FR-012**: The `channels_update` result MUST preserve the updated channel resource content, selected writable parts, source operation identity, quota context, and relevant request context in a near-raw endpoint-backed shape.
- **FR-013**: The `channels_update` tool MUST surface upstream quota, authorization, missing channel, invalid request, unavailable service, and unexpected upstream failures according to the shared Layer 2 error conventions.
- **FR-014**: The `channels_update` contract MUST explain that banner image upload is handled by the separate `channelBanners_insert` tool and that `channels_update` only applies supported channel resource changes such as a returned banner URL.
- **FR-015**: The `channels_update` contract MUST remain close to the upstream `channels.update` endpoint and MUST NOT add channel lookup, analytics, ranking, enrichment, video expansion, playlist expansion, banner upload, or multi-step channel-management orchestration.
- **FR-016**: The `channels_update` tool MUST comply with the Layer 2 naming, metadata, quota, auth, availability, response-shaping, error, and example standards established by YT-201 and YT-202.
- **FR-017**: The `channels_update` tool MUST rely on the existing Layer 1 `channels.update` capability from YT-111 for endpoint behavior rather than redefining a separate upstream contract.
- **FR-018**: The feature MUST include caller-facing examples for at least one `brandingSettings` update, one `localizations` update, one banner URL activation update, one missing-authorization failure, one part-to-body mismatch, and one read-only or unsupported field rejection.
- **FR-019**: The feature MUST include validation evidence that clients can discover, call, understand OAuth and writable-part requirements, interpret update results, and handle failures for `channels_update` without consulting implementation-only artifacts.

### Key Entities

- **Channels Update Tool**: The public Layer 2 MCP tool named `channels_update`, representing one low-level endpoint-backed channel update operation.
- **Channels Update Request**: One caller-submitted update attempt, including selected writable parts, target channel context, and an aligned channel body.
- **Writable Channel Part**: A channel resource section that this slice permits callers to update, including `brandingSettings` and `localizations`.
- **Channel Body**: The caller-provided channel resource content that identifies the target channel and contains fields aligned to the selected writable parts.
- **Access Context**: The caller's OAuth authorization and channel-management eligibility for the requested update.
- **Updated Channel Result**: The returned channel resource outcome for a successful mutation, including selected writable parts and endpoint context.
- **Quota Disclosure**: The caller-facing statement that each `channels_update` invocation costs 50 official quota units.
- **Writable Boundary Disclosure**: The caller-facing explanation of supported writable parts, read-only exclusions, part-to-body alignment, and out-of-scope channel-management behavior.

### Assumptions

- YT-111 provides the Layer 1 `channels.update` capability that this public Layer 2 tool exposes.
- YT-201 and YT-202 provide the shared Layer 2 naming, metadata, quota, auth, response-shaping, error, example, and validation standards this feature must follow.
- `channels_update` is a low-level endpoint-backed tool for direct access, debugging, channel configuration updates, and power-user workflows; higher-level channel management, lookup, analytics, enrichment, and multi-step branding workflows belong to separate endpoint or Layer 3 features.
- The supported writable surface for this slice follows the existing YT-111 boundary of `brandingSettings` and `localizations`, including banner URL activation through `brandingSettings.image.bannerExternalUrl`.
- The official YouTube Data API documentation is the default source for `channels.update` quota cost, auth behavior, writable-part behavior, availability state, and failure caveats, with any discovered caveats recorded explicitly.
- Representative coverage of supported channel updates, missing auth, part-to-body mismatches, read-only fields, unsupported parts, quota/auth disclosure, and updated-resource outcomes is sufficient for this slice.

### Dependencies

- `YT-111` Layer 1 `channels.update` wrapper is available for endpoint behavior.
- `YT-201` shared Layer 2 YouTube contracts are available for naming, request mapping, response, error, auth, quota, layout, and validation conventions.
- `YT-202` Layer 2 metadata standards are available for public naming, quota, auth, availability, description, example, and response-shaping rules.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `channels_update` discovery metadata, descriptions, and examples produced by this feature display the mapped `channels.update` identity and official quota-unit cost of `50`.
- **SC-002**: A client developer can identify the OAuth requirement, supported writable parts, read-only exclusions, and part-to-body alignment rule in under 1 minute by reading the tool contract alone.
- **SC-003**: 100% of representative valid `channels_update` requests return an updated channel resource result with selected writable parts, source operation identity, quota context, and request context preserved.
- **SC-004**: 100% of representative invalid channel update requests with missing auth, missing body content, unsupported parts, read-only fields, or part-to-body mismatches are rejected with caller-facing feedback before being treated as supported endpoint requests.
- **SC-005**: Reviewers can verify in a single review pass that `channels_update` complies with YT-201 and YT-202 Layer 2 naming, metadata, quota, auth, response, error, and example standards.
- **SC-006**: A power user can discover `channels_update`, understand the 50-unit cost, identify required authorization, choose a supported writable part, and prepare a valid first request in under 3 minutes using only the public tool contract.
- **SC-007**: Final review evidence includes passing focused `channels_update` contract and validation checks, passing full repository behavior checks, and passing code-quality checks for the endpoint tool work.
