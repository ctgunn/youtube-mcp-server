# Research: Layer 2 Thumbnails Set Tool

## Decision: Implement `thumbnails_set` as the concrete Layer 2 tool for `thumbnails.set`

**Rationale**: The YT-244 seed requires exposing `thumbnails.set` as the low-level MCP tool named `thumbnails_set`. The PRD requires one Layer 2 public tool per supported YouTube Data API resource method, using resource-method naming and near-direct endpoint semantics. The thumbnails family is already reserved in the shared family registry, so a concrete thumbnails Layer 2 module is the cohesive place for this tool.

**Alternatives considered**: Add thumbnail-setting behavior to playlist image tools or video tools; rejected because `thumbnails.set` is a distinct upstream resource method and the spec explicitly excludes playlist-image management, video metadata updates, thumbnail generation, image transformation, analytics, and higher-level workflows. Keep a representative placeholder only; rejected because YT-244 requires a public endpoint-backed tool.

## Decision: Rely on the existing Layer 1 `build_thumbnails_set_wrapper()`

**Rationale**: YT-144 already provides the Layer 1 `thumbnails.set` wrapper, including endpoint identity, `POST /youtube/v3/thumbnails/set`, required `videoId`, required `media`, OAuth-required auth, quota cost `50`, and target/upload validation guidance. YT-244 should expose that capability publicly instead of redefining upstream behavior in Layer 2.

**Alternatives considered**: Implement a direct upstream call inside Layer 2; rejected because Layer 2 tools must depend on Layer 1 wrappers for endpoint behavior. Change Layer 1 as part of YT-244; rejected unless implementation tests later reveal a narrow export, metadata, or validation gap.

## Decision: Support only `videoId` plus `media` as required public inputs

**Rationale**: The Layer 1 wrapper and feature spec identify a video identifier and thumbnail upload content as the required request pair. Keeping the request shape to required `videoId` and required `media` preserves endpoint semantics, makes validation clear, and avoids implying thumbnail generation, image transformation, video lookup, video metadata editing, or bulk behavior.

**Alternatives considered**: Accept video URLs, search terms, channel selectors, metadata bodies, image transformation instructions, thumbnail generation prompts, or listing modifiers; rejected because those require separate endpoint calls or higher-level composition. Add bulk thumbnail setting; rejected because the endpoint-backed Layer 2 tool should set one video's thumbnail per call.

## Decision: Require OAuth-backed authorization for every `thumbnails_set` call

**Rationale**: Thumbnail setting mutates video presentation and uploads media for an authorized account. The seed requires OAuth requirements to be documented clearly, and the Layer 1 wrapper enforces OAuth-required access. Metadata, descriptions, examples, validation, and errors must make this visible before invocation.

**Alternatives considered**: Allow API-key access for public thumbnail setting; rejected because media-upload mutation is account-scoped. Silently attempt execution without OAuth and rely on upstream rejection; rejected because local validation should give safer and clearer feedback.

## Decision: Publish official quota cost `50` everywhere the caller evaluates the tool

**Rationale**: The YT-244 seed identifies official quota cost `50`. YT-202 requires quota visibility in metadata, descriptions, and examples. Result context should also carry quota cost so callers can audit successful and failed workflows.

**Alternatives considered**: Put quota only in shared metadata; rejected because the seed explicitly requires tool description/examples to document the cost. Defer quota to external documentation; rejected because clients must understand cost from discovery and contract artifacts alone.

## Decision: Return a thumbnail-set result with safe target and upload context

**Rationale**: `thumbnails.set` can return a sparse result or a returned thumbnail payload depending on upstream behavior. The Layer 2 result should preserve endpoint identity, quota cost, requested video id, OAuth mode, sanitized upload descriptor, and any safe returned upstream context without fabricating thumbnail, video, channel, analytics, or enrichment details.

**Alternatives considered**: Return raw upload content or complete video metadata; rejected because raw media and unrelated metadata are unsafe or not guaranteed by the endpoint. Return only `true`; rejected because callers need enough context to identify the operation and audit quota/access behavior.

## Decision: Map target-video, upload, and upstream failures into safe Layer 2 categories

**Rationale**: The spec requires clear distinctions between validation failures, access failures, target-video failures, unsupported upload failures, upstream upload rejections, quota failures, invalid requests, unavailable service, deprecated behavior, and unexpected upstream failures. Existing media-upload mutation tools map normalized upstream categories to safe caller-facing categories while sanitizing credentials, raw uploads, and raw diagnostics.

**Alternatives considered**: Pass through raw upstream failures; rejected because the constitution requires secure, deterministic, machine-readable outputs without secret, media, or diagnostic leaks. Collapse target-video and upload failures into one generic error; rejected because callers need to distinguish correctable local upload issues from upstream target-state rejections.

## Decision: Add focused thumbnails family tests and shared registry coverage

**Rationale**: The thumbnails Layer 2 family is not yet concrete, so this slice should add `tests/contract/test_youtube_thumbnails_contract.py`, `tests/unit/test_youtube_thumbnails.py`, and `tests/integration/test_youtube_thumbnails_registration.py`, while also updating common catalog and registration tests. This matches YT-201/YT-202 patterns and proves public discovery, validation, execution, and default registry behavior.

**Alternatives considered**: Place all assertions in shared common tests; rejected because endpoint-specific media-upload behavior deserves a cohesive family test file. Use only unit tests; rejected by the constitution and spec, which require contract, integration, and full-suite validation.

## Decision: Require reStructuredText docstrings for all new or changed Python functions

**Rationale**: Constitution v1.2.0 requires every new or modified Python function to include a reStructuredText docstring covering purpose, inputs, outputs, raised errors when relevant, and side effects when relevant. YT-244 implementation will likely add or change contract builders, descriptor builders, handlers, validators, result mappers, error mappers, default executor helpers, exports, and fake wrapper methods in tests.

**Alternatives considered**: Add docstrings only to public functions; rejected because the constitution applies to every new or changed Python function. Defer docstrings to review cleanup; rejected because docstrings are a planning and implementation gate.
