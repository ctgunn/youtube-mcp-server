# ruff: noqa: F401,F403,F405
"""Shared foundations for Layer 1 resource-family wrappers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from mcp_server.integrations.auth import AuthContext, AuthMode
from mcp_server.integrations.contracts import (
    EndpointMetadata,
    EndpointRequestShape,
    require_mapping_fields,
    require_optional_mapping_fields,
)
from mcp_server.integrations.executor import IntegrationExecutor, RequestExecution
from mcp_server.integrations.resources.constants import *
from mcp_server.integrations.resources.validators import *

@dataclass(frozen=True)
class RepresentativeEndpointWrapper:
    """Represent one metadata-driven Layer 1 wrapper.

    :param metadata: Declared wrapper metadata and request shape.
    :ivar metadata: Includes upstream identity, quota cost, auth mode, and review notes.
    """

    metadata: EndpointMetadata

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute the representative wrapper through the shared executor.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        """
        self.metadata.request_shape.validate_arguments(arguments)
        execution = RequestExecution(
            metadata=self.metadata,
            arguments=arguments,
            auth_context=auth_context,
        )
        return executor.execute(execution)

    def review_surface(self) -> dict[str, object]:
        """Return the maintainer-facing metadata surface for this wrapper.

        The returned payload keeps endpoint identity, quota cost, auth mode,
        and lifecycle caveats visible near the wrapper definition.

        :return: Reviewable metadata derived from the wrapper contract.
        """
        return self.metadata.review_surface()

__all__ = [
    "Any",
    "AuthContext",
    "AuthMode",
    "EndpointMetadata",
    "EndpointRequestShape",
    "IntegrationExecutor",
    "RepresentativeEndpointWrapper",
    "RequestExecution",
    "_CHANNELS_UPDATE_SUPPORTED_PARTS",
    "_CHANNEL_BANNER_ALLOWED_MIME_TYPES",
    "_CHANNEL_BANNER_MAX_BYTES",
    "_CHANNEL_SECTIONS_CHANNEL_TYPES",
    "_CHANNEL_SECTIONS_PLAYLIST_TYPES",
    "_CHANNEL_SECTIONS_TITLE_REQUIRED_TYPES",
    "_SEARCH_RESTRICTED_FIELDS",
    "_SEARCH_VIDEO_ONLY_FIELDS",
    "_VIDEOS_INSERT_UPLOAD_MODES",
    "_VIDEOS_REPORT_ABUSE_BODY_FIELDS",
    "_WATERMARK_ALLOWED_MIME_TYPES",
    "_WATERMARK_MAX_BYTES",
    "_channels_update_parts",
    "_require_channel_banner_media",
    "_require_channel_sections_insert_body",
    "_require_channel_sections_update_body",
    "_require_channels_update_body",
    "_require_comment_threads_insert_body",
    "_require_comments_delete_arguments",
    "_require_comments_insert_body",
    "_require_comments_set_moderation_status_arguments",
    "_require_comments_update_body",
    "_require_playlist_images_delete_arguments",
    "_require_playlist_images_list_arguments",
    "_require_playlist_images_update_body",
    "_require_playlist_items_delete_arguments",
    "_require_playlist_items_insert_body",
    "_require_playlist_items_list_arguments",
    "_require_playlist_items_update_body",
    "_require_playlists_delete_arguments",
    "_require_playlists_insert_body",
    "_require_playlists_list_arguments",
    "_require_playlists_update_body",
    "_require_search_list_arguments",
    "_require_subscriptions_delete_arguments",
    "_require_subscriptions_insert_body",
    "_require_subscriptions_list_arguments",
    "_require_thumbnails_set_arguments",
    "_require_videos_delete_arguments",
    "_require_videos_get_rating_arguments",
    "_require_videos_insert_arguments",
    "_require_videos_list_arguments",
    "_require_videos_rate_arguments",
    "_require_videos_report_abuse_arguments",
    "_require_videos_update_body",
    "_require_watermarks_set_arguments",
    "_require_watermarks_unset_arguments",
    "_subscriptions_insert_target_channel_id",
    "_subscriptions_insert_target_resource_kind",
    "_validate_channel_sections_body",
    "_validated_comment_ids",
    "_validated_reference_values",
    "_validated_videos_get_rating_ids",
    "dataclass",
    "require_mapping_fields",
    "require_optional_mapping_fields",
]
