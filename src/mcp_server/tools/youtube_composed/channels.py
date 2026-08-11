"""Concrete channel-family public YouTube tools."""

from __future__ import annotations

from datetime import datetime
import re
from typing import Any
from urllib.parse import urlparse

from mcp_server.tools.youtube_common.channels import ChannelsListToolError, build_channels_list_handler
from mcp_server.tools.youtube_common.conventions import safe_upstream_error_message, sanitize_error_details
from mcp_server.tools.youtube_common.playlist_items import PlaylistItemsListToolError, build_playlist_items_list_handler
from mcp_server.tools.youtube_composed.families import get_family

FAMILY_SCAFFOLDING = get_family("channels")
PLANNED_TOOLS = FAMILY_SCAFFOLDING.planned_tools
CHANNELS_GET_CHANNEL_TOOL_NAME = "channels_getChannel"
CHANNELS_GET_CHANNEL_INPUT_SCHEMA = {
    "type": "object",
    "required": ["channelId"],
    "properties": {"channelId": {"type": "string", "minLength": 1}},
    "additionalProperties": False,
}
_EMAIL_PATTERN = re.compile(r"(?<![\w@])[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,63}(?![\w@])", re.IGNORECASE)
_URL_PATTERN = re.compile(r"https?://[^\s<>()]+", re.IGNORECASE)
_CREATOR_SIGNAL_TERMS = (("creator", "public_creator_term"), ("artist", "public_artist_term"), ("developer", "public_developer_term"))
_BRAND_SIGNAL_TERMS = (("official", "public_official_term"), ("company", "public_company_term"), ("brand", "public_brand_term"), ("inc", "public_inc_term"))


class ChannelsGetChannelToolError(ValueError):
    """Represent a safe caller-facing channel-detail failure.

    :param message: Caller-safe explanation of the failure.
    :param category: Stable public error category.
    :param details: Candidate diagnostic details to sanitize.
    """

    def __init__(self, message: str, *, category: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the safe public channel-detail error.

        :param message: Caller-safe explanation of the failure.
        :param category: Stable public error category.
        :param details: Candidate diagnostic details to sanitize.
        """
        super().__init__(message)
        self.category = category
        self.details = sanitize_error_details(details or {})


def build_channels_get_channel_metadata() -> dict[str, Any]:
    """Build safe discovery metadata for the concrete channel-detail tool.

    :return: JSON-compatible executable tool metadata without a representative marker.
    """
    return {
        "name": CHANNELS_GET_CHANNEL_TOOL_NAME,
        "family": "channels",
        "parameters": ["channelId"],
        "inputContract": CHANNELS_GET_CHANNEL_INPUT_SCHEMA,
        "compositionBoundary": {
            "kind": "normalized_enrichment",
            "lowerLayerDependencies": ["channels.list", "playlistItems.list"],
            "boundedness": "one channel and at most one playlist item",
            "partialResultPolicy": "Preserve a core profile when latest-video enrichment is unavailable or safely partial.",
        },
        "lowerLayerDependencies": ["channels.list", "playlistItems.list"],
        "authAndQuotaNotes": [
            "Uses the public channel lookup and, when available, one public uploads-playlist item lookup.",
            "Latest-video enrichment is optional and can be unavailable or partial without discarding an available channel profile.",
        ],
        "responseFields": [
            {"fieldName": "channelId", "category": "raw_upstream", "source": "id"},
            {"fieldName": "title", "category": "raw_upstream", "source": "snippet.title"},
            {"fieldName": "description", "category": "raw_upstream", "source": "snippet.description"},
            {"fieldName": "thumbnails", "category": "raw_upstream", "source": "snippet.thumbnails"},
            {"fieldName": "normalizedMetadata.country", "category": "normalized", "source": "snippet.country"},
            {"fieldName": "normalizedMetadata.defaultLanguage", "category": "normalized", "source": "snippet.defaultLanguage"},
            {"fieldName": "normalizedMetadata.joinedAt", "category": "normalized", "source": "snippet.publishedAt"},
            {"fieldName": "normalizedMetadata.customUrl", "category": "normalized", "source": "snippet.customUrl"},
            {"fieldName": "normalizedMetadata.emailsFound", "category": "heuristic_inferred", "source": "public channel material"},
            {"fieldName": "normalizedMetadata.contactLinks", "category": "heuristic_inferred", "source": "public channel material"},
            {"fieldName": "latestVideoPublishedAt", "category": "normalized", "source": "uploads playlist item contentDetails.videoPublishedAt"},
            {"fieldName": "enrichment", "category": "normalized", "source": "bounded latest-video enrichment"},
            {"fieldName": "heuristics.creatorClassification", "category": "heuristic_inferred", "source": "public channel material"},
            {"fieldName": "heuristics.creatorSignals", "category": "heuristic_inferred", "source": "public channel material"},
        ],
        "heuristics": [
            {
                "name": "publicContactExtraction",
                "basis": "Public channel material returned for this request.",
                "limitations": "Contact values are not verified identity, ownership, or permission to contact.",
            },
            {
                "name": "creatorClassification",
                "basis": "Positive public channel metadata signals.",
                "limitations": "Classification is inferred, can be incomplete or incorrect, and is not canonical source truth.",
            },
        ],
        "errorCategories": [
            "invalid_parameters",
            "unavailable_resource",
            "authorization_sensitive_data",
            "quota_exhaustion",
            "upstream_failure",
            "partial_enrichment_failure",
        ],
        "errorGuidance": {
            "invalid_parameters": "Correct the identified request field and retry.",
            "unavailable_resource": "Use a different accessible channel identifier.",
            "authorization_sensitive_data": "Obtain appropriate authorization if applicable.",
            "quota_exhaustion": "Retry after capacity is available.",
            "upstream_failure": "Retry when the source service is available.",
            "partial_enrichment_failure": "Use the returned profile and retry enrichment later when the safe cause category is actionable.",
        },
    }


def validate_channels_get_channel_arguments(arguments: dict[str, Any]) -> dict[str, str]:
    """Validate and normalize the public single-channel request.

    :param arguments: Candidate public tool arguments.
    :return: Normalized request containing one stripped channel identifier.
    :raises ChannelsGetChannelToolError: If public input is missing or invalid.
    """
    if not isinstance(arguments, dict):
        raise ChannelsGetChannelToolError(
            "channels_getChannel arguments must be an object",
            category="invalid_parameters",
            details={"field": "arguments"},
        )
    unexpected_fields = set(arguments) - {"channelId"}
    if unexpected_fields:
        raise ChannelsGetChannelToolError(
            "channels_getChannel received an unsupported field",
            category="invalid_parameters",
            details={"field": sorted(unexpected_fields)[0]},
        )
    channel_id = arguments.get("channelId")
    if not isinstance(channel_id, str) or not channel_id.strip():
        raise ChannelsGetChannelToolError(
            "channels_getChannel requires a non-empty channelId",
            category="invalid_parameters",
            details={"field": "channelId"},
        )
    return {"channelId": channel_id.strip()}


def _copy_if_present(result: dict[str, Any], source: dict[str, Any], field: str) -> None:
    """Copy an available source field into a public result using the same name.

    :param result: Result mapping being assembled.
    :param source: Source mapping that may contain the field.
    :param field: Source and public result field name.
    """
    if field in source:
        result[field] = source[field]


def _public_contact_text(snippet: dict[str, Any]) -> str:
    """Return public profile text permitted for contact-value extraction.

    :param snippet: Public source profile metadata.
    :return: Concatenated description and HTTP(S) custom URL text when present.
    """
    values = []
    description = snippet.get("description")
    if isinstance(description, str):
        values.append(description)
    custom_url = snippet.get("customUrl")
    if isinstance(custom_url, str) and custom_url.lower().startswith(("http://", "https://")):
        values.append(custom_url)
    return "\n".join(values)


def _public_contacts(snippet: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Extract deterministic public email and HTTP(S) contact values.

    :param snippet: Public source profile metadata.
    :return: De-duplicated normalized email addresses and contact links.
    """
    text = _public_contact_text(snippet)
    emails: list[str] = []
    email_keys: set[str] = set()
    for match in _EMAIL_PATTERN.finditer(text):
        email = match.group(0).lower()
        if email not in email_keys:
            email_keys.add(email)
            emails.append(email)
    links: list[str] = []
    link_keys: set[str] = set()
    for match in _URL_PATTERN.finditer(text):
        link = match.group(0).rstrip(".,;:!?)]}")
        parsed = urlparse(link)
        if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc or parsed.username or parsed.password:
            continue
        key = link.lower()
        if key not in link_keys:
            link_keys.add(key)
            links.append(link)
    return emails, links


def _has_term(text: str, term: str) -> bool:
    """Return whether one public classification term appears as a whole word.

    :param text: Lower-cased public profile text.
    :param term: Lower-cased candidate classification term.
    :return: ``True`` when the term appears outside another word.
    """
    return re.search(rf"(?<!\w){re.escape(term)}(?!\w)", text) is not None


def _creator_classification(snippet: dict[str, Any]) -> tuple[str, list[str]]:
    """Classify a channel conservatively from positive public profile signals.

    :param snippet: Public source profile metadata.
    :return: ``creator``, ``brand``, or ``unknown`` and safe supporting signals.
    """
    title = snippet.get("title") if isinstance(snippet.get("title"), str) else ""
    description = snippet.get("description") if isinstance(snippet.get("description"), str) else ""
    text = f"{title}\n{description}".lower()
    creator_signals = [signal for term, signal in _CREATOR_SIGNAL_TERMS if _has_term(text, term)]
    brand_signals = [signal for term, signal in _BRAND_SIGNAL_TERMS if _has_term(text, term)]
    if creator_signals and not brand_signals:
        return "creator", creator_signals
    if brand_signals and not creator_signals:
        return "brand", brand_signals
    return "unknown", []


def _normalized_metadata(snippet: dict[str, Any]) -> dict[str, Any]:
    """Build the stable normalized metadata group from public profile values.

    :param snippet: Public source profile metadata.
    :return: Normalized metadata with safely derived public contact collections.
    """
    emails, contact_links = _public_contacts(snippet)
    metadata: dict[str, Any] = {"emailsFound": emails, "contactLinks": contact_links}
    for source_name, result_name in (
        ("country", "country"),
        ("defaultLanguage", "defaultLanguage"),
        ("publishedAt", "joinedAt"),
        ("customUrl", "customUrl"),
    ):
        if source_name in snippet:
            metadata[result_name] = snippet[source_name]
    return metadata


def _uploads_playlist_id(item: dict[str, Any]) -> str | None:
    """Return one usable public uploads-playlist identifier when available.

    :param item: Source channel record containing optional content details.
    :return: Nonblank uploads-playlist identifier, or ``None`` when unavailable.
    """
    content_details = item.get("contentDetails") if isinstance(item.get("contentDetails"), dict) else {}
    related_playlists = content_details.get("relatedPlaylists") if isinstance(content_details.get("relatedPlaylists"), dict) else {}
    uploads = related_playlists.get("uploads")
    return uploads.strip() if isinstance(uploads, str) and uploads.strip() else None


def _latest_video_published_at(payload: dict[str, Any]) -> str | None:
    """Return the latest available publication timestamp from one playlist response.

    :param payload: Lower-level playlist-items result with at most one item requested.
    :return: Timezone-aware publication timestamp, or ``None`` when unavailable or malformed.
    """
    items = payload.get("items") if isinstance(payload, dict) else None
    if not isinstance(items, list) or not items or not isinstance(items[0], dict):
        return None
    content_details = items[0].get("contentDetails") if isinstance(items[0].get("contentDetails"), dict) else {}
    timestamp = content_details.get("videoPublishedAt")
    if not isinstance(timestamp, str) or not timestamp.strip():
        return None
    value = timestamp.strip()
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00" if value.endswith("Z") else value)
    except ValueError:
        return None
    return value if parsed.tzinfo is not None else None


def _field_provenance(result: dict[str, Any]) -> dict[str, str]:
    """Build provenance labels for every currently returned public field path.

    :param result: Channel result before its provenance mapping is attached.
    :return: Public field-path-to-provenance mapping.
    """
    provenance: dict[str, str] = {}
    for field in ("channelId", "title", "description", "thumbnails"):
        if field in result:
            provenance[field] = "raw_upstream"
    metadata = result.get("normalizedMetadata") if isinstance(result.get("normalizedMetadata"), dict) else {}
    for field in ("country", "defaultLanguage", "joinedAt", "customUrl"):
        if field in metadata:
            provenance[f"normalizedMetadata.{field}"] = "normalized"
    provenance["normalizedMetadata.emailsFound"] = "heuristic_inferred"
    provenance["normalizedMetadata.contactLinks"] = "heuristic_inferred"
    if "latestVideoPublishedAt" in result:
        provenance["latestVideoPublishedAt"] = "normalized"
    provenance["enrichment"] = "normalized"
    provenance["heuristics.creatorClassification"] = "heuristic_inferred"
    provenance["heuristics.creatorSignals"] = "heuristic_inferred"
    return provenance


def _normalize_channel_result(payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Normalize one available lower-level channel item into a public profile.

    :param payload: Lower-level channel-list result containing one item.
    :return: Public result before latest enrichment and the source channel item.
    :raises ChannelsGetChannelToolError: If no usable channel item is available.
    """
    items = payload.get("items") if isinstance(payload, dict) else None
    if not isinstance(items, list) or not items or not isinstance(items[0], dict):
        raise ChannelsGetChannelToolError(
            "The requested channel is unavailable",
            category="unavailable_resource",
            details={"resource": "channel"},
        )
    item = items[0]
    channel_id = item.get("id")
    if not isinstance(channel_id, str) or not channel_id.strip():
        raise ChannelsGetChannelToolError(
            "The requested channel is unavailable",
            category="unavailable_resource",
            details={"resource": "channel"},
        )
    snippet = item.get("snippet") if isinstance(item.get("snippet"), dict) else {}
    result: dict[str, Any] = {"channelId": channel_id}
    for field in ("title", "description", "thumbnails"):
        _copy_if_present(result, snippet, field)
    result["normalizedMetadata"] = _normalized_metadata(snippet)
    classification, signals = _creator_classification(snippet)
    result["heuristics"] = {"creatorClassification": classification, "creatorSignals": signals}
    return result, item


def _map_channels_list_error(error: ChannelsListToolError) -> ChannelsGetChannelToolError:
    """Translate a lower-level core lookup error to the public taxonomy.

    :param error: Safe lower-level channel-list failure.
    :return: Sanitized public channel-detail error.
    """
    if error.category in {"resource_not_found", "removed"}:
        return ChannelsGetChannelToolError(
            "The requested channel is unavailable",
            category="unavailable_resource",
            details={"resource": "channel"},
        )
    category = {
        "invalid_request": "invalid_parameters",
        "authentication_failed": "authorization_sensitive_data",
        "authorization_failed": "authorization_sensitive_data",
        "quota_exhausted": "quota_exhaustion",
    }.get(error.category, "upstream_failure")
    return ChannelsGetChannelToolError(safe_upstream_error_message(), category=category, details=error.details)


def _partial_enrichment_state(error: PlaylistItemsListToolError) -> dict[str, str]:
    """Build a safe partial state from a post-profile playlist lookup failure.

    :param error: Safe lower-level playlist-items failure.
    :return: Public partial-enrichment status with a safe cause category.
    """
    cause_category = {
        "authentication_failed": "authorization_sensitive_data",
        "authorization_failed": "authorization_sensitive_data",
        "quota_exhausted": "quota_exhaustion",
    }.get(error.category, "upstream_failure")
    return {
        "status": "partial",
        "category": "partial_enrichment_failure",
        "causeCategory": cause_category,
    }


def build_channels_get_channel_handler(*, channels=None, playlist_items=None):
    """Build a callable handler for one normalized and enriched channel lookup.

    :param channels: Optional lower-level channel-list handler override for tests.
    :param playlist_items: Optional lower-level playlist-items handler override for tests.
    :return: Callable public channel-detail handler with complete, unavailable, or partial enrichment.
    """
    selected_channels = channels or build_channels_list_handler()
    selected_playlist_items = playlist_items or build_playlist_items_list_handler()

    def handler(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute one validated public channel-detail request.

        :param arguments: Caller-provided public arguments.
        :return: Normalized public profile with complete, unavailable, or safely partial enrichment.
        :raises ChannelsGetChannelToolError: If validation or core lookup fails.
        """
        request = validate_channels_get_channel_arguments(arguments)
        try:
            payload = selected_channels({"part": "snippet,contentDetails", "id": request["channelId"]})
        except ChannelsListToolError as exc:
            raise _map_channels_list_error(exc) from exc
        result, item = _normalize_channel_result(payload)
        uploads_playlist_id = _uploads_playlist_id(item)
        if uploads_playlist_id:
            try:
                latest_payload = selected_playlist_items(
                    {"part": "contentDetails", "playlistId": uploads_playlist_id, "maxResults": 1}
                )
            except PlaylistItemsListToolError as exc:
                result["enrichment"] = _partial_enrichment_state(exc)
            else:
                latest_timestamp = _latest_video_published_at(latest_payload)
                if latest_timestamp:
                    result["latestVideoPublishedAt"] = latest_timestamp
                    result["enrichment"] = {"status": "complete"}
                else:
                    result["enrichment"] = {"status": "unavailable"}
        else:
            result["enrichment"] = {"status": "unavailable"}
        result["fieldProvenance"] = _field_provenance(result)
        return result

    return handler


def build_channels_get_channel_tool_descriptor(*, channels=None, playlist_items=None) -> dict[str, Any]:
    """Build the executable MCP descriptor for ``channels_getChannel``.

    :param channels: Optional lower-level channel-list handler override for tests.
    :param playlist_items: Optional lower-level playlist-items handler override for tests.
    :return: Descriptor consumable by the in-memory dispatcher.
    """
    return {
        "name": CHANNELS_GET_CHANNEL_TOOL_NAME,
        "description": "Return normalized and enriched details for one YouTube channel.",
        "inputSchema": CHANNELS_GET_CHANNEL_INPUT_SCHEMA,
        "handler": build_channels_get_channel_handler(channels=channels, playlist_items=playlist_items),
        "metadata": build_channels_get_channel_metadata(),
    }
