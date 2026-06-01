# Research: YT-206 Layer 2 Tool `captions_update`

## Decision: Implement One Concrete Layer 2 Tool Backed by Existing Layer 1 `captions.update`

YT-206 should expose only the public `captions_update` MCP tool and should rely on the existing YT-106 Layer 1 `captions.update` wrapper for endpoint identity, OAuth behavior, quota cost, delegation context, request validation, optional media validation, upstream execution, and updated-resource result shape.

**Rationale**: The seed defines YT-206 as a single endpoint-tool slice. YT-201 and YT-202 already define shared Layer 2 naming, metadata, response-boundary, mutation, quota, auth, and safety standards; YT-106 already provides the internal `captions.update` capability. Reusing those artifacts keeps implementation small and avoids a duplicate upstream request path.

**Alternatives considered**:

- Reimplement `captions.update` request execution directly in the Layer 2 handler: rejected because it would duplicate Layer 1 execution and error normalization.
- Add a broad caption mutation framework in this slice: rejected because YT-206 is scoped to one endpoint and later mutation/media endpoints can extract shared helpers only after repeated need is visible.
- Defer public execution and add only another representative descriptor: rejected because YT-206 acceptance requires Layer 2 to expose `captions_update`.

## Decision: Use Official `captions.update` Contract as the Public Tool Boundary

The public `captions_update` input contract should preserve the official endpoint concepts: media upload support, upload file constraints, required `part`, required caption resource `body.id`, optional writable `body.snippet.isDraft`, optional `onBehalfOfContentOwner`, deprecated `sync`, official quota cost `450`, and updated caption-resource response.

**Rationale**: Layer 2 is the near-raw endpoint layer. The current official YouTube documentation describes `captions.update` as a method that updates a caption track by changing draft status, uploading a new caption file, or both. It supports media upload with a 100MB maximum file size and accepted media MIME types `text/xml`, `application/octet-stream`, and `*/*`; uses `PUT https://www.googleapis.com/upload/youtube/v3/captions`; requires OAuth authorization; requires `part` with allowed values `id` and `snippet`; requires a caption resource body with `id`; allows `snippet.isDraft`; returns a caption resource; and carries quota cost `450`. Source: https://developers.google.com/youtube/v3/docs/captions/update

**Alternatives considered**:

- Hide update details behind a generic mutation acknowledgment: rejected because Layer 2 callers need endpoint-backed detail and the official endpoint returns a caption resource.
- Require media for every update: rejected because the official endpoint supports changing draft status without replacing track content.
- Add friendlier aliases for update fields: rejected because Layer 2 should stay close to upstream semantics.
- Auto-download, translate, or normalize caption content after update: rejected because those behaviors belong to separate endpoints or higher layers.

## Decision: Declare OAuth-Required Auth With Delegation Notes

`captions_update` should declare auth mode `oauth_required`. Public metadata and usage notes must make clear that eligible OAuth authorization is required and that `onBehalfOfContentOwner` is optional delegated content-owner context when the caller has the matching permission.

**Rationale**: Caption update is permission-sensitive and cannot be represented as public API-key behavior. The official docs list OAuth scopes for the method, and the existing YT-106 Layer 1 wrapper models the operation as OAuth-required. Public callers need this before invocation so they do not treat caption update as public video metadata.

**Alternatives considered**:

- Declare the tool `api_key`: rejected because that would misrepresent caption update access.
- Declare mixed/conditional auth: rejected because the supported request path requires OAuth.
- Hide delegation details until errors occur: rejected because delegated-owner context materially affects valid caption update.

## Decision: Support Body-Only and Body-Plus-Media Update Modes

The public contract should support body-only update requests for metadata/draft-state updates and body-plus-media update requests for caption content replacement. Media without a valid body remains invalid.

**Rationale**: YT-106 explicitly defines the internal wrapper boundary as body-required, with body-only and body-plus-media as the supported modes. The official docs also distinguish changing draft status from uploading a new caption file. Keeping both modes visible lets callers avoid treating `captions_update` as either metadata-only or media-only.

**Alternatives considered**:

- Support only body-plus-media requests: rejected because that would exclude draft-status update use cases.
- Support media-only requests: rejected because both the official request body and YT-106 wrapper require a caption resource body.
- Add a dry-run mode: rejected because that would invent behavior outside the upstream endpoint.

## Decision: Preserve Near-Raw Updated Caption Resource Results

Successful `captions_update` results should preserve the upstream-visible updated caption resource, requested parts, endpoint identity, quota cost, safe update-body summary, safe media summary when media is supplied, and delegation summary when present.

**Rationale**: Layer 2 callers need endpoint-backed data for direct caption management and debugging. Shared YT-201/YT-202 conventions allow light wrapper fields for MCP clarity but reject higher-level composition, caption download, language ranking, transcript extraction, and heuristics.

**Alternatives considered**:

- Return only a generic mutation acknowledgment: rejected because the official endpoint returns a caption resource and callers need the updated resource.
- Return raw media content or uploaded file contents: rejected because public result surfaces must not expose caption file contents or raw media payloads.
- Fetch caption tracks after update: rejected because follow-up listing is a separate endpoint call and would add cross-endpoint composition.

## Decision: Validate Update Body, Optional Media Input, and OAuth Before Invocation

The public tool should require `part`, a valid caption update body with `id`, eligible OAuth authorization, and valid delegated content-owner context before treating the request as supported endpoint usage. Optional media descriptors should be validated when present. Missing-body, media-without-body, unsupported media, and unsupported option requests must be rejected with clear caller-facing guidance.

**Rationale**: The endpoint combines mutation, optional upload, high quota cost, and authorization behavior. Early validation gives MCP callers stable remediation guidance, protects against expensive failed attempts, and keeps invalid media descriptors or missing update identity from becoming ambiguous upstream errors.

**Alternatives considered**:

- Let upstream YouTube reject invalid body or media input: rejected because MCP callers should receive stable local validation guidance where the public contract can identify invalid shape.
- Treat missing authorization as not found: rejected because callers need to distinguish inaccessible caption tracks from missing caption resources or invalid update input.
- Allow unsupported fields and pass them through: rejected because the public Layer 2 schema should be deterministic.

## Decision: Document Deprecated `sync` Without Making It a Recommended Path

The public contract should mention `sync` as an optional deprecated upstream parameter when supported by the Layer 1 wrapper or schema, and examples should avoid presenting it as the normal path. If accepted, its caveat must state that the upstream server processes it only when an updated caption file is included.

**Rationale**: The official documentation still lists `sync` but marks it deprecated. Layer 2 stays close to upstream semantics, so callers should be warned rather than surprised, and reviewers should be able to verify that the tool does not promote deprecated behavior.

**Alternatives considered**:

- Omit `sync` entirely: rejected unless implementation chooses not to support deprecated upstream options, because callers would lack a visible caveat for an official parameter.
- Feature `sync` in the primary example: rejected because deprecated behavior should not be the recommended path.
- Convert `sync` into automatic transcript alignment behavior: rejected because that would add higher-level semantics.

## Decision: Register Through Existing Dispatcher-Compatible Tool Descriptors

Implementation should add `captions_update` in the existing MCP tool registration/discovery path, using the same name, description, input schema, metadata, and handler concepts used by `activities_list`, `captions_list`, and `captions_insert`.

**Rationale**: The dispatcher already registers callable tools with `name`, `description`, `inputSchema`, `handler`, and optional metadata. YT-203, YT-204, and YT-205 established concrete Layer 2 endpoint patterns. YT-206 should follow them instead of changing transport or registry architecture.

**Alternatives considered**:

- Add a new transport route for media-update tools: rejected because MCP tool discovery/invocation already exists.
- Special-case YouTube invocation outside the dispatcher: rejected because it would bypass existing registry and contract tests.
- Change all remaining captions endpoints into executable tools in this slice: rejected because YT-206 is scoped only to `captions_update`.

## Decision: Extend the Captions Layer 2 Module

The concrete `captions_update` tool should live in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`, with public exports added through `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`.

**Rationale**: YT-201 resource-family placement points endpoint tools to family modules, and YT-204/YT-205 already established the concrete captions resource-module pattern. Extending the captions module keeps endpoint-specific schema, OAuth validation, media validation, handler wiring, examples, and result shaping out of broad shared files while still using common contracts and conventions.

**Alternatives considered**:

- Add `captions_update` directly to `youtube_common/examples.py`: rejected because examples are representative and not the concrete execution surface.
- Add endpoint-specific behavior to `contracts.py` or `conventions.py`: rejected because those modules own shared cross-cutting primitives.
- Create a separate update-specific module for one endpoint: rejected until multiple concrete update/media Layer 2 tools need shared helpers.

## Decision: Keep Discovery Metadata Explicit and Safe

The implementation must ensure callers can inspect `captions_update` quota, auth, upstream identity, availability, required update body, optional media replacement, delegation caveats, deprecated `sync` caveat, and usage notes before invocation. If default dispatcher discovery needs metadata changes, those changes must be additive and preserve existing tool descriptors.

**Rationale**: YT-206 requires cost, OAuth, update, and media visibility before calling. Existing shared contracts include safe public metadata validation, and current concrete Layer 2 tools already surface endpoint metadata through dispatcher-compatible descriptors.

**Alternatives considered**:

- Rely only on Python contract objects: rejected because MCP-facing discovery is user-visible behavior.
- Rewrite dispatcher descriptors broadly: rejected because baseline tools and current MCP contract tests must remain stable.
- Hide update/media requirements only in prose docs: rejected because clients and reviewers need deterministic pre-invocation visibility.

## Decision: Keep Verification Constitution-Driven

Implementation must begin with failing tests, add minimal code, refactor, and finish with targeted checks plus `python3 -m pytest` and `python3 -m ruff check .`. Every new or changed Python function must include a reStructuredText docstring.

**Rationale**: The project constitution makes Red-Green-Refactor, integration/regression coverage, full-suite validation, and reStructuredText docstrings mandatory. YT-206 extends the concrete Layer 2 endpoint pattern established by YT-203, YT-204, and YT-205 and will influence later captions mutation/upload slices.

**Alternatives considered**:

- Run only focused `captions_update` tests: rejected because the constitution requires full-suite validation after final code changes.
- Treat docstrings as optional for private helper functions: rejected because the constitution requires every new or modified Python function.
- Skip integration checks because the handler can be unit-tested: rejected because public tool discovery and registration are MCP-facing behavior.
