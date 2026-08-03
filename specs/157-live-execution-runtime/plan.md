# Implementation Plan: YT-157 Layer 1 Live YouTube Data API Execution Runtime

**Branch**: `157-live-execution-runtime` | **Date**: 2026-07-31 | **Spec**: [/Users/ctgunn/Projects/youtube-mcp-server/specs/157-live-execution-runtime/spec.md](/Users/ctgunn/Projects/youtube-mcp-server/specs/157-live-execution-runtime/spec.md)
**Input**: Feature specification from `/Users/ctgunn/Projects/youtube-mcp-server/specs/157-live-execution-runtime/spec.md`

## Summary

Replace the implicit representative default for configured Layer 1 execution with one runtime-configured, authenticated YouTube Data API path. Reuse the existing shared request executor, concrete YouTube transport, wrapper metadata, request validation, response normalizers, retry policy, observability hooks, and safe error mapping. Add a small configuration and composition seam that injects the live executor and real credential availability into public descriptor construction, while retaining controlled executors only when an explicit test or local-development caller supplies them. This slice establishes the reusable cutover mechanism and proves one configured public-tool path; YT-158 through YT-160 perform the resource-family-wide default-executor replacements.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: FastAPI, Pydantic v2, Uvicorn, Python standard-library `urllib`/JSON/dataclasses, existing Layer 1 integration modules, pytest, and Ruff  
**Storage**: No feature-specific persistent storage; runtime configuration and credentials are environment/secret-backed and request state remains in memory  
**Testing**: `python3 -m pytest` for unit, contract, integration, and transport coverage; `python3 -m ruff check .` for lint validation  
**Documentation Style**: reStructuredText docstrings for every new or changed Python function; feature-local Markdown contracts for runtime configuration and live-execution behavior  
**Target Platform**: Local macOS/Linux development and the existing hosted Linux MCP service  
**Project Type**: Python MCP web service with internal Layer 1 YouTube integration and public Layer 2 tool descriptors  
**Performance Goals**: Preserve the existing live transport default timeout of 10 seconds and default maximum of three attempts; do not add per-endpoint latency, persistence, or concurrency behavior in this slice  
**Constraints**: The configured default must make real authenticated upstream requests; no configured-path fallback to static data; API keys, OAuth tokens, authorization headers, request URLs containing secrets, raw bodies, and media must never appear in logs, errors, results, documentation examples, or test evidence; existing public schemas, metadata, result shapes, and safe error categories remain compatible; every changed Python function must have a reStructuredText docstring  
**Scale/Scope**: One shared runtime configuration and composition mechanism for the completed Layer 1 endpoint inventory, one configured public-tool proof path, existing transport/request-form coverage, and no resource-family-by-resource-family executor migration (reserved for YT-158 through YT-160)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

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

- The plan records the new configuration and execution-selection boundary in feature-local contracts while preserving every existing MCP tool schema, metadata field, result shape, and safe error category.
- Each phase and user story begins with focused failing tests, adds only the smallest shared wiring needed to pass them, then removes duplication and runs regression checks. Final validation is `python3 -m pytest` and `python3 -m ruff check .` from `/Users/ctgunn/Projects/youtube-mcp-server`.
- New or changed configuration loaders, runtime factories, dispatcher composition helpers, and transport helpers must use reStructuredText docstrings with `:param:`, `:return:`, `:raises:` when applicable, and side-effect documentation. Docstrings and tests must use placeholders only, never credential values.
- The design centralizes live selection and secret handling rather than reproducing it in endpoint modules. Existing observability events, retry selection, error normalization, and redaction mechanisms remain the single path for live calls.

## Project Structure

### Documentation (this feature)

```text
/Users/ctgunn/Projects/youtube-mcp-server/specs/157-live-execution-runtime/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── layer1-live-execution-runtime-contract.md
│   └── layer1-runtime-configuration-contract.md
└── tasks.md                       # Created later by /speckit.tasks
```

### Source Code (repository root)

```text
/Users/ctgunn/Projects/youtube-mcp-server/src/
└── mcp_server/
    ├── app.py
    ├── config.py
    ├── observability.py
    ├── transport/
    │   └── http.py
    ├── tools/
    │   ├── dispatcher.py
    │   └── youtube_common/        # Existing explicit test/local executor seams
    └── integrations/
        ├── auth.py
        ├── errors.py
        ├── executor.py
        ├── retry.py
        ├── youtube.py             # Existing concrete live request transport
        └── resources/
            ├── base.py
            └── normalizers.py

/Users/ctgunn/Projects/youtube-mcp-server/tests/
├── unit/
│   ├── test_runtime_config_validation.py
│   ├── test_layer1_foundation.py
│   └── test_youtube_transport.py
├── integration/
│   ├── test_layer1_foundation.py
│   └── test_youtube_*_registration.py
└── contract/
    ├── test_layer1_consumer_contract.py
    └── test_layer1_resource_modules_contract.py
```

**Structure Decision**: Keep the existing single Python service. Add only a shared runtime-settings/factory and dependency-injection seam near the configuration and integration boundaries, then pass that dependency through the existing application/transport/dispatcher construction path. Do not add a new service, database, public MCP route, or per-resource live-executor implementation.

## Phase 0: Research and Open Questions

### Research Findings

- The concrete live transport already exists in `mcp_server.integrations.youtube`: it builds requests from endpoint metadata and execution context, supports query-only, JSON-body, raw-media, and multipart requests, attaches API-key or OAuth credentials, normalizes upstream responses and failures, and builds a shared executor with three attempts by default.
- `RepresentativeEndpointWrapper.call` already validates its request shape and delegates to `IntegrationExecutor`; the executor already owns hooks, retry selection, and exception normalization. These are preservation boundaries, not work to reimplement.
- Public descriptor builders still create local representative executors and placeholder credentials when called with no dependencies. Dispatcher creation currently supplies neither runtime settings nor a live executor, so normal configured registration does not reach the live transport.
- Current hosted configuration recognizes `YOUTUBE_API_KEY` but does not provide a named OAuth runtime credential. The runtime needs one explicit operator-supplied OAuth credential setting and deterministic mode selection for mixed/conditional endpoints.
- Existing retry policy decides whether to retry but does not sleep or add jitter. This feature preserves that established behavior; it does not add a new backoff scheduler.

### Phase 0 Red-Green-Refactor

- **Red**: Add tests that demonstrate the present defect: configured dispatcher construction selects a representative executor or placeholder credential instead of the concrete live executor; missing required configuration can otherwise reach representative data; and the selected runtime cannot be audited without exposing a secret.
- **Green**: Resolve the findings in `research.md` by defining a runtime-settings value, credential-selection rules, live-executor factory, dispatcher injection boundary, safe error/redaction behavior, and the explicit test/local override rule.
- **Refactor**: Keep research and later code limited to the shared seam. Remove any proposal to copy request, retry, observability, normalization, or secret handling into individual endpoint modules.

## Phase 1: Design and Contracts

### Design Goals

- Create one validated Layer 1 runtime configuration that can supply an API key, an OAuth access token, or both without displaying their values.
- Use the existing endpoint metadata and selected auth context to choose the appropriate configured credential. Conditional operations follow their wrapper-selected mode; no heuristic fallback switches a request from OAuth to API key or vice versa.
- Build the existing concrete live executor with the existing retry and observability hooks, then inject it and the configured credentials through application, transport, and dispatcher construction.
- Preserve explicit executor and credential injection for controlled tests and deliberate local development. Omitted dependencies in a configured runtime must not select representative defaults.
- Preserve existing Layer 1 validation, response normalizers, public tool names/schemas/metadata, tool-result shapes, and normalized client-safe error behavior.
- Limit YT-157 to the reusable shared runtime and a configured public-tool proof. The individual resource-family default-executor substitutions remain owned by YT-158, YT-159, and YT-160.

### Design Artifacts

- `/Users/ctgunn/Projects/youtube-mcp-server/specs/157-live-execution-runtime/data-model.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/157-live-execution-runtime/contracts/layer1-runtime-configuration-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/157-live-execution-runtime/contracts/layer1-live-execution-runtime-contract.md`
- `/Users/ctgunn/Projects/youtube-mcp-server/specs/157-live-execution-runtime/quickstart.md`

### Phase 1 Red-Green-Refactor

- **Red**: Identify missing design commitments for OAuth configuration, conditional-auth selection, dispatcher injection, no-fallback behavior, safe error visibility, and rollback. Confirm that these decisions are testable without a real credential or external request.
- **Green**: Produce the data model, configuration contract, execution contract, and quickstart with complete request, credential, error, observability, and test boundaries.
- **Refactor**: Remove duplicated descriptions across artifacts, preserve the strict distinction between live configuration and explicit test/local injection, and re-check that later resource-family cutovers are not pulled into this slice.

## Phase 2: Implementation Strategy

### Shared Runtime Foundation

- **Red**: Add failing unit tests for loading/sanitizing runtime configuration, selecting API-key/OAuth credential contexts, rejecting missing or unusable credentials, and building a configured live executor rather than a representative executor. Add a test that records a representative credential value and asserts it is absent from configuration failures, execution events, and tool-safe details.
- **Green**: Add the minimum runtime-settings and factory code necessary to validate configuration, build the existing `build_youtube_data_api_executor`, attach existing observability hooks, and expose a safe dependency bundle to the dispatcher path. Keep request construction, response normalization, retry selection, and error category logic in their current shared modules.
- **Refactor**: Consolidate credential lookup and safe validation in one place, remove placeholder-default paths from the configured construction flow only, audit reStructuredText docstrings on every modified Python function, then run focused configuration, executor, and transport tests.

### User Story 1 - Invoke Live YouTube Data

- **Red**: Add an integration test that constructs the normal configured application/transport/dispatcher path with controlled configuration and a controlled request opener, invokes one public-tool flow, and fails if a local representative transport or placeholder credential is used.
- **Green**: Thread the shared runtime dependency through the existing application, HTTP transport, and dispatcher construction path so the verified configured descriptor uses the concrete live executor and receives the selected configured credential. Preserve descriptor schemas and existing explicit dependency overrides.
- **Refactor**: Remove duplicate composition code, keep the route and MCP protocol behavior unchanged, document every changed composition helper with a reStructuredText docstring, and run focused dispatcher/registration and Layer 1 integration tests.

### User Story 2 - Receive Safe Failure Instead of Sample Data

- **Red**: Add tests for absent API-key configuration, absent OAuth configuration, invalid selected mode, upstream authorization failure, malformed upstream payload, timeout, and retryable failure. Each test must fail if it returns a representative success or includes the configured credential in errors, results, request logging, or observability output.
- **Green**: Map missing configuration and unavailable credentials to the established safe configuration/authorization tool failures. Route upstream failures through the existing normalizer, retry policy, observability hooks, and caller-detail sanitizer; do not catch them and substitute sample data.
- **Refactor**: Share any safe-error conversion needed at the runtime boundary, leave endpoint-specific public categories unchanged, remove temporary test-only branches, and run focused redaction, error-mapping, retry, and MCP result tests.

### User Story 3 - Reuse Shared Execution Behavior

- **Red**: Add characterization tests proving wrappers still validate request shapes before execution, retain endpoint metadata, support query/JSON/media/multipart forms through the concrete transport, and retain response-normalizer selection and retry/observability behavior after live factory injection.
- **Green**: Reuse `RepresentativeEndpointWrapper`, `RequestExecution`, `IntegrationExecutor`, `RetryPolicy`, `build_observability_hooks`, and `build_youtube_data_api_executor`; add only the runtime factory and dependency injection needed to select them by default.
- **Refactor**: Delete any endpoint-specific implementation of credential handling, live transport construction, retry, logging, or error normalization introduced during the change. Keep controlled transports as explicit test/local dependencies and run focused transport, foundation, and contract suites.

### Regression Strategy

- Run the focused Red-Green suites: `python3 -m pytest tests/unit/test_runtime_config_validation.py tests/unit/test_layer1_foundation.py tests/unit/test_youtube_transport.py tests/integration/test_layer1_foundation.py tests/contract/test_layer1_consumer_contract.py tests/contract/test_layer1_resource_modules_contract.py`.
- Include at least one configured public-descriptor test through the normal app/transport/dispatcher composition path with a controlled opener; it must prove selection of the live runtime without calling the external service.
- Preserve and run resource-specific registration tests as impacted by dependency injection: `python3 -m pytest tests/integration/test_youtube_*_registration.py`.
- Before completion, run `python3 -m pytest` and then `python3 -m ruff check .`. Any full-suite failure must be fixed before the feature is complete.

### Rollback and Mitigation

- Keep the existing explicit executor, opener, and credential injection seams available so test and local-development behavior remains deterministic.
- Isolate the runtime factory and dependency propagation behind existing construction boundaries. If a deployment issue occurs, revert the configured injection path without changing endpoint metadata, wrapper validation, public schemas, or response normalizers.
- Never use a representative result as a fallback for a failed configured request. Rollback means a clear safe configuration/authorization failure, not synthetic data.
- Treat API keys and OAuth tokens as secrets: only their setting names and auth mode may appear in diagnostics; redact query keys, bearer values, raw request bodies, raw media, and authorization headers.

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

- The two feature-local contracts define the configuration, credential selection, live-default, injection, no-fallback, compatibility, observability, and safe-failure expectations for all downstream callers.
- The design uses existing shared executor and transport primitives rather than adding a second execution architecture or per-resource copies.
- Every implementation grouping has explicit Red, Green, and Refactor steps; the final full-suite and lint commands are named in the regression strategy.
- Docstring work is explicit for every changed Python function, including runtime/configuration, injection, and test-support functions.
- The design keeps credential material outside tool defaults and safe diagnostic output, and retains existing request lifecycle instrumentation and retry/error semantics.

## Complexity Tracking

No constitution violations or added architectural complexity are required for this plan.
