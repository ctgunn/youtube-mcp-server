# Data Model: Layer 1 Catalog, Membership, and Playlist Live-Call Retrofit

## Configured Runtime Dependency

Represents the existing non-persistent YT-157 runtime passed from transport composition into public descriptor construction.

| Field | Description | Validation |
| --- | --- | --- |
| `executor` | Shared executor backed by the concrete YouTube request transport. | Required for every configured default descriptor in scope. |
| `api_key_available` | Availability of the configured API-key credential. | Required only for an API-key-selected operation; the value is secret. |
| `oauth_token_available` | Availability of the configured OAuth credential. | Required only for an OAuth-selected operation; the value is secret. |
| `timeout_seconds` | Existing per-attempt timeout. | Preserved at the runtime default unless explicitly configured; no endpoint override is added. |
| `retry_policy` | Existing retry-selection policy. | Preserved from YT-157; no resource-specific retry behavior is added. |

## Catalog, Membership, and Playlist Operation

Represents one of the 17 existing resource-wrapper operations that receives the configured runtime dependency.

| Family | Operations | Authorization rule | Request forms |
| --- | --- | --- | --- |
| Guide categories | `guideCategories.list` | API key. | GET query. |
| Localization | `i18nLanguages.list`, `i18nRegions.list` | API key. | GET query. |
| Members | `members.list` | OAuth required. | GET query. |
| Membership levels | `membershipsLevels.list` | OAuth required. | GET query. |
| Playlist images | `playlistImages.list`, `insert`, `update`, `delete` | OAuth required. | GET/DELETE query; POST/PUT multipart metadata and media. |
| Playlist items | `playlistItems.list`, `insert`, `update`, `delete` | API key for list; OAuth required for mutations. | GET/DELETE query; POST/PUT JSON body. |
| Playlists | `playlists.list`, `insert`, `update`, `delete` | Conditional list: API key for `channelId`/`id`, OAuth for `mine`; OAuth required for mutations. | GET/DELETE query; POST/PUT JSON body. |

**Validation rules**:

- Existing `EndpointRequestShape` and resource-specific validators remain authoritative for required and allowed fields, exclusive selectors, writable bodies, media, paging, and delegation values.
- `guideCategories.list` requires `part` and exactly one of `regionCode` or `id`; its deprecated lifecycle note remains visible.
- Localization requests require `part` and optionally accept `hl`. Members require `part` and `mode`; membership levels require `part`.
- Playlist-image and playlist-item lists select exactly one supported ID or playlist selector. Paging remains limited to collection selectors.
- Playlist-image mutations retain validated metadata plus `mimeType` and media content. Playlist-item and playlist mutations retain their existing minimum writable body fields.
- Conditional playlist listing chooses credentials from the existing selector rule; it does not choose another mode merely because one is available.

## Request Execution

Represents the existing request passed through the common executor.

| Field | Description | Relationship |
| --- | --- | --- |
| `metadata` | Immutable operation identity, method, path, request-shape, authorization requirement, and quota data. | Supplied by the existing Layer 1 wrapper. |
| `arguments` | Validated caller arguments. | Must pass generic and family-specific validation before execution. |
| `auth_context` | Selected API-key or OAuth credential context. | Derived from the operation's established authorization rule and configured runtime availability. |
| `request_form` | Derived query-only, JSON, or multipart request. | Built only by the existing concrete transport. |

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
  -> dispatcher passes runtime to in-scope descriptor
  -> descriptor validates public arguments
  -> wrapper validates metadata/request shape and resolves authorization
  -> required configured credential available?
       -> no: existing safe normalized configuration/authorization failure
       -> yes: shared executor builds live request
  -> existing transport sends controlled/live request and emits safe event
       -> retryable normalized failure: existing retry selection
       -> terminal failure: existing normalized public failure
       -> success: existing response normalizer and public result mapper
```

The prohibited transition is: a configured default invocation → representative executor or static successful response.
