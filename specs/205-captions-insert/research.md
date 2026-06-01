# Research: YT-205 Layer 2 Tool `captions_insert`

## Decision: Implement One Concrete Layer 2 Tool Backed by Existing Layer 1 `captions.insert`

YT-205 should expose only the public `captions_insert` MCP tool and should rely on the existing YT-105 Layer 1 `captions.insert` wrapper for endpoint identity, OAuth behavior, quota cost, delegation context, request validation, media-upload validation, upstream execution, and created-resource result shape.

**Rationale**: The seed defines YT-205 as a single endpoint-tool slice. YT-201 and YT-202 already define shared Layer 2 naming, metadata, response-boundary, quota, auth, and safety standards; YT-105 already provides the internal `captions.insert` capability. Reusing those artifacts keeps implementation small and avoids a duplicate upstream request path.

**Alternatives considered**:

- Reimplement `captions.insert` request execution directly in the Layer 2 handler: rejected because it would duplicate Layer 1 execution and error normalization.
- Add a broad captions media-upload framework in this slice: rejected because YT-205 is scoped to one endpoint and later media-upload endpoints can extract shared helpers only after repeated need is visible.
- Defer public execution and add only another representative descriptor: rejected because YT-205 acceptance requires Layer 2 to expose `captions_insert`.

## Decision: Use Official `captions.insert` Contract as the Public Tool Boundary

The public `captions_insert` input contract should preserve the official endpoint concepts: media upload support, upload file constraints, required `part`, required caption body fields, optional `onBehalfOfContentOwner`, deprecated `sync`, official quota cost `400`, and created caption-resource response.

**Rationale**: Layer 2 is the near-raw endpoint layer. The current official YouTube documentation describes `captions.insert` as a media-upload method with maximum file size 100MB, accepted media MIME types `text/xml`, `application/octet-stream`, and `*/*`, quota cost `400`, `POST https://www.googleapis.com/upload/youtube/v3/captions`, required OAuth authorization, required query parameter `part`, optional delegated content-owner parameter, deprecated `sync`, required request-body properties `snippet.videoId`, `snippet.language`, and `snippet.name`, optional `snippet.isDraft`, and a successful response containing a caption resource. Source: https://developers.google.com/youtube/v3/docs/captions/insert

**Alternatives considered**:

- Hide upload details behind a metadata-only request: rejected because the official endpoint requires caption track contents.
- Add friendlier aliases for metadata fields: rejected because Layer 2 should stay close to upstream semantics.
- Auto-download, translate, or normalize caption content after insertion: rejected because those behaviors belong to separate endpoints or higher layers.

## Decision: Declare OAuth-Required Auth With Delegation Notes

`captions_insert` should declare auth mode `oauth_required`. Public metadata and usage notes must make clear that eligible OAuth authorization is required and that `onBehalfOfContentOwner` is optional delegated content-owner context when the caller has the matching permission.

**Rationale**: Caption creation is permission-sensitive and cannot be represented as public API-key behavior. The official docs list OAuth scopes for the method, and the existing YT-105 Layer 1 wrapper models the operation as OAuth-required. Public callers need this before invocation so they do not treat caption insertion as public video metadata.

**Alternatives considered**:

- Declare the tool `api_key`: rejected because that would misrepresent caption creation access.
- Declare mixed/conditional auth: rejected because the supported request path requires OAuth.
- Hide delegation details until errors occur: rejected because delegated-owner context materially affects valid caption creation.

## Decision: Preserve Near-Raw Created Caption Resource Results

Successful `captions_insert` results should preserve the upstream-visible created caption resource, requested parts, endpoint identity, quota cost, metadata summary, safe media summary, and delegation summary when present.

**Rationale**: Layer 2 callers need endpoint-backed data for direct caption management and debugging. Shared YT-201/YT-202 conventions allow light wrapper fields for MCP clarity but reject higher-level composition, caption download, language ranking, transcript extraction, and heuristics.

**Alternatives considered**:

- Return only a generic mutation acknowledgment: rejected because the official endpoint returns a caption resource and callers need the created resource.
- Return raw media content or uploaded file contents: rejected because public result surfaces must not expose caption file contents or raw media payloads.
- Fetch caption tracks after insertion: rejected because follow-up listing is a separate endpoint call and would add cross-endpoint composition.

## Decision: Validate Metadata, Media Input, and OAuth Before Invocation

The public tool should require `part`, required caption metadata body fields, supported media-upload input, eligible OAuth authorization, and valid delegated content-owner context before treating the request as supported endpoint usage. Metadata-only and media-only requests must be rejected with clear caller-facing guidance.

**Rationale**: The endpoint combines mutation, upload, and authorization behavior. Early validation gives MCP callers stable remediation guidance, protects against expensive failed attempts, and keeps invalid media descriptors or missing metadata from becoming ambiguous upstream errors.

**Alternatives considered**:

- Let upstream YouTube reject invalid metadata or media input: rejected because MCP callers should receive stable local validation guidance where the public contract can identify invalid shape.
- Allow metadata-only requests for dry runs: rejected because the Layer 2 tool should represent the actual endpoint and not invent unsupported behavior.
- Treat missing authorization as not found: rejected because callers need to distinguish inaccessible videos from missing caption media or invalid metadata.

## Decision: Document Deprecated `sync` Without Making It a Recommended Path

The public contract should mention `sync` as an optional deprecated upstream parameter when supported by the Layer 1 wrapper or schema, and examples should avoid presenting it as the normal path.

**Rationale**: The official documentation still lists `sync` but marks it deprecated. Layer 2 stays close to upstream semantics, so callers should be warned rather than surprised, and reviewers should be able to verify that the tool does not promote deprecated behavior.

**Alternatives considered**:

- Omit `sync` entirely: rejected unless implementation chooses not to support deprecated upstream options, because callers would lack a visible caveat for an official parameter.
- Feature `sync` in the primary example: rejected because deprecated behavior should not be the recommended path.
- Convert `sync` into automatic transcript alignment behavior: rejected because that would add higher-level semantics.

## Decision: Register Through Existing Dispatcher-Compatible Tool Descriptors

Implementation should add `captions_insert` in the existing MCP tool registration/discovery path, using the same name, description, input schema, metadata, and handler concepts used by `activities_list` and `captions_list`.

**Rationale**: The dispatcher already registers callable tools with `name`, `description`, `inputSchema`, `handler`, and optional metadata. YT-203 and YT-204 established concrete Layer 2 endpoint patterns. YT-205 should follow them instead of changing transport or registry architecture.

**Alternatives considered**:

- Add a new transport route for media-upload tools: rejected because MCP tool discovery/invocation already exists.
- Special-case YouTube invocation outside the dispatcher: rejected because it would bypass existing registry and contract tests.
- Change all captions endpoints into executable tools in this slice: rejected because YT-205 is scoped only to `captions_insert`.

## Decision: Extend the Captions Layer 2 Module

The concrete `captions_insert` tool should live in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`, with public exports added through `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`.

**Rationale**: YT-201 resource-family placement points endpoint tools to family modules, and YT-204 already established the concrete captions resource-module pattern. Extending the captions module keeps endpoint-specific schema, OAuth validation, media-upload validation, handler wiring, examples, and result shaping out of broad shared files while still using common contracts and conventions.

**Alternatives considered**:

- Add `captions_insert` directly to `youtube_common/examples.py`: rejected because examples are representative and not the concrete execution surface.
- Add endpoint-specific behavior to `contracts.py` or `conventions.py`: rejected because those modules own shared cross-cutting primitives.
- Create a separate upload-specific module for one endpoint: rejected until multiple concrete media-upload Layer 2 tools need shared upload helpers.

## Decision: Keep Discovery Metadata Explicit and Safe

The implementation must ensure callers can inspect `captions_insert` quota, auth, upstream identity, availability, required metadata, media-upload inputs, delegation caveats, deprecated `sync` caveat, and usage notes before invocation. If default dispatcher discovery needs metadata changes, those changes must be additive and preserve existing tool descriptors.

**Rationale**: YT-205 requires cost, OAuth, and upload visibility before calling. Existing shared contracts include safe public metadata validation, and current concrete Layer 2 tools already surface endpoint metadata through dispatcher-compatible descriptors.

**Alternatives considered**:

- Rely only on Python contract objects: rejected because MCP-facing discovery is user-visible behavior.
- Rewrite dispatcher descriptors broadly: rejected because baseline tools and current MCP contract tests must remain stable.
- Hide upload requirements only in prose docs: rejected because clients and reviewers need deterministic pre-invocation visibility.

## Decision: Keep Verification Constitution-Driven

Implementation must begin with failing tests, add minimal code, refactor, and finish with targeted checks plus `python3 -m pytest` and `python3 -m ruff check .`. Every new or changed Python function must include a reStructuredText docstring.

**Rationale**: The project constitution makes Red-Green-Refactor, integration/regression coverage, full-suite validation, and reStructuredText docstrings mandatory. YT-205 extends the concrete Layer 2 endpoint pattern established by YT-203 and YT-204 and will influence later captions mutation/upload slices.

**Alternatives considered**:

- Run only focused `captions_insert` tests: rejected because the constitution requires full-suite validation after final code changes.
- Treat docstrings as optional for private helper functions: rejected because the constitution requires every new or modified Python function.
- Skip integration checks because the handler can be unit-tested: rejected because public tool discovery and registration are MCP-facing behavior.
