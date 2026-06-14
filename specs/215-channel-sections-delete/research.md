# Research: Layer 2 Tool `channelSections_delete`

## Decision: Implement `channelSections_delete` as an endpoint-backed Layer 2 tool in the existing channel-sections resource-family module

**Rationale**: The PRD defines Layer 2 tools as one-to-one public MCP tools for documented YouTube Data API methods, and the local codebase already implements `channelSections_list`, `channelSections_insert`, and `channelSections_update` in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/channel_sections.py`. Keeping delete in the same module preserves YT-201 resource-family cohesion and avoids another abstraction layer.

**Alternatives considered**: A separate delete module was rejected because it would split one resource family. A higher-level channel layout editor was rejected because YT-215 is explicitly low-level and endpoint-backed.

## Decision: Use public tool name `channelSections_delete`

**Rationale**: YT-202 requires `resource_method` naming without a redundant `youtube_` prefix while preserving official resource casing. Existing nearby tools use `channelSections_list`, `channelSections_insert`, and `channelSections_update`.

**Alternatives considered**: `channel_sections_delete`, `youtube_channelSections_delete`, and `delete_channel_section` were rejected because they drift from established Layer 2 naming and upstream casing rules.

## Decision: Require OAuth and accept no API-key-only path

**Rationale**: The official `channelSections.delete` documentation says the request requires authorization with at least one YouTube scope, including `youtubepartner`, `youtube`, or `youtube.force-ssl`. The local Layer 1 wrapper from YT-115 already requires `oauth_required` auth. This matches the destructive mutation semantics.

**Alternatives considered**: API-key fallback was rejected because the upstream endpoint requires authorized user or partner credentials. Mixed auth was rejected because no public read-only mode exists for deletion.

## Decision: Use an input contract with required `id`, optional partner-only `onBehalfOfContentOwner`, and no request body

**Rationale**: Official docs list `id` as the required query parameter identifying the channel section to delete, `onBehalfOfContentOwner` as an optional properly authorized content-partner parameter, and explicitly state not to provide a request body. The Layer 1 YT-115 wrapper also accepts deletion arguments shaped around `id` plus partner context.

**Alternatives considered**: A `body.id` pattern was rejected because delete uses query parameters, unlike update. `onBehalfOfContentOwnerChannel` was rejected for this Layer 2 delete contract because the official delete page documents only `onBehalfOfContentOwner`; the spec's delegated-channel wording should be satisfied through documentation that paired channel context is not supported by this endpoint unless Layer 1 official support changes.

## Decision: Record quota cost as 50 everywhere the caller sees the tool

**Rationale**: Official YouTube quota documentation lists `channelSections.delete` at 50 units. YT-202 and the feature spec require the quota cost in metadata, description, usage notes, and examples.

**Alternatives considered**: Omitting quota from examples was rejected because FR-004 and YT-202 require pre-invocation quota visibility. Treating invalid requests as free was rejected because YouTube quota guidance says API requests can incur quota cost even when invalid; local validation still avoids unnecessary upstream calls.

## Decision: Map success to a deletion acknowledgment that can preserve a returned upstream body but does not fabricate resource fields

**Rationale**: The feature spec requires clear deletion acknowledgment and no fabricated deleted-channel-section data when upstream success returns no resource body. Current official docs say success returns a `channelSection` resource, so the result contract should allow returned upstream fields when present while also supporting no-body success from Layer 1 or transport mocks.

**Alternatives considered**: Always returning a synthetic `item` was rejected because it would fabricate resource fields. Treating empty responses as failure was rejected because deletion endpoints and existing local test patterns can return no-content acknowledgments.

## Decision: Reuse shared Layer 2 safe error categories and sanitize partner/credential details

**Rationale**: YT-201 requires consistent public error conventions. Existing channel-section tools map Layer 1 categories to safe values such as `invalid_request`, `authentication_failed`, `authorization_failed`, `quota_exhausted`, `resource_not_found`, `endpoint_unavailable`, and `upstream_failure`. Official errors include invalid ID, missing ID, not editable, forbidden, channel not found, and channel-section not found; these map cleanly into shared categories.

**Alternatives considered**: Exposing raw Google error details was rejected because project safety rules prohibit leaking credentials, stack traces, owner IDs, or unsafe diagnostics.

## Decision: Follow Red-Green-Refactor with focused contract, unit, integration, full-suite, and lint evidence

**Rationale**: The constitution makes Red-Green-Refactor non-negotiable and requires full repository test-suite execution after final code changes. The implementation should begin with failing tests for discovery, schema, validation, handler behavior, result mapping, error mapping, examples, exports, and default registry integration.

**Alternatives considered**: Implementing first and adding tests afterward was rejected by the constitution. Running only focused tests was rejected because full-suite validation is required before completion.

## Official References Checked

- YouTube Data API `channelSections.delete`: https://developers.google.com/youtube/v3/docs/channelSections/delete
- YouTube Data API quota cost table: https://developers.google.com/youtube/v3/determine_quota_cost
