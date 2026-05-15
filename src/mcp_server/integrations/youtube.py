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
        if execution.metadata.operation_key == "thumbnails.set":
            return _thumbnails_set_payload(execution, payload)
        if execution.metadata.operation_key == "videos.insert":
            return _videos_insert_payload(execution, payload)
        if execution.metadata.operation_key == "playlistImages.insert":
            return _playlist_images_insert_payload(execution, payload)
        if execution.metadata.operation_key == "playlistItems.insert":
            return _playlist_items_insert_payload(execution, payload)
        if execution.metadata.operation_key == "playlists.insert":
            return _playlists_insert_payload(execution, payload)
        if execution.metadata.operation_key == "subscriptions.insert":
            return _subscriptions_insert_payload(execution, payload)
        if execution.metadata.operation_key == "subscriptions.delete":
            return _subscriptions_delete_payload(execution)
        if execution.metadata.operation_key == "videos.rate":
            return _videos_rate_payload(execution, payload)
        if execution.metadata.operation_key == "videos.getRating":
            return _videos_get_rating_payload(execution, payload)
        if execution.metadata.operation_key == "videos.reportAbuse":
            return _videos_report_abuse_payload(execution, payload)
        if execution.metadata.operation_key == "videos.update":
            return _videos_update_payload(execution, payload)
        if execution.metadata.operation_key == "playlists.update":
            return _playlists_update_payload(execution, payload)
        if execution.metadata.operation_key == "playlists.delete":
            return _playlists_delete_payload(execution)
        if execution.metadata.operation_key == "playlistItems.update":
            return _playlist_items_update_payload(execution, payload)
        if execution.metadata.operation_key == "playlistItems.delete":
            return _playlist_items_delete_payload(execution)
        if execution.metadata.operation_key == "playlistImages.update":
            return _playlist_images_update_payload(execution, payload)
        if execution.metadata.operation_key == "playlistImages.delete":
            return _playlist_images_delete_payload(execution)
        if execution.metadata.operation_key == "channelSections.list":
            return _channel_sections_list_payload(payload)
        if execution.metadata.operation_key == "comments.list":
            return _comments_list_payload(payload)
        if execution.metadata.operation_key == "commentThreads.list":
            return _comment_threads_list_payload(payload)
        if execution.metadata.operation_key == "guideCategories.list":
            return _guide_categories_list_payload(payload)
        if execution.metadata.operation_key == "i18nLanguages.list":
            return _i18n_languages_list_payload(payload)
        if execution.metadata.operation_key == "i18nRegions.list":
            return _i18n_regions_list_payload(payload)
        if execution.metadata.operation_key == "videoAbuseReportReasons.list":
            return _video_abuse_report_reasons_list_payload(payload)
        if execution.metadata.operation_key == "videoCategories.list":
            return _video_categories_list_payload(execution, payload)
        if execution.metadata.operation_key == "videos.list":
            return _videos_list_payload(execution, payload)
        if execution.metadata.operation_key == "members.list":
            return _members_list_payload(payload)
        if execution.metadata.operation_key == "membershipsLevels.list":
            return _memberships_levels_list_payload(payload)
        if execution.metadata.operation_key == "playlistImages.list":
            return _playlist_images_list_payload(execution, payload)
        if execution.metadata.operation_key == "playlistItems.list":
            return _playlist_items_list_payload(execution, payload)
        if execution.metadata.operation_key == "playlists.list":
            return _playlists_list_payload(execution, payload)
        if execution.metadata.operation_key == "subscriptions.list":
            return _subscriptions_list_payload(execution, payload)
        if execution.metadata.operation_key == "search.list":
            return _search_list_payload(execution, payload)
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
            "guideCategories.list",
            "i18nLanguages.list",
            "i18nRegions.list",
            "videoAbuseReportReasons.list",
            "videoCategories.list",
            "videos.list",
            "videos.insert",
            "videos.getRating",
            "videos.reportAbuse",
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


def _thumbnails_set_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `thumbnails.set` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed thumbnail-update payload with stable metadata fields.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    parsed["videoId"] = parsed.get("videoId") or execution.arguments.get("videoId")
    parsed["thumbnailUrl"] = parsed.get("thumbnailUrl") or parsed.get("url")
    parsed["isUpdated"] = bool(parsed.get("videoId"))
    return parsed


def _playlist_images_insert_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `playlistImages.insert` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed playlist-image create payload with stable metadata fields.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    body = execution.arguments.get("body")
    snippet = body.get("snippet", {}) if isinstance(body, dict) else {}
    parsed["part"] = execution.arguments.get("part")
    parsed["playlistId"] = parsed.get("playlistId") or snippet.get("playlistId")
    return parsed


def _playlist_images_update_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `playlistImages.update` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed playlist-image update payload with stable metadata fields.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    body = execution.arguments.get("body")
    snippet = body.get("snippet", {}) if isinstance(body, dict) else {}
    parsed["part"] = execution.arguments.get("part")
    parsed["playlistId"] = parsed.get("playlistId") or snippet.get("playlistId")
    return parsed


def _playlist_items_insert_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `playlistItems.insert` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed playlist-item create payload with stable metadata fields.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    body = execution.arguments.get("body")
    snippet = body.get("snippet", {}) if isinstance(body, dict) else {}
    resource_id = snippet.get("resourceId", {}) if isinstance(snippet, dict) else {}
    parsed_snippet = parsed.get("snippet", {}) if isinstance(parsed.get("snippet"), dict) else {}
    parsed_resource_id = (
        parsed_snippet.get("resourceId", {}) if isinstance(parsed_snippet.get("resourceId"), dict) else {}
    )
    parsed["part"] = execution.arguments.get("part")
    parsed["playlistId"] = parsed.get("playlistId") or parsed_snippet.get("playlistId") or snippet.get("playlistId")
    parsed["videoId"] = (
        parsed.get("videoId")
        or parsed_resource_id.get("videoId")
        or resource_id.get("videoId")
    )
    return parsed


def _playlists_insert_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `playlists.insert` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed playlist create payload with stable metadata fields.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    body = execution.arguments.get("body")
    snippet = body.get("snippet", {}) if isinstance(body, dict) else {}
    parsed_snippet = parsed.get("snippet", {}) if isinstance(parsed.get("snippet"), dict) else {}
    parsed["part"] = execution.arguments.get("part")
    parsed["title"] = parsed.get("title") or parsed_snippet.get("title") or snippet.get("title")
    return parsed


def _subscriptions_insert_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `subscriptions.insert` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed subscription create payload with stable metadata fields.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    body = execution.arguments.get("body")
    snippet = body.get("snippet", {}) if isinstance(body, dict) else {}
    resource_id = snippet.get("resourceId", {}) if isinstance(snippet, dict) else {}
    parsed_snippet = parsed.get("snippet", {}) if isinstance(parsed.get("snippet"), dict) else {}
    parsed_resource_id = (
        parsed_snippet.get("resourceId", {}) if isinstance(parsed_snippet.get("resourceId"), dict) else {}
    )
    parsed["part"] = execution.arguments.get("part")
    parsed["subscriptionId"] = parsed.get("subscriptionId") or parsed.get("id")
    parsed["targetChannelId"] = (
        parsed.get("targetChannelId")
        or parsed_resource_id.get("channelId")
        or resource_id.get("channelId")
    )
    parsed["targetResourceKind"] = (
        parsed.get("targetResourceKind")
        or parsed_resource_id.get("kind")
        or resource_id.get("kind")
        or "youtube#channel"
    )
    return parsed


def _subscriptions_delete_payload(execution: RequestExecution) -> dict[str, Any]:
    """Return the internal result shape for a `subscriptions.delete` response.

    :param execution: Shared request execution details.
    :return: Lightweight delete result with stable metadata fields.
    """
    return {
        "subscriptionId": _stringify_scalar(execution.arguments.get("id")),
        "isDeleted": True,
        "upstreamBodyState": "empty",
    }


def _playlist_items_update_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `playlistItems.update` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed playlist-item update payload with stable metadata fields.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    body = execution.arguments.get("body")
    snippet = body.get("snippet", {}) if isinstance(body, dict) else {}
    resource_id = snippet.get("resourceId", {}) if isinstance(snippet, dict) else {}
    parsed_snippet = parsed.get("snippet", {}) if isinstance(parsed.get("snippet"), dict) else {}
    parsed_resource_id = (
        parsed_snippet.get("resourceId", {}) if isinstance(parsed_snippet.get("resourceId"), dict) else {}
    )
    parsed["part"] = execution.arguments.get("part")
    parsed["playlistItemId"] = parsed.get("playlistItemId") or parsed.get("id") or (body.get("id") if isinstance(body, dict) else None)
    parsed["playlistId"] = parsed.get("playlistId") or parsed_snippet.get("playlistId") or snippet.get("playlistId")
    parsed["videoId"] = (
        parsed.get("videoId")
        or parsed_resource_id.get("videoId")
        or resource_id.get("videoId")
    )
    return parsed


def _playlists_update_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `playlists.update` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed playlist update payload with stable metadata fields.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    return _update_payload_with_request_fallbacks(execution, payload)


def _videos_update_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `videos.update` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed video update payload with stable metadata fields.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    return _update_payload_with_request_fallbacks(execution, payload)


def _videos_rate_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `videos.rate` response.

    :param execution: Shared request execution details.
    :param payload: Raw payload returned by the upstream response, if any.
    :return: Lightweight rating acknowledgement with stable metadata fields.
    :raises ValueError: If a non-empty upstream response is not a JSON object.
    """
    parsed: dict[str, Any] = {}
    if payload.strip():
        loaded = json.loads(payload)
        if not isinstance(loaded, dict):
            raise ValueError("YouTube Data API responses must decode to an object")
        parsed = loaded

    requested_rating = _stringify_scalar(execution.arguments.get("rating"))
    video_id = _stringify_scalar(execution.arguments.get("id"))
    parsed["videoId"] = parsed.get("videoId") or video_id
    parsed["requestedRating"] = parsed.get("requestedRating") or requested_rating
    parsed["isRated"] = parsed.get("isRated") if "isRated" in parsed else requested_rating != "none"
    parsed["isCleared"] = parsed.get("isCleared") if "isCleared" in parsed else requested_rating == "none"
    parsed["ratingState"] = parsed.get("ratingState") or ("cleared" if requested_rating == "none" else "applied")
    parsed["upstreamBodyState"] = parsed.get("upstreamBodyState") or ("json" if payload.strip() else "empty")
    return parsed


def _videos_get_rating_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `videos.getRating` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed rating lookup payload with stable per-video result fields.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")

    requested_id = _stringify_scalar(execution.arguments.get("id"))
    requested_video_ids = _split_comma_delimited_ids(requested_id)
    items = parsed.get("items")
    normalized_items: list[dict[str, Any]] = []
    if isinstance(items, list):
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                continue
            fallback_video_id = requested_video_ids[index] if index < len(requested_video_ids) else None
            video_id = _stringify_scalar(item.get("videoId")) or fallback_video_id
            rating = _normalized_video_rating_state(item.get("rating"))
            is_unrated = rating == "none"
            normalized_items.append(
                {
                    "videoId": video_id,
                    "rating": rating,
                    "isRated": not is_unrated,
                    "isUnrated": is_unrated,
                }
            )

    parsed["requestedId"] = requested_id
    parsed["authPath"] = "oauth_required"
    parsed["videoRatings"] = normalized_items
    parsed["ratingStateSummary"] = _videos_get_rating_summary(normalized_items)
    return parsed


def _videos_report_abuse_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `videos.reportAbuse` response.

    :param execution: Shared request execution details.
    :param payload: Raw payload returned by the upstream response, if any.
    :return: Lightweight report acknowledgement with stable metadata fields.
    :raises ValueError: If a non-empty upstream response is not a JSON object.
    """
    parsed: dict[str, Any] = {}
    if payload.strip():
        loaded = json.loads(payload)
        if not isinstance(loaded, dict):
            raise ValueError("YouTube Data API responses must decode to an object")
        parsed = loaded

    body = execution.arguments.get("body")
    report_body = body if isinstance(body, dict) else {}
    parsed["isAccepted"] = parsed.get("isAccepted", True)
    parsed["reportedVideoId"] = parsed.get("reportedVideoId") or _stringify_scalar(report_body.get("videoId"))
    parsed["reasonId"] = parsed.get("reasonId") or _stringify_scalar(report_body.get("reasonId"))
    if report_body.get("secondaryReasonId") is not None:
        parsed["secondaryReasonId"] = parsed.get("secondaryReasonId") or _stringify_scalar(
            report_body.get("secondaryReasonId")
        )
    if report_body.get("language") is not None:
        parsed["language"] = parsed.get("language") or _stringify_scalar(report_body.get("language"))
    parsed["hasComments"] = parsed.get("hasComments") if "hasComments" in parsed else bool(report_body.get("comments"))
    parsed["authPath"] = parsed.get("authPath") or "oauth_required"
    parsed["sourceOperation"] = parsed.get("sourceOperation") or execution.metadata.operation_key
    parsed["upstreamBodyState"] = parsed.get("upstreamBodyState") or ("json" if payload.strip() else "empty")
    return parsed


def _update_payload_with_request_fallbacks(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return a parsed update payload with request-derived fallback fields.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed update payload with stable `part`, `id`, and `title` fields.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    body = execution.arguments.get("body")
    snippet = body.get("snippet", {}) if isinstance(body, dict) else {}
    parsed_snippet = parsed.get("snippet", {}) if isinstance(parsed.get("snippet"), dict) else {}
    parsed["part"] = execution.arguments.get("part")
    parsed["id"] = parsed.get("id") or (body.get("id") if isinstance(body, dict) else None)
    parsed["title"] = parsed.get("title") or parsed_snippet.get("title") or snippet.get("title")
    return parsed


def _split_comma_delimited_ids(raw_value: str) -> tuple[str, ...]:
    """Return normalized comma-delimited identifiers from one scalar value.

    :param raw_value: Raw comma-delimited identifier string.
    :return: Ordered identifier values with blanks removed.
    """
    return tuple(part.strip() for part in raw_value.split(",") if part.strip())


def _normalized_video_rating_state(raw_value: object) -> str:
    """Return the stable rating-state label for one upstream lookup entry.

    :param raw_value: Upstream rating value for one video.
    :return: Stable internal rating-state label.
    """
    normalized = _stringify_scalar(raw_value).strip().lower()
    if normalized in {"like", "liked"}:
        return "liked"
    if normalized in {"dislike", "disliked"}:
        return "disliked"
    if normalized in {"none", "unrated", ""}:
        return "none"
    return normalized


def _videos_get_rating_summary(video_ratings: Sequence[Mapping[str, object]]) -> str:
    """Return a stable summary label for normalized rating-state outcomes.

    :param video_ratings: Normalized per-video rating entries.
    :return: Stable summary label for downstream review surfaces.
    """
    if not video_ratings:
        return "empty"

    rated_count = sum(1 for entry in video_ratings if bool(entry.get("isRated")))
    unrated_count = sum(1 for entry in video_ratings if bool(entry.get("isUnrated")))
    if rated_count and unrated_count:
        return "mixed_rated_and_unrated"
    if rated_count:
        return "all_rated"
    return "all_unrated"


def _playlist_images_delete_payload(execution: RequestExecution) -> dict[str, Any]:
    """Return the internal result shape for a `playlistImages.delete` response.

    :param execution: Shared request execution details.
    :return: Lightweight delete result with stable metadata fields.
    """
    return {
        "playlistImageId": _stringify_scalar(execution.arguments.get("id")),
        "isDeleted": True,
        "upstreamBodyState": "empty",
    }


def _playlists_delete_payload(execution: RequestExecution) -> dict[str, Any]:
    """Return the internal result shape for a `playlists.delete` response.

    :param execution: Shared request execution details.
    :return: Lightweight delete result with stable metadata fields.
    """
    return {
        "playlistId": _stringify_scalar(execution.arguments.get("id")),
        "isDeleted": True,
        "upstreamBodyState": "empty",
    }


def _playlist_items_delete_payload(execution: RequestExecution) -> dict[str, Any]:
    """Return the internal result shape for a `playlistItems.delete` response.

    :param execution: Shared request execution details.
    :return: Lightweight delete result with stable metadata fields.
    """
    return {
        "playlistItemId": _stringify_scalar(execution.arguments.get("id")),
        "isDeleted": True,
        "upstreamBodyState": "empty",
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


def _guide_categories_list_payload(payload: str) -> dict[str, Any]:
    """Return the internal result shape for a `guideCategories.list` response.

    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed guide-categories list payload for retrieval consumers.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    return parsed


def _i18n_languages_list_payload(payload: str) -> dict[str, Any]:
    """Return the internal result shape for an `i18nLanguages.list` response.

    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed i18n-languages list payload for retrieval consumers.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    return parsed


def _i18n_regions_list_payload(payload: str) -> dict[str, Any]:
    """Return the internal result shape for an `i18nRegions.list` response.

    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed i18n-regions list payload for retrieval consumers.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    return parsed


def _video_abuse_report_reasons_list_payload(payload: str) -> dict[str, Any]:
    """Return the internal result shape for a `videoAbuseReportReasons.list` response.

    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed video-abuse-report-reasons payload for retrieval consumers.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    return parsed


def _video_categories_list_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `videoCategories.list` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed video-categories payload with stable selector context.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    selector_name = next(
        (
            selector
            for selector in ("id", "regionCode")
            if selector in execution.arguments and execution.arguments.get(selector) not in (None, "")
        ),
        None,
    )
    parsed["selectedSelector"] = selector_name
    if selector_name == "id":
        parsed["id"] = execution.arguments.get("id")
    if selector_name == "regionCode":
        parsed["regionCode"] = execution.arguments.get("regionCode")
    if execution.arguments.get("hl") not in (None, ""):
        parsed["hl"] = execution.arguments.get("hl")
    return parsed


def _videos_list_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `videos.list` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed videos payload with stable selector and auth context.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    selector_name = next(
        (
            selector
            for selector in ("id", "chart", "myRating")
            if selector in execution.arguments and execution.arguments.get(selector) not in (None, "")
        ),
        None,
    )
    parsed["part"] = execution.arguments.get("part")
    parsed["selectedSelector"] = selector_name
    parsed["authPath"] = "oauth_required" if selector_name == "myRating" else "api_key"
    if selector_name:
        parsed[selector_name] = execution.arguments.get(selector_name)
    for field in ("regionCode", "videoCategoryId", "pageToken", "maxResults"):
        if execution.arguments.get(field) not in (None, ""):
            parsed[field] = execution.arguments.get(field)
    return parsed


def _videos_insert_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `videos.insert` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed video-create payload with stable metadata fields.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    body = execution.arguments.get("body")
    snippet = body.get("snippet", {}) if isinstance(body, dict) else {}
    status = body.get("status", {}) if isinstance(body, dict) else {}
    parsed_status = parsed.get("status", {}) if isinstance(parsed.get("status"), dict) else {}
    parsed["part"] = execution.arguments.get("part")
    parsed["uploadMode"] = execution.arguments.get("uploadMode") or "multipart"
    parsed["authPath"] = "oauth_required"
    parsed["title"] = parsed.get("title") or snippet.get("title")
    parsed["privacyStatus"] = parsed.get("privacyStatus") or parsed_status.get("privacyStatus") or status.get(
        "privacyStatus"
    )
    parsed["visibilityCaveat"] = (
        "audit/private-default caveat applies until the caller completes the required review flow"
    )
    return parsed


def _members_list_payload(payload: str) -> dict[str, Any]:
    """Return the internal result shape for a `members.list` response.

    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed members list payload for retrieval consumers.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    return parsed


def _memberships_levels_list_payload(payload: str) -> dict[str, Any]:
    """Return the internal result shape for a `membershipsLevels.list` response.

    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed memberships-levels list payload for retrieval consumers.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    return parsed


def _playlist_images_list_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `playlistImages.list` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed playlist-images list payload with stable selector context.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    selector_name = next(
        (
            selector
            for selector in ("playlistId", "id")
            if selector in execution.arguments and execution.arguments.get(selector) not in (None, "")
        ),
        None,
    )
    parsed["part"] = execution.arguments.get("part")
    parsed["selectorName"] = selector_name
    parsed["selectorValue"] = execution.arguments.get(selector_name) if selector_name else None
    return parsed


def _playlist_items_list_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `playlistItems.list` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed playlist-items list payload with stable selector context.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    selector_name = next(
        (
            selector
            for selector in ("playlistId", "id")
            if selector in execution.arguments and execution.arguments.get(selector) not in (None, "")
        ),
        None,
    )
    parsed["part"] = execution.arguments.get("part")
    parsed["selectorName"] = selector_name
    parsed["selectorValue"] = execution.arguments.get(selector_name) if selector_name else None
    return parsed


def _playlists_list_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `playlists.list` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed playlists list payload with stable selector context.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    selector_name = next(
        (
            selector
            for selector in ("channelId", "id", "mine")
            if selector in execution.arguments and execution.arguments.get(selector) not in (None, "")
        ),
        None,
    )
    parsed["part"] = execution.arguments.get("part")
    parsed["selectorName"] = selector_name
    parsed["selectorValue"] = execution.arguments.get(selector_name) if selector_name else None
    return parsed


def _search_list_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `search.list` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed search payload with stable request context.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    parsed["queryContext"] = {
        key: value
        for key, value in execution.arguments.items()
        if value not in (None, "")
        and key
        in {
            "part",
            "q",
            "type",
            "channelId",
            "publishedAfter",
            "publishedBefore",
            "regionCode",
            "relevanceLanguage",
            "safeSearch",
            "order",
            "pageToken",
            "maxResults",
        }
    }
    parsed["part"] = execution.arguments.get("part")
    parsed["query"] = execution.arguments.get("q")
    parsed["searchType"] = execution.arguments.get("type")
    parsed["authPath"] = (
        "restricted"
        if any(
            execution.arguments.get(field) not in (None, "", False)
            for field in ("forContentOwner", "forDeveloper", "forMine")
        )
        else "public"
    )
    return parsed


def _subscriptions_list_payload(
    execution: RequestExecution,
    payload: str,
) -> dict[str, Any]:
    """Return the internal result shape for a `subscriptions.list` response.

    :param execution: Shared request execution details.
    :param payload: Raw JSON payload returned by the upstream response.
    :return: Parsed subscriptions list payload with stable selector context.
    :raises ValueError: If the upstream response is not a JSON object.
    """
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("YouTube Data API responses must decode to an object")
    selector_name = next(
        (
            selector
            for selector in ("channelId", "id", "mine", "myRecentSubscribers", "mySubscribers")
            if (isinstance(execution.arguments.get(selector), str) and bool(str(execution.arguments.get(selector)).strip()))
            or execution.arguments.get(selector) is True
        ),
        None,
    )
    selector_value = execution.arguments.get(selector_name) if selector_name else None
    parsed["part"] = execution.arguments.get("part")
    parsed["selectorName"] = selector_name
    parsed["selectorValue"] = selector_value
    parsed["authPath"] = (
        "oauth"
        if selector_name in {"mine", "myRecentSubscribers", "mySubscribers"}
        else "public"
    )
    parsed["requestContext"] = {
        key: value
        for key, value in {
            "part": execution.arguments.get("part"),
            "selectorName": selector_name,
            "selectorValue": selector_value,
            "pageToken": execution.arguments.get("pageToken"),
            "maxResults": execution.arguments.get("maxResults"),
            "order": execution.arguments.get("order"),
        }.items()
        if value not in (None, "", False)
    }
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
