"""Representative higher-layer consumer for Layer 1 wrappers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from mcp_server.integrations.auth import AuthContext
from mcp_server.integrations.executor import IntegrationExecutor
from mcp_server.integrations.wrappers import RepresentativeEndpointWrapper


@dataclass(frozen=True)
class RepresentativeHigherLayerConsumer:
    """Compose typed Layer 1 wrapper methods in a higher-layer workflow.

    :param wrapper: Representative typed wrapper used by the consumer.
    :param executor: Shared request executor used for wrapper calls.
    """

    wrapper: RepresentativeEndpointWrapper
    executor: IntegrationExecutor

    def fetch_video_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a simplified higher-layer summary from a typed wrapper result.

        :param arguments: Wrapper arguments needed to fetch the video.
        :param auth_context: Auth context for the wrapper call.
        :return: Higher-layer summary derived from the typed wrapper response.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        item = result["items"][0]
        return {
            "videoId": item["id"],
            "title": item.get("title"),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
        }

    def fetch_activity_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from an `activities.list` wrapper result.

        :param arguments: Wrapper arguments needed to fetch activities.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing source contract details and result volume.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        items = result.get("items", [])
        return {
            "activityCount": len(items),
            "isEmpty": not items,
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
        }

    def fetch_channels_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `channels.list` wrapper result.

        :param arguments: Wrapper arguments needed to fetch channels.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing selector use and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        items = result.get("items", [])
        selector_used = next(
            (
                selector
                for selector in ("id", "mine", "forHandle", "forUsername")
                if selector in arguments and arguments.get(selector) not in (None, "")
            ),
            None,
        )
        return {
            "channelCount": len(items),
            "isEmpty": not items,
            "selectorUsed": selector_used,
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceAuthConditionNote": self.wrapper.metadata.auth_condition_note,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def update_channel_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `channels.update` wrapper result.

        :param arguments: Wrapper arguments needed to update channel state.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing updated channel identity and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        updated_parts = tuple(part.strip() for part in str(arguments.get("part", "")).split(",") if part.strip())
        branding_settings = arguments.get("body", {}).get("brandingSettings", {}) if isinstance(arguments.get("body"), dict) else {}
        image_settings = branding_settings.get("image", {}) if isinstance(branding_settings, dict) else {}
        return {
            "channelId": result.get("id"),
            "isUpdated": bool(result.get("id")),
            "updatedParts": updated_parts,
            "bannerUrlUsed": image_settings.get("bannerExternalUrl"),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def fetch_channel_sections_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `channelSections.list` wrapper result.

        :param arguments: Wrapper arguments needed to fetch channel sections.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing selector use and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        items = result.get("items", [])
        selector_used = next(
            (
                selector
                for selector in ("channelId", "id", "mine")
                if selector in arguments and arguments.get(selector) not in (None, "")
            ),
            None,
        )
        return {
            "channelSectionCount": len(items),
            "isEmpty": not items,
            "selectorUsed": selector_used,
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceAuthConditionNote": self.wrapper.metadata.auth_condition_note,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def fetch_comments_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `comments.list` wrapper result.

        :param arguments: Wrapper arguments needed to fetch comments.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing selector use and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        items = result.get("items", [])
        selector_used = next(
            (
                selector
                for selector in ("id", "parentId")
                if selector in arguments and arguments.get(selector) not in (None, "", [], ())
            ),
            None,
        )
        return {
            "commentCount": len(items),
            "isEmpty": not items,
            "selectorUsed": selector_used,
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def fetch_comment_threads_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `commentThreads.list` wrapper result.

        :param arguments: Wrapper arguments needed to fetch comment threads.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing selector use and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        items = result.get("items", [])
        selector_used = next(
            (
                selector
                for selector in ("videoId", "allThreadsRelatedToChannelId", "id")
                if selector in arguments and arguments.get(selector) not in (None, "", [], ())
            ),
            None,
        )
        return {
            "commentThreadCount": len(items),
            "isEmpty": not items,
            "selectorUsed": selector_used,
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def fetch_guide_categories_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `guideCategories.list` wrapper result.

        :param arguments: Wrapper arguments needed to fetch guide categories.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing region use and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        items = result.get("items", [])
        return {
            "guideCategoryCount": len(items),
            "isEmpty": not items,
            "regionCode": arguments.get("regionCode"),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceLifecycleState": self.wrapper.metadata.lifecycle_state,
            "sourceCaveatNote": self.wrapper.metadata.caveat_note,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def fetch_i18n_languages_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from an `i18nLanguages.list` wrapper result.

        :param arguments: Wrapper arguments needed to fetch localization languages.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing display-language use and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        items = result.get("items", [])
        return {
            "languageCount": len(items),
            "isEmpty": not items,
            "hl": arguments.get("hl"),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def fetch_i18n_regions_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from an `i18nRegions.list` wrapper result.

        :param arguments: Wrapper arguments needed to fetch localization regions.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing display-language use and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        items = result.get("items", [])
        return {
            "regionCount": len(items),
            "isEmpty": not items,
            "hl": arguments.get("hl"),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def fetch_members_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `members.list` wrapper result.

        :param arguments: Wrapper arguments needed to fetch membership records.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing membership mode use and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        items = result.get("items", [])
        return {
            "memberCount": len(items),
            "isEmpty": not items,
            "mode": arguments.get("mode"),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def fetch_memberships_levels_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `membershipsLevels.list` wrapper result.

        :param arguments: Wrapper arguments needed to fetch membership levels.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing required request input use and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        items = result.get("items", [])
        return {
            "membershipLevelCount": len(items),
            "isEmpty": not items,
            "part": arguments.get("part"),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def fetch_playlist_images_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `playlistImages.list` wrapper result.

        :param arguments: Wrapper arguments needed to fetch playlist images.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing selector use and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        items = result.get("items", [])
        selector_used = next(
            (
                selector
                for selector in ("playlistId", "id")
                if selector in arguments and arguments.get(selector) not in (None, "")
            ),
            None,
        )
        return {
            "playlistImageCount": len(items),
            "isEmpty": not items,
            "selectorUsed": selector_used,
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def create_comment_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `comments.insert` wrapper result.

        :param arguments: Wrapper arguments needed to create one reply comment.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing created comment identity and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        snippet = result.get("snippet", {}) if isinstance(result.get("snippet"), dict) else {}
        return {
            "commentId": result.get("id"),
            "isCreated": bool(result.get("id")),
            "parentCommentId": snippet.get("parentId"),
            "delegatedOwner": result.get("delegatedOwner"),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def create_comment_thread_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `commentThreads.insert` wrapper result.

        :param arguments: Wrapper arguments needed to create one comment thread.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing created thread identity and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        snippet = result.get("snippet", {}) if isinstance(result.get("snippet"), dict) else {}
        top_level_comment = (
            snippet.get("topLevelComment", {}) if isinstance(snippet.get("topLevelComment"), dict) else {}
        )
        return {
            "commentThreadId": result.get("id"),
            "isCreated": bool(result.get("id")),
            "videoId": snippet.get("videoId"),
            "topLevelCommentId": top_level_comment.get("id"),
            "delegatedOwner": result.get("delegatedOwner"),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def update_comment_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `comments.update` wrapper result.

        :param arguments: Wrapper arguments needed to update one comment.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing updated comment identity and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        snippet = result.get("snippet", {}) if isinstance(result.get("snippet"), dict) else {}
        return {
            "commentId": result.get("id"),
            "isUpdated": bool(result.get("id")),
            "updatedText": snippet.get("textOriginal"),
            "delegatedOwner": result.get("delegatedOwner"),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def moderate_comments_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a moderation-status wrapper result.

        :param arguments: Wrapper arguments needed to moderate comments.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing moderation outcome and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        return {
            "commentIds": tuple(result.get("commentIds", ())),
            "isModerated": bool(result.get("isModerated")),
            "moderationStatus": result.get("moderationStatus"),
            "authorBanApplied": bool(result.get("authorBanApplied")),
            "delegatedOwner": result.get("delegatedOwner"),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def delete_comment_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `comments.delete` wrapper result.

        :param arguments: Wrapper arguments needed to delete one comment.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing deleted comment identity and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        return {
            "commentId": result.get("commentId"),
            "isDeleted": bool(result.get("isDeleted")),
            "delegationApplied": bool(result.get("delegatedOwner")),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def create_channel_section_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `channelSections.insert` result.

        :param arguments: Wrapper arguments needed to create one channel section.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing created section identity and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        snippet = result.get("snippet", {}) if isinstance(result.get("snippet"), dict) else {}
        return {
            "channelSectionId": result.get("id"),
            "isCreated": bool(result.get("id")),
            "createdType": snippet.get("type"),
            "delegatedOwner": result.get("delegatedOwner"),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def update_channel_section_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `channelSections.update` result.

        :param arguments: Wrapper arguments needed to update one channel section.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing updated section identity and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        snippet = result.get("snippet", {}) if isinstance(result.get("snippet"), dict) else {}
        return {
            "channelSectionId": result.get("id"),
            "isUpdated": bool(result.get("id")),
            "updatedType": snippet.get("type"),
            "delegatedOwner": result.get("delegatedOwner"),
            "delegatedOwnerChannel": result.get("delegatedOwnerChannel"),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def delete_channel_section_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `channelSections.delete` result.

        :param arguments: Wrapper arguments needed to delete one channel section.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing deleted section identity and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        return {
            "channelSectionId": result.get("channelSectionId"),
            "isDeleted": bool(result.get("isDeleted")),
            "delegationApplied": bool(result.get("delegatedOwner")),
            "delegatedOwnerChannel": result.get("delegatedOwnerChannel"),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def fetch_caption_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `captions.list` wrapper result.

        :param arguments: Wrapper arguments needed to fetch captions.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing source contract details and result volume.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        items = result.get("items", [])
        return {
            "captionCount": len(items),
            "isEmpty": not items,
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def create_caption_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `captions.insert` wrapper result.

        :param arguments: Wrapper arguments needed to create a caption track.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing source contract details and created caption identity.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        return {
            "captionId": result.get("id"),
            "isCreated": bool(result.get("id")),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def update_caption_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `captions.update` wrapper result.

        :param arguments: Wrapper arguments needed to update a caption track.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing source contract details and updated caption identity.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        return {
            "captionId": result.get("id"),
            "isUpdated": bool(result.get("id")),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def download_caption_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `captions.download` result.

        :param arguments: Wrapper arguments needed to download caption content.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing source contract details and download outcome.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        content = result.get("content")
        return {
            "captionId": result.get("captionId"),
            "hasContent": isinstance(content, str) and bool(content),
            "contentFormat": result.get("contentFormat"),
            "contentLanguage": result.get("contentLanguage"),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def delete_caption_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `captions.delete` result.

        :param arguments: Wrapper arguments needed to delete a caption track.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing source contract details and delete outcome.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        return {
            "captionId": result.get("captionId"),
            "isDeleted": bool(result.get("isDeleted")),
            "delegationApplied": bool(result.get("delegatedOwner")),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def upload_channel_banner_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `channelBanners.insert` result.

        :param arguments: Wrapper arguments needed to upload banner artwork.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing source contract details and upload outcome.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        return {
            "bannerUrl": result.get("bannerUrl") or result.get("url"),
            "isUploaded": bool(result.get("isUploaded") or result.get("url")),
            "delegationApplied": bool(result.get("delegatedOwner")),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def create_playlist_image_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `playlistImages.insert` result.

        :param arguments: Wrapper arguments needed to create a playlist image.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing source contract details and create outcome.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        snippet = result.get("snippet")
        body = arguments.get("body")
        body_snippet = body.get("snippet", {}) if isinstance(body, dict) else {}
        return {
            "playlistImageId": result.get("id"),
            "isCreated": bool(result.get("id")),
            "playlistId": (
                result.get("playlistId")
                or (snippet.get("playlistId") if isinstance(snippet, dict) else None)
                or body_snippet.get("playlistId")
            ),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def update_playlist_image_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `playlistImages.update` result.

        :param arguments: Wrapper arguments needed to update a playlist image.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing source contract details and update outcome.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        snippet = result.get("snippet")
        body = arguments.get("body")
        body_snippet = body.get("snippet", {}) if isinstance(body, dict) else {}
        return {
            "playlistImageId": result.get("id"),
            "isUpdated": bool(result.get("id")),
            "playlistId": (
                result.get("playlistId")
                or (snippet.get("playlistId") if isinstance(snippet, dict) else None)
                or body_snippet.get("playlistId")
            ),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceNotes": self.wrapper.metadata.notes,
        }
