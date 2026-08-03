# Implementation Plan: YT-158 Layer 1 Live Calls for Channel and Community Resources

**Branch**: `158-channel-community-live-calls` | **Date**: 2026-08-02 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/158-channel-community-live-calls/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/158-channel-community-live-calls/spec.md`

## Summary

Retrofit the 20 existing channel and community Layer 1 operations so that normal configured public-tool invocation reaches the YT-157 shared live runtime rather than family-specific representative executors. Extend the existing application → HTTP transport → dispatcher dependency-injection seam from `activities_list` to the other 19 operations. Preserve existing wrapper metadata, selector and body validation, quota documentation, authorization selection, response normalizers, MCP schemas and metadata, safe error mapping, retry behavior, and observability. Explicit fake executors, credentials, and controlled openers remain allowed only as supplied test or local-development dependencies.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: FastAPI, Pydantic v2, Uvicorn, Python standard-library `urllib`/JSON/dataclasses, existing Layer 1 integration modules, pytest, and Ruff  
**Storage**: No feature-specific persistent storage; runtime settings and credentials are environment/secret-backed, and request/observability state is in memory  
**Testing**: `python3 -m pytest` for unit, contract, integration, and transport coverage; `python3 -m ruff check .` for lint validation  
**Documentation Style**: reStructuredText docstrings for every new or changed Python function; feature-local Markdown contract documentation  
**Target Platform**: Local macOS/Linux development and the existing hosted Linux MCP service  
**Project Type**: Python MCP web service with internal Layer 1 YouTube integrations and public Layer 2 tool descriptors  
**Performance Goals**: Preserve the shared live runtime's existing 10-second per-attempt timeout and three-attempt maximum; add no endpoint-specific persistence, concurrency, or retry policy  
**Constraints**: All 20 configured default operations must use the shared live executor; no configured-path fallback may return representative data; API keys, OAuth tokens, bearer headers, credential-bearing URLs, raw request bodies, and media must not appear in logs, errors, MCP results, documentation examples, or test evidence; existing MCP schemas, metadata, wrapper contracts, normalizers, and safe error categories remain compatible; every changed Python function requires a reStructuredText docstring  
**Scale/Scope**: Seven resource families and 20 existing operations: activities (1), captions (5), channel banners (1), channels (2), channel sections (4), comments (5), and comment threads (2); no new endpoint inventory or public MCP tools

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

- [layer1-channel-community-live-call-contract.md](contracts/layer1-channel-community-live-call-contract.md) records the configured default-execution boundary and guarantees stable public tool schemas, metadata, results, and error categories.
- Every implementation grouping below starts with failing tests, adds only runtime injection, then performs behavior-preserving cleanup. Final verification from `/Users/ctgunn/Projects/youtube-mcp-server` is `python3 -m pytest` followed by `python3 -m ruff check .`.
- Any changed Python builder, handler, test helper, or dispatcher helper must retain or gain a reStructuredText docstring with `:param:`, `:return:`, `:raises:` where applicable, and side-effect documentation. No docstring or test fixture may contain a real credential.
- The design reuses `ConfiguredYouTubeRuntime`, `IntegrationExecutor`, the existing concrete YouTube transport, response normalizers, error mapper, retry policy, and observability hooks. It adds no second client, endpoint-specific transport, storage, MCP route, or secret source.

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/158-channel-community-live-calls/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── layer1-channel-community-live-call-contract.md
└── tasks.md                         # Created later by /speckit.tasks
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/
├── app.py                            # Existing runtime-settings composition root
├── transport/http.py                 # Builds the configured runtime and dispatcher
├── tools/
│   ├── dispatcher.py                 # Extends runtime injection to all 20 descriptors
│   └── youtube_common/
│       ├── activities.py
│       ├── captions.py
│       ├── channel_banners.py
│       ├── channels.py
│       ├── channel_sections.py
│       ├── comments.py
│       └── comment_threads.py         # Existing handlers/descriptors and test seams
└── integrations/
    ├── runtime.py                     # YT-157 configured runtime (reuse)
    ├── executor.py                    # Shared executor, retry, and observability hooks (reuse)
    ├── youtube.py                     # Concrete request builder/transport/normalization (reuse)
    └── resources/
        ├── base.py
        ├── activities.py
        ├── captions.py
        ├── channel_banners.py
        ├── channels.py
        ├── channel_sections.py
        ├── comments.py
        └── comment_threads.py         # Existing metadata/validation compatibility boundary

/Users/ctgunn/Projects/youtube-mcp-server/tests/
├── unit/
│   ├── test_layer1_live_runtime.py
│   ├── test_youtube_transport.py
│   └── test_youtube_{activities,captions,channel_banners,channels,channel_sections,comments,comment_threads}.py
├── integration/
│   ├── test_layer1_live_runtime.py
│   └── test_youtube_{activities,captions,channel_banners,channels,channel_sections,comments,comment_threads}_registration.py
└── contract/
    ├── test_layer1_{activities,captions,channel_banners,channels,channel_sections,comments,comment_threads}_contract.py
    └── test_youtube_{activities,captions,channel_banners,channels,channel_sections,comments,comment_threads}_contract.py
```

**Structure Decision**: Keep the existing single Python MCP service and YT-157 composition path. Make the minimal dispatcher wiring change needed to pass the same configured runtime executor and configured credentials to every in-scope descriptor. Resource modules remain the validation/metadata boundary and `youtube_common` modules retain explicit test/local overrides; no new project, route, client, database, or endpoint-specific execution layer is introduced.

## Phase 0: Research and Open Questions

### Research Findings

- `ConfiguredYouTubeRuntime` already wraps the shared concrete executor, resolves a secret-backed API-key or OAuth context, and supplies credential-free configuration failures. `MCPHTTPTransport` already creates this runtime and passes it to `InMemoryToolDispatcher`.
- `InMemoryToolDispatcher._baseline_tool_definitions()` currently injects runtime dependencies only into `activities_list`; the other 19 in-scope descriptors use their family-local representative default executor. Every relevant descriptor already accepts an executor and the required API-key/OAuth values, so extending the existing injection seam is sufficient.
- `RepresentativeEndpointWrapper` is a legacy name for the common metadata-driven wrapper. It validates endpoint arguments, builds `RequestExecution`, and invokes the supplied shared executor. Existing resource modules retain selector/write authorization rules and endpoint-specific validators; they should not receive a second live transport implementation.
- The concrete request path in `integrations/youtube.py` uses endpoint metadata and `RequestExecution`, attaches API keys as query credentials or OAuth as bearer authorization, supports query-only, JSON, raw-media, and multipart forms, dispatches existing response normalizers, and maps upstream failures into the shared error model.
- Existing Layer 2 descriptors are the external contract boundary. Their public tool name, description, input schema, metadata, result mapper, and safe error mapper must remain unchanged when their executor changes from the representative default to the configured live runtime.
- Controlled openers and explicit executors provide deterministic verification without real credentials or network calls. A distinctive controlled response and captured request prove that a flow reached live request construction instead of a representative transport.

### Phase 0 Red-Green-Refactor

- **Red**: Add characterization tests that fail because configured dispatcher construction injects the live runtime only into `activities_list`, while the other 19 operations use local representative defaults. Cover absent selected credentials, captured request shape, safe upstream failure mapping, and no secret leakage.
- **Green**: Define the complete 20-operation injection matrix, credential rules, and public compatibility obligations in `research.md`, `data-model.md`, and the feature contract. Use the existing runtime's executor/settings pair as the only configured dependency source.
- **Refactor**: Remove any proposed per-resource HTTP client, credential lookup, response mapper, retry logic, or observability path. Keep all research conclusions consistent with the established YT-157 runtime contract.

## Phase 1: Design and Contracts

### Design Goals

- Use the existing configured runtime for every normal public descriptor in the seven in-scope families.
- Preserve the 20 existing Layer 1 metadata/request-validation contracts and the 20 existing Layer 2/MCP contracts.
- Resolve conditional authorization from current selector rules and retain API-key-only and OAuth-required behavior without heuristic fallback.
- Let existing request shaping submit query-only, JSON, raw-media, or multipart forms; no descriptor or wrapper reimplements HTTP transport behavior.
- Preserve explicit test/local executor, opener, and credential injection only when a caller deliberately supplies it.
- Preserve safe normalized errors, response normalizers, retry selection, and secret-free integration observability.

### Design Artifacts

- [research.md](research.md)
- [data-model.md](data-model.md)
- [layer1-channel-community-live-call-contract.md](contracts/layer1-channel-community-live-call-contract.md)
- [quickstart.md](quickstart.md)

### Phase 1 Red-Green-Refactor

- **Red**: Confirm the artifacts expose no unresolved decisions and that they identify a failing test for each default-execution gap, public-contract preservation rule, and safe-failure path.
- **Green**: Produce the entity/request-state model, the compatibility contract, and reproducible controlled-runtime verification instructions. Document each operation family and request form without changing public schemas.
- **Refactor**: Deduplicate material inherited from YT-157 by referencing its existing shared runtime responsibilities. Re-check that all artifacts keep the feature limited to channel and community resource-family live-call retrofits.

## Phase 2: Implementation Strategy

### Shared Configured-Descriptor Wiring

- **Red**: Add a parameterized dispatcher/registration test that constructs `ConfiguredYouTubeRuntime` with a controlled opener and fails unless all 20 descriptor builders receive its executor and configured credential availability. Assert a configured descriptor cannot select a `_default_*_executor` or placeholder token.
- **Green**: In `tools/dispatcher.py`, construct one shared runtime-dependency argument set and pass it to the existing descriptor builders for captions, channel banners, channels, channel sections, comments, and comment threads, matching the already-working activities pattern. Do not modify the application or transport composition unless a narrowly demonstrated propagation defect requires it.
- **Refactor**: Centralize repeated dispatcher dependency construction, keep explicit descriptor arguments intact for isolated tests/local development, audit all changed Python docstrings, and run focused dispatcher/registration checks.

### User Story 1 - Receive Live Channel and Community Results

- **Red**: Add 20 parameterized request-level cases that call the configured path with a controlled opener. Each case must fail if it returns a representative payload or does not build the expected live request for: activities (1), captions (5), channel banners (1), channels (2), channel sections (4), comments (5), and comment threads (2).
- **Green**: Route each existing handler to the injected `IntegrationExecutor` and existing resource wrapper, without changing its handler result mapper, wrapper metadata, selector validation, quota documentation, or response normalizer.
- **Refactor**: Consolidate test fixtures for controlled upstream success responses and captured request assertions; retain only existing family-specific result mapping and avoid resource-specific execution helpers. Add or update reStructuredText docstrings on every changed Python function.

### User Story 2 - Apply the Correct Authorization and Request Form

- **Red**: For every operation, assert the method, path, query values, selected credential location, body, and upload form where applicable. Add controlled failures for missing API-key/OAuth credentials, HTTP authorization rejection, malformed response, timeout, and retryable upstream failure; each must fail if it exposes a secret or returns a representative success.
- **Green**: Reuse current conditional selector decisions for `activities.list`, `channels.list`, and `channelSections.list`; retain API-key reads for comments/comment threads and OAuth rules for caption, banner, and mutation flows. Rely on the concrete transport for GET/query, JSON, raw banner media, and caption multipart/media request forms.
- **Refactor**: Keep credential selection and safe error mapping centralized in existing runtime/transport/tool conventions. Remove any temporary test-only branches and document changed helper inputs, results, raised errors, and side effects in reStructuredText docstrings.

### User Story 3 - Use Live Wrappers Through Public Tools

- **Red**: Add seven configured public-tool flow tests—one each for activities, captions, channel banners, channels, channel sections, comments, and comment threads—that fail unless the controlled opener sees a live request through application/transport/dispatcher composition. Include a normalized upstream-failure flow to prove no bypass or sample fallback.
- **Green**: Keep the existing descriptor registration and MCP dispatch behavior while supplying the shared runtime to each selected tool. Use controlled upstream payloads distinct from the existing representative defaults and assert the existing public result/error shape.
- **Refactor**: Reuse a single controlled runtime fixture and request recorder where possible; preserve family-specific public error classes and schema metadata. Run focused integration and contract suites after cleanup.

### Regression Strategy

- Run targeted live-runtime and transport checks: `python3 -m pytest tests/unit/test_layer1_live_runtime.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_live_runtime.py`.
- Run all affected resource unit, registration, and contract suites: `python3 -m pytest tests/unit/test_youtube_activities.py tests/unit/test_youtube_captions.py tests/unit/test_youtube_channel_banners.py tests/unit/test_youtube_channels.py tests/unit/test_youtube_channel_sections.py tests/unit/test_youtube_comments.py tests/unit/test_youtube_comment_threads.py tests/integration/test_youtube_activities_registration.py tests/integration/test_youtube_captions_registration.py tests/integration/test_youtube_channel_banners_registration.py tests/integration/test_youtube_channels_registration.py tests/integration/test_youtube_channel_sections_registration.py tests/integration/test_youtube_comments_registration.py tests/integration/test_youtube_comment_threads_registration.py`.
- Run affected Layer 1 and public contract suites: `python3 -m pytest tests/contract/test_layer1_activities_contract.py tests/contract/test_layer1_captions_contract.py tests/contract/test_layer1_channel_banners_contract.py tests/contract/test_layer1_channels_contract.py tests/contract/test_layer1_channel_sections_contract.py tests/contract/test_layer1_comments_contract.py tests/contract/test_youtube_activities_contract.py tests/contract/test_youtube_captions_contract.py tests/contract/test_youtube_channel_banners_contract.py tests/contract/test_youtube_channels_contract.py tests/contract/test_youtube_channel_sections_contract.py tests/contract/test_youtube_comments_contract.py`.
- Before completion, run `python3 -m pytest` and then `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`. Any full-suite failure must be fixed before the feature is complete.

### Rollback and Mitigation

- Keep all existing explicit executor, opener, wrapper, and credential injection parameters so unit and local-development callers remain deterministic.
- Confine the change to descriptor dependency selection. If a rollout needs reversal, revert that configured injection change while preserving endpoint metadata, public schemas, validation, normalizers, and error categories.
- Never roll back to a representative successful response on a configured live-path failure; return the existing safe configuration, authorization, or upstream failure instead.
- Continue to redact API keys, OAuth tokens, bearer headers, credential-bearing query strings, raw request bodies, raw media, stack traces, and raw upstream failure bodies from all diagnostics, results, and review evidence.

## Post-Design Constitution Check

- [x] Contracts defined or updated for all external/MCP-facing behavior changes
- [x] Plan includes explicit Red-Green-Refactor steps for each phase and user story
- [x] Red phase identifies failing tests before implementation tasks begin
- [x] Green phase limits implementation to minimum code required for passing tests
- [x] Refactor phase includes cleanup tasks with a full repository test-suite re-run
- [x] Integration and regression coverage strategy is documented
- [x] Plan names the command that proves the full repository test suite passes before completion
- [x] Plan defines how reStructuredText docstrings will be added or preserved for new and changed Python functions
- [x] Observability, security, and simplicity constraints are addressed

Post-design rationale:

- The feature contract records the configuration-to-public-tool boundary and explicitly preserves all external/MCP contracts.
- The implementation strategy begins with 20 request-level and seven public-flow failing tests, adds only dispatcher dependency injection, and ends with focused and full-suite cleanup verification.
- The existing shared runtime, executor, transport, normalizers, retry policy, and observability hooks remain the only execution architecture; this is the simplest design that satisfies the live-call gate.
- Docstring work, safe diagnostics, credential redaction, and rollback behavior are explicit for every changed function and all proof paths.

## Complexity Tracking

No constitution violations or added architectural complexity are required for this plan.
