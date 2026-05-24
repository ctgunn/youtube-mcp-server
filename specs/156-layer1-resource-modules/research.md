# Research: YT-156 Layer 1 Resource-Family Module Reorganization

## Decision: Use Resource-Family Modules With Compatibility Facades

Resource-specific Layer 1 wrapper classes, builder functions, endpoint metadata declarations, and endpoint-specific validators will move into resource-family modules under the existing integration layer. Existing imports from `mcp_server.integrations`, `mcp_server.integrations.wrappers`, and `mcp_server.integrations.youtube` will remain valid through compatibility facades.

**Rationale**: The seed slice identifies broad-file concentration as the maintainability problem. Local inspection confirms that `wrappers.py` contains many wrapper classes and builder functions, while package-level imports currently re-export those builders. A resource-family package improves discoverability for future Layer 2 and Layer 3 authors without forcing downstream code or tests to migrate in this refactor.

**Alternatives considered**:

- Keep all code in the broad files and only add comments: rejected because it does not satisfy the resource-family discoverability requirement.
- Move everything and remove old imports immediately: rejected because the feature explicitly requires public import compatibility.
- Create one module per endpoint: rejected because it fragments shared family behavior and makes resource-family review harder.

## Decision: Keep Shared Foundations Centralized

Authentication, request execution, retry policy, observability hooks, contracts, upstream error normalization, and generic request construction remain in the shared integration modules. Resource-family modules depend on those foundations rather than duplicating them.

**Rationale**: The spec requires a behavior-preserving refactor. Duplicating shared foundations would create drift risk for credential attachment, error normalization, retry behavior, and logs. Keeping shared foundations centralized also supports rollback of individual resource-family moves.

**Alternatives considered**:

- Copy shared helpers into each resource-family module: rejected because it increases the chance of inconsistent behavior.
- Introduce a separate framework abstraction for resource modules: rejected as unnecessary for this organization-only slice.

## Decision: Replace Central Response Branching With Explicit Dispatch

Endpoint-specific response normalizers will be grouped by resource family and registered through an explicit operation-key-to-normalizer dispatch mechanism. Generic JSON parsing remains the fallback for operations that do not require specialized payload normalization. The dispatch design must account for the existing mix of normalizers that need only execution context, only parsed or raw payload, or both execution context and payload.

**Rationale**: Local inspection shows response normalization currently selected by a long `operation_key` conditional flow in `youtube.py`. An explicit dispatch table makes operation-to-normalizer mapping auditable while preserving each endpoint's current payload shape. The existing handler signatures vary across no-content acknowledgements, downloads, uploads, list payloads, and mutation responses, so a small adapter or consistent callable wrapper is safer than assuming one raw function signature fits every operation.

**Alternatives considered**:

- Keep the existing conditional chain: rejected because the seed explicitly calls for explicit dispatch rather than a single long central chain.
- Use dynamic name lookup by operation key: rejected because explicit registration is easier to audit and safer for compatibility tests.

## Decision: Characterize Before Moving Each Family

Implementation will start with characterization tests for resource-family access, compatibility imports, response-normalizer mapping, and representative behavior before each family is moved.

**Rationale**: The constitution requires Red-Green-Refactor and the feature depends on behavior preservation. Existing contract tests are already split by resource family, and broad unit/integration tests cover compatibility and shared execution paths. Characterization tests protect against accidental endpoint contract drift during moves.

**Alternatives considered**:

- Move all families first and rely only on final full-suite tests: rejected because failures would be harder to localize.
- Rewrite all tests before moving code: rejected because it increases scope beyond the minimum behavior-preserving refactor.

## Decision: Treat Feature Contracts as Internal Layer 1 Contracts

The contracts for this slice document internal Layer 1 compatibility and response-normalizer dispatch rather than public MCP tool behavior.

**Rationale**: YT-156 does not add or change a public MCP tool. However, the constitution requires contract-first planning, and later public Layer 2 and Layer 3 work depends on stable Layer 1 integration surfaces.

**Alternatives considered**:

- Skip contracts because the slice is internal: rejected because the constitution requires explicit contracts for interface boundaries.
- Define a public MCP contract: rejected because that would invent scope not present in the feature spec.

## Decision: Require reStructuredText Docstrings for All Changed Python Functions

Every new or changed Python function, method, registry helper, normalizer dispatch function, or compatibility facade helper will include a reStructuredText docstring.

**Rationale**: The project constitution and AGENTS instructions require reStructuredText docstrings for all new or changed Python functions. This is especially important for a refactor where docstrings help reviewers confirm purpose without implying behavior changes.

**Alternatives considered**:

- Keep docstrings only on public functions: rejected because the constitution requires every new or modified Python function.
- Defer docstrings to implementation cleanup: rejected because docstring work must be planned before tasking.

## Decision: Verification Uses Targeted Layer 1 Runs Before Full Repository Runs

Focused verification will use Layer 1 unit, transport, integration, and contract tests first, followed by full `python3 -m pytest` and `python3 -m ruff check .`.

**Rationale**: Resource-family moves are likely to touch many imports. Targeted tests provide fast feedback per family, while full-suite validation is constitutionally required after final changes.

**Alternatives considered**:

- Run only resource-family contract files: rejected because compatibility and transport behavior are also in unit and integration tests.
- Run only the full suite at the end: rejected because it weakens Red-Green-Refactor feedback.
