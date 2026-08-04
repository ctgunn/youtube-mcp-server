# Implementation Plan: YT-160 Layer 1 Live Calls for Discovery, Video, and Branding Resources

**Branch**: `160-discovery-video-live-calls` | **Date**: 2026-08-03 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/160-discovery-video-live-calls/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/160-discovery-video-live-calls/spec.md`

## Summary

Retrofit the original 16 discovery, subscription, video, and branding configured-default operations so a normal public-tool invocation reaches the shared live runtime rather than a family-local representative executor. YT-160 is also the shared live-execution completion owner for every YouTube Data API-backed tool: capability readiness, renewable OAuth, Google media upload protocol, resumable video upload, method-safe retry, and operator-gated real verification. Preserve public MCP schemas and metadata, wrapper contracts, validation, quota disclosures, authorization selection, response normalizers, safe error mapping, and observability. Explicit fake executors, credentials, and controlled openers remain test or deliberate local-development dependencies only.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: FastAPI, Pydantic v2, Uvicorn, Python standard-library `urllib`/JSON/dataclasses, existing Layer 1 integration modules, pytest, and Ruff  
**Storage**: No feature-specific persistent storage; runtime settings and credentials are environment/secret-backed, while request and observability state are in memory  
**Testing**: `python3 -m pytest` for unit, contract, integration, and transport coverage; `python3 -m ruff check .` for lint validation  
**Documentation Style**: reStructuredText docstrings for every new or changed Python function; feature-local Markdown contract documentation  
**Target Platform**: Local macOS/Linux development and the existing hosted Linux MCP service  
**Project Type**: Python MCP web service with internal Layer 1 YouTube integrations and public Layer 2 and Layer 3 tools  
**Performance Goals**: Preserve the configured per-attempt timeout; use bounded exponential backoff only for idempotent retries; transfer resumable video uploads in configurable 256 KiB-aligned chunks
**Constraints**: All configured default YouTube Data API operations must use the shared live executor; the original 16 operations remain the request-level regression matrix; `videos_getVideo` must delegate to the configured live `videos.list` handler; no configured-path fallback may return representative data; API keys, OAuth tokens, bearer headers, credential-bearing URLs, raw request bodies, media, and opaque resumable session URLs must not appear in logs, errors, MCP results, documentation examples, or test evidence; existing MCP schemas, metadata, wrapper contracts, normalizers, and safe error categories remain compatible; every changed Python function requires a reStructuredText docstring
**Scale/Scope**: Shared execution capability for all YouTube Data API-backed tools, with the original seven-family/16-operation set retained for configured-default regression coverage; no new public tool inventory or persistent credential store

## Constitution Check

*GATE: Passed before Phase 0 research. Re-checked and passed after Phase 1 design.*

- [x] Contracts defined or updated for all external/MCP-facing behavior changes
- [x] Plan includes explicit Red-Green-Refactor steps for each phase and user story
- [x] Red phase identifies failing tests before implementation tasks begin
- [x] Green phase limits implementation to minimum code required for passing tests
- [x] Refactor phase includes cleanup tasks with a full repository test-suite re-run
- [x] Integration and regression coverage strategy is documented
- [x] Plan names the command that proves the full repository test suite passes before completion
- [x] Plan defines how reStructuredText docstrings will be added or preserved for new and changed Python functions
- [x] Observability, security, and simplicity constraints are addressed

Gate rationale:

- [layer1-discovery-video-branding-live-call-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/160-discovery-video-live-calls/contracts/layer1-discovery-video-branding-live-call-contract.md) defines the configured default-execution boundary and preserves public MCP contracts, Layer 1 contracts, and error categories.
- Every implementation grouping begins with failing characterization tests, adds only dependency injection or a narrowly scoped composed lookup injection, then performs behavior-preserving cleanup. Final verification from `/Users/ctgunn/Projects/youtube-mcp-server` is `python3 -m pytest` followed by `python3 -m ruff check .`.
- Any changed Python builder, handler, helper, or dispatcher function must retain or gain a reStructuredText docstring with `:param:`, `:return:`, `:raises:` where applicable, and side-effect documentation. No docstring or test fixture may contain a real credential.
- The design reuses `ConfiguredYouTubeRuntime`, `IntegrationExecutor`, the concrete YouTube transport, response normalizers, error mapper, retry policy, and observability hooks. It adds shared OAuth refresh and Google upload protocol support, but no second client, resource-family transport, storage, MCP route, public tool, or persistent secret source.

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/160-discovery-video-live-calls/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── layer1-discovery-video-branding-live-call-contract.md
└── tasks.md                         # Created later by /speckit.tasks
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/
├── app.py                            # Existing runtime-settings composition root (reuse)
├── transport/http.py                 # Builds configured runtime and dispatcher (reuse)
├── tools/
│   ├── dispatcher.py                 # Inject runtime dependencies into in-scope descriptors
│   ├── youtube_common/
│   │   ├── search.py
│   │   ├── subscriptions.py
│   │   ├── thumbnails.py
│   │   ├── video_abuse_report_reasons.py
│   │   ├── video_categories.py
│   │   ├── videos.py
│   │   └── watermarks.py              # Existing descriptors/handlers and test seams
│   └── youtube_composed/videos.py     # Inject configured lower-level video lookup
└── integrations/
    ├── runtime.py                     # YT-157 configured runtime (reuse)
    ├── executor.py                    # Shared executor, retries, observability hooks (reuse)
    ├── youtube.py                     # Concrete request builder, transport, normalization (reuse)
    └── resources/
        ├── base.py
        ├── search.py
        ├── subscriptions.py
        ├── thumbnails.py
        ├── video_abuse_report_reasons.py
        ├── video_categories.py
        ├── videos.py
        └── watermarks.py              # Existing metadata/validation compatibility boundary

/Users/ctgunn/Projects/youtube-mcp-server/tests/
├── unit/
│   ├── test_layer1_live_runtime.py
│   ├── test_youtube_transport.py
│   └── test_youtube_{search,subscriptions,thumbnails,video_abuse_report_reasons,video_categories,videos,watermarks}.py
├── integration/
│   ├── test_layer1_live_runtime.py
│   ├── test_youtube_tool_registration.py
│   ├── test_youtube_composed_tool_registration.py
│   └── test_youtube_{search,subscriptions,thumbnails,video_abuse_report_reasons,video_categories,videos,watermarks}_registration.py
└── contract/
    ├── test_layer1_videos_contract.py
    ├── test_youtube_composed_videos_contract.py
    └── test_youtube_{search,subscriptions,thumbnails,video_abuse_report_reasons,video_categories,videos,watermarks}_contract.py
```

**Structure Decision**: Keep the existing single Python MCP service and YT-157 composition path. Change only the dispatcher dependency selection and the composed-video lookup injection required to pass the configured runtime executor and configured credentials to every in-scope descriptor. Preserve resource modules as the validation and metadata boundary, `youtube_common` modules as explicit test/local override seams, and `videos_getVideo` as a composition-only consumer of `videos.list`; introduce no project, route, client, database, endpoint-specific execution layer, or public schema.

## Phase 0: Research and Open Questions

### Research Findings

- `create_app()` loads secret-backed settings, the HTTP transport builds `ConfiguredYouTubeRuntime`, and `InMemoryToolDispatcher` already builds conditional, API-key, and OAuth dependency groups. The seven YT-160 descriptor families are currently built without these groups, which selects their local representative defaults; the dispatcher is the single intended retrofit point.
- The dependency matrix is conditional credentials for `search.list`, `subscriptions.list`, and `videos.list`; API-key credentials for `videoAbuseReportReasons.list` and `videoCategories.list`; and OAuth credentials for subscription writes, thumbnail and watermark operations, and all video writes or ratings. `videos_getVideo` must receive a lookup built from the configured conditional `videos.list` handler because its descriptor accepts a lookup rather than runtime dependencies.
- Existing resource wrappers retain metadata-defined target, method, request validation, selector behavior, quota documentation, authorization rules, and response normalization. The shared executor and concrete transport own query parameters, JSON bodies, raw-media and multipart forms, credentials, retry behavior, upstream-error normalization, and secret-safe observability.
- The media operations are `thumbnails.set`, `videos.insert`, and `watermarks.set`. They must use the existing shared transport only. Existing `videos.insert` validation continues to expose `multipart` and `resumable` upload-mode values; this retrofit does not introduce a resumable-session protocol or resource-specific upload code, and continues to use the shared transport's established body-and-media request behavior.
- Controlled openers and distinctive responses prove configured composition and request construction without external network access, quota consumption, account-state dependencies, or real secrets.

### Phase 0 Red-Green-Refactor

- **Red**: Add failing characterization tests showing each of the 16 configured descriptor paths captures the configured runtime executor rather than a local executor or local credential. Add a failing `videos_getVideo` test showing that its default composed lookup currently selects a local `videos.list` handler.
- **Green**: Record the complete operation, authorization, request-form, public-compatibility, upload, error, and secret-redaction decisions in [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/160-discovery-video-live-calls/research.md), [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/160-discovery-video-live-calls/data-model.md), and the feature contract. Select the configured runtime executor and settings pair as the only configured dependency source.
- **Refactor**: Reject any proposal for a per-resource HTTP client, credential lookup, response mapper, retry logic, media-transfer logic, or observability path. Keep all conclusions aligned with the existing YT-157 runtime contract.

## Phase 1: Design and Contracts

### Design Goals

- Use the existing configured runtime for every normal public descriptor in the seven in-scope families.
- Preserve the 16 existing Layer 1 metadata and request-validation contracts and all Layer 2 and Layer 3 public contracts.
- Retain API-key-only, OAuth-required, and selector-driven conditional authorization without fallback based merely on another available credential.
- Make `videos_getVideo` call the configured `videos.list` handler; it must not make its own raw YouTube request.
- Let the existing transport submit query-only, JSON, raw-media, and multipart requests; no descriptor or wrapper reimplements request behavior.
- Preserve explicit test/local executor, opener, wrapper, and credential injection only when a caller deliberately supplies it.
- Preserve safe normalized errors, response normalizers, retry selection, and secret-free integration observability.

### Design Artifacts

- [research.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/160-discovery-video-live-calls/research.md)
- [data-model.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/160-discovery-video-live-calls/data-model.md)
- [layer1-discovery-video-branding-live-call-contract.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/160-discovery-video-live-calls/contracts/layer1-discovery-video-branding-live-call-contract.md)
- [quickstart.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/160-discovery-video-live-calls/quickstart.md)

### Phase 1 Red-Green-Refactor

- **Red**: Confirm the design exposes no unresolved decisions and identifies a failing test for every default-execution gap, public-contract preservation rule, media path, and safe-failure path.
- **Green**: Produce the entity and request-state model, compatibility contract, and reproducible controlled-runtime verification instructions. Document each operation family and request form without changing public schemas.
- **Refactor**: Deduplicate material already guaranteed by YT-157 by referencing its shared runtime responsibilities. Re-check that all artifacts remain limited to discovery, subscription, video, and branding live-call retrofits.

## Phase 2: Implementation Strategy

### Shared Configured-Descriptor Wiring

- **Red**: Add a parameterized dispatcher test that constructs `ConfiguredYouTubeRuntime` with a controlled opener and fails unless all 16 descriptor builders capture its executor and only its configured credential values. Add a composed-tool test that fails unless `videos_getVideo` captures a configured `videos.list` lookup. Assert no configured descriptor closure selects a `_default_*_executor`, `local-api-key`, or `local-oauth-token`.
- **Green**: In `tools/dispatcher.py`, pass conditional dependencies to the search, subscription-list, and video-list descriptor builders; API-key dependencies to video-abuse-reason and video-category list builders; and OAuth dependencies to subscription writes, thumbnail, video mutation/rating, and watermark builders. Build the `videos_getVideo` lookup using the same configured conditional `videos.list` dependencies and supply it to the composed descriptor.
- **Refactor**: Centralize repeated dispatcher dependency construction where it improves clarity, retain explicit descriptor arguments for isolated tests and local development, audit every changed Python docstring, and run focused dispatcher and registration checks.

### User Story 1 - Receive Live Discovery and Video Results

- **Red**: Add 16 parameterized request-level cases that call the configured path with a controlled opener. Each case must fail if it returns a representative payload or does not build the expected live request for search (1), subscriptions (3), thumbnails (1), video abuse-report reasons (1), video categories (1), videos (7), and watermarks (2).
- **Green**: Route each existing handler to the injected `IntegrationExecutor` and existing resource wrapper without changing result mappers, wrapper metadata, request validation, quota documentation, selector behavior, or response normalizers.
- **Refactor**: Consolidate controlled upstream success payloads and captured-request assertions. Retain only existing family-specific result mapping, avoid resource-specific execution helpers, and add or update reStructuredText docstrings for every changed Python function.

### User Story 2 - Perform Authorized Video and Subscription Changes

- **Red**: For every operation, assert the method, path, query values, selected credential location, body, raw-media or multipart form where applicable. Add controlled missing-credential, upstream authorization, malformed-response, timeout, and retryable-failure cases; each must fail if it exposes a secret or returns representative success.
- **Green**: Preserve API-key public reads for video abuse reasons and categories; selector-driven API-key versus OAuth access for search, subscriptions, and video listing; and OAuth-only subscription writes, thumbnail, video mutation/rating, and watermark operations. Rely on the concrete transport for GET/query, JSON, raw-media, and multipart request forms.
- **Refactor**: Keep credential selection and safe error mapping in current runtime, transport, and tool conventions. Remove temporary test-only branches and document changed helper inputs, results, raised errors, and side effects in reStructuredText docstrings.

### User Story 3 - Reach Live Wrappers Through Existing Public Tools

- **Red**: Add three configured public-tool flow tests for `search_list`, `videos_list`, and `videos_getVideo` that fail unless the controlled opener sees a live request through application, transport, dispatcher, descriptor, wrapper, and common transport composition. Include one normalized upstream-failure flow that proves no bypass or sample fallback.
- **Green**: Keep existing descriptor registration, MCP dispatch behavior, and composed video-detail normalization while supplying the shared runtime to every selected tool. Use controlled upstream payloads distinct from representative defaults and assert existing public result and error shapes.
- **Refactor**: Reuse one controlled runtime fixture and request recorder where possible; preserve existing public error classes and schema metadata. Run focused integration and contract suites after cleanup.

### Regression Strategy

- Run targeted runtime and transport checks: `python3 -m pytest tests/unit/test_layer1_live_runtime.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_live_runtime.py tests/integration/test_youtube_tool_registration.py tests/integration/test_youtube_composed_tool_registration.py`.
- Run affected unit and registration suites: `python3 -m pytest tests/unit/test_youtube_search.py tests/unit/test_youtube_subscriptions.py tests/unit/test_youtube_thumbnails.py tests/unit/test_youtube_video_abuse_report_reasons.py tests/unit/test_youtube_video_categories.py tests/unit/test_youtube_videos.py tests/unit/test_youtube_watermarks.py tests/integration/test_youtube_search_registration.py tests/integration/test_youtube_subscriptions_registration.py tests/integration/test_youtube_thumbnails_registration.py tests/integration/test_youtube_video_abuse_report_reasons_registration.py tests/integration/test_youtube_video_categories_registration.py tests/integration/test_youtube_videos_registration.py tests/integration/test_youtube_watermarks_registration.py`.
- Run affected Layer 1 and public contract suites: `python3 -m pytest tests/contract/test_layer1_videos_contract.py tests/contract/test_youtube_composed_videos_contract.py tests/contract/test_youtube_search_contract.py tests/contract/test_youtube_subscriptions_contract.py tests/contract/test_youtube_thumbnails_contract.py tests/contract/test_youtube_video_abuse_report_reasons_contract.py tests/contract/test_youtube_video_categories_contract.py tests/contract/test_youtube_videos_contract.py tests/contract/test_youtube_watermarks_contract.py`.
- Before completion, run `python3 -m pytest` and then `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`. Any full-suite failure must be fixed before the feature is complete.

### Rollback and Mitigation

- Keep all existing explicit executor, opener, wrapper, and credential injection parameters so unit and local-development callers remain deterministic.
- Confine production-path changes to dispatcher dependency selection and composed video-detail lookup injection. If a rollout needs reversal, revert that injection while preserving endpoint metadata, public schemas, validation, normalizers, and error categories.
- Never roll back to a representative successful response on a configured live-path failure; return the existing safe configuration, authorization, or upstream failure instead.
- Continue to redact API keys, OAuth tokens, bearer headers, credential-bearing query strings, raw request bodies, raw media, stack traces, and raw upstream failure bodies from diagnostics, results, and review evidence.

## Post-Design Constitution Check

- [x] Contract records the execution-only change for every external/MCP-facing tool while preserving existing schemas, metadata, success results, and error categories.
- [x] Phase 0, Phase 1, shared wiring, and every user-story strategy explicitly follows Red-Green-Refactor, with Red before implementation and Refactor before completion.
- [x] Unit, integration, transport, contract, public-tool flow, missing-credential, upstream-failure, retry, and redaction coverage are defined, with required full-suite execution.
- [x] Final commands are `python3 -m pytest` and `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- [x] Changed Python functions require reStructuredText docstrings containing purpose, parameters, result, raised errors where applicable, and side effects where applicable.
- [x] The design reuses one configured runtime, executor, transport, normalizer registry, retry policy, observability path, and secret source. It adds no unneeded complexity and keeps all diagnostics credential-free.

## Complexity Tracking

No constitution violations or complexity exceptions require justification.
