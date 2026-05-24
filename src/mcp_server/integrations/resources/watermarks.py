# ruff: noqa: F405
"""Watermarks resource-family wrappers for Layer 1 YouTube integrations."""

from __future__ import annotations

from mcp_server.integrations.resources.base import *  # noqa: F403

@dataclass(frozen=True)
class WatermarksSetWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `watermarks.set`.

    Official quota cost: ``50`` quota units. The wrapper requires one
    ``channelId``, one watermark ``body`` metadata payload, and one ``media``
    upload payload on an authorized request.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `watermarks.set` with OAuth and upload validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("watermarks.set requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

@dataclass(frozen=True)
class WatermarksUnsetWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `watermarks.unset`.

    Official quota cost: ``50`` quota units. The wrapper requires one
    ``channelId`` and rejects watermark metadata or media-upload payloads on an
    authorized removal request.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `watermarks.unset` with OAuth and no-upload validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("watermarks.unset requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

def build_watermarks_set_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `watermarks.set`.

    Official quota cost: ``50`` quota units. The wrapper requires a target
    `channelId`, watermark `body` metadata, and one `media` upload payload on
    authorized requests while keeping the 10 MB media boundary visible.

    :return: Representative wrapper configured for `watermarks.set`.
    """
    metadata = EndpointMetadata(
        resource_name="watermarks",
        operation_name="set",
        http_method="POST",
        path_shape="/upload/youtube/v3/watermarks/set",
        request_shape=EndpointRequestShape(
            required_fields=("channelId", "body", "media"),
            validators=(
                _require_watermarks_set_arguments,
            ),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=50,
        notes=(
            "Requires oauth_required auth. Use `channelId` for the single target "
            "channel, use `body` for watermark timing and position metadata, use "
            "`media` for watermark image upload content, keep the 10 MB limit and "
            "accepted MIME types image/jpeg, image/png, and application/octet-stream "
            "visible for review, reject metadata-only or media-only request shapes, "
            "treat successful 204 responses as watermark-update acknowledgements, "
            "and keep partner-only `onBehalfOfContentOwner` outside this slice unless "
            "a later contract explicitly supports it."
        ),
    )
    return WatermarksSetWrapper(metadata=metadata)

def build_watermarks_unset_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `watermarks.unset`.

    Official quota cost: ``50`` quota units. The wrapper requires a target
    `channelId` on authorized requests, rejects watermark metadata and media
    upload payloads, and keeps no-removal outcomes visible for review.

    :return: Representative wrapper configured for `watermarks.unset`.
    """
    metadata = EndpointMetadata(
        resource_name="watermarks",
        operation_name="unset",
        http_method="POST",
        path_shape="/youtube/v3/watermarks/unset",
        request_shape=EndpointRequestShape(
            required_fields=("channelId",),
            validators=(
                _require_watermarks_unset_arguments,
            ),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=50,
        notes=(
            "Requires oauth_required auth. Use `channelId` for the single target "
            "channel, send no media upload and no `body` watermark metadata for "
            "this unset request, reject upload-oriented, metadata-oriented, or "
            "set-only request shapes, treat successful 204 responses as "
            "watermark-removal acknowledgements, keep no-removal outcomes distinct "
            "from successful removals, and keep partner-only `onBehalfOfContentOwner` "
            "outside this slice unless a later contract explicitly supports it."
        ),
    )
    return WatermarksUnsetWrapper(metadata=metadata)

FAMILY_NAME = "watermarks"
RESOURCE_NAMES = ("watermarks",)
BUILDER_FUNCTIONS = {
    "watermarks.set": build_watermarks_set_wrapper,
    "watermarks.unset": build_watermarks_unset_wrapper,
}
RESPONSE_NORMALIZER_KEYS = ("watermarks.set", "watermarks.unset")

__all__ = [
    "BUILDER_FUNCTIONS",
    "FAMILY_NAME",
    "RESOURCE_NAMES",
    "RESPONSE_NORMALIZER_KEYS",
    "WatermarksSetWrapper",
    "WatermarksUnsetWrapper",
    "build_watermarks_set_wrapper",
    "build_watermarks_unset_wrapper",
]
