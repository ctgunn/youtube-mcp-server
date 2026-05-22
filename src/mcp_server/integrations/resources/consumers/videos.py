"""Higher-layer consumer summary methods for videos resources."""

from __future__ import annotations

from typing import Any

from mcp_server.integrations.auth import AuthContext


class VideosConsumerMixin:
    """Provide higher-layer summaries for videos resources."""

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

    def fetch_videos_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `videos.list` wrapper result.

        :param arguments: Wrapper arguments needed to fetch videos.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing selector use, volume, and source contract details.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        items = result.get("items", [])
        return {
            "videoCount": len(items),
            "isEmpty": not items,
            "selectedSelector": result.get("selectedSelector"),
            "id": result.get("id"),
            "chart": result.get("chart"),
            "myRating": result.get("myRating"),
            "regionCode": result.get("regionCode"),
            "videoCategoryId": result.get("videoCategoryId"),
            "nextPageToken": result.get("nextPageToken"),
            "authPathUsed": result.get("authPath"),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceAuthConditionNote": self.wrapper.metadata.auth_condition_note,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def create_video_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `videos.insert` wrapper result.

        :param arguments: Wrapper arguments needed to create a video.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing source contract details and created video identity.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        return {
            "videoId": result.get("id"),
            "isCreated": bool(result.get("id")),
            "uploadMode": result.get("uploadMode"),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceCaveatNote": self.wrapper.metadata.caveat_note,
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def update_video_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `videos.update` result.

        :param arguments: Wrapper arguments needed to update a video.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing source contract details, required update
            inputs, and update outcome.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        body = arguments.get("body")
        body_snippet = body.get("snippet", {}) if isinstance(body, dict) else {}
        snippet = result.get("snippet")
        return {
            "videoId": result.get("id") or (body.get("id") if isinstance(body, dict) else None),
            "isUpdated": bool(result.get("id") or (body.get("id") if isinstance(body, dict) else None)),
            "title": (
                result.get("title")
                or (snippet.get("title") if isinstance(snippet, dict) else None)
                or body_snippet.get("title")
            ),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceRequiredFields": self.wrapper.metadata.request_shape.required_fields,
            "sourceWritablePart": arguments.get("part"),
            "sourceRequiredIdentifierField": "body.id",
            "sourceRequiredTitleField": "body.snippet.title",
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def rate_video_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `videos.rate` result.

        :param arguments: Wrapper arguments needed to rate a video.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing source contract details, required inputs,
            requested rating action, and acknowledgement outcome.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        requested_rating = result.get("requestedRating") or arguments.get("rating")
        return {
            "videoId": result.get("videoId") or arguments.get("id"),
            "requestedRating": requested_rating,
            "isRated": bool(result.get("isRated")),
            "isCleared": bool(result.get("isCleared")),
            "ratingState": result.get("ratingState"),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceRequiredFields": self.wrapper.metadata.request_shape.required_fields,
            "sourceRequiredIdentifierField": "id",
            "sourceRequiredRatingField": "rating",
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def get_video_rating_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `videos.getRating` result.

        :param arguments: Wrapper arguments needed to look up video ratings.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing requested identifiers, returned states, and
            source contract details for downstream review surfaces.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        video_ratings = result.get("videoRatings")
        normalized_ratings = video_ratings if isinstance(video_ratings, list) else []
        ratings_by_video_id: dict[str, str] = {}
        for entry in normalized_ratings:
            if not isinstance(entry, dict):
                continue
            video_id = entry.get("videoId")
            rating = entry.get("rating")
            if isinstance(video_id, str) and video_id.strip() and isinstance(rating, str):
                ratings_by_video_id[video_id] = rating
        return {
            "requestedId": result.get("requestedId") or arguments.get("id"),
            "resultCount": len(ratings_by_video_id),
            "ratingStateSummary": result.get("ratingStateSummary"),
            "ratingsByVideoId": ratings_by_video_id,
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceRequiredFields": self.wrapper.metadata.request_shape.required_fields,
            "sourceRequiredIdentifierField": "id",
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def report_video_abuse_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `videos.reportAbuse` result.

        :param arguments: Wrapper arguments needed to report video abuse.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing submitted report context, acknowledgement
            state, and source contract details without exposing credentials or
            raw reporter comments.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        body = arguments.get("body")
        report_body = body if isinstance(body, dict) else {}
        return {
            "isAccepted": bool(result.get("isAccepted")),
            "reportedVideoId": result.get("reportedVideoId") or report_body.get("videoId"),
            "reasonId": result.get("reasonId") or report_body.get("reasonId"),
            "secondaryReasonId": result.get("secondaryReasonId") or report_body.get("secondaryReasonId"),
            "hasComments": bool(result.get("hasComments")),
            "language": result.get("language") or report_body.get("language"),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceRequiredFields": self.wrapper.metadata.request_shape.required_fields,
            "sourceRequiredVideoIdField": "body.videoId",
            "sourceRequiredReasonField": "body.reasonId",
            "sourceOptionalBodyFields": ("secondaryReasonId", "comments", "language"),
            "sourceNotes": self.wrapper.metadata.notes,
        }

    def delete_video_summary(
        self,
        *,
        arguments: dict[str, Any],
        auth_context: AuthContext,
    ) -> dict[str, Any]:
        """Return a higher-layer summary from a `videos.delete` result.

        :param arguments: Wrapper arguments needed to delete one video.
        :param auth_context: Auth context for the wrapper call.
        :return: Summary showing deleted video identity, acknowledgement
            state, and source contract details without exposing credentials or
            target-owner identity.
        """
        result = self.wrapper.call(self.executor, arguments=arguments, auth_context=auth_context)
        return {
            "isDeleted": bool(result.get("isDeleted")),
            "videoId": result.get("videoId") or arguments.get("id"),
            "sourceOperation": self.wrapper.metadata.operation_key,
            "sourceAuthMode": self.wrapper.metadata.review_auth_mode,
            "sourceQuotaCost": self.wrapper.metadata.quota_cost,
            "sourceRequiredFields": self.wrapper.metadata.request_shape.required_fields,
            "sourceRequiredIdentifierField": "id",
            "sourceBodyBehavior": "no_request_body",
            "sourceNotes": self.wrapper.metadata.notes,
        }
