# Research: YT-153 Layer 1 Endpoint `videos.delete`

## Decision: Model `videos.delete` as an OAuth-required destructive mutation wrapper with one required target identifier

**Rationale**: Local product artifacts define YT-153 as a typed Layer 1 wrapper for the YouTube Data API `DELETE /videos` endpoint with visible OAuth expectations and a 50-unit quota cost. Official Google documentation identifies `id` as the required query parameter and states that delete operations require authorized access. Nearby delete wrappers keep the request boundary explicit and reject unsupported shapes before execution. The smallest consistent fit is therefore a wrapper that requires one non-empty `id`, uses OAuth-backed access, and keeps the delete target visible in metadata, contracts, docstrings, and summaries. Sources: `/Users/ctgunn/Projects/youtube-mcp-server/requirements/spec-kit-seed.md`, `/Users/ctgunn/Projects/youtube-mcp-server/specs/153-videos-delete/spec.md`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, https://developers.google.com/youtube/v3/docs/videos/delete

**Alternatives considered**: Accepting a body-driven delete request was rejected because the official endpoint states not to provide a request body. Supporting bulk deletion was rejected because the endpoint contract requires one `id` per call and the feature scope is one Layer 1 endpoint wrapper. Treating deletion as API-key compatible was rejected because the endpoint requires authorized access.

## Decision: Keep `onBehalfOfContentOwner` visible but outside the guaranteed supported boundary unless deliberately implemented in the wrapper

**Rationale**: Official Google documentation lists `onBehalfOfContentOwner` as an optional query parameter intended exclusively for properly authorized YouTube content partners. This parameter expands authorization semantics beyond ordinary OAuth-backed video deletion. Existing local delete slices either explicitly support delegated owner context when that behavior is part of the slice or mark it as a bounded optional path. For YT-153, the feature spec asks for the typed wrapper, quota cost, and OAuth requirement, not partner delegation. The plan should therefore require the contract to mention the partner-only parameter and require unsupported partner delegation to be rejected or clearly flagged unless implementation tasks deliberately add it as a supported optional field.

**Alternatives considered**: Fully supporting `onBehalfOfContentOwner` by default was rejected because it broadens security review and test obligations. Ignoring the parameter was rejected because later maintainers need to know whether partner delegation is supported or outside the slice.

## Decision: Normalize HTTP 204 no-content success into a deletion acknowledgement

**Rationale**: Official Google documentation states that a successful `videos.delete` call returns HTTP 204 with no content. Adjacent mutation and delete wrappers expose normalized acknowledgement-style outcomes so downstream layers do not infer success from an empty response. YT-153 should follow that pattern by preserving source operation, target video identifier, quota cost, auth mode, and acknowledgement state while avoiding credentials or owner identity in the result.

**Alternatives considered**: Returning an empty mapping was rejected because it is ambiguous for higher layers and does not satisfy the spec's request-context preservation requirement. Fetching the deleted video after deletion was rejected because successful deletion should not require a refreshed resource and may not be possible.

## Decision: Separate invalid request, access failure, forbidden delete, not-found, upstream unavailable, and successful acknowledgement outcomes

**Rationale**: The repository already uses wrapper-level validation and normalized upstream failures to keep local request problems distinct from runtime failures. Official Google documentation identifies forbidden delete failures and `videoNotFound` as documented error cases. Because this is a destructive operation with a 50-unit quota cost, the plan must preserve a clear difference between malformed local input, missing OAuth-backed access, upstream refusal after execution begins, missing targets, transient upstream failures, and successful deletion acknowledgement.

**Alternatives considered**: Collapsing all delete failures into a generic upstream error was rejected because calling workflows need to know whether to correct input, obtain different authorization, stop because the video is absent, or retry later. Treating already-deleted and nonexistent videos as successful local idempotence was rejected because the upstream contract reports missing targets as not found.

## Decision: Reuse existing Layer 1 wrapper, transport, consumer-summary, and test seams

**Rationale**: Adjacent video endpoint slices expose the wrapper contract in three places: `review_surface()` metadata from the wrapper, feature-local contracts under `specs/<feature>/contracts/`, and higher-layer summary fields in `consumer.py` that keep source operation, quota, auth mode, and request-boundary notes visible without reading lower-level code. YT-153 should follow that same pattern by adding a `videos.delete` review surface, wrapper contract plus auth-delete contract, and a summary path that echoes target video id, deletion acknowledgement, source contract details, and absence of credential exposure.

**Alternatives considered**: Creating a new deletion abstraction was rejected because existing delete wrappers already provide the required seams. Skipping consumer-summary coverage was rejected because nearby Layer 1 slices use it to prove downstream reviewability before public tools are introduced.
