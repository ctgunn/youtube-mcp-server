# ruff: noqa: F405
"""Channel Banners resource-family wrappers for Layer 1 YouTube integrations."""

from __future__ import annotations

from mcp_server.integrations.resources.base import *  # noqa: F403

@dataclass(frozen=True)
class ChannelBannersInsertWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `channelBanners.insert`.

    Official quota cost: ``50`` quota units. The wrapper requires one `media`
    upload payload and supports optional `onBehalfOfContentOwner` delegation on
    an authorized request.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `channelBanners.insert` with OAuth and upload validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("channelBanners.insert requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

def build_channel_banners_insert_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `channelBanners.insert`.

    Official quota cost: ``50`` quota units. The wrapper requires one `media`
    upload payload, supports optional `onBehalfOfContentOwner` delegation on
    authorized requests, and keeps image constraints plus the returned response
    URL visible for higher-layer reuse.

    :return: Representative wrapper configured for `channelBanners.insert`.
    """
    metadata = EndpointMetadata(
        resource_name="channelBanners",
        operation_name="insert",
        http_method="POST",
        path_shape="/youtube/v3/channelBanners/insert",
        request_shape=EndpointRequestShape(
            required_fields=("media",),
            optional_fields=("onBehalfOfContentOwner",),
            validators=(
                _require_channel_banner_media,
            ),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=50,
        notes=(
            "Requires oauth_required auth. Use `media` for the banner image "
            "upload payload, keep the documented 16:9 image constraints, 6 MB "
            "size limit, and accepted MIME types visible for review, treat "
            "`onBehalfOfContentOwner` as optional delegation context, and "
            "preserve the returned response URL for later `channels.update` reuse."
        ),
    )
    return ChannelBannersInsertWrapper(metadata=metadata)

FAMILY_NAME = "channel_banners"
RESOURCE_NAMES = ("channelBanners",)
BUILDER_FUNCTIONS = {"channelBanners.insert": build_channel_banners_insert_wrapper}

__all__ = [
    "BUILDER_FUNCTIONS",
    "ChannelBannersInsertWrapper",
    "FAMILY_NAME",
    "RESOURCE_NAMES",
    "build_channel_banners_insert_wrapper",
]
