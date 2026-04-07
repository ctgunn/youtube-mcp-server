"""Concrete YouTube Data API transport helpers for Layer 1 wrappers."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping, Sequence
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
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
            raise _normalized_upstream_failure(details["message"], status_code=error.code, details=details)
        except URLError as error:
            raise _normalized_upstream_failure(str(error.reason), details={"reason": str(error.reason)})
        except TimeoutError as error:
            raise _normalized_upstream_failure(str(error), status_code=504, details={"reason": "timeout"})

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
    query_arguments = _query_arguments(execution.metadata.http_method, execution.arguments)
    query = _query_parameters(query_arguments, execution.credentials)
    url = f"{YOUTUBE_DATA_API_ORIGIN}{execution.metadata.path_shape}?{urlencode(query, doseq=True)}"
    headers = {"Accept": "application/json"}
    request_data = _request_data(execution.metadata.http_method, execution.arguments)
    oauth_token = execution.credentials.get("oauthToken")
    if oauth_token:
        headers["Authorization"] = f"Bearer {oauth_token}"
    if request_data is not None:
        headers["Content-Type"] = _request_content_type(execution.arguments)
    return Request(url, data=request_data, method=execution.metadata.http_method.upper(), headers=headers)


def _query_arguments(http_method: str, arguments: Mapping[str, object]) -> Mapping[str, object]:
    """Return the argument subset that should remain in the query string.

    :param http_method: Upstream HTTP method for the request.
    :param arguments: Wrapper arguments selected for the execution.
    :return: Arguments that belong in the request URL.
    """
    if http_method.upper() not in {"POST", "PUT", "PATCH"}:
        return arguments
    return {key: value for key, value in arguments.items() if key not in {"body", "media"}}


def _request_data(http_method: str, arguments: Mapping[str, object]) -> bytes | None:
    """Return encoded request data for upload-sensitive operations.

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
    if isinstance(body, dict):
        return json.dumps(body).encode("utf-8")
    return None


def _request_content_type(arguments: Mapping[str, object]) -> str:
    """Return the content type for the outgoing request body.

    :param arguments: Wrapper arguments selected for the execution.
    :return: Content type header value.
    """
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
        status_code=status_code,
        details=details,
    )
