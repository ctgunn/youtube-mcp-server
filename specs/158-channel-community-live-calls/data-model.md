# Data Model: Layer 1 Channel and Community Live-Call Retrofit

## Configured Runtime Dependency

Represents the existing, non-persistent YT-157 runtime passed from transport composition into public descriptor construction.

| Field | Description | Validation |
| --- | --- | --- |
| `executor` | Shared executor backed by the concrete YouTube request transport. | Required for every configured default descriptor in scope. |
| `api_key_available` | Availability of the configured API-key credential. | Required only when the selected operation rule is API-key access; the value is secret. |
| `oauth_token_available` | Availability of the configured OAuth credential. | Required only when the selected operation rule is OAuth access; the value is secret. |
| `timeout_seconds` | Existing per-attempt timeout. | Preserved at the runtime default unless explicitly configured; no endpoint override is added. |
| `retry_policy` | Existing retry-selection policy. | Preserved from YT-157; no resource-specific retry behavior is added. |

## Channel and Community Operation

Represents one of the 20 existing resource-wrapper operations that receives the configured runtime dependency.

| Family | Operations | Authorization rule | Request forms |
| --- | --- | --- | --- |
| Activities | `activities.list` | Conditional: API key for `channelId`; OAuth for `mine`/`home`. | GET query. |
| Captions | `captions.list`, `insert`, `update`, `download`, `delete` | OAuth required. | GET/DELETE query or item path; JSON/body plus media or multipart where declared. |
| Channel banners | `channelBanners.insert` | OAuth required. | POST raw media. |
| Channels | `channels.list`, `channels.update` | Conditional public selectors/OAuth `mine`; OAuth required for update. | GET query; PUT JSON body. |
| Channel sections | `channelSections.list`, `insert`, `update`, `delete` | Conditional public selectors/OAuth `mine`; OAuth required for mutations. | GET/DELETE query; POST/PUT JSON body. |
| Comments | `comments.list`, `insert`, `update`, `setModerationStatus`, `delete` | API key for list; OAuth required for mutations. | GET/POST/DELETE query; POST/PUT JSON body. |
| Comment threads | `commentThreads.list`, `commentThreads.insert` | API key for list; OAuth required for insert. | GET query; POST JSON body. |

**Validation rules**:

- The existing `EndpointRequestShape` and resource-specific validators remain authoritative for required fields, allowed fields, exclusive selectors, writable bodies, media, and delegation values.
- Conditional operations choose the credential from their existing selector rules; they do not fall back to another mode.
- All operations retain their endpoint metadata, quota cost, authorization metadata, lifecycle notes, response normalizer, and public descriptor metadata.

## Request Execution

Represents the existing request passed through the common executor.

| Field | Description | Relationship |
| --- | --- | --- |
| `metadata` | Immutable operation identity, method, path, request-shape, authorization requirement, and quota data. | Supplied by the existing Layer 1 wrapper. |
| `arguments` | Validated caller arguments. | Must pass generic and family-specific validation before execution. |
| `auth_context` | Selected API-key or OAuth credential context. | Derived from the operation's established authorization rule and configured runtime availability. |
| `request_form` | Derived query-only, JSON, raw-media, or multipart request. | Built only by the existing concrete transport. |

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
