# ruff: noqa: F405
"""Captions resource-family wrappers for Layer 1 YouTube integrations."""

from __future__ import annotations

from mcp_server.integrations.resources.base import *  # noqa: F403

@dataclass(frozen=True)
class CaptionsListWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `captions.list`.

    Official quota cost: ``50`` quota units. The wrapper uses ``videoId`` for
    caption inventory lookup and ``id`` for direct caption-track lookup.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `captions.list` with OAuth and delegation validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("captions.list requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

@dataclass(frozen=True)
class CaptionsInsertWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `captions.insert`.

    Official quota cost: ``400`` quota units. The wrapper requires a `body`
    metadata payload plus a `media` upload payload on an authorized request.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `captions.insert` with OAuth and upload validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("captions.insert requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

@dataclass(frozen=True)
class CaptionsUpdateWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `captions.update`.

    Official quota cost: ``450`` quota units. The wrapper requires a `body`
    caption resource payload and supports an optional `media` payload for
    body-plus-media content replacement on an authorized request.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `captions.update` with OAuth and update validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("captions.update requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

@dataclass(frozen=True)
class CaptionsDownloadWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `captions.download`.

    Official quota cost: ``200`` quota units. The wrapper requires a caption
    track ``id`` and supports optional ``tfmt`` and ``tlang`` modifiers plus
    optional `onBehalfOfContentOwner` delegation on an authorized request.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `captions.download` with OAuth and option validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("captions.download requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

@dataclass(frozen=True)
class CaptionsDeleteWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `captions.delete`.

    Official quota cost: ``50`` quota units. The wrapper requires a caption
    track ``id`` and supports optional ``onBehalfOfContentOwner`` delegation on
    an authorized request with ownership-sensitive behavior.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `captions.delete` with OAuth and delegation validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the request requires a different auth mode.
        """
        if not auth_context.requires_oauth_access():
            raise ValueError("captions.delete requires oauth_required auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

def build_captions_list_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `captions.list`.

    Official quota cost: ``50`` quota units. The wrapper supports selector
    paths via ``videoId`` and ``id`` and allows optional
    ``onBehalfOfContentOwner`` delegation on authorized requests.

    :return: Representative wrapper configured for `captions.list`.
    """
    metadata = EndpointMetadata(
        resource_name="captions",
        operation_name="list",
        http_method="GET",
        path_shape="/youtube/v3/captions",
        request_shape=EndpointRequestShape(
            required_fields=("part",),
            optional_fields=("videoId", "id", "onBehalfOfContentOwner", "pageToken", "maxResults"),
            exactly_one_of=("videoId", "id"),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=50,
        notes=(
            "Requires oauth_required auth. Use `videoId` for caption inventory "
            "lookup, use `id` for direct caption-track lookup, and treat "
            "`onBehalfOfContentOwner` as optional delegation context."
        ),
    )
    return CaptionsListWrapper(metadata=metadata)

def build_captions_insert_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `captions.insert`.

    Official quota cost: ``400`` quota units. The wrapper requires a `body`
    metadata payload and a `media` upload payload, allows optional
    `onBehalfOfContentOwner` delegation on authorized requests, and keeps the
    upload-sensitive contract visible for higher-layer reuse.

    :return: Representative wrapper configured for `captions.insert`.
    """
    metadata = EndpointMetadata(
        resource_name="captions",
        operation_name="insert",
        http_method="POST",
        path_shape="/youtube/v3/captions",
        request_shape=EndpointRequestShape(
            required_fields=("part", "body", "media"),
            optional_fields=("onBehalfOfContentOwner", "sync"),
            validators=(
                require_mapping_fields("body", required_keys=("snippet",)),
                require_mapping_fields("media", required_keys=("mimeType", "content")),
            ),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=400,
        notes=(
            "Requires oauth_required auth. Use `body` for caption metadata, "
            "use `media` for caption upload content, and treat "
            "`onBehalfOfContentOwner` as optional delegation context."
        ),
    )
    return CaptionsInsertWrapper(metadata=metadata)

def build_captions_update_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `captions.update`.

    Official quota cost: ``450`` quota units. The wrapper requires a `body`
    caption-resource payload, supports body-only updates and body-plus-media
    content replacement, allows optional `onBehalfOfContentOwner` delegation on
    authorized requests, and keeps the update boundary visible for higher-layer
    reuse.

    :return: Representative wrapper configured for `captions.update`.
    """
    metadata = EndpointMetadata(
        resource_name="captions",
        operation_name="update",
        http_method="PUT",
        path_shape="/youtube/v3/captions",
        request_shape=EndpointRequestShape(
            required_fields=("part", "body"),
            optional_fields=("media", "onBehalfOfContentOwner"),
            validators=(
                require_mapping_fields("body", required_keys=("id", "snippet")),
                require_optional_mapping_fields("media", required_keys=("mimeType", "content")),
            ),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=450,
        notes=(
            "Requires oauth_required auth. Use `body` for the caption resource "
            "being updated, use `media` only for supported body-plus-media "
            "content replacement, and treat `onBehalfOfContentOwner` as "
            "optional delegation context."
        ),
    )
    return CaptionsUpdateWrapper(metadata=metadata)

def build_captions_download_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `captions.download`.

    Official quota cost: ``200`` quota units. The wrapper requires one caption
    track ``id``, supports optional ``tfmt`` format conversion and ``tlang``
    translation inputs, and keeps permission-sensitive and delegated download
    guidance visible for higher-layer reuse.

    :return: Representative wrapper configured for `captions.download`.
    """
    metadata = EndpointMetadata(
        resource_name="captions",
        operation_name="download",
        http_method="GET",
        path_shape="/youtube/v3/captions/{id}",
        request_shape=EndpointRequestShape(
            required_fields=("id",),
            optional_fields=("tfmt", "tlang", "onBehalfOfContentOwner"),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=200,
        notes=(
            "Requires oauth_required auth. Use `id` for the caption track being "
            "downloaded, use `tfmt` and `tlang` only for supported output "
            "variants, note that some downloads remain permission-sensitive "
            "even with authorized access, and treat `onBehalfOfContentOwner` "
            "as optional delegation context."
        ),
    )
    return CaptionsDownloadWrapper(metadata=metadata)

def build_captions_delete_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `captions.delete`.

    Official quota cost: ``50`` quota units. The wrapper requires one caption
    track ``id`` and supports optional ``onBehalfOfContentOwner`` delegation
    while keeping ownership-sensitive delete guidance visible for higher-layer
    reuse.

    :return: Representative wrapper configured for `captions.delete`.
    """
    metadata = EndpointMetadata(
        resource_name="captions",
        operation_name="delete",
        http_method="DELETE",
        path_shape="/youtube/v3/captions/{id}",
        request_shape=EndpointRequestShape(
            required_fields=("id",),
            optional_fields=("onBehalfOfContentOwner",),
        ),
        auth_mode=AuthMode.OAUTH_REQUIRED,
        quota_cost=50,
        notes=(
            "Requires oauth_required auth. Use `id` for the caption track being "
            "deleted, note that deletion remains ownership-sensitive even with "
            "authorized access, and treat `onBehalfOfContentOwner` as optional "
            "delegation context."
        ),
    )
    return CaptionsDeleteWrapper(metadata=metadata)

FAMILY_NAME = "captions"
RESOURCE_NAMES = ("captions",)
BUILDER_FUNCTIONS = {
    "captions.list": build_captions_list_wrapper,
    "captions.insert": build_captions_insert_wrapper,
    "captions.update": build_captions_update_wrapper,
    "captions.download": build_captions_download_wrapper,
    "captions.delete": build_captions_delete_wrapper,
}
RESPONSE_NORMALIZER_KEYS = ("captions.download", "captions.delete")

__all__ = [
    "BUILDER_FUNCTIONS",
    "CaptionsDeleteWrapper",
    "CaptionsDownloadWrapper",
    "CaptionsInsertWrapper",
    "CaptionsListWrapper",
    "CaptionsUpdateWrapper",
    "FAMILY_NAME",
    "RESOURCE_NAMES",
    "RESPONSE_NORMALIZER_KEYS",
    "build_captions_delete_wrapper",
    "build_captions_download_wrapper",
    "build_captions_insert_wrapper",
    "build_captions_list_wrapper",
    "build_captions_update_wrapper",
]
