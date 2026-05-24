# ruff: noqa: F405
"""Search resource-family wrappers for Layer 1 YouTube integrations."""

from __future__ import annotations

from mcp_server.integrations.resources.base import *  # noqa: F403

@dataclass(frozen=True)
class SearchListWrapper(RepresentativeEndpointWrapper):
    """Represent the typed Layer 1 wrapper for `search.list`.

    Official quota cost: ``100`` quota units. The wrapper supports public
    API-key search for standard queries and restricted-filter searches that
    require stronger authorization.
    """

    def call(
        self,
        executor: IntegrationExecutor,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Execute `search.list` with filter-aware auth validation.

        :param executor: Shared executor for request processing.
        :param arguments: Wrapper arguments to validate and execute.
        :param auth_context: Selected auth context for the call.
        :return: Structured response payload.
        :raises ValueError: If the selected search path requires a different auth mode.
        """
        if self._uses_restricted_filters(arguments):
            if auth_context.mode is not AuthMode.OAUTH_REQUIRED:
                raise ValueError("restricted search filters require oauth_required auth")
        elif auth_context.mode is not AuthMode.API_KEY:
            raise ValueError("public search requires api_key auth")
        return super().call(executor, arguments=arguments, auth_context=auth_context)

    @staticmethod
    def _uses_restricted_filters(arguments: dict[str, Any]) -> bool:
        """Return whether one search request uses a restricted auth path.

        :param arguments: Wrapper arguments to inspect.
        :return: ``True`` when any restricted filter is present.
        """
        return any(
            (arguments.get(field) is True) or (isinstance(arguments.get(field), str) and str(arguments.get(field)).strip())
            for field in _SEARCH_RESTRICTED_FIELDS
        )

def build_search_list_wrapper() -> RepresentativeEndpointWrapper:
    """Build the typed internal wrapper for `search.list`.

    Official quota cost: ``100`` quota units. The wrapper requires ``part``
    plus ``q`` for baseline search, keeps near-raw search refinements
    reviewable, and documents restricted filters that require stronger
    authorization.

    :return: Representative wrapper configured for `search.list`.
    """
    metadata = EndpointMetadata(
        resource_name="search",
        operation_name="list",
        http_method="GET",
        path_shape="/youtube/v3/search",
        request_shape=EndpointRequestShape(
            required_fields=("part", "q"),
            optional_fields=(
                "channelId",
                "forContentOwner",
                "forDeveloper",
                "forMine",
                "publishedAfter",
                "publishedBefore",
                "regionCode",
                "relevanceLanguage",
                "safeSearch",
                "type",
                "videoCaption",
                "videoDefinition",
                "videoDuration",
                "videoEmbeddable",
                "videoLicense",
                "videoPaidProductPlacement",
                "videoSyndicated",
                "videoType",
                "order",
                "pageToken",
                "maxResults",
            ),
            validators=(_require_search_list_arguments,),
        ),
        auth_mode=AuthMode.CONDITIONAL,
        quota_cost=100,
        lifecycle_state="inconsistent-docs",
        caveat_note=(
            "Official quota guidance differs between public overview and "
            "endpoint reference pages for `search.list`."
        ),
        auth_condition_note=(
            "Use API-key auth for baseline public search requests. Use "
            "`forContentOwner`, `forDeveloper`, or `forMine` only when "
            "oauth_required auth is available."
        ),
        notes=(
            "Requires `part` plus `q` for one deterministic search request, "
            "keeps `type`, pagination, date filtering, and language or region "
            "refinements reviewable, rejects undocumented modifiers, preserves "
            "empty result sets as successful no-match outcomes, and keeps the "
            "high-cost quota guidance visible for later reuse."
        ),
    )
    return SearchListWrapper(metadata=metadata)

FAMILY_NAME = "search"
RESOURCE_NAMES = ("search",)
BUILDER_FUNCTIONS = {"search.list": build_search_list_wrapper}

__all__ = ["BUILDER_FUNCTIONS", "FAMILY_NAME", "RESOURCE_NAMES", "SearchListWrapper", "build_search_list_wrapper"]
