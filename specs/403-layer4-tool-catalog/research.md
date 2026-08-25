# Phase 0 Research: Layer 4 Default MCP Tool-Catalog Integration Coverage

## Decision 1: Discover and invoke through the existing public MCP routes

**Decision**: Build the suite around an in-process default MCP transport. Discover the catalog with a `tools/list` request and invoke each fixture with a `tools/call` request through that transport.

**Rationale**: The default dispatcher is the current authoritative registry, while the protocol route applies the same request validation, error mapping, and result serialization that MCP clients receive. Current local discovery returns 77 tools, but the suite will derive the count at run time rather than encode it.

**Alternatives considered**:

- Call the dispatcher directly: rejected because it bypasses the public MCP route and cannot prove route-level behavior.
- Maintain a fixed list of expected tool names: rejected because it duplicates the registry and would conceal catalog drift.

## Decision 2: Use one explicit deterministic fixture per public tool

**Decision**: Maintain a test-owned mapping keyed by public tool name. Each entry supplies object-shaped safe arguments and declares either a successful outcome or a documented safe MCP error category.

**Rationale**: The tool catalog contains nested, alternative, write, media, and read-only invocation shapes, so safe representative inputs require deliberate review. A single mapping permits an exact bidirectional comparison with discovered names and produces one readable test case per tool.

**Alternatives considered**:

- Generate arguments from discovery schemas: rejected because schemas cannot reliably select a safe value for alternative, mutation, or media inputs.
- Scatter fixture choices among unrelated tests: rejected because completeness and stale-fixture checks need one reviewable source.
- Assert full result snapshots: rejected because the requirement is for outcome and contract verification, not brittle data snapshots.

## Decision 3: Keep catalog verification deterministic and credential-free

**Decision**: Use the default local dispatcher without a configured YouTube runtime and install a controlled outbound-request guard for the suite. Live credentials and live YouTube calls remain exclusively in the separately opt-in smoke workflow.

**Rationale**: The default local descriptors already provide deterministic behavior and safe expected failures. A configured runtime intentionally applies credential/capability behavior, which belongs to OPS-404 rather than this catalog release gate.

**Alternatives considered**:

- Use real API credentials or a live endpoint: rejected because the feature must not require credentials, make outbound requests, or mutate external state.
- Treat every unavailable local result as a success: rejected because expected-error fixtures must prove the documented safe MCP error category.

## Decision 4: Validate response outcomes at the MCP boundary

**Decision**: Successful fixtures assert a JSON-RPC MCP result with non-error status, nonempty content, and structured content. Expected-error fixtures assert a JSON-RPC error envelope and its documented `error.data.category`, without any process-level exception escaping. When a successful structured result includes `endpoint` and discovery metadata includes `upstream.operationKey`, assert they are equal.

**Rationale**: These checks exactly cover the Layer 4 release-verification obligation while allowing tools without upstream metadata or endpoint result data to remain valid.

**Alternatives considered**:

- Require an endpoint identity from every tool: rejected because baseline, retrieval, and composed tools need not expose one.
- Only assert that a handler did not raise: rejected because it does not prove MCP result/error contract behavior.

## Decision 5: Expose a focused operator command and document its boundary

**Decision**: Add a `make test-tools` target that runs the catalog suite, add it to the declared Make targets, and document it beside `make test` in the README. The documentation explicitly distinguishes deterministic catalog verification from the credential-gated live smoke workflow.

**Rationale**: Maintainers need a stable, fast command for the release-verification layer while retaining the existing complete suite command and avoiding any implication that the focused check verifies real YouTube access.

**Alternatives considered**:

- Require a raw test-runner command only: rejected because the specification requires a focused project command.
- Run live verification as part of the target: rejected because it would add credential, availability, quota, and mutation risks that this feature forbids.

## Decision 6: Preserve documentation, diagnostics, and source-code standards

**Decision**: Give each parameterized case the public tool name as its test identifier, make missing/stale fixture failures list the affected names, and require complete reStructuredText docstrings on every new or modified Python function, including test helpers.

**Rationale**: Individually reported tool results make release failures actionable. Complete docstrings and secret-free diagnostics meet the repository's maintainability and security rules without adding logging infrastructure.

**Alternatives considered**:

- Use one loop inside one test: rejected because failures would not be individually reported.
- Add runtime logs or persistent reports: rejected because pytest reporting already supplies the necessary release evidence and the feature requires no runtime behavior.
