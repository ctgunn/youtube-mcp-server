# Research: YT-152 Layer 1 Endpoint `videos.reportAbuse`

## Decision: Model `videos.reportAbuse` as an OAuth-required mutation wrapper with one deterministic body contract

**Rationale**: Local product artifacts define YT-152 as a typed Layer 1 wrapper for `POST /videos/reportAbuse` with visible OAuth expectations and a 50-unit quota cost. Official Google documentation confirms that the report action is a POST request requiring authorization and a request body that identifies the video and reason. Nearby Layer 1 mutation wrappers keep endpoint-specific bodies explicit rather than accepting arbitrary mapping shapes. The smallest consistent fit is therefore a wrapper that requires a `body` object with documented report fields and validates that body before execution. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/152-videos-report-abuse/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, https://developers.google.com/youtube/v3/docs/videos/reportAbuse

**Alternatives considered**:

- Put `videoId` and `reasonId` at the top-level wrapper argument boundary. Rejected because the existing transport helper already treats `body` as the mutation payload carrier for POST-style request data.
- Accept arbitrary body mappings for future expansion. Rejected because the current wrapper foundation is built around deterministic field validation.
- Treat the endpoint as mixed-auth or conditionally public. Rejected because the endpoint performs a user-affecting report action and the official endpoint requires authorized access.

## Decision: Require `videoId` and `reasonId`; support only documented optional body fields `secondaryReasonId`, `comments`, and `language`

**Rationale**: Official Google documentation identifies `videoId` and `reasonId` as required request-body properties and lists `secondaryReasonId`, `comments`, and `language` as optional body properties. This aligns with the feature spec's requirement to document abuse-report payload expectations and gives maintainers enough information to build or validate reports without reading transport code. Unsupported or misspelled body fields should be rejected or clearly flagged instead of passed through silently because this is a sensitive mutation with a meaningful quota cost. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/152-videos-report-abuse/spec.md`, https://developers.google.com/youtube/v3/docs/videos/reportAbuse

**Alternatives considered**:

- Support only required fields and reject all optional body fields. Rejected because the official endpoint documents optional detail fields and the feature spec calls for payload expectations beyond only required fields.
- Accept optional body fields without naming them in metadata. Rejected because maintainers need reviewable payload guidance before reuse.
- Add extra local aliases such as `video_id` or `reason_id`. Rejected because adjacent Layer 1 wrappers stay close to upstream field names when those names are already understandable.

## Decision: Keep `onBehalfOfContentOwner` outside the guaranteed request boundary for this slice

**Rationale**: The official endpoint documents `onBehalfOfContentOwner` as a partner-only authorized query parameter. The current feature spec asks for abuse-report payload expectations and OAuth requirements, not delegated content-owner behavior. Adding partner delegation would broaden authorization semantics, testing obligations, and security review for a single endpoint slice. The plan should therefore document that partner-only delegated reporting remains outside the guaranteed wrapper boundary unless a later slice explicitly adds it. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/152-videos-report-abuse/spec.md`, https://developers.google.com/youtube/v3/docs/videos/reportAbuse

**Alternatives considered**:

- Support `onBehalfOfContentOwner` immediately. Rejected because it introduces partner-specific authorization behavior beyond the current slice.
- Ignore the parameter entirely. Rejected because maintainers need to know it is intentionally outside the promised boundary.
- Treat partner delegation as a generic optional field. Rejected because the official documentation ties it to a specialized authorization context.

## Decision: Normalize successful report submission as an acknowledgement because the upstream success response has no body

**Rationale**: Official Google documentation states that successful `videos.reportAbuse` calls return an HTTP 204 no-content response. Adjacent mutation wrappers expose normalized acknowledgement-style outcomes so downstream layers do not need to infer success from an empty response. YT-152 should follow that pattern by preserving source operation, reported video, abuse reason, quota cost, and auth path in a normalized acknowledgement while avoiding credentials or reporter identity. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/150-videos-rate/spec.md`, https://developers.google.com/youtube/v3/docs/videos/reportAbuse

**Alternatives considered**:

- Return an empty dictionary for success. Rejected because downstream layers need enough request context to interpret the mutation.
- Fetch the video after reporting and return a refreshed video resource. Rejected because the feature is scoped to one report endpoint and should not spend extra quota or add a second endpoint dependency.
- Treat 204 success as a generic transport result without endpoint-specific fields. Rejected because reviewability and reuse require source and submitted-report context.

## Decision: Preserve explicit separation between invalid request shapes, missing OAuth access, invalid reason combinations, upstream refusal, rate limiting, video-not-found, and successful acknowledgements

**Rationale**: The repository already normalizes upstream failures and relies on wrapper-level validation to keep local request problems distinct from runtime failures. YT-152 adds a policy-sensitive mutation, and official documentation identifies invalid abuse reason combinations, rate-limit failures, forbidden responses, and missing videos as expected error boundaries. The planning boundary must preserve a clear difference between malformed local body input, missing authorized access, upstream refusal after execution begins, rate limiting, missing targets, and successful report acknowledgement. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/152-videos-report-abuse/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, https://developers.google.com/youtube/v3/docs/videos/reportAbuse

**Alternatives considered**:

- Flatten malformed requests and upstream refusals into one generic error path. Rejected because caller remediation differs substantially depending on the failure type.
- Treat rate-limit failures as local validation failures. Rejected because they occur after execution begins and should remain distinct from malformed payloads.
- Add a much larger moderation failure taxonomy during planning. Rejected because the feature only requires the main remediation boundaries to stay separate.

## Decision: Update maintainer-facing review surfaces in `review_surface`, feature-local contracts, and a dedicated higher-layer summary path

**Rationale**: Adjacent video endpoint slices expose the wrapper contract in three places: `review_surface()` metadata from the wrapper, feature-local contracts under `specs/<feature>/contracts/`, and higher-layer summary fields in `consumer.py` that keep source operation, quota, auth mode, and request-boundary notes visible without reading lower-level code. YT-152 should follow that same pattern by adding a `videos.reportAbuse` review surface, a wrapper contract plus auth-payload contract, and a summary path that echoes submitted report context, success acknowledgement, source contract details, and absence of credential exposure. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/150-videos-rate/contracts/`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/151-videos-get-rating/contracts/`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_videos_contract.py`

**Alternatives considered**:

- Keep all guidance only in markdown contracts. Rejected because adjacent slices also expose the contract through wrapper metadata and consumer summaries.
- Update wrapper metadata only and skip a dedicated summary surface. Rejected because the repo already uses higher-layer summaries as a reusable maintainer-facing review path.
- Reuse the existing `videos.rate` summary unchanged. Rejected because `videos.reportAbuse` needs abuse-report-specific fields rather than rating-action semantics.

## Decision: Keep the implementation seam centered on `wrappers.py`, `youtube.py`, `consumer.py`, `__init__.py`, and the existing Layer 1 video test suites

**Rationale**: `wrappers.py` already contains the endpoint-specific metadata and validation pattern used by neighboring video wrappers, `youtube.py` is the transport seam for request construction and normalized response shaping, `consumer.py` already exposes higher-layer summaries that surface source metadata, `__init__.py` exports endpoint builders, and the existing unit, contract, integration, and transport tests cover adjacent video list, video rate, and video rating lookup slices with minimal duplication. This is the smallest extension path for one OAuth-required video abuse-report endpoint. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/consumer.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/__init__.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_layer1_foundation.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/unit/test_youtube_transport.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_videos_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/contract/test_layer1_consumer_contract.py`, `/Users/ctgunn/Projects/youtube-mcp-server/tests/integration/test_layer1_foundation.py`

**Alternatives considered**:

- Create a new moderation-specific integration submodule. Rejected because one endpoint slice does not justify new architecture.
- Limit validation to metadata-only checks. Rejected because the constitution requires integration and regression coverage.
- Skip consumer-summary updates. Rejected because the feature spec expects maintainer-visible reuse guidance beyond raw transport details.

## Decision: Use two feature-local contracts separating wrapper identity from auth and abuse-report payload boundary guidance

**Rationale**: Nearby video endpoint slices separate wrapper-level metadata requirements from more specific auth and domain-boundary guidance. Reusing that split for YT-152 keeps one contract focused on wrapper identity and normalized result expectations and a second focused on required body inputs, OAuth requirements, optional payload fields, unsupported partner-only query behavior, and failure interpretation. That structure matches adjacent review patterns and keeps the planning boundary easy to audit. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/specs/150-videos-rate/contracts/layer1-videos-rate-auth-rating-contract.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/151-videos-get-rating/contracts/layer1-videos-get-rating-wrapper-contract.md`

**Alternatives considered**:

- Use one contract file only. Rejected because wrapper requirements and abuse-report payload semantics become harder to review together.
- Put all guidance in the plan and skip feature-local contracts. Rejected because the constitution requires contract-first design artifacts.
- Create a larger multi-endpoint abuse-reporting contract now. Rejected because this slice should stay scoped to one endpoint.

## Clarification Closure

All planning-time clarifications for YT-152 are resolved in this research artifact. No unresolved clarification markers remain.
