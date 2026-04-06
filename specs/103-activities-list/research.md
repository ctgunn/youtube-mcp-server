# Research: YT-103 Layer 1 Endpoint `activities.list`

## Decision: Model `activities.list` as a mixed or conditional auth wrapper

**Rationale**: The YT-103 spec requires the wrapper contract to distinguish public channel-based retrieval from authorized-user activity views. The existing Layer 1 foundation already supports conditional auth metadata through `AuthMode.CONDITIONAL`, `auth_condition_note`, and runtime `conditional_reason`, so the smallest extension is to treat `activities.list` as one endpoint whose access mode depends on the selected filter path.

**Alternatives considered**:

- Declare `activities.list` as `api_key` only. Rejected because that would hide the authorized-user access paths the spec explicitly calls out.
- Declare `activities.list` as `oauth_required` only. Rejected because that would overstate the auth requirement for public channel activity retrieval and make later reuse unnecessarily restrictive.
- Split the endpoint into two independent wrappers. Rejected because this feature is about one endpoint-specific Layer 1 wrapper, and the current repo abstractions already support conditional auth on a single wrapper contract.

## Decision: Support one channel-oriented public path and one authorized-user path in the initial wrapper contract

**Rationale**: The spec needs maintainers to make the main reuse decision quickly: whether they want public channel activity or an authorized-user activity view. The initial contract therefore documents `channelId` as the supported public selector and `mine` plus `home` as the supported authorized-user selectors without trying to exhaustively surface every possible upstream parameter in this slice.

**Alternatives considered**:

- Enumerate every upstream request parameter in the initial contract. Rejected because it would bloat the first endpoint-specific slice and dilute the main auth/filter boundary the spec is trying to make clear.
- Limit support to public-channel retrieval only. Rejected because the feature specifically requires supported auth behavior to be documented, which would be incomplete without the authorized-user path.
- Limit support to authorized-user retrieval only. Rejected because that would weaken later Layer 2 and Layer 3 reuse for public research flows.

## Decision: Treat filter selection as mutually exclusive and reject unsupported combinations before execution

**Rationale**: The current `EndpointRequestShape` already rejects unexpected fields, but YT-103 needs stronger endpoint-specific semantics so callers cannot accidentally combine incompatible activity filters and assume the wrapper supports them. Early rejection keeps the contract deterministic and easy to review.

**Alternatives considered**:

- Pass all combinations through to upstream transport and rely on upstream errors. Rejected because later layers would not know which combinations are intentionally supported by the internal contract.
- Accept multiple filter paths and silently prioritize one. Rejected because that would hide user intent and create unstable downstream behavior.

## Decision: Represent empty valid activity responses as successful outcomes, not wrapper failures

**Rationale**: The spec explicitly distinguishes "no recent activity" from execution failure. The shared executor already separates success from normalized upstream error paths, so the wrapper contract should keep empty but valid collections on the success path.

**Alternatives considered**:

- Convert empty responses into a wrapper-specific error. Rejected because the absence of items is a legitimate business outcome, not an upstream failure.
- Add a separate wrapper mode just for empty-result handling. Rejected because the existing response path is already sufficient.

## Decision: Implement YT-103 by extending the current Layer 1 foundation modules and tests

**Rationale**: The repo already has the minimal seam needed for this slice in `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/contracts.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/auth.py`, `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/wrappers.py`, and the Layer 1 test files under `/Users/ctgunn/Projects/youtube-mcp-server/tests/`. The live upstream gap is closed by adding a concrete YouTube Data API transport under `/Users/ctgunn/Projects/youtube-mcp-server/src/mcp_server/integrations/youtube.py` that plugs into the existing executor contract rather than replacing it.

**Alternatives considered**:

- Introduce a dedicated `activities.py` integration module immediately. Rejected for planning because the current representative wrapper pattern may still be the smallest implementation path; the plan should not force a broader module split before Red tests confirm it is necessary.
- Add public tool or protocol changes in YT-103. Rejected because YT-203 is the separate Layer 2 exposure slice.

## Decision: Use a concrete `urllib`-backed transport to call the YouTube Data API from the existing executor seam

**Rationale**: The current Layer 1 executor is already designed around an injected transport callable. Adding a concrete transport that builds requests for `https://www.googleapis.com/youtube/v3/activities`, attaches API key or bearer-token auth, parses JSON responses, and normalizes HTTP failures closes the missing live-integration gap without changing the wrapper contract.

**Alternatives considered**:

- Keep the transport abstract and defer the live HTTP implementation. Rejected because YT-103 is the slice that should actually wrap `GET /activities`.
- Introduce a third-party Google client library for this slice. Rejected because the project already leans on the Python standard library for core transport and the executor seam only needs a small concrete HTTP implementation.

## Decision: Use two feature-local contract artifacts to guide later reuse

**Rationale**: YT-103 needs one contract focused on the wrapper identity and review surface, and a second contract focused on auth and filter interpretation. Separating those concerns keeps downstream YT-203 planning clear without mixing endpoint identity, auth semantics, and later public tool design into one overloaded document.

**Alternatives considered**:

- Keep all design guidance only in the implementation plan. Rejected because later tasking and reuse need stable contract artifacts.
- Keep all design guidance in one contract file. Rejected because auth/filter semantics are important enough for this endpoint to deserve a dedicated reusable artifact.
