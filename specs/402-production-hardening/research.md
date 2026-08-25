# Phase 0 Research: Production Hardening

## Decision 1: Use separate shared policy stores for hosted admission, result reuse, and alert state

**Decision**: Add small policy-specific stores with in-memory local/test implementations and Redis-compatible hosted implementations. Keep their namespaces separate from existing stream/session records. Rate-limit admission uses an atomic rolling-window operation; result entries expire at their policy TTL; alert state retains only bounded window aggregates and incident state.

**Rationale**: Cloud Run may route successive requests to different instances. Process-local state would allow limits to be bypassed, cache entries to be inconsistent, and alert recovery to be lost. The repository already deploys a Redis-compatible shared dependency for durable sessions, but its session abstraction is JSON read/write and is not safe for atomic admission counting or unrelated data lifecycles.

**Alternatives considered**:

- Reuse the existing session store directly: rejected because it lacks atomic rate-limit semantics and couples retention/keys to session continuity.
- Keep all policy state in process memory: rejected for hosted multi-instance correctness; retained only for local development and deterministic unit tests.
- Add a separate database or service: rejected because the existing Redis-compatible dependency meets the short-lived shared-state need without a new platform dependency.

## Decision 2: Limit only valid public `tools/call` requests and resolve callers from trusted authentication context

**Decision**: Enforce admission after hosted security, protocol validation, and session checks confirm a valid `tools/call`, but before dispatcher and upstream execution. Use an explicitly trusted gateway principal when the deployment guarantees it is stripped/injected by that gateway; otherwise derive an internal non-reversible digest from a validated bearer credential. Requests without either use the anonymous bucket. The default limits are 60 identified and 10 anonymous calls per rolling 60 seconds.

**Rationale**: This protects shared capacity without penalizing platform probes, invalid requests, authentication failures, initialization, or tool discovery. The current bearer credential can be a shared credential; it therefore creates one authenticated allowance unless a trusted gateway or distinct validated credential provides a finer caller identity. A user-controlled request header cannot be trusted as an identity source.

**Alternatives considered**:

- Use the raw bearer token or a client-supplied identifier as the limiter key: rejected because secrets must not be retained and public callers can forge headers.
- Rate-limit every `/mcp` request: rejected because protocol/session setup and malformed/denied requests are not public tool consumption and would harm normal recovery.
- Add HTTP-only 429 responses: rejected because Streamable HTTP MCP callers require a protocol-native JSON-RPC error; retain the current response mechanism and provide additive safe error details and a `Retry-After` header.

## Decision 3: Begin with a conservative, explicit public-result cache allowlist

**Decision**: Cache only complete successful results from an explicit public-safe allowlist: static `fetch` for 300 seconds; API-key-only public reference lookups for no more than 300 seconds; `playlistItems_list` for 60 seconds; and `commentThreads_list` for 30 seconds only when `moderationStatus` is absent. No entry may outlive 300 seconds. All OAuth, mixed/conditional, mutation, upload, download, rating, moderation, composed, `search`, and remaining baseline operations start ineligible.

**Rationale**: Current tool metadata has authentication and response conventions but no complete cache-safety classification. Many names that appear read-only can accept owner, moderation, partner, or private selectors. An allowlist makes the first production policy safe and reviewable; later tools require an explicit argument-level classifier before becoming eligible.

**Alternatives considered**:

- Cache all read-like or `*_list` tools: rejected because mixed/OAuth selectors could disclose caller-sensitive data.
- Cache per caller: rejected because it does not make sensitive data safe and depends on a stronger general identity model.
- Return expired entries if refresh fails: rejected by the feature specification; callers must receive the current normalized failure.

## Decision 4: Isolate cache entries by normalized public behavior and invalidate only mapped relations

**Decision**: Form a cache identity from policy version, catalog/configuration revision, normalized tool name, and canonical validated non-secret public arguments. Never include credentials, sessions, request IDs, raw caller identity, raw payloads, or result contents. Invalidate mapped read entries before reporting a successful mutation; rotate policy/catalog namespace for broad policy changes instead of scanning/deleting broadly.

**Rationale**: The identity captures values that can change a public result while avoiding secret retention and unbounded observability. Explicit invalidation mapping gives mutations a safe relationship to a small initial cache footprint without inventing broad destructive invalidation behavior.

**Alternatives considered**:

- Use raw JSON input or request headers as a key: rejected because ordering is unstable and it risks storing secrets or identity data.
- Invalidate every entry on every mutation: rejected as unnecessarily disruptive and difficult to coordinate across instances.
- Never invalidate until TTL: rejected because it violates the successful-mutation requirement for related entries.

## Decision 5: Use bounded application-level alert state and Terraform-managed monitoring policies

**Decision**: Emit sanitized application events classified only by endpoint, finite tool class (`simple_cached` or `transcript_heavy`), and finite outcome (`success`, `service_failure`, `upstream_failure`, `capacity_rejection`, or `client_failure`). Maintain shared alert state for 10-minute windows and hold an incident active until 15 consecutive minutes of normal eligible observations. Terraform creates log-based metrics and monitoring policies from the bounded incident state, with operator-managed verified notification channel identifiers.

**Rationale**: Cloud Run HTTP metrics cannot accurately represent MCP tool failures because MCP failures can be returned in successful streams or non-5xx JSON-RPC responses. Platform monitoring deduplicates open incidents and provides delivery/audit evidence, while the application’s bounded state supplies the specified delayed recovery behavior that an immediate metric-threshold clear would not provide.

**Alternatives considered**:

- Use Cloud Run HTTP errors/latency alone: rejected because it cannot distinguish the relevant MCP failures or tool latency classes.
- Send webhooks directly from application code: rejected because it duplicates notification secrets, retry, and delivery management.
- Let monitoring close the incident as soon as the metric normalizes: rejected because the feature requires 15 consecutive normal minutes before recovery.

## Decision 6: Keep production monitoring destinations outside application configuration

**Decision**: Treat alert enablement, safe thresholds, and classes as versioned operational configuration; pass pre-verified monitoring notification-channel resource identifiers through Terraform. Do not create or store webhook/chat/email secret values in the application or repository. Monitor no-data behavior without treating missing data as a recovery signal.

**Rationale**: Alert destinations have independent ownership and verification requirements. Keeping them in the monitoring platform makes open/close delivery auditable and avoids secret exposure. No data is not evidence of a healthy service and must not close an active incident.

**Alternatives considered**:

- Put notification endpoints in Cloud Run environment variables: rejected because it adds sensitive delivery configuration to the runtime and duplicates platform capabilities.
- Create notification channels from repository code: rejected because channel verification and secret labels are operator-managed.
- Treat absent samples as healthy: rejected because it creates false recovery signals during telemetry outages.
