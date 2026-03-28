# Research: OpenAI Retrieval Compatibility

## Decision 1: Treat the OpenAI retrieval contract as the authoritative external contract for FND-023

- **Decision**: Use the current OpenAI MCP guidance for ChatGPT Apps, deep research, and company knowledge as the authoritative external contract for `search` and `fetch`.
- **Rationale**: The current OpenAI guide says that, for ChatGPT deep research and company knowledge, an MCP server should implement two read-only tools, `search` and `fetch`, using the documented compatibility schema. It also describes the expected `search` return shape as a `results` array with `id`, `title`, and `url`, and the `fetch` input as a single string identifier that returns an object with `id`, `title`, `text`, `url`, and optional `metadata`. This is materially narrower than the current repo contract, so the plan needs to target the OpenAI shape explicitly rather than infer it from older internal behavior.
- **Alternatives considered**:
  - Keep the current repo-specific retrieval contract and document it as “close enough.” Rejected because it would not satisfy the current OpenAI-specific compatibility requirement.
  - Delay the feature until broader retrieval guidance stabilizes. Rejected because FND-023 exists specifically to close this gap now.

## Decision 2: Prefer direct alignment of `search` and `fetch` over a persistent parallel adapter layer

- **Decision**: Implement direct alignment of the existing `search` and `fetch` tools to the OpenAI-facing contract and reject undocumented legacy fetch shapes explicitly.
- **Rationale**: The repo currently exposes only one retrieval surface through the same MCP tool names. Prior retrieval plans and tests assume one discovery and invocation path, not dual retrieval pipelines. Direct alignment keeps the design simpler, reduces drift between discovery and runtime validation, and matches the constitution’s simplicity principle.
- **Alternatives considered**:
  - Maintain the current contract internally and always translate it through a permanent adapter. Rejected because it adds another rule system and makes contract drift more likely.
  - Expose separate OpenAI-specific tool names. Rejected because the current guidance and the feature spec both center on `search` and `fetch`.

## Decision 3: Preserve MCP-native wrapping while changing the retrieval payload shape

- **Decision**: Keep the existing MCP `content` array pattern and protected `/mcp` invocation path, but change the retrieval-specific JSON payload inside the text content and mirrored structured content to match the OpenAI-compatible contract.
- **Rationale**: Current repo behavior already returns MCP-native tool results with one text content item. OpenAI’s MCP guide also expects a single text content item containing JSON-encoded retrieval data. This means FND-023 is primarily a retrieval payload alignment feature, not a transport or protocol redesign.
- **Alternatives considered**:
  - Introduce a new HTTP endpoint or non-MCP wrapper for OpenAI retrieval. Rejected because it would violate the project’s MCP-first design.
  - Remove structured content entirely and return text only. Rejected because the repo’s prior MCP slices rely on structured content for internal consistency and testing, and the spec does not require removing it.

## Decision 4: Treat the current repo contract as a legacy shape that must either adapt explicitly or fail predictably

- **Decision**: Model the current `query` plus `pageSize`/`cursor` search shape and `resourceId`/`uri` fetch shape as legacy retrieval behavior for FND-023 planning purposes. If retained temporarily, it must be handled through an explicit compatibility boundary; otherwise it should fail with stable structured errors.
- **Rationale**: Current implementation and tests are still built around repo-specific fields that do not match the OpenAI guidance. The feature spec explicitly requires clear documentation of any intentional divergence from prior internal shapes, so silent coexistence is not acceptable.
- **Alternatives considered**:
  - Keep accepting both contracts without documentation. Rejected because it undermines discovery clarity and testability.
  - Remove old behavior with no migration note. Rejected because maintainers and operators need to understand what changed and why.

## Decision 5: Keep empty-search and unavailable-fetch behavior stable at the semantic level

- **Decision**: Preserve the semantic distinction already established by earlier retrieval slices: empty `search` results remain a successful non-error outcome, and unavailable `fetch` targets remain stable structured failures.
- **Rationale**: Earlier retrieval features and tests already encode these behaviors, and nothing in the current OpenAI guidance requires changing those semantics. Preserving them reduces regression risk while still allowing the payload shape to change.
- **Alternatives considered**:
  - Convert empty `search` into an error for OpenAI-targeted flows. Rejected because it reduces usability and is not implied by the guidance.
  - Collapse unavailable fetches into generic internal errors. Rejected because it weakens contract clarity and diagnostics.

## Decision 6: Implementation and testing should stay in the existing retrieval seams

- **Decision**: Limit implementation planning to the current retrieval/tool publication, MCP method/result shaping, hosted verification, and retrieval-focused test seams.
- **Rationale**: The repo already has clear seams in `src/mcp_server/tools/retrieval.py`, `src/mcp_server/tools/dispatcher.py`, `src/mcp_server/protocol/methods.py`, `tests/unit/test_retrieval_tools.py`, `tests/contract/test_deep_research_tools_contract.py`, and hosted verification/docs flows. FND-023 is a contract-alignment slice, not a new subsystem.
- **Alternatives considered**:
  - Create a new retrieval module or new verifier. Rejected because the current seams are sufficient.
  - Defer docs and hosted verification to a later slice. Rejected because the spec requires OpenAI-specific examples and end-to-end compatibility proof.

## Decision 7: Hosted verification must prove the OpenAI-specific flow, not just generic retrieval success

- **Decision**: Require hosted or hosted-like verification evidence for initialize, discovery, one valid OpenAI-compatible `search`, one valid OpenAI-compatible `fetch`, and at least one representative unsupported legacy-shape request.
- **Rationale**: Current hosted verification proves only the generic retrieval contract. FND-023’s acceptance criteria require OpenAI-specific examples and end-to-end proof of the intended retrieval flow.
- **Alternatives considered**:
  - Rely on unit or contract tests alone. Rejected because earlier foundation slices consistently require hosted verification for MCP-facing behavior.
  - Treat documentation examples as sufficient evidence. Rejected because the constitution requires integration and regression proof, not documentation alone.

## Sources

- OpenAI MCP guide: https://developers.openai.com/api/docs/mcp
  - Current guidance accessed on 2026-03-25.
  - Key sections: `search`/`fetch` compatibility shape for ChatGPT deep research and company knowledge.
