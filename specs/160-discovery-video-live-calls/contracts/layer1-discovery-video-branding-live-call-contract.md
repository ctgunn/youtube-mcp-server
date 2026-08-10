# Layer 1 Discovery, Video, and Branding Live-Call Contract

## Purpose

Define configured default execution for existing discovery, subscription, video, and branding resource families. This contract retrofits the public descriptors to the YT-157 shared live runtime without changing exposed MCP tool contracts or underlying Layer 1 wrapper contracts.

## In-Scope Operations

| Resource family | Operations | Access | Request form |
| --- | --- | --- | --- |
| Search | `search.list` | Selector-driven API key or OAuth | GET query |
| Subscriptions | `subscriptions.list`, `subscriptions.insert`, `subscriptions.delete` | Selector-driven list; OAuth mutations | GET/DELETE query; insert JSON |
| Thumbnails | `thumbnails.set` | OAuth | POST raw media |
| Video abuse-report reasons | `videoAbuseReportReasons.list` | API key | GET query |
| Video categories | `videoCategories.list` | API key | GET query |
| Videos | `videos.list`, `videos.insert`, `videos.update`, `videos.rate`, `videos.getRating`, `videos.reportAbuse`, `videos.delete` | Selector-driven list; OAuth mutations and ratings | GET/DELETE query; POST/PUT JSON or action; insert multipart metadata and media |
| Watermarks | `watermarks.set`, `watermarks.unset` | OAuth | POST raw media; POST query |

## Configured Default Behavior

1. Normal application composition loads existing YT-157 live settings, constructs one configured runtime, and passes it through the HTTP transport to the dispatcher.
2. The dispatcher passes the configured runtime executor and applicable credential availability to descriptors for every operation in scope.
3. A descriptor validates public arguments, selects authorization by its existing selector or write rules, and calls its existing Layer 1 wrapper with the shared executor.
4. The wrapper validates its existing request shape and delegates a request execution to the existing concrete transport.
5. The concrete transport preserves metadata-defined target, method, parameters, body, and media form; attaches the selected credential; uses Google's upload endpoint and upload protocol where media is present; and returns the existing normalized success or normalized failure.
6. The `videos_getVideo` descriptor receives a lower-level `videos.list` lookup built with the same configured conditional dependencies, then performs its existing higher-level normalization and error translation.
7. A configured default invocation must never create or select a family-local representative executor, placeholder credential, static result, separate direct upstream path, or independently constructed local-default composed lookup.

## Authorization and Request Rules

| Rule | Required behavior |
| --- | --- |
| Conditional search | Use an API key for baseline public search and OAuth for restricted filters; do not substitute one mode for another. |
| Conditional subscriptions list | Use an API key for `channelId` or `id`; use OAuth for `mine`, `myRecentSubscribers`, or `mySubscribers`; do not infer another mode from credential availability. |
| Conditional videos list | Use an API key for `id` or `chart`; use OAuth for `myRating`; do not infer another mode from credential availability. |
| API-key operation | Use a nonblank configured API key only where current metadata and selector rules permit it. A missing key must produce the existing safe caller-facing failure at invocation time. |
| OAuth-required operation | Use a nonblank static access token or complete refresh-token credential configuration; do not fall back to an API key. Refresh tokens are exchanged internally and neither the token nor client secret is surfaced. |
| Query-only operation | Preserve metadata-defined query target and parameters. |
| JSON action or mutation | Preserve existing body validation and submit the validated body through the shared transport. |
| Direct media operation | Preserve existing media and metadata validation and send raw media with `uploadType=media` or metadata-plus-media with `uploadType=multipart` to `/upload/youtube/v3/...` through the shared transport. |
| Resumable video upload | For `videos.insert` with `uploadMode=resumable`, create a Google resumable session, send bounded chunks, and use the session's committed-range status to recover after an interrupted chunk. Session URLs are opaque and never exposed. |
| Retry | Apply bounded full-jitter exponential backoff only to idempotent request methods (`GET`, `HEAD`, `PUT`, and `DELETE`). Do not automatically replay non-idempotent POST mutations. |
| Capability readiness | Report API-key, OAuth, and OAuth lifecycle availability safely; a missing optional OAuth capability is reported as partial capability, not as a health-check secret leak. |

## Compatibility Guarantees

The following remain unchanged for every in-scope operation:

- Public MCP tool name, description, input schema, metadata, quota and authorization disclosure, lifecycle information, and caller examples.
- Layer 1 endpoint metadata, method/path declaration, selector and body validation, quota documentation, and authorization rule.
- Family-specific result mapping, response-normalizer selection, safe public error category/message, and no-match behavior.
- `videos_getVideo` request and normalized result contract, its exclusive lower-layer `videos.list` dependency, and its safe error translation.
- Shared, method-safe retry selection, bounded backoff, and safe integration observability behavior.
- Explicit wrapper, executor, opener, credential, and composed lookup injection for isolated tests or deliberate local development.

## Failure and Security Rules

| Condition | Required outcome |
| --- | --- |
| Missing or blank selected credential | Existing safe normalized configuration, authentication, or authorization failure; no request and no representative success. |
| Invalid input or incompatible selector | Existing validation failure before live execution. |
| Upstream authorization rejection, malformed response, timeout, quota, or service failure | Existing normalized family-specific public failure after shared retry selection where applicable. |
| Explicit test/local executor, opener, or composed lookup | Allowed only when supplied deliberately; it must not be selected by configured default composition. |
| Diagnostic, log, result, or test evidence | Must omit API keys, OAuth tokens, bearer headers, credential-bearing URLs, raw body/media, stack traces, and unfiltered upstream failures. |

## Verification Obligations

- Parameterized request-level tests cover all 16 operations: path, method, parameters, selected credential mode and location, body or media form where applicable, normalized success, and normalized upstream failure.
- Transport tests cover Google upload endpoint selection, direct upload types, resumable session/chunk/recovery behavior, OAuth refresh caching, and retry eligibility/backoff.
- Configured public-tool flow tests prove `search_list`, `videos_list`, and `videos_getVideo` reach the shared live request path through transport and dispatcher composition.
- Existing unit and contract tests prove unchanged wrapper validation, descriptor schema and metadata, result shape, and safe error behavior.
- Final validation runs `python3 -m pytest` followed by `python3 -m ruff check .`.
- A real read-only smoke test runs only when `RUN_YOUTUBE_LIVE_SMOKE=1` and a real `YOUTUBE_API_KEY` are supplied; it is not a default CI test.
