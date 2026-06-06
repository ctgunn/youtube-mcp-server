# Research: YT-207 Layer 2 Tool `captions_download`

## Decision: Implement One Concrete Layer 2 Tool Backed by Existing Layer 1 `captions.download`

YT-207 should expose only the public `captions_download` MCP tool and should rely on the existing YT-107 Layer 1 `captions.download` wrapper for endpoint identity, OAuth behavior, quota cost, delegation context, request validation, upstream execution, and downloaded-content result shape.

**Rationale**: The seed defines YT-207 as a single endpoint-tool slice. YT-201 and YT-202 already define shared Layer 2 naming, metadata, response-boundary, downloaded-content, quota, auth, and safety standards; YT-107 already provides the internal `captions.download` capability. Reusing those artifacts keeps implementation small and avoids a duplicate upstream request path.

**Alternatives considered**:

- Reimplement `captions.download` request execution directly in the Layer 2 handler: rejected because it would duplicate Layer 1 execution and error normalization.
- Add a broad transcript retrieval framework in this slice: rejected because YT-207 is scoped to one low-level endpoint and Layer 3 transcript workflows belong to separate features.
- Defer public execution and add only another representative descriptor: rejected because YT-207 acceptance requires Layer 2 to expose `captions_download`.

## Decision: Use Official `captions.download` Contract as the Public Tool Boundary

The public `captions_download` input contract should preserve the official endpoint concepts: required caption track `id`, optional `onBehalfOfContentOwner`, optional `tfmt`, optional `tlang`, official quota cost `200`, OAuth authorization, permission to edit the video, and binary downloaded-file response. The official docs list supported `tfmt` values as `sbv`, `scc`, `srt`, `ttml`, and `vtt`, and define `tlang` as an ISO 639-1 two-letter language code for machine-generated translation. Source: https://developers.google.com/youtube/v3/docs/captions/download

**Rationale**: Layer 2 is the near-raw endpoint layer. The current official YouTube documentation describes `captions.download` as returning the caption track in its original format unless `tfmt` is supplied and in its original language unless `tlang` is supplied. It returns a binary file with `application/octet-stream` response context, requires authorization, lists OAuth scopes, and documents permission, conversion, and not-found errors.

**Alternatives considered**:

- Convert the result into a higher-level transcript object: rejected because Layer 2 should stay close to upstream semantics and higher-level transcript workflows belong to Layer 3.
- Require `tfmt` or `tlang` for every download: rejected because the upstream endpoint supports default original-format and original-language download.
- Add friendly aliases for output formats or language fields: rejected because Layer 2 should preserve upstream field names for direct endpoint access.
- Store downloaded files persistently: rejected because this slice does not introduce persistence and callers need an endpoint-backed result, not storage lifecycle management.

## Decision: Declare OAuth-Required Auth With Permission-to-Edit and Delegation Notes

`captions_download` should declare auth mode `oauth_required`. Public metadata and usage notes must make clear that eligible OAuth authorization is required, that the user must have permission to edit the video, and that `onBehalfOfContentOwner` is optional delegated content-owner context for eligible YouTube content partners.

**Rationale**: Caption download is permission-sensitive and cannot be represented as public API-key behavior. The official docs list OAuth scopes and state the permission-to-edit requirement. Callers need this before invocation so they do not treat caption download as public video metadata or as a general unauthenticated transcript fetch.

**Alternatives considered**:

- Declare the tool `api_key`: rejected because that would misrepresent caption download access.
- Declare mixed/conditional auth: rejected because the supported request path requires OAuth.
- Hide permission and delegation details until errors occur: rejected because those rules materially affect valid caption download requests.

## Decision: Support Default Download, Format Conversion, and Target-Language Conversion

The public contract should support default caption download by `id`, supported output-format conversion through `tfmt`, and supported target-language conversion through `tlang`. `tfmt` must be limited to the documented values `sbv`, `scc`, `srt`, `ttml`, and `vtt`; `tlang` must be represented as an ISO 639-1 two-letter language code. Requests using unsupported conversion options should be rejected locally when possible or mapped safely from upstream conversion errors.

**Rationale**: YT-107 explicitly defines the internal wrapper boundary as `id` plus optional `tfmt` and `tlang`. The official docs define both conversion options and document a `couldNotConvert` error when the requested language or format cannot be produced. Making conversion support explicit lets callers prepare valid requests without inventing transcript conversion behavior outside the endpoint.

**Alternatives considered**:

- Support only default downloads: rejected because the seed specifically calls out format/language conversion options.
- Accept any `tfmt` string and rely on upstream errors: rejected because the supported values are finite and can be validated in the public contract.
- Treat `tlang` as arbitrary prose language names: rejected because the official endpoint expects ISO 639-1 language codes.
- Implement local translation or format conversion: rejected because upstream `captions.download` already defines conversion behavior and local conversion would add higher-layer semantics.

## Decision: Preserve Near-Raw Downloaded Caption Content Results

Successful `captions_download` results should preserve the endpoint-backed downloaded caption content and include light MCP clarity fields such as endpoint identity, quota cost, caption track id, requested `tfmt`, requested `tlang`, content type, content form, safe size indicators when available, and delegation context when supplied.

**Rationale**: The upstream result is not a JSON caption resource; it is a downloadable file response. Layer 2 callers need the content or safe content representation plus enough operation context to understand what was downloaded. Shared response-boundary rules allow light wrapper fields for MCP clarity while rejecting transcript enrichment, summarization, language ranking, and cross-endpoint composition.

**Alternatives considered**:

- Return only a generic download acknowledgment: rejected because callers need the caption content or content representation.
- Return a normalized transcript with segments and timestamps: rejected because that is a higher-level transcript workflow, not the raw endpoint result.
- Return raw private caption content in public examples or logs: rejected for security and privacy; examples and diagnostics must use placeholders and safe descriptors.

## Decision: Validate Identifier, Conversion Options, and OAuth Before Invocation

The public tool should require a non-empty caption track `id`, eligible OAuth authorization, valid delegated content-owner context when supplied, a documented `tfmt` value when supplied, and a valid ISO 639-1-style `tlang` value when supplied before treating the request as supported endpoint usage. Missing identifier, unsupported format, malformed language, and missing authorization requests must be rejected with clear caller-facing guidance.

**Rationale**: The endpoint combines high quota cost, permission requirements, and optional conversion behavior. Early validation gives MCP callers stable remediation guidance, protects against expensive failed attempts, and keeps unsupported conversion options from becoming ambiguous upstream errors.

**Alternatives considered**:

- Let upstream YouTube reject invalid identifiers or options: rejected where local validation can give deterministic guidance from the public contract.
- Treat missing authorization as not found: rejected because callers need to distinguish inaccessible caption tracks from missing caption resources.
- Allow unsupported fields and pass them through: rejected because the public Layer 2 schema should be deterministic.

## Decision: Map Official Download Errors to Shared Safe Error Categories

The tool should map upstream `forbidden` to `authorization_failed`, `couldNotConvert` to `invalid_request` or a conversion-specific safe invalid request detail, and `captionNotFound` to `resource_not_found`. Quota exhaustion, unavailable service, and unexpected upstream failures should use the shared Layer 2 error categories.

**Rationale**: The official docs identify permission, conversion, and not-found failures for `captions.download`. Shared YT-201/YT-202 error conventions keep MCP-facing errors stable and safe while preserving enough context for callers to correct the request.

**Alternatives considered**:

- Surface raw upstream error payloads directly: rejected because errors must be MCP-safe and must not expose sensitive details.
- Collapse all download errors into `upstream_failure`: rejected because conversion, auth, and not-found outcomes are distinct user-remediable categories.
- Hide conversion failure as empty content: rejected because failed conversion is not a successful caption download.

## Decision: Register Through Existing Dispatcher-Compatible Tool Descriptors

Implementation should add `captions_download` in the existing MCP tool registration/discovery path, using the same name, description, input schema, metadata, and handler concepts used by `activities_list`, `captions_list`, `captions_insert`, and `captions_update`.

**Rationale**: The dispatcher already registers callable tools with `name`, `description`, `inputSchema`, `handler`, and optional metadata. YT-203 through YT-206 established concrete Layer 2 endpoint patterns. YT-207 should follow them instead of changing transport or registry architecture.

**Alternatives considered**:

- Add a new binary-download route outside MCP tools: rejected because MCP tool discovery/invocation already exists and the feature is a Layer 2 MCP tool.
- Special-case YouTube invocation outside the dispatcher: rejected because it would bypass existing registry and contract tests.
- Change all remaining captions endpoints into executable tools in this slice: rejected because YT-207 is scoped only to `captions_download`.

## Decision: Extend the Captions Layer 2 Module

The concrete `captions_download` tool should live in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/captions.py`, with public exports added through `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/tools/youtube_common/__init__.py`.

**Rationale**: YT-201 resource-family placement points endpoint tools to family modules, and YT-204 through YT-206 already established the concrete captions resource-module pattern. Extending the captions module keeps endpoint-specific schema, OAuth validation, conversion validation, handler wiring, examples, and result shaping out of broad shared files while still using common contracts and conventions.

**Alternatives considered**:

- Add `captions_download` directly to `youtube_common/examples.py`: rejected because examples are representative and not the concrete execution surface.
- Add endpoint-specific behavior to `contracts.py` or `conventions.py`: rejected because those modules own shared cross-cutting primitives.
- Create a separate download-specific module for one endpoint: rejected until multiple concrete download/content-returning Layer 2 tools need shared helpers.

## Decision: Keep Discovery Metadata Explicit and Safe

The implementation must ensure callers can inspect `captions_download` quota, auth, upstream identity, availability, permission-to-edit caveat, required `id`, supported `tfmt`, supported `tlang`, delegation caveats, binary response context, and usage notes before invocation. If default dispatcher discovery needs metadata changes, those changes must be additive and preserve existing tool descriptors.

**Rationale**: YT-207 requires cost, permission, format, and language visibility before calling. Existing shared contracts include safe public metadata validation, and current concrete Layer 2 tools already surface endpoint metadata through dispatcher-compatible descriptors.

**Alternatives considered**:

- Rely only on Python contract objects: rejected because MCP-facing discovery is user-visible behavior.
- Rewrite dispatcher descriptors broadly: rejected because baseline tools and current MCP contract tests must remain stable.
- Hide conversion requirements only in prose docs: rejected because clients and reviewers need deterministic pre-invocation visibility.

## Decision: Keep Verification Constitution-Driven

Implementation must begin with failing tests, add minimal code, refactor, and finish with targeted checks plus `python3 -m pytest` and `python3 -m ruff check .`. Every new or changed Python function must include a reStructuredText docstring.

**Rationale**: The project constitution makes Red-Green-Refactor, integration/regression coverage, full-suite validation, and reStructuredText docstrings mandatory. YT-207 extends the concrete Layer 2 endpoint pattern established by YT-203 through YT-206 and will influence later captions delete and transcript-oriented slices.

**Alternatives considered**:

- Run only focused `captions_download` tests: rejected because the constitution requires full-suite validation after final code changes.
- Treat docstrings as optional for private helper functions: rejected because the constitution requires every new or modified Python function.
- Skip integration checks because the handler can be unit-tested: rejected because public tool discovery and registration are MCP-facing behavior.
