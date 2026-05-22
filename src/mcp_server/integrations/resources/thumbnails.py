# ruff: noqa: F405
"""Thumbnails resource-family wrappers for Layer 1 YouTube integrations."""

from __future__ import annotations

from mcp_server.integrations.resources.base import *  # noqa: F403

@dataclass(frozen=True)
class ThumbnailsSetWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `thumbnails.set`.

    Official quota cost: ``50`` quota units. The wrapper requires one target
    ``videoId`` plus one ``media`` upload payload on an authorized request.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `thumbnails.set` with OAuth and upload validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("thumbnails.set requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

def build_thumbnails_set_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `thumbnails.set`.

    Official quota cost: ``50`` quota units. The wrapper requires one target
    `videoId` plus one `media` upload payload on authorized requests and keeps
    the upload-sensitive update boundary visible for higher-layer reuse.

    :return: Representative wrapper configured for `thumbnails.set`.
    """
    metadata = EndpointMetadata(
        resource_name="thumbnails",
        operation_name="set",
        http_method="POST",
        path_shape="/youtube/v3/thumbnails/set",
        request_shape=EndpointRequestShape(
            required_fields=("videoId", "media"),
            validators=(
                _require_thumbnails_set_arguments,
            ),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=50,
        notes=(
            "Requires oauth_required auth. Use `videoId` for the single target "
            "video, use `media` for thumbnail upload content, reject upload-only "
            "or target-only request shapes, and keep the update boundary visible "
            "for review."
        ),
    )
    return ThumbnailsSetWrapper(metadata=metadata)

FAMILY_NAME = "thumbnails"
RESOURCE_NAMES = ("thumbnails",)
BUILDER_FUNCTIONS = {"thumbnails.set": build_thumbnails_set_wrapper}

__all__ = ["BUILDER_FUNCTIONS", "FAMILY_NAME", "RESOURCE_NAMES", "ThumbnailsSetWrapper", "build_thumbnails_set_wrapper"]
