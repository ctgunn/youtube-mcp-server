# Research: FND-017 Retrieval Tool Contract Completeness

## Decision 1: Express valid `fetch` request shapes in discovery metadata with explicit schema composition

Rationale:
- FND-017 is specifically about removing trial-and-error from `fetch` invocation.
- The current discovery schema lists `resourceId` and `uri`, but it does not machine-readably express that at least one is required and that both are only valid when they identify the same source.
- Explicit schema composition is the most direct way to publish valid request shapes to MCP clients through `tools/list` instead of relying on prose or runtime-only failures.

Alternatives considered:
- Keep the current flat property list and describe valid combinations only in tool documentation.
  - Rejected because it leaves the core invocation contract outside machine-readable discovery.
- Only require `resourceId` and treat `uri` as an undocumented convenience path.
  - Rejected because the current runtime behavior already supports both identifiers and the feature should describe real supported behavior, not narrow it silently.

## Decision 2: Keep `search` strict and fully self-describing, but avoid adding new retrieval behavior in this slice

Rationale:
- `search` already publishes its required `query` field and basic validation rules, so FND-017 should tighten completeness rather than redesign the tool.
- The current `search` contract already depends on a strict object schema with known optional controls; preserving that approach keeps the feature small and regression-safe.
- The feature goal is contract completeness, not new search capability.

Alternatives considered:
- Expand `search` with new optional filters or pagination semantics while touching the schema.
  - Rejected because that would broaden scope beyond contract completeness.
- Leave `search` untouched and focus only on `fetch`.
  - Rejected because FND-017 requires both retrieval tools to be constructible from discovery output alone.

## Decision 3: Treat discovery metadata and runtime validation as one contract that must be updated together

Rationale:
- The current code splits structural validation between dispatcher schema checks and tool-specific runtime checks.
- If the schema is tightened without corresponding runtime coverage, or vice versa, the exact mismatch FND-017 is meant to close will persist.
- A single contract source for allowed shapes reduces drift and keeps tests straightforward.

Alternatives considered:
- Let discovery schema stay looser than runtime checks and rely on tests to document the difference.
  - Rejected because clients would still encounter avoidable trial-and-error.
- Move all validation into runtime code and keep discovery metadata descriptive only.
  - Rejected because it fails the machine-readable contract requirement.

## Decision 4: Publish representative examples for every supported `fetch` identifier pattern and the primary invalid shapes

Rationale:
- Clients need proof that the machine-readable contract works in practice, especially for the supported `resourceId`-only, `uri`-only, and matching combined-identifier flows.
- Operators also need hosted evidence that the documented discovery contract maps to real requests.
- Examples close the gap between schema publication and release verification without expanding the runtime surface.

Alternatives considered:
- Only provide one success example and assume clients can generalize.
  - Rejected because the supported `fetch` shapes are the core ambiguity this feature is resolving.
- Only test invalid shapes in unit tests.
  - Rejected because contract completeness must hold at discovery, MCP, and hosted verification levels.

## Decision 5: Keep the implementation centered in the existing retrieval and dispatcher seams

Rationale:
- The current retrieval contract lives in `src/mcp_server/tools/retrieval.py` and is surfaced through `src/mcp_server/tools/dispatcher.py`.
- Hosted examples and contract checks already pass through `README.md`, `tests/contract/test_deep_research_tools_contract.py`, `tests/integration/test_mcp_request_flow.py`, and `tests/integration/test_hosted_http_routes.py`.
- Constraining the work to those seams keeps the change simple and avoids touching unrelated transport or security behavior.

Alternatives considered:
- Introduce a new retrieval-specific contract layer separate from the current tool registration flow.
  - Rejected because it would add unnecessary complexity for a narrow contract-completeness slice.
- Push retrieval-contract logic into hosted transport code.
  - Rejected because the concern is tool discovery and validation, not HTTP routing behavior.
