# MCP Admission and Result-Reuse Contract

## Scope and Compatibility

This contract applies only to public hosted `tools/call` invocations. It does not add a public tool, change a tool’s input schema, or change a successful tool result’s `content` or `structuredContent` shape. Existing initialization, discovery, health, readiness, security, session, and error behavior remains intact unless explicitly stated below.

## Admission Order

1. Evaluate existing hosted path, method, browser, authentication, protocol, and session rules.
2. Confirm the request is a valid `tools/call` invocation.
3. Resolve the safe caller class and evaluate admission.
4. If accepted, evaluate cache eligibility and invoke the existing dispatcher only when a fresh result is required.
5. Emit bounded operational observations without input, caller, credential, or result content.

Requests that fail before step 2, and `/health`, `/ready`, `initialize`, and `tools/list`, do not consume an allowance.

## Rate-limited Outcome

When the applicable allowance is exhausted, the response remains a valid MCP JSON-RPC error delivered through the same Streamable HTTP negotiation path as other tool-call errors. It contains the following additive safe data:

```json
{
  "category": "rate_limited",
  "retryable": true,
  "retryAfterSeconds": 12
}
```

- `retryAfterSeconds` is a positive bounded integer calculated from the active rolling window.
- The hosted response includes `Retry-After` with the same whole-second value.
- No tool handler, dispatcher execution, or upstream operation occurs for this response.
- The error contains no raw token, caller identity, limiter key, allowance count, request argument, or backend detail.
- Existing Streamable HTTP success/error framing is retained; the contract does not rely on a client parsing an HTTP-only 429 response.

## Cache-Status Header

For valid hosted `tools/call` responses, the service adds the additive `MCP-Cache-Status` response header:

| Value | Meaning |
| --- | --- |
| `hit` | A matching fresh, eligible public result was reused. |
| `miss` | The request was eligible but required fresh dispatcher/upstream evaluation. |
| `bypass` | The request was ineligible, rejected, or could not safely use the result cache. |

Browser response-header exposure is extended only as needed for this new safe header. The header never reveals why a request was ineligible, cache keys, stored values, identity information, or backend state.

## Reuse Eligibility and Isolation

Initially eligible result variants are limited to the following complete successful public reads:

| Tool or variant | Maximum freshness | Additional condition |
| --- | ---: | --- |
| `fetch` | 300 seconds | Static documented retrieval corpus only. |
| `i18nLanguages_list`, `i18nRegions_list`, `guideCategories_list`, `videoCategories_list`, `videoAbuseReportReasons_list` | 300 seconds | API-key-only public reference lookup. |
| `playlistItems_list` | 60 seconds | API-key-only public read. |
| `commentThreads_list` | 30 seconds | `moderationStatus` is absent. |

All mutations, uploads, downloads, ratings, moderation actions, errors, partial results, OAuth-required calls, mixed/conditional calls, composed tools, `search`, and other baseline tools are ineligible unless this contract is intentionally revised.

The internal identity of an entry includes policy version, catalog/configuration revision, normalized tool name, and canonical validated non-secret public arguments. An entry is never reused across authorization capabilities or any input context that can alter returned data. The service never stores stale content after expiry or returns stale content if a refresh fails.

## Invalidation

Before reporting a successful mutation, the service invalidates explicitly related eligible entries. The initial mapping invalidates `playlistItems_list` entries related to playlist-item mutations and `commentThreads_list` entries related to comment-thread/comment mutations. A mutation with no eligible relation records a safe no-op invalidation reason. A failed mutation does not invalidate existing entries.

## Contract Validation

Contract tests must prove protocol-native rate-limited shape, matching `Retry-After` data/header, no rejected dispatch, cache-header values, preserved successful content shapes, zero credential/identity leakage, cache isolation, expiry, and mutation invalidation ordering.
