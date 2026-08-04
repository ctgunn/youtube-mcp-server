# Data Model: Layer 1 Discovery, Video, and Branding Live-Call Retrofit

## Configured Runtime Dependency

Represents the existing non-persistent YT-157 runtime passed from transport composition into public descriptor construction.

| Field | Description | Validation |
| --- | --- | --- |
| `executor` | Shared executor backed by the concrete YouTube request transport. | Required for every configured default descriptor in scope. |
| `api_key_available` | Availability of the configured API-key credential. | Required only for an API-key-selected operation; the value is secret. |
| `oauth_token_available` | Availability of the configured OAuth credential. | Required only for an OAuth-selected operation; the value is secret. |
| `oauth_lifecycle` | OAuth lifecycle state: `not_configured`, `static`, or `refreshable`. | Safe readiness metadata only; it must not include credential values. |
| `timeout_seconds` | Existing per-attempt timeout. | Preserved at the runtime default unless explicitly configured; no endpoint override is added. |
| `retry_policy` | Shared method-safe retry policy. | Uses bounded exponential backoff only for idempotent methods; POST mutations are not replayed automatically. |

## Discovery, Video, Subscription, and Branding Operation

Represents a YouTube Data API-backed resource-wrapper operation that receives the configured runtime dependency. The 16-operation table below remains the original YT-160 configured-default regression subset.

| Family | Operations | Authorization rule | Request forms |
| --- | --- | --- | --- |
| Search | `search.list` | API key for public search; OAuth for restricted filters. | GET query. |
| Subscriptions | `subscriptions.list`, `subscriptions.insert`, `subscriptions.delete` | API key for `channelId` or `id` list selectors; OAuth for owner selectors and mutations. | GET/DELETE query; POST JSON. |
| Thumbnails | `thumbnails.set` | OAuth required. | POST raw media. |
| Video abuse-report reasons | `videoAbuseReportReasons.list` | API key. | GET query. |
| Video categories | `videoCategories.list` | API key. | GET query. |
| Videos | `videos.list`, `videos.insert`, `videos.update`, `videos.rate`, `videos.getRating`, `videos.reportAbuse`, `videos.delete` | API key for `id`/`chart` list selectors; OAuth for `myRating` and all other operations. | GET/DELETE query; POST/PUT JSON; POST query actions; insert multipart metadata and media. |
| Watermarks | `watermarks.set`, `watermarks.unset` | OAuth required. | POST raw media; POST query. |

**Validation rules**:

- Existing endpoint request shapes and resource-specific validators remain authoritative for required fields, exclusive selectors, writable bodies, media, paging, and delegation values.
- Search restricted filters select OAuth; baseline search selects an API key. Subscription owner selectors select OAuth, while `channelId` and `id` select an API key. Video `myRating` selects OAuth, while `id` and `chart` select an API key.
- Subscription writes, thumbnail changes, all video writes/rating operations, and watermark changes require OAuth and must not fall back to an API key.
- Video insertion retains required metadata and media plus `multipart` or `resumable` upload-mode validation. The shared transport selects the Google upload endpoint and upload protocol; no resource wrapper constructs its own HTTP client.

## Request Execution

Represents the existing request passed through the common executor.

| Field | Description | Relationship |
| --- | --- | --- |
| `metadata` | Immutable operation identity, method, path, request shape, authorization requirement, and quota data. | Supplied by the existing Layer 1 wrapper. |
| `arguments` | Validated caller arguments. | Must pass generic and family-specific validation before execution. |
| `auth_context` | Selected API-key or OAuth credential context. | Derived from established selector and operation rules plus runtime availability. |
| `request_form` | Derived query-only, JSON, raw-media, multipart, or resumable request. | Built only by the shared concrete transport. |
| `upload_type` | Google media protocol selector. | `media`, `multipart`, or `resumable` only when media is present. |
| `upload_endpoint` | Google endpoint used for media transfer. | Must be `/upload/youtube/v3/...`; standard JSON/query calls use `/youtube/v3/...`. |

## OAuth Credential Lifecycle

| Field | Description | Validation |
| --- | --- | --- |
| `static_access_token` | Optional operator-provided short-lived OAuth access token. | May be used directly but is never returned, logged, or persisted. |
| `refresh_token` | Optional long-lived OAuth refresh credential. | Requires both client ID and client secret; must be injected as a secret. |
| `client_id` / `client_secret` | OAuth client credentials used only for Google token refresh. | Required together with `refresh_token`; never emitted in diagnostics. |
| `cached_access_token` | In-memory refreshed OAuth access token. | Reused only until shortly before expiry; no persistent storage. |

## Resumable Upload Session

| Field | Description | Validation |
| --- | --- | --- |
| `session_url` | Opaque URL returned by Google during `videos.insert` initialization. | Internal-only; must never appear in a result, log, or normalized error. |
| `chunk_size` | Maximum transfer size for one PUT request. | Positive multiple of 256 KiB. |
| `committed_range` | Byte range confirmed by Google's resumable status response. | Used only to compute the next safe chunk offset. |
| `next_offset` | First byte of the next chunk. | Derived from `committed_range`; status recovery occurs after a failed chunk. |

## Composed Video Detail Lookup

Represents the higher-level `videos_getVideo` public flow's one dependency on the configured lower-level video-list handler.

| Field | Description | Validation |
| --- | --- | --- |
| `video_id` | Requested public video identifier. | Must pass the existing detail-tool identifier validation. |
| `requested_parts` | Core and optionally requested video field groups. | The existing detail-tool part validation remains authoritative. |
| `configured_lookup` | Lower-level `videos.list` handler created with configured conditional dependencies. | Required for configured dispatcher composition; it must not be a local-default handler. |
| `normalized_detail` | Existing higher-level result derived from the lower-level normalized list result. | Must retain existing details result and safe error translation. |

## Normalized Outcome

Represents the caller-visible result after a configured request.

| Field | Description | Validation |
| --- | --- | --- |
| `success_payload` | Existing family-specific normalized result. | Must retain the public result shape for the operation. |
| `failure_category` | Existing safe configuration, authentication, authorization, quota, not-found, transient, or upstream category. | Must retain the operation's existing public error mapping. |
| `retryable` | Existing shared retry determination. | Derived from normalized error and shared policy. |
| `safe_details` | Permitted diagnostics. | Must exclude credential values, authorization headers, credential-bearing URLs, raw body/media, stack traces, and raw upstream payloads. |

## State Transitions

```text
configured transport runtime
  -> dispatcher passes runtime dependencies to an in-scope descriptor
  -> descriptor validates public arguments
  -> wrapper validates metadata/request shape and resolves authorization
  -> required configured credential available?
       -> no: existing safe normalized configuration/authorization failure
       -> yes: shared executor builds live request
  -> existing transport sends controlled/live request and emits safe event
       -> retryable idempotent failure: bounded exponential backoff and retry
       -> retryable POST mutation failure: terminal normalized failure; no replay
       -> terminal failure: existing normalized public failure
       -> success: existing response normalizer and public result mapper

configured videos_getVideo
  -> existing detail validation
  -> injected configured videos.list lookup
  -> same video-wrapper live transition above
  -> existing detail result normalization or safe error translation

configured videos.insert with uploadMode=resumable
  -> shared transport initializes opaque Google upload session
  -> bounded PUT chunk
  -> 308 or failed-chunk status recovery computes next offset
  -> final normalized video result
```

The prohibited transitions are: configured default invocation → representative executor or static successful response; and configured `videos_getVideo` → independently constructed local-default video lookup or direct upstream request.
