# Research: Layer 1 Live YouTube Data API Execution Runtime

## Decision 1: Reuse the existing concrete YouTube transport and shared executor

**Decision**: Build the configured runtime on `build_youtube_data_api_executor` and inject it through the existing Layer 1 and dispatcher construction boundaries. Do not introduce a second HTTP client, request model, response mapper, retry loop, or endpoint-specific transport.

**Rationale**: `src/mcp_server/integrations/youtube.py` already constructs authenticated YouTube requests from `EndpointMetadata` and `RequestExecution`, supports the required request forms, and invokes response normalization. `src/mcp_server/integrations/executor.py` already provides the shared retry and observability lifecycle. Reusing these paths protects established endpoint behavior and confines the change to default selection and configuration.

**Alternatives considered**:

- Reimplement live requests in each public tool: rejected because it duplicates shared concerns and contradicts the Layer 1 boundary.
- Replace the existing transport library: rejected because the standard-library transport is already tested and supports the required forms.
- Keep representative executors as the configured default: rejected because it violates the seed slice's live-data release gate.

## Decision 2: Define one explicit runtime credential configuration contract

**Decision**: Use `YOUTUBE_API_KEY` for API-key access and introduce `YOUTUBE_OAUTH_TOKEN` as the optional opaque OAuth access-token setting. The runtime configuration validates presence without echoing values. An operation's existing auth mode selects its credential: API-key operations require `YOUTUBE_API_KEY`, OAuth-required operations require `YOUTUBE_OAUTH_TOKEN`, and conditional operations use the mode selected by their existing wrapper/handler rules.

**Rationale**: The repository already uses `YOUTUBE_API_KEY` in hosted configuration. A separately named OAuth setting makes selection auditable and avoids the current hard-coded placeholder tokens. OAuth token issuance and refresh remain external operator concerns; this slice consumes an available token and safely reports its absence.

**Alternatives considered**:

- Reuse `MCP_AUTH_TOKEN` for YouTube OAuth: rejected because it authenticates access to the MCP server, not YouTube upstream access.
- Add automatic OAuth authorization-code or refresh-token flows: rejected because it expands the feature into identity management and persistent secret lifecycle work.
- Fall back from OAuth to API key for any operation: rejected because existing wrapper authorization rules define the permitted mode and API keys cannot authorize OAuth-only operations.

## Decision 3: Make live execution the configured default; retain controlled injection only explicitly

**Decision**: Normal application/HTTP transport/dispatcher composition must pass a configured live runtime to descriptor handlers. Explicit caller-supplied executors, openers, credentials, and representative transports remain valid for isolated tests and opt-in local development only. No configured path may construct a representative executor when a credential or runtime setting is missing.

**Rationale**: The current `youtube_common` modules use private representative executors and placeholder credentials if no dependency is supplied. Injecting one live runtime at the composition root removes that unsafe implicit default without forcing every endpoint module to own transport logic.

**Alternatives considered**:

- Delete all fake executors: rejected because deterministic unit and contract tests need controlled upstream behavior.
- Convert every resource module in this slice: rejected because YT-158 through YT-160 explicitly own the grouped resource-family cutovers.
- Return an empty successful collection when configuration is missing: rejected because it is indistinguishable from live data and violates the no-fallback requirement.

## Decision 4: Preserve existing request, retry, normalization, and observability behavior

**Decision**: Preserve the current request construction for query, JSON, raw-media, and multipart uploads; preserve `RetryPolicy` retry selection and the concrete executor's default three attempts; preserve response-normalizer dispatch and integration execution events. Do not add timed backoff, jitter, or new endpoint semantics in YT-157.

**Rationale**: Existing `test_youtube_transport.py` covers the request forms and controlled upstream normalization. `RetryPolicy` currently selects retries but does not implement delays, so claiming a new backoff behavior would create unrelated scope. `build_observability_hooks` already records only safe endpoint/auth/outcome information.

**Alternatives considered**:

- Add exponential backoff and jitter now: rejected because this would be a new retry policy and needs its own performance and operational design.
- Bypass normalizers for live results: rejected because public result compatibility depends on the existing normalizer registry.
- Log full request URLs for diagnosis: rejected because API-key query values would expose secrets.

## Decision 5: Prove the cutover with controlled live-path tests and one public-tool flow

**Decision**: Add focused unit tests for runtime configuration, credential selection, redaction, and factory selection; integration tests for wrapper-to-live-executor execution using a controlled opener; contract tests for stable public behavior; and one configured public descriptor flow that fails if it uses a representative executor. Finish with the full test suite and Ruff.

**Rationale**: Tests can prove the real transport is selected and observe its constructed request without sending an external request or requiring a production credential. This gives evidence for the shared runtime without prematurely applying YT-158 through YT-160's family-wide changes.

**Alternatives considered**:

- Use a real YouTube account in automated tests: rejected because it is non-deterministic, consumes quota, and introduces secret management into CI.
- Test only the transport module: rejected because it misses the configuration-to-dispatcher default-selection defect.
- Test only public descriptors: rejected because unit coverage is needed for configuration, credential selection, request forms, and redaction edge cases.

## Resolved Questions

There are no remaining `NEEDS CLARIFICATION` items. The feature boundary, configuration names, credential-selection behavior, injection policy, retry behavior, and verification strategy are defined above.
