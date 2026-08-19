"""Concrete YouTube Data API transport helpers for Layer 1 wrappers."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping, Sequence
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from mcp_server.integrations.executor import (
    IntegrationExecutor,
    IntegrationHooks,
    RequestExecution,
)
from mcp_server.integrations.resources.normalizers import (
    ResponseNormalizer,
    build_response_normalizer_registry,
    default_response_normalizer_registry,
    normalize_youtube_response,
)
from mcp_server.integrations.retry import RetryPolicy

YOUTUBE_DATA_API_ORIGIN = "https://www.googleapis.com"
DEFAULT_RESUMABLE_CHUNK_SIZE = 8 * 1024 * 1024
_MAX_RESUMABLE_RECOVERY_ATTEMPTS = 2

__all__ = [
    "YOUTUBE_DATA_API_ORIGIN",
    "ResponseNormalizer",
    "build_response_normalizer_registry",
    "build_youtube_data_api_executor",
    "build_youtube_data_api_request",
    "build_youtube_data_api_transport",
    "default_response_normalizer_registry",
    "normalize_youtube_response",
]

def build_youtube_data_api_transport(
    *,
    opener: Callable[..., Any] | None = None,
    timeout_seconds: float = 10.0,
    resumable_chunk_size: int = DEFAULT_RESUMABLE_CHUNK_SIZE,
) -> Callable[[RequestExecution], dict[str, Any]]:
    """Build a transport callable that executes Layer 1 requests against YouTube.

    :param opener: Optional request opener compatible with ``urllib.request.urlopen``.
    :param timeout_seconds: Timeout used for upstream requests.
    :param resumable_chunk_size: Maximum bytes sent in each resumable upload chunk.
    :return: Transport callable suitable for ``IntegrationExecutor``.
    """
    request_opener = opener or urlopen
    if resumable_chunk_size <= 0 or resumable_chunk_size % (256 * 1024) != 0:
        raise ValueError("resumable_chunk_size must be a positive multiple of 256 KiB")

    def transport(execution: RequestExecution) -> dict[str, Any]:
        """Execute one YouTube Data API request for the given execution context.

        :param execution: Shared request execution details.
        :return: Parsed JSON response from the upstream API.
        """
        try:
            if _is_resumable_upload(execution.arguments):
                payload = _execute_resumable_upload(
                    execution,
                    opener=request_opener,
                    timeout_seconds=timeout_seconds,
                    chunk_size=resumable_chunk_size,
                )
            else:
                request = build_youtube_data_api_request(execution)
                with request_opener(request, timeout=timeout_seconds) as response:
                    payload = response.read().decode("utf-8")
        except HTTPError as error:
            details = _error_details(error)
            raise _normalized_upstream_failure(
                str(details["message"]),
                category=_normalized_category_for_execution(execution, status_code=error.code, details=details),
                status_code=error.code,
                details=details,
            )
        except URLError as error:
            raise _normalized_upstream_failure(
                str(error.reason),
                category=_normalized_category_for_execution(
                    execution,
                    status_code=None,
                    details={"reason": str(error.reason)},
                ),
                details={"reason": str(error.reason)},
            )
        except TimeoutError as error:
            raise _normalized_upstream_failure(
                str(error),
                category=_normalized_category_for_execution(
                    execution,
                    status_code=504,
                    details={"reason": "timeout"},
                ),
                status_code=504,
                details={"reason": "timeout"},
            )

        return normalize_youtube_response(
            execution,
            payload,
            registry=default_response_normalizer_registry(),
        )

    return transport


def build_youtube_data_api_executor(
    *,
    opener: Callable[..., Any] | None = None,
    timeout_seconds: float = 10.0,
    resumable_chunk_size: int = DEFAULT_RESUMABLE_CHUNK_SIZE,
    retry_policy: RetryPolicy | None = None,
    hooks: IntegrationHooks | None = None,
) -> IntegrationExecutor:
    """Build an executor wired to the concrete YouTube Data API transport.

    :param opener: Optional request opener compatible with ``urllib.request.urlopen``.
    :param timeout_seconds: Timeout used for upstream requests.
    :param resumable_chunk_size: Maximum bytes sent in each resumable upload chunk.
    :param retry_policy: Optional retry policy override.
    :param hooks: Optional request lifecycle hooks.
    :return: Shared executor configured for live YouTube requests.
    """
    return IntegrationExecutor(
        transport=build_youtube_data_api_transport(
            opener=opener,
            timeout_seconds=timeout_seconds,
            resumable_chunk_size=resumable_chunk_size,
        ),
        retry_policy=retry_policy or RetryPolicy(max_attempts=3),
        hooks=hooks,
    )


def build_youtube_data_api_request(execution: RequestExecution) -> Request:
    """Build one concrete HTTP request for a YouTube Data API execution.

    :param execution: Shared request execution details.
    :return: Configured HTTP request object.
    """
    resolved_path = _resolved_path_shape(execution.metadata.path_shape, execution.arguments)
    query_arguments = dict(_query_arguments(
        execution.metadata.http_method,
        execution.metadata.path_shape,
        execution.arguments,
    ))
    if _has_media_upload(execution.arguments):
        resolved_path = _upload_path(resolved_path)
        query_arguments["uploadType"] = (
            "resumable" if _is_resumable_upload(execution.arguments) else _upload_type(execution.arguments)
        )
    query = _query_parameters(query_arguments, execution.credentials)
    query_string = urlencode(query, doseq=True)
    url = f"{YOUTUBE_DATA_API_ORIGIN}{resolved_path}"
    if query_string:
        url = f"{url}?{query_string}"
    headers = {"Accept": "application/json"}
    request_data = _request_data(
        execution.metadata.http_method,
        execution.arguments,
        resumable_initialization=_is_resumable_upload(execution.arguments),
    )
    oauth_token = execution.credentials.get("oauthToken")
    if oauth_token:
        headers["Authorization"] = f"Bearer {oauth_token}"
    if request_data is not None:
        headers["Content-Type"] = _request_content_type(
            execution.arguments,
            resumable_initialization=_is_resumable_upload(execution.arguments),
        )
    if _is_resumable_upload(execution.arguments):
        media = execution.arguments["media"]
        assert isinstance(media, Mapping)
        media_bytes = _media_content_bytes(media.get("content"))
        headers["X-Upload-Content-Length"] = str(len(media_bytes))
        headers["X-Upload-Content-Type"] = str(media.get("mimeType", "application/octet-stream"))
    return Request(url, data=request_data, method=execution.metadata.http_method.upper(), headers=headers)


def _has_media_upload(arguments: Mapping[str, object]) -> bool:
    """Return whether an execution includes a media upload payload.

    :param arguments: Wrapper arguments selected for the execution.
    :return: ``True`` when the request must use Google's upload endpoint.
    """
    return isinstance(arguments.get("media"), Mapping)


def _upload_path(path: str) -> str:
    """Return the Google upload endpoint path for a media request.

    :param path: Resolved standard or upload endpoint path.
    :return: Upload endpoint path preserving an explicitly declared upload path.
    """
    if path.startswith("/upload/"):
        return path
    if path.startswith("/youtube/"):
        return f"/upload{path}"
    raise ValueError(f"unsupported YouTube Data API path for media upload: {path}")


def _upload_type(arguments: Mapping[str, object]) -> str:
    """Return Google's direct upload type for one media request.

    :param arguments: Wrapper arguments selected for the execution.
    :return: ``multipart`` for metadata plus media, otherwise ``media``.
    """
    return "multipart" if isinstance(arguments.get("body"), Mapping) else "media"


def _is_resumable_upload(arguments: Mapping[str, object]) -> bool:
    """Return whether an execution selects the supported resumable upload flow.

    :param arguments: Wrapper arguments selected for the execution.
    :return: ``True`` when the upload must create and use a resumable session.
    """
    return arguments.get("uploadMode") == "resumable"


def _query_arguments(
    http_method: str,
    path_shape: str,
    arguments: Mapping[str, object],
) -> Mapping[str, object]:
    """Return the argument subset that should remain in the query string.

    :param http_method: Upstream HTTP method for the request.
    :param path_shape: Upstream path shape for the request.
    :param arguments: Wrapper arguments selected for the execution.
    :return: Arguments that belong in the request URL.
    """
    path_fields = set(_path_parameters(path_shape))
    if http_method.upper() not in {"POST", "PUT", "PATCH"}:
        return {key: value for key, value in arguments.items() if key not in path_fields}
    return {
        key: value
        for key, value in arguments.items()
        if key not in {"body", "media", "uploadMode"} and key not in path_fields
    }


def _resolved_path_shape(path_shape: str, arguments: Mapping[str, object]) -> str:
    """Return the path shape with placeholder fields filled from arguments.

    :param path_shape: Declared upstream path shape.
    :param arguments: Wrapper arguments selected for the execution.
    :return: Resolved path safe for URL construction.
    """
    resolved = path_shape
    for field_name in _path_parameters(path_shape):
        resolved = resolved.replace(f"{{{field_name}}}", quote(_stringify_scalar(arguments.get(field_name)), safe=""))
    return resolved


def _path_parameters(path_shape: str) -> tuple[str, ...]:
    """Return placeholder field names referenced by one path shape.

    :param path_shape: Declared upstream path shape.
    :return: Ordered placeholder names without braces.
    """
    parameters: list[str] = []
    start_index = 0
    while True:
        open_index = path_shape.find("{", start_index)
        if open_index == -1:
            break
        close_index = path_shape.find("}", open_index + 1)
        if close_index == -1:
            break
        parameters.append(path_shape[open_index + 1 : close_index])
        start_index = close_index + 1
    return tuple(parameters)


def _request_data(
    http_method: str,
    arguments: Mapping[str, object],
    *,
    resumable_initialization: bool = False,
) -> bytes | None:
    """Return encoded request data for caption write operations.

    :param http_method: Upstream HTTP method for the request.
    :param arguments: Wrapper arguments selected for the execution.
    :return: Encoded request payload when the method carries a body.
    """
    if http_method.upper() not in {"POST", "PUT", "PATCH"}:
        return None
    body = arguments.get("body")
    media = arguments.get("media")
    if resumable_initialization and isinstance(body, Mapping):
        return json.dumps(body).encode("utf-8")
    if isinstance(body, dict) and isinstance(media, dict):
        return _multipart_related_payload(body=body, media=media)
    if isinstance(media, dict):
        return _media_content_bytes(media.get("content"))
    if isinstance(body, dict):
        return json.dumps(body).encode("utf-8")
    return None


def _request_content_type(
    arguments: Mapping[str, object],
    *,
    resumable_initialization: bool = False,
) -> str:
    """Return the content type for the outgoing request body.

    :param arguments: Wrapper arguments selected for the execution.
    :return: Content type header value.
    """
    if resumable_initialization:
        return "application/json; charset=utf-8"
    media = arguments.get("media")
    if isinstance(media, dict) and not isinstance(arguments.get("body"), dict):
        return str(media.get("mimeType", "application/octet-stream"))
    if isinstance(arguments.get("media"), dict):
        return 'multipart/related; boundary="yt-mcp-boundary"'
    return "application/json; charset=utf-8"


def _query_parameters(
    arguments: Mapping[str, object],
    credentials: Mapping[str, str],
) -> list[tuple[str, str]]:
    """Return ordered query parameters for one execution.

    :param arguments: Request arguments selected for the wrapper.
    :param credentials: Resolved credential payload for the execution.
    :return: Ordered key/value pairs suitable for URL encoding.
    """
    params: list[tuple[str, str]] = []
    for key, value in arguments.items():
        params.extend((key, encoded) for encoded in _encode_values(value))
    api_key = credentials.get("apiKey")
    if api_key:
        params.append(("key", api_key))
    return params


def _multipart_related_payload(
    *,
    body: Mapping[str, object],
    media: Mapping[str, object],
) -> bytes:
    """Build a multipart payload for caption upload requests.

    :param body: Caption metadata payload.
    :param media: Media-upload payload including ``mimeType`` and ``content``.
    :return: Encoded multipart body.
    """
    boundary = "yt-mcp-boundary"
    metadata = json.dumps(body).encode("utf-8")
    media_bytes = _media_content_bytes(media.get("content"))
    mime_type = str(media.get("mimeType", "application/octet-stream"))
    parts = [
        f"--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n".encode(),
        metadata,
        b"\r\n",
        f"--{boundary}\r\nContent-Type: {mime_type}\r\n\r\n".encode(),
        media_bytes,
        b"\r\n",
        f"--{boundary}--\r\n".encode(),
    ]
    return b"".join(parts)


def _media_content_bytes(content: object) -> bytes:
    """Convert media content into request-body bytes.

    :param content: Media payload content from wrapper arguments.
    :return: Byte representation of the media content.
    """
    if isinstance(content, bytes):
        return content
    return str(content).encode("utf-8")


def _encode_values(value: object) -> Sequence[str]:
    """Encode one wrapper argument value for query-string transport.

    :param value: Argument value to encode.
    :return: One or more string values.
    """
    if isinstance(value, bool):
        return ("true" if value else "false",)
    if isinstance(value, (list, tuple)):
        return tuple(_stringify_scalar(item) for item in value)
    return (_stringify_scalar(value),)


def _stringify_scalar(value: object) -> str:
    """Convert one scalar wrapper argument value into its query-string form.

    :param value: Scalar value to encode.
    :return: String form suitable for URL encoding.
    """
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _execute_resumable_upload(
    execution: RequestExecution,
    *,
    opener: Callable[..., Any],
    timeout_seconds: float,
    chunk_size: int,
) -> str:
    """Create a resumable session and upload its media in bounded chunks.

    A failed chunk is recovered by querying the session's committed byte range
    before attempting the remaining bytes again. The session URL is intentionally
    never returned or included in normalized errors.

    :param execution: Shared request execution details.
    :param opener: HTTP request opener compatible with ``urllib.request.urlopen``.
    :param timeout_seconds: Timeout used for each upstream request.
    :param chunk_size: Maximum bytes for each upload request.
    :return: The final JSON response payload from YouTube.
    :raises RuntimeError: If YouTube does not return a resumable session location.
    """
    initialization_request = build_youtube_data_api_request(execution)
    with opener(initialization_request, timeout=timeout_seconds) as response:
        session_url = _response_header(response, "Location")
    if not session_url:
        raise RuntimeError("YouTube did not provide a resumable upload session")

    media = execution.arguments.get("media")
    assert isinstance(media, Mapping)
    media_bytes = _media_content_bytes(media.get("content"))
    mime_type = str(media.get("mimeType", "application/octet-stream"))
    offset = 0
    recovery_attempts = 0

    while offset < len(media_bytes):
        chunk = media_bytes[offset : offset + chunk_size]
        chunk_end = offset + len(chunk) - 1
        request = _resumable_chunk_request(
            session_url=session_url,
            data=chunk,
            mime_type=mime_type,
            start=offset,
            end=chunk_end,
            total=len(media_bytes),
            credentials=execution.credentials,
        )
        try:
            with opener(request, timeout=timeout_seconds) as response:
                status_code = _response_status(response)
                payload = response.read().decode("utf-8")
                committed_range = _response_header(response, "Range")
        except HTTPError as error:
            if error.code != 308:
                if recovery_attempts >= _MAX_RESUMABLE_RECOVERY_ATTEMPTS:
                    raise
                offset = _recover_resumable_offset(
                    session_url=session_url,
                    total=len(media_bytes),
                    credentials=execution.credentials,
                    opener=opener,
                    timeout_seconds=timeout_seconds,
                )
                recovery_attempts += 1
                continue
            status_code = error.code
            payload = error.read().decode("utf-8", errors="replace")
            committed_range = _error_header(error, "Range")

        if status_code == 308:
            offset = _next_resumable_offset(committed_range, fallback=chunk_end + 1)
            continue
        if 200 <= status_code < 300:
            return payload
        raise RuntimeError(f"unexpected resumable upload response status: {status_code}")

    raise RuntimeError("YouTube resumable upload completed without a final response")


def _resumable_chunk_request(
    *,
    session_url: str,
    data: bytes,
    mime_type: str,
    start: int,
    end: int,
    total: int,
    credentials: Mapping[str, str],
) -> Request:
    """Build one bounded resumable media upload request.

    :param session_url: Opaque session URL supplied by YouTube.
    :param data: Bytes for this upload chunk.
    :param mime_type: Media MIME type.
    :param start: Zero-based first byte in the chunk.
    :param end: Zero-based last byte in the chunk.
    :param total: Total media size in bytes.
    :param credentials: Resolved credentials for the execution.
    :return: Configured PUT request for the upload session.
    """
    headers = {
        "Content-Type": mime_type,
        "Content-Length": str(len(data)),
        "Content-Range": f"bytes {start}-{end}/{total}",
    }
    oauth_token = credentials.get("oauthToken")
    if oauth_token:
        headers["Authorization"] = f"Bearer {oauth_token}"
    return Request(session_url, data=data, method="PUT", headers=headers)


def _recover_resumable_offset(
    *,
    session_url: str,
    total: int,
    credentials: Mapping[str, str],
    opener: Callable[..., Any],
    timeout_seconds: float,
) -> int:
    """Query a resumable session for the next safe byte offset.

    :param session_url: Opaque session URL supplied by YouTube.
    :param total: Total media size in bytes.
    :param credentials: Resolved credentials for the execution.
    :param opener: HTTP request opener compatible with ``urllib.request.urlopen``.
    :param timeout_seconds: Timeout used for the status query.
    :return: Next byte offset confirmed by the session.
    """
    headers = {"Content-Length": "0", "Content-Range": f"bytes */{total}"}
    oauth_token = credentials.get("oauthToken")
    if oauth_token:
        headers["Authorization"] = f"Bearer {oauth_token}"
    request = Request(session_url, data=b"", method="PUT", headers=headers)
    try:
        with opener(request, timeout=timeout_seconds) as response:
            status_code = _response_status(response)
            committed_range = _response_header(response, "Range")
    except HTTPError as error:
        if error.code != 308:
            raise
        status_code = error.code
        committed_range = _error_header(error, "Range")
    if status_code != 308:
        raise RuntimeError("YouTube resumable upload session did not return its upload status")
    return _next_resumable_offset(committed_range, fallback=0)


def _next_resumable_offset(committed_range: str | None, *, fallback: int) -> int:
    """Return the next upload offset based on YouTube's committed byte range.

    :param committed_range: ``Range`` header returned by the resumable session.
    :param fallback: Next offset when YouTube did not include a range header.
    :return: Safe byte offset for the next chunk.
    """
    if not committed_range:
        return fallback
    try:
        return int(committed_range.rsplit("-", maxsplit=1)[1]) + 1
    except (IndexError, ValueError):
        return fallback


def _response_header(response: Any, name: str) -> str | None:
    """Return one response header across urllib and test response shapes.

    :param response: Upstream HTTP response.
    :param name: Header name to retrieve.
    :return: Header value when present.
    """
    getheader = getattr(response, "getheader", None)
    if callable(getheader):
        value = getheader(name)
        if value:
            return str(value)
    headers = getattr(response, "headers", None)
    if headers is not None:
        value = headers.get(name)
        if value:
            return str(value)
    return None


def _error_header(error: HTTPError, name: str) -> str | None:
    """Return one header from an ``HTTPError`` without exposing it externally.

    :param error: HTTP error returned by the upstream request.
    :param name: Header name to retrieve.
    :return: Header value when present.
    """
    if error.headers is None:
        return None
    value = error.headers.get(name)
    return str(value) if value else None


def _response_status(response: Any) -> int:
    """Return an HTTP response status, defaulting test doubles to success.

    :param response: Upstream HTTP response.
    :return: Integer HTTP status code.
    """
    getcode = getattr(response, "getcode", None)
    if callable(getcode):
        status = getcode()
        if isinstance(status, int):
            return status
    status = getattr(response, "status", None)
    return status if isinstance(status, int) else 200


def _error_details(error: HTTPError) -> dict[str, object]:
    """Extract safe error details from an upstream HTTP failure.

    :param error: HTTP error returned by the upstream request.
    :return: Sanitized error details for normalization.
    """
    body = ""
    try:
        body = error.read().decode("utf-8", errors="replace")
    except (OSError, ValueError):  # pragma: no cover - best effort only
        body = ""
    message = _extract_error_message(body) or error.reason or str(error)
    details: dict[str, object] = {"reason": str(error.reason)}
    if body:
        details["responseBody"] = body
    return {"message": message, **details}


def _extract_error_message(body: str) -> str | None:
    """Return a readable error message from a YouTube error payload.

    :param body: Raw error payload text.
    :return: Extracted message when available.
    """
    if not body:
        return None
    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        return body.strip() or None
    if not isinstance(parsed, dict):
        return body.strip() or None
    error_payload = parsed.get("error")
    if isinstance(error_payload, dict):
        message = error_payload.get("message")
        if isinstance(message, str) and message.strip():
            return message.strip()
    return body.strip() or None


def _normalized_upstream_failure(
    message: str,
    *,
    category: str | None = None,
    status_code: int | None = None,
    details: dict[str, object] | None = None,
) -> Exception:
    """Build a normalized upstream failure from concrete transport errors.

    :param message: Safe upstream failure message.
    :param status_code: Optional upstream HTTP status.
    :param details: Optional structured error details.
    :return: Normalized exception raised by the transport.
    """
    from mcp_server.integrations.errors import normalize_upstream_error

    return normalize_upstream_error(
        RuntimeError(message),
        category=category,
        status_code=status_code,
        details=details,
    )


def _normalized_category_for_execution(
    execution: RequestExecution,
    *,
    status_code: int | None,
    details: Mapping[str, object],
) -> str | None:
    """Return an operation-specific normalized error category when needed.

    :param execution: Shared request execution details.
    :param status_code: Optional upstream status code.
    :param details: Sanitized upstream error details.
    :return: Explicit normalized category override when one is needed.
    """
    if execution.metadata.operation_key != "channelBanners.insert":
        if execution.metadata.operation_key not in {
            "channels.update",
            "channelSections.update",
            "channelSections.delete",
            "guideCategories.list",
            "i18nLanguages.list",
            "i18nRegions.list",
            "videoAbuseReportReasons.list",
            "videoCategories.list",
            "videos.list",
            "videos.insert",
            "videos.getRating",
            "videos.reportAbuse",
            "videos.delete",
            "videos.rate",
            "videos.update",
            "members.list",
            "membershipsLevels.list",
            "playlistImages.list",
            "playlistItems.list",
            "playlists.list",
            "subscriptions.list",
            "subscriptions.insert",
            "subscriptions.delete",
            "search.list",
            "playlistItems.insert",
            "playlists.insert",
            "playlists.update",
            "playlists.delete",
            "playlistItems.update",
            "playlistItems.delete",
            "playlistImages.insert",
            "thumbnails.set",
            "watermarks.set",
            "watermarks.unset",
            "playlistImages.update",
            "playlistImages.delete",
            "commentThreads.list",
            "commentThreads.insert",
            "comments.list",
            "comments.insert",
            "comments.update",
            "comments.setModerationStatus",
            "comments.delete",
        }:
            return None
        message = str(details.get("message", "")).lower()
        reason = str(details.get("reason", "")).lower()
        body = str(details.get("responseBody", "")).lower()
        combined = " ".join(part for part in (message, reason, body) if part)
        if execution.metadata.operation_key == "commentThreads.list":
            if status_code in {400, 422} or "invalid" in combined or "required" in combined:
                return "invalid_request"
            return None
        if execution.metadata.operation_key == "commentThreads.insert":
            if "comments disabled" in combined or "disabled comments" in combined:
                return "target_eligibility"
            if "discussion" in combined and (
                "disabled" in combined or "unavailable" in combined or "ineligible" in combined
            ):
                return "target_eligibility"
            if status_code == 404 and (
                "video" in combined or "discussion" in combined or "target" in combined
            ):
                return "target_eligibility"
            if status_code in {400, 422} or "invalid" in combined or "required" in combined:
                return "invalid_request"
            return None
        if execution.metadata.operation_key == "comments.list":
            if status_code in {400, 422} or "invalid" in combined or "required" in combined:
                return "invalid_request"
            return None
        if execution.metadata.operation_key == "guideCategories.list":
            if status_code in {400, 422} or "invalid" in combined or "required" in combined:
                return "invalid_request"
            if "deprecated" in combined or "unavailable" in combined or "legacy" in combined:
                return "lifecycle_unavailable"
            return None
        if execution.metadata.operation_key == "i18nLanguages.list":
            if status_code in {400, 422} or "invalid" in combined or "required" in combined:
                return "invalid_request"
            return None
        if execution.metadata.operation_key == "i18nRegions.list":
            if status_code in {400, 422} or "invalid" in combined or "required" in combined:
                return "invalid_request"
            return None
        if execution.metadata.operation_key == "videoAbuseReportReasons.list":
            if status_code in {400, 422} or "invalid" in combined or "required" in combined:
                return "invalid_request"
            return None
        if execution.metadata.operation_key == "videoCategories.list":
            if status_code in {400, 422} or "invalid" in combined or "required" in combined:
                return "invalid_request"
            return None
        if execution.metadata.operation_key == "videos.list":
            if status_code in {400, 422} or "invalid" in combined or "required" in combined:
                return "invalid_request"
            return None
        if execution.metadata.operation_key == "videos.insert":
            if _is_invalid_update_request(status_code=status_code, combined=combined):
                return "invalid_request"
            if status_code == 403 and ("private" in combined or "audit" in combined or "policy" in combined):
                return "policy_restricted"
            return None
        if execution.metadata.operation_key == "videos.update":
            if _is_invalid_update_request(status_code=status_code, combined=combined):
                return "invalid_request"
            if _is_missing_update_target(status_code=status_code, combined=combined, target_terms=("video", "target")):
                return "not_found"
            return None
        if execution.metadata.operation_key == "members.list":
            if status_code in {400, 422} or "invalid" in combined or "required" in combined:
                return "invalid_request"
            return None
        if execution.metadata.operation_key == "membershipsLevels.list":
            if status_code in {400, 422} or "invalid" in combined or "required" in combined:
                return "invalid_request"
            return None
        if execution.metadata.operation_key == "playlistImages.list":
            if status_code in {400, 422} or "invalid" in combined or "required" in combined:
                return "invalid_request"
            return None
        if execution.metadata.operation_key == "playlistItems.list":
            if status_code in {400, 422} or "invalid" in combined or "required" in combined:
                return "invalid_request"
            return None
        if execution.metadata.operation_key == "playlists.list":
            if status_code in {400, 422} or "invalid" in combined or "required" in combined:
                return "invalid_request"
            return None
        if execution.metadata.operation_key == "subscriptions.list":
            if status_code in {400, 422} or "invalid" in combined or "required" in combined:
                return "invalid_request"
            return None
        if execution.metadata.operation_key == "subscriptions.insert":
            if status_code in {400, 422} or "invalid" in combined or "required" in combined:
                return "invalid_request"
            if (
                status_code == 409
                or "duplicate" in combined
                or "already subscribed" in combined
                or "already exists" in combined
                or "ineligible" in combined
                or ("cannot subscribe" in combined)
                or ("subscribe to yourself" in combined)
            ):
                return "duplicate_or_ineligible_target"
            if status_code == 404 and ("channel" in combined or "subscription" in combined or "target" in combined):
                return "not_found"
            return None
        if execution.metadata.operation_key == "subscriptions.delete":
            if status_code in {400, 422} or "invalid" in combined or "required" in combined:
                return "invalid_request"
            if status_code == 404 and ("subscription" in combined or "target" in combined):
                return "not_found"
            return None
        if execution.metadata.operation_key == "videos.rate":
            if status_code in {400, 422} or "invalid" in combined or "required" in combined:
                return "invalid_request"
            if status_code == 404 and ("video" in combined or "target" in combined):
                return "not_found"
            if (
                status_code == 403
                and (
                    "disabled rating" in combined
                    or "ratings disabled" in combined
                    or "not allowed to rate" in combined
                    or "forbidden" in combined
                    or "policy" in combined
                )
            ):
                return "policy_restricted"
            return None
        if execution.metadata.operation_key == "videos.getRating":
            if status_code in {400, 422} or "invalid" in combined or "required" in combined:
                return "invalid_request"
            if status_code == 404 and ("video" in combined or "target" in combined):
                return "not_found"
            if status_code in {500, 502, 503, 504} or "tempor" in combined or "unavailable" in combined:
                return "upstream_unavailable"
            return None
        if execution.metadata.operation_key == "videos.reportAbuse":
            if "rate" in combined and ("limit" in combined or "exceeded" in combined or "quota" in combined):
                return "rate_limited"
            if status_code == 404 and ("video" in combined or "target" in combined):
                return "not_found"
            if status_code in {500, 502, 503, 504} or "tempor" in combined or "unavailable" in combined:
                return "upstream_unavailable"
            if status_code in {400, 422} or "invalid" in combined or "required" in combined:
                return "invalid_request"
            if status_code == 403 or "forbidden" in combined or "permission" in combined:
                return "auth"
            return None
        if execution.metadata.operation_key == "videos.delete":
            if status_code in {400, 422} or "invalid" in combined or "required" in combined:
                return "invalid_request"
            if status_code == 404 and ("video" in combined or "target" in combined):
                return "not_found"
            if status_code in {500, 502, 503, 504} or "tempor" in combined or "unavailable" in combined:
                return "upstream_unavailable"
            if status_code == 403 or "forbidden" in combined or "permission" in combined:
                return "forbidden"
            return None
        if execution.metadata.operation_key == "search.list":
            if status_code in {400, 422} or "invalid" in combined or "required" in combined:
                return "invalid_request"
            return None
        if execution.metadata.operation_key == "playlistItems.insert":
            if status_code in {400, 422} or "invalid" in combined or "required" in combined:
                return "invalid_request"
            if status_code == 404 and (
                "playlist" in combined or "video" in combined or "resource" in combined
            ):
                return "not_found"
            return None
        if execution.metadata.operation_key == "playlists.insert":
            if status_code in {400, 422} or "invalid" in combined or "required" in combined:
                return "invalid_request"
            if status_code == 404 and ("channel" in combined or "playlist" in combined or "target" in combined):
                return "not_found"
            return None
        if execution.metadata.operation_key == "playlists.update":
            if _is_invalid_update_request(status_code=status_code, combined=combined):
                return "invalid_request"
            if _is_missing_update_target(
                status_code=status_code,
                combined=combined,
                target_terms=("playlist", "target"),
            ):
                return "not_found"
            return None
        if execution.metadata.operation_key == "playlists.delete":
            if status_code in {400, 422} or "invalid" in combined or "required" in combined:
                return "invalid_request"
            if status_code == 404 and ("playlist" in combined or "target" in combined):
                return "not_found"
            return None
        if execution.metadata.operation_key == "playlistItems.update":
            if status_code in {400, 422} or "invalid" in combined or "required" in combined:
                return "invalid_request"
            if status_code == 404 and (
                "playlist" in combined or "video" in combined or "resource" in combined or "target" in combined
            ):
                return "not_found"
            return None
        if execution.metadata.operation_key == "playlistItems.delete":
            if status_code in {400, 422} or "invalid" in combined or "required" in combined:
                return "invalid_request"
            if status_code == 404 and ("playlist item" in combined or "playlistitem" in combined or "target" in combined):
                return "not_found"
            return None
        if execution.metadata.operation_key == "playlistImages.insert":
            if status_code in {400, 422} or "invalid" in combined or "required" in combined:
                return "invalid_request"
            return None
        if execution.metadata.operation_key == "thumbnails.set":
            if status_code in {400, 422} or "invalid" in combined or "required" in combined:
                return "invalid_request"
            if status_code == 404 and ("thumbnail" in combined or "video" in combined or "target" in combined):
                return "target_video"
            return None
        if execution.metadata.operation_key == "watermarks.set":
            if status_code in {400, 422} or "invalid" in combined or "required" in combined or "image" in combined:
                return "invalid_request"
            if status_code in {500, 502, 503, 504} or "tempor" in combined or "unavailable" in combined:
                return "upstream_unavailable"
            if status_code == 403 or "forbidden" in combined or "permission" in combined:
                return "forbidden"
            return None
        if execution.metadata.operation_key == "watermarks.unset":
            if status_code in {400, 422} or "invalid" in combined or "required" in combined:
                return "invalid_request"
            if status_code in {500, 502, 503, 504} or "tempor" in combined or "unavailable" in combined:
                return "upstream_unavailable"
            if status_code == 403 or "forbidden" in combined or "permission" in combined:
                return "forbidden"
            if status_code == 404 or "not found" in combined or "already removed" in combined or "no watermark" in combined:
                return "no_removal_possible"
            return None
        if execution.metadata.operation_key == "playlistImages.update":
            if status_code in {400, 422} or "invalid" in combined or "required" in combined:
                return "invalid_request"
            if status_code == 404 and ("playlist image" in combined or "playlistimage" in combined or "target" in combined):
                return "not_found"
            return None
        if execution.metadata.operation_key == "playlistImages.delete":
            if status_code in {400, 422} or "invalid" in combined or "required" in combined:
                return "invalid_request"
            if status_code == 404 and ("playlist image" in combined or "playlistimage" in combined or "target" in combined):
                return "not_found"
            return None
        if execution.metadata.operation_key == "comments.insert":
            if status_code in {400, 422} or "invalid" in combined or "required" in combined:
                return "invalid_request"
            return None
        if execution.metadata.operation_key == "comments.update":
            if status_code in {400, 422} or "invalid" in combined or "required" in combined:
                return "invalid_request"
            return None
        if execution.metadata.operation_key == "comments.setModerationStatus":
            if status_code in {400, 422} or "invalid" in combined or "required" in combined:
                return "invalid_request"
            return None
        if execution.metadata.operation_key == "comments.delete":
            if status_code in {400, 422} or "invalid" in combined or "required" in combined:
                return "invalid_request"
            if status_code == 404 or "not found" in combined or "already removed" in combined:
                return "not_found"
            return None
        if execution.metadata.operation_key == "channelSections.delete":
            if status_code in {400, 422} or "invalid" in combined or "required" in combined:
                return "invalid_request"
            if status_code == 404 or "not found" in combined or "already removed" in combined:
                return "not_found"
            return None
        if status_code in {400, 422} or "read-only" in combined or "readonly" in combined:
            return "invalid_request"
        return None
    message = str(details.get("message", "")).lower()
    reason = str(details.get("reason", "")).lower()
    body = str(details.get("responseBody", "")).lower()
    combined = " ".join(part for part in (message, reason, body) if part)
    if status_code in {400, 422} or "mediabodyrequired" in combined or "invalid image" in combined:
        return "invalid_request"
    if status_code == 404 or "target channel" in combined or "channel banner target" in combined:
        return "target_channel"
    return None


def _is_invalid_update_request(*, status_code: int | None, combined: str) -> bool:
    """Return whether an update-style request failed due to request shape.

    :param status_code: Optional upstream status code.
    :param combined: Lower-cased combined error text.
    :return: ``True`` when the error indicates invalid request input.
    """
    return status_code in {400, 422} or "invalid" in combined or "required" in combined


def _is_missing_update_target(
    *,
    status_code: int | None,
    combined: str,
    target_terms: tuple[str, ...],
) -> bool:
    """Return whether an update-style request failed because the target is missing.

    :param status_code: Optional upstream status code.
    :param combined: Lower-cased combined error text.
    :param target_terms: Terms that indicate the upstream target identity.
    :return: ``True`` when the target is missing.
    """
    return status_code == 404 and any(term in combined for term in target_terms)
