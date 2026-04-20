"""Concrete YouTube Data API transport helpers for Layer 1 wrappers."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping, Sequence
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from mcp_server.integrations.executor import IntegrationExecutor, IntegrationHooks, RequestExecution
from mcp_server.integrations.retry import RetryPolicy

YOUTUBE_DATA_API_ORIGIN = "https://www.googleapis.com"


def build_youtube_data_api_transport(
    *,
    opener: Callable[..., Any] | None = None,
    timeout_seconds: float = 10.0,
) -> Callable[[RequestExecution], dict[str, Any]]:
    """Build a transport callable that executes Layer 1 requests against YouTube.

    :param opener: Optional request opener compatible with ``urllib.request.urlopen``.
    :param timeout_seconds: Timeout used for upstream requests.
    :return: Transport callable suitable for ``IntegrationExecutor``.
    """
    request_opener = opener or urlopen

    def transport(execution: RequestExecution) -> dict[str, Any]:
        """Execute one YouTube Data API request for the given execution context.

        :param execution: Shared request execution details.
        :return: Parsed JSON response from the upstream API.
        """
        request = build_youtube_data_api_request(execution)
        try:
            with request_opener(request, timeout=timeout_seconds) as response:
                payload = response.read().decode("utf-8")
        except HTTPError as error:
            details = _error_details(error)
            raise _normalized_upstream_failure(
                details["message"],
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

        if execution.metadata.operation_key == "captions.download":
            return _download_payload(execution, payload)
        if execution.metadata.operation_key == "captions.delete":
            return _delete_payload(execution)
        if execution.metadata.operation_key == "channelSections.delete":
            return _channel_sections_delete_payload(execution)
        if execution.metadata.operation_key == "channelBanners.insert":
            return _channel_banners_insert_payload(execution, payload)
        if execution.metadata.operation_key == "channelSections.list":
            return _channel_sections_list_payload(payload)
        if execution.metadata.operation_key == "comments.list":
            return _comments_list_payload(payload)
        if execution.metadata.operation_key == "commentThreads.list":
            return _comment_threads_list_payload(payload)
        if execution.metadata.operation_key == "commentThreads.insert":
            return _comment_threads_insert_payload(execution, payload)
        if execution.metadata.operation_key == "comments.insert":
            return _comments_insert_payload(execution, payload)
        if execution.metadata.operation_key == "comments.update":
            return _comments_update_payload(execution, payload)
        if execution.metadata.operation_key == "comments.setModerationStatus":
            return _comments_set_moderation_status_payload(execution)
        if execution.metadata.operation_key == "comments.delete":
            return _comments_delete_payload(execution)
        if execution.metadata.operation_key == "channelSections.insert":
            return _channel_sections_insert_payload(execution, payload)
        if execution.metadata.operation_key == "channelSections.update":
            return _channel_sections_update_payload(execution, payload)
        if execution.metadata.operation_key == "channels.update":
            return _channels_update_payload(payload)

        parsed = json.loads(payload)
        if not isinstance(parsed, dict):
            raise ValueError("YouTube Data API responses must decode to an object")
        return parsed

    return transport


def build_youtube_data_api_executor(
    *,
    opener: Callable[..., Any] | None = None,
    timeout_seconds: float = 10.0,
    retry_policy: RetryPolicy | None = None,
    hooks: IntegrationHooks | None = None,
) -> IntegrationExecutor:
    """Build an executor wired to the concrete YouTube Data API transport.

    :param opener: Optional request opener compatible with ``urllib.request.urlopen``.
    :param timeout_seconds: Timeout used for upstream requests.
    :param retry_policy: Optional retry policy override.
    :param hooks: Optional request lifecycle hooks.
    :return: Shared executor configured for live YouTube requests.
    """
    return IntegrationExecutor(
        transport=build_youtube_data_api_transport(opener=opener, timeout_seconds=timeout_seconds),
        retry_policy=retry_policy or RetryPolicy(max_attempts=3),
        hooks=hooks,
    )


def build_youtube_data_api_request(execution: RequestExecution) -> Request:
    """Build one concrete HTTP request for a YouTube Data API execution.

    :param execution: Shared request execution details.
    :return: Configured HTTP request object.
    """
    resolved_path = _resolved_path_shape(execution.metadata.path_shape, execution.arguments)
    query_arguments = _query_arguments(
        execution.metadata.http_method,
        execution.metadata.path_shape,
        execution.arguments,
    )
    query = _query_parameters(query_arguments, execution.credentials)
    query_string = urlencode(query, doseq=True)
    url = f"{YOUTUBE_DATA_API_ORIGIN}{resolved_path}"
    if query_string:
        url = f"{url}?{query_string}"
    headers = {"Accept": "application/json"}
    request_data = _request_data(execution.metadata.http_method, execution.arguments)
    oauth_token = execution.credentials.get("oauthToken")
    if oauth_token:
        headers["Authorization"] = f"Bearer {oauth_token}"
    if request_data is not None:
        headers["Content-Type"] = _request_content_type(execution.arguments)
    return Request(url, data=request_data, method=execution.metadata.http_method.upper(), headers=headers)


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
        if key not in {"body", "media"} and key not in path_fields
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


def _request_data(http_method: str, arguments: Mapping[str, object]) -> bytes | None:
    """Return encoded request data for caption write operations.

    :param http_method: Upstream HTTP method for the request.
    :param arguments: Wrapper arguments selected for the execution.
    :return: Encoded request payload when the method carries a body.
    """
    if http_method.upper() not in {"POST", "PUT", "PATCH"}:
        return None
    body = arguments.get("body")
    media = arguments.get("media")
    if isinstance(body, dict) and isinstance(media, dict):
        return _multipart_related_payload(body=body, media=media)
    if isinstance(media, dict):
        return _media_content_bytes(media.get("content"))
    if isinstance(body, dict):
        return json.dumps(body).encode("utf-8")
    return None


def _request_content_type(arguments: Mapping[str, object]) -> str:
    """Return the content type for the outgoing request body.

    :param arguments: Wrapper arguments selected for the execution.
    :return: Content type header value.
    """
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
        f"--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n".encode("utf-8"),
        metadata,
        b"\r\n",
        f"--{boundary}\r\nContent-Type: {mime_type}\r\n\r\n".encode("utf-8"),
        media_bytes,
        b"\r\n",
        f"--{boundary}--\r\n".encode("utf-8"),
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


def _error_details(error: HTTPError) -> dict[str, object]:
    """Extract safe error details from an upstream HTTP failure.

    :param error: HTTP error returned by the upstream request.
    :return: Sanitized error details for normalization.
    """
    body = ""
    try:
        body = error.read().decode("utf-8", errors="replace")
    except Exception:  # pragma: no cover - best effort only
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


def _download_payload(execution: RequestExecution, payload: str) -> dict[str, Any]:
    """Return the internal result shape for a `captions.download` response.

    :param execution: Shared request execution details.
    :param payload: Raw caption body returned by the upstream response.
    :return: Lightweight download result with stable metadata fields.
    """
    return {
        "captionId": _stringify_scalar(execution.arguments.get("id")),
        "content": payload,
        "contentFormat": execution.arguments.get("tfmt"),
        "contentLanguage": execution.arguments.get("tlang"),
        "delegatedOwner": execution.arguments.get("onBehalfOfContentOwner"),
    }


def _delete_payload(execution: RequestExecution) -> dict[str, Any]:
    """Return the internal result shape for a `captions.delete` response.

    :param execution: Shared request execution details.
    :return: Lightweight delete result with stable metadata fields.
    """
    return {
        "captionId": _stringify_scalar(execution.arguments.get("id")),
        "isDeleted": True,
        "delegatedOwner": execution.arguments.get("onBehalfOfContentOwner"),
    }


def _channel_sections_delete_payload(execution: RequestExecution) -> dict[str, Any]:
    """Return the internal result shape for a `channelSections.delete` response.

    :param execution: Shared request execution details.
    :return: Lightweight delete result with stable metadata fields.
    """
    return {
        "channelSectionId": _stringify_scalar(execution.arguments.get("id")),
        "isDeleted": True,
        "delegatedOwner": execution.arguments.get("onBehalfOfContentOwner"),
        "delegatedOwnerChannel": execution.arguments.get("onBehalfOfContentOwnerChannel"),
    }


def _channel_banners_insert_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `channelBanners.insert` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Lightweight banner-upload result with stable metadata fields.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    return {
        "bannerUrl": parsed.get("url"),
        "isUploaded": bool(parsed.get("url")),
        "delegatedOwner": execution.arguments.get("onBehalfOfContentOwner"),
    }


def _channel_sections_list_payload(payload: str) -> dict[str, Any]:
    """Return the internal result shape for a `channelSections.list` response.

    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed channel-sections list payload for retrieval consumers.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    return parsed


def _comments_list_payload(payload: str) -> dict[str, Any]:
    """Return the internal result shape for a `comments.list` response.

    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed comments list payload for retrieval consumers.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    return parsed


def _comment_threads_list_payload(payload: str) -> dict[str, Any]:
    """Return the internal result shape for a `commentThreads.list` response.

    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed comment-threads list payload for retrieval consumers.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    return parsed


def _comments_insert_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `comments.insert` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed comment create payload with stable metadata fields.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    parsed["delegatedOwner"] = execution.arguments.get("onBehalfOfContentOwner")
    return parsed


def _comment_threads_insert_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `commentThreads.insert` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed comment-thread create payload with stable metadata fields.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    parsed["delegatedOwner"] = execution.arguments.get("onBehalfOfContentOwner")
    return parsed


def _comments_update_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `comments.update` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed comment update payload with stable metadata fields.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    parsed["delegatedOwner"] = execution.arguments.get("onBehalfOfContentOwner")
    return parsed


def _comments_set_moderation_status_payload(
    execution: RequestExecution,
) -> dict[str, Any]:
    """Return the internal result shape for a moderation-status response.

    :param execution: Shared request execution details.
    :return: Lightweight moderation acknowledgment with stable metadata fields.
    """
    raw_ids = execution.arguments.get("id")
    if isinstance(raw_ids, str):
        comment_ids = (raw_ids,)
    elif isinstance(raw_ids, (list, tuple)):
        comment_ids = tuple(str(value) for value in raw_ids)
    else:
        comment_ids = ()
    return {
        "commentIds": comment_ids,
        "isModerated": True,
        "moderationStatus": execution.arguments.get("moderationStatus"),
        "authorBanApplied": bool(execution.arguments.get("banAuthor")),
        "delegatedOwner": execution.arguments.get("onBehalfOfContentOwner"),
        "upstreamBodyState": "empty",
    }


def _comments_delete_payload(execution: RequestExecution) -> dict[str, Any]:
    """Return the internal result shape for a `comments.delete` response.

    :param execution: Shared request execution details.
    :return: Lightweight delete result with stable metadata fields.
    """
    return {
        "commentId": _stringify_scalar(execution.arguments.get("id")),
        "isDeleted": True,
        "delegatedOwner": execution.arguments.get("onBehalfOfContentOwner"),
        "upstreamBodyState": "empty",
    }


def _channel_sections_insert_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `channelSections.insert` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed channel-section create payload with stable metadata fields.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    parsed["delegatedOwner"] = execution.arguments.get("onBehalfOfContentOwner")
    parsed["delegatedOwnerChannel"] = execution.arguments.get("onBehalfOfContentOwnerChannel")
    return parsed


def _channel_sections_update_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `channelSections.update` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed channel-section update payload with stable metadata fields.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    parsed["delegatedOwner"] = execution.arguments.get("onBehalfOfContentOwner")
    parsed["delegatedOwnerChannel"] = execution.arguments.get("onBehalfOfContentOwnerChannel")
    return parsed


def _channels_update_payload(payload: str) -> dict[str, Any]:
    """Return the internal result shape for a `channels.update` response.

    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed channel-resource payload for update consumers.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    return parsed
