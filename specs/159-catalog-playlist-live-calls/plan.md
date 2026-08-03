# Implementation Plan: YT-159 Layer 1 Live Calls for Catalog, Membership, and Playlist Resources

**Branch**: `159-catalog-playlist-live-calls` | **Date**: 2026-08-02 | **Spec**: [spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/159-catalog-playlist-live-calls/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/159-catalog-playlist-live-calls/spec.md`

## Summary

Retrofit the 17 existing catalog, membership, and playlist Layer 1 operations so normal configured public-tool invocation reaches the YT-157 shared live runtime rather than family-specific representative executors. Extend the existing application → HTTP transport → dispatcher dependency-injection seam from the YT-158 families to the seven YT-159 families. Preserve wrapper metadata, validation, quota documentation, authorization selection, response normalizers, MCP schemas and metadata, safe error mapping, retries, and observability. Explicit fake executors, credentials, and controlled openers remain available only as test or local-development dependencies.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: FastAPI, Pydantic v2, Uvicorn, Python standard-library `urllib`/JSON/dataclasses, existing Layer 1 integration modules, pytest, and Ruff  
**Storage**: No feature-specific persistent storage; runtime settings and credentials are environment/secret-backed, and request/observability state is in memory  
**Testing**: `python3 -m pytest` for unit, contract, integration, and transport coverage; `python3 -m ruff check .` for lint validation  
**Documentation Style**: reStructuredText docstrings for every new or changed Python function; feature-local Markdown contract documentation  
**Target Platform**: Local macOS/Linux development and the existing hosted Linux MCP service  
**Project Type**: Python MCP web service with internal Layer 1 YouTube integrations and public Layer 2 tool descriptors  
**Performance Goals**: Preserve the shared live runtime's existing 10-second per-attempt timeout and three-attempt maximum; add no endpoint-specific persistence, concurrency, or retry policy  
**Constraints**: All 17 configured default operations must use the shared live executor; no configured-path fallback may return representative data; API keys, OAuth tokens, bearer headers, credential-bearing URLs, raw request bodies, and media must not appear in logs, errors, MCP results, documentation examples, or test evidence; existing MCP schemas, metadata, wrapper contracts, normalizers, and safe error categories remain compatible; every changed Python function requires a reStructuredText docstring  
**Scale/Scope**: Seven resource families and 17 existing operations: guide categories (1), localization (2), members (1), membership levels (1), playlist images (4), playlist items (4), and playlists (4); no new endpoint inventory or public MCP tools

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

- [layer1-catalog-membership-playlist-live-call-contract.md](contracts/layer1-catalog-membership-playlist-live-call-contract.md) records the configured default-execution boundary and guarantees stable public tool schemas, metadata, results, and error categories.
- Every implementation grouping below starts with failing tests, adds only runtime injection or a narrowly scoped safe credential-construction correction, then performs behavior-preserving cleanup. Final verification from `/Users/ctgunn/Projects/youtube-mcp-server` is `python3 -m pytest` followed by `python3 -m ruff check .`.
- Any changed Python builder, handler, helper, or dispatcher function must retain or gain a reStructuredText docstring with `:param:`, `:return:`, `:raises:` where applicable, and side-effect documentation. No docstring or test fixture may contain a real credential.
- The design reuses `ConfiguredYouTubeRuntime`, `IntegrationExecutor`, the existing concrete YouTube transport, response normalizers, error mapper, retry policy, and observability hooks. It adds no second client, endpoint-specific transport, storage, MCP route, or secret source.

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/159-catalog-playlist-live-calls/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── layer1-catalog-membership-playlist-live-call-contract.md
└── tasks.md                         # Created later by /speckit.tasks
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/
├── app.py                            # Existing runtime-settings composition root (reuse)
├── transport/http.py                 # Builds configured runtime and dispatcher (reuse)
├── tools/
│   ├── dispatcher.py                 # Extend runtime injection to all 17 descriptors
│   └── youtube_common/
│       ├── guide_categories.py
│       ├── localization.py
│       ├── members.py
│       ├── memberships_levels.py
│       ├── playlist_images.py
│       ├── playlist_items.py
│       └── playlists.py               # Existing handlers/descriptors and test seams
└── integrations/
    ├── runtime.py                     # YT-157 configured runtime (reuse)
    ├── executor.py                    # Shared executor, retry, and observability hooks (reuse)
    ├── youtube.py                     # Concrete request builder/transport/normalization (reuse)
    └── resources/
        ├── base.py
        ├── guide_categories.py
        ├── localization.py
        ├── members.py
        ├── memberships_levels.py
        ├── playlist_images.py
        ├── playlist_items.py
        └── playlists.py               # Existing metadata/validation compatibility boundary

/Users/ctgunn/Projects/youtube-mcp-server/tests/
├── unit/
│   ├── test_layer1_live_runtime.py
│   ├── test_youtube_transport.py
│   ├── test_youtube_{guide_categories,i18n_languages,i18n_regions,members,memberships_levels}.py
│   └── test_youtube_{playlist_images,playlist_items,playlists}.py
├── integration/
│   ├── test_layer1_live_runtime.py
│   ├── test_youtube_tool_registration.py
│   └── test_youtube_{guide_categories,i18n_languages,i18n_regions,members,memberships_levels,playlist_images,playlist_items,playlists}_registration.py
└── contract/
    ├── test_layer1_{localization,members,memberships_levels,playlist_images,playlist_items,playlists}_contract.py
    └── test_youtube_{guide_categories,members,memberships_levels,playlist_images,playlist_items,playlists}_contract.py
```

**Structure Decision**: Keep the existing single Python MCP service and YT-157 composition path. Make the minimal dispatcher wiring change needed to pass the same configured runtime executor and configured credentials to every in-scope descriptor. Preserve resource modules as the validation/metadata boundary and `youtube_common` modules as explicit test/local override seams; no new project, route, client, database, or endpoint-specific execution layer is introduced.

## Phase 0: Research and Open Questions

### Research Findings

- `create_app()` loads the existing secret-backed settings, `MCPHTTPTransport` builds `ConfiguredYouTubeRuntime`, and the transport passes it to `InMemoryToolDispatcher`. The configured runtime supplies the concrete shared executor, timeout, retry policy, and safe observability hooks; no application or transport change is expected.
- `InMemoryToolDispatcher._baseline_tool_definitions()` already forms conditional, API-key, and OAuth dependency groups. The affected 17 descriptor builders are currently called without those groups and therefore select their family-local representative defaults. The dispatcher is the single intended retrofit point.
- The correct dependency matrix is: API key for `guideCategories.list`, `i18nLanguages.list`, `i18nRegions.list`, and `playlistItems.list`; OAuth for `members.list`, `membershipsLevels.list`, all four playlist-image operations, the three playlist-item mutations, and the three playlist mutations; conditional credentials for `playlists.list`.
- Existing wrapper modules remain the metadata, validation, authorization, quota, and normalization boundary. The concrete shared transport remains responsible for request URLs, query credentials, bearer credentials, JSON payloads, media/multipart payloads, retry integration, error normalization, and safe observability.
- `playlistImages.insert` and `playlistImages.update` already declare their media and metadata inputs. Their multipart form must be built only by the common transport, not by a playlist-image handler or wrapper.
- Guide-category and localization handlers construct an API-key context during descriptor construction. When a configured API key is absent, they must be adjusted, if needed, to return an existing safe per-call configuration/authentication failure rather than failing dispatcher construction. This must remain compatible with explicit test/local dependencies.
- Controlled openers and distinctive responses provide deterministic proof that configured defaults select the live path without network calls, quota usage, or credentials in tests.

### Phase 0 Red-Green-Refactor

- **Red**: Add characterization tests that fail because configured dispatcher construction leaves all 17 operations on local representative defaults. Add a failing no-API-key configured-runtime case for guide categories and localization that currently would fail during construction rather than return a safe caller-facing failure.
- **Green**: Define the complete 17-operation dependency, authorization, request-form, and public-compatibility matrix in `research.md`, `data-model.md`, and the feature contract. Use the configured runtime's executor/settings pair as the only configured dependency source.
- **Refactor**: Reject any proposed per-resource HTTP client, credential lookup, response mapper, retry logic, or observability path. Keep all conclusions aligned with the existing YT-157 runtime contract.

## Phase 1: Design and Contracts

### Design Goals

- Use the existing configured runtime for every normal public descriptor in the seven in-scope families.
- Preserve the 17 existing Layer 1 metadata/request-validation contracts and Layer 2/MCP contracts.
- Retain API-key-only, OAuth-required, and selector-driven conditional authorization without fallback based merely on another available credential.
- Let the existing transport submit query-only, JSON, and multipart media requests; no descriptor or wrapper reimplements HTTP transport behavior.
- Preserve explicit test/local executor, opener, and credential injection only when a caller deliberately supplies it.
- Preserve safe normalized errors, response normalizers, retry selection, and secret-free integration observability.

### Design Artifacts

- [research.md](research.md)
- [data-model.md](data-model.md)
- [layer1-catalog-membership-playlist-live-call-contract.md](contracts/layer1-catalog-membership-playlist-live-call-contract.md)
- [quickstart.md](quickstart.md)

### Phase 1 Red-Green-Refactor

- **Red**: Confirm the artifacts expose no unresolved decisions and identify a failing test for each default-execution gap, public-contract preservation rule, and safe-failure path.
- **Green**: Produce the entity/request-state model, compatibility contract, and reproducible controlled-runtime verification instructions. Document each operation family and request form without changing public schemas.
- **Refactor**: Deduplicate material inherited from YT-157 by referencing its existing shared runtime responsibilities. Re-check that all artifacts remain limited to catalog, membership, and playlist live-call retrofits.

## Phase 2: Implementation Strategy

### Shared Configured-Descriptor Wiring

- **Red**: Add a parameterized dispatcher/registration test that constructs `ConfiguredYouTubeRuntime` with a controlled opener and fails unless all 17 descriptor builders receive its executor and the applicable configured credential availability. Assert a configured descriptor cannot select a `_default_*_executor` or placeholder credential.
- **Green**: In `tools/dispatcher.py`, pass the existing dependency groups to the 17 listed descriptor builders: API-key dependencies to guide-category, localization, and playlist-item list builders; OAuth dependencies to membership, membership-level, playlist-image, playlist-item mutation, and playlist mutation builders; and conditional dependencies to the playlists list builder. Address guide-category/localization missing-key construction only with a deferred safe credential helper if the tests demonstrate it is necessary.
- **Refactor**: Centralize repeated dispatcher dependency construction, keep explicit descriptor arguments intact for isolated tests/local development, audit all changed Python docstrings, and run focused dispatcher/registration checks.

### User Story 1 - Receive Live Catalog, Membership, and Playlist Results

- **Red**: Add 17 parameterized request-level cases that call the configured path with a controlled opener. Each case must fail if it returns a representative payload or does not build the expected live request for guide categories (1), localization (2), members (1), membership levels (1), playlist images (4), playlist items (4), and playlists (4).
- **Green**: Route each existing handler to the injected `IntegrationExecutor` and existing resource wrapper without changing handler result mappers, wrapper metadata, request validation, quota documentation, selector behavior, or response normalizers.
- **Refactor**: Consolidate controlled upstream success payloads and captured-request assertions. Retain only existing family-specific result mapping and avoid resource-specific execution helpers. Add or update reStructuredText docstrings on every changed Python function.

### User Story 2 - Apply the Correct Authorization and Request Form

- **Red**: For every operation, assert the method, path, query values, selected credential location, body, and upload form where applicable. Add controlled failures for missing API-key/OAuth credentials, upstream authorization rejection, malformed response, timeout, and retryable upstream failure; each must fail if it exposes a secret or returns a representative success.
- **Green**: Preserve API-key reads for guide categories, localization, and playlist-item listing; OAuth rules for membership and mutation/media flows; and selector-driven API-key versus OAuth access for `playlists.list`. Rely on the concrete transport for GET/query, JSON mutations, and playlist-image multipart media forms.
- **Refactor**: Keep credential selection and safe error mapping in current runtime/transport/tool conventions. Remove temporary test-only branches and document changed helper inputs, results, raised errors, and side effects in reStructuredText docstrings.

### User Story 3 - Use Live Wrappers Through Public Tools

- **Red**: Add seven configured public-tool flow tests—one each for guide categories, localization, members, membership levels, playlist images, playlist items, and playlists—that fail unless the controlled opener sees a live request through application/transport/dispatcher composition. Include a normalized upstream-failure flow to prove no bypass or sample fallback.
- **Green**: Keep existing descriptor registration and MCP dispatch behavior while supplying the shared runtime to each selected tool. Use controlled upstream payloads distinct from representative defaults and assert the existing public result/error shape.
- **Refactor**: Reuse a single controlled runtime fixture and request recorder where possible; preserve family-specific public error classes and schema metadata. Run focused integration and contract suites after cleanup.

### Regression Strategy

- Run targeted runtime and transport checks: `python3 -m pytest tests/unit/test_layer1_live_runtime.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_live_runtime.py tests/integration/test_youtube_tool_registration.py`.
- Run affected unit and registration suites: `python3 -m pytest tests/unit/test_youtube_guide_categories.py tests/unit/test_youtube_i18n_languages.py tests/unit/test_youtube_i18n_regions.py tests/unit/test_youtube_members.py tests/unit/test_youtube_memberships_levels.py tests/unit/test_youtube_playlist_images.py tests/unit/test_youtube_playlist_items.py tests/unit/test_youtube_playlists.py tests/integration/test_youtube_guide_categories_registration.py tests/integration/test_youtube_i18n_languages_registration.py tests/integration/test_youtube_i18n_regions_registration.py tests/integration/test_youtube_members_registration.py tests/integration/test_youtube_memberships_levels_registration.py tests/integration/test_youtube_playlist_images_registration.py tests/integration/test_youtube_playlist_items_registration.py tests/integration/test_youtube_playlists_registration.py`.
- Run affected Layer 1 and public contract suites: `python3 -m pytest tests/contract/test_layer1_localization_contract.py tests/contract/test_layer1_members_contract.py tests/contract/test_layer1_memberships_levels_contract.py tests/contract/test_layer1_playlist_images_contract.py tests/contract/test_layer1_playlist_items_contract.py tests/contract/test_layer1_playlists_contract.py tests/contract/test_youtube_guide_categories_contract.py tests/contract/test_youtube_i18n_languages_contract.py tests/contract/test_youtube_i18n_regions_contract.py tests/contract/test_youtube_members_contract.py tests/contract/test_youtube_memberships_levels_contract.py tests/contract/test_youtube_playlist_images_contract.py tests/contract/test_youtube_playlist_items_contract.py tests/contract/test_youtube_playlists_contract.py`.
- Before completion, run `python3 -m pytest` and then `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`. Any full-suite failure must be fixed before the feature is complete.

### Rollback and Mitigation

- Keep all existing explicit executor, opener, wrapper, and credential injection parameters so unit and local-development callers remain deterministic.
- Confine the change to descriptor dependency selection plus any narrowly necessary deferred safe credential construction. If a rollout needs reversal, revert that configured injection change while preserving endpoint metadata, public schemas, validation, normalizers, and error categories.
- Never roll back to a representative successful response on a configured live-path failure; return the existing safe configuration, authorization, or upstream failure instead.
- Continue to redact API keys, OAuth tokens, bearer headers, credential-bearing query strings, raw request bodies, raw media, stack traces, and raw upstream failure bodies from diagnostics, results, and review evidence.

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
- The implementation strategy starts every shared and user-story grouping with failing tests, limits Green work to dispatcher injection or a safe deferred credential helper, and ends with focused and full-suite cleanup verification.
- The existing shared runtime, executor, transport, normalizers, retry policy, and observability hooks remain the only execution architecture; this is the simplest design that satisfies the live-call gate.
- Docstring work, safe diagnostics, credential redaction, and rollback behavior are explicit for every changed function and all proof paths.

## Complexity Tracking

No constitution violations or added architectural complexity are required for this plan.
