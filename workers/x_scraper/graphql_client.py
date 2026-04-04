"""
Twitter GraphQL client — guest token auth, no login required.

Handles:
- Guest token acquisition and rotation
- GraphQL query hash extraction from Twitter's JS bundles
- UserTweets and UserByScreenName queries
- Automatic token refresh on 403/401
"""

from __future__ import annotations

import json
import logging
import re
import time
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)

_BEARER = "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"

_FEATURES = {
    "rweb_tipjar_consumption_enabled": True,
    "responsive_web_graphql_exclude_directive_enabled": True,
    "verified_phone_label_enabled": False,
    "responsive_web_graphql_timeline_navigation_enabled": True,
    "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
    "view_counts_everywhere_api_enabled": True,
    "longform_notetweets_consumption_enabled": True,
    "responsive_web_edit_tweet_api_enabled": True,
    "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
    "longform_notetweets_rich_text_read_enabled": True,
    "longform_notetweets_inline_media_enabled": True,
    "responsive_web_enhance_cards_enabled": False,
    "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
    "freedom_of_speech_not_reach_fetch_enabled": True,
    "standardized_nudges_misinfo": True,
    "creator_subscriptions_tweet_preview_api_enabled": True,
    "communities_web_enable_tweet_community_results_fetch": True,
    "c9s_tweet_anatomy_moderator_badge_enabled": True,
    "articles_preview_enabled": True,
    "responsive_web_twitter_article_tweet_consumption_enabled": True,
    "rweb_video_timestamps_enabled": True,
    "creator_subscriptions_quote_tweet_preview_enabled": False,
    "tweet_awards_web_tipping_enabled": False,
}

_FEATURES_JSON = json.dumps(_FEATURES)


class GraphQLClient:
    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": _BEARER,
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        })
        self._guest_token: Optional[str] = None
        self._hashes: dict[str, str] = {}
        self._request_count = 0
        self._token_requests = 0

    @property
    def request_count(self) -> int:
        return self._request_count

    # ------------------------------------------------------------------
    # Guest token management
    # ------------------------------------------------------------------

    def _ensure_guest_token(self) -> None:
        if self._guest_token:
            return
        self._refresh_guest_token()

    def _refresh_guest_token(self) -> None:
        for attempt in range(3):
            try:
                resp = self._session.post(
                    "https://api.twitter.com/1.1/guest/activate.json",
                    timeout=10,
                )
                if resp.status_code == 200:
                    self._guest_token = resp.json()["guest_token"]
                    self._session.headers["x-guest-token"] = self._guest_token
                    self._token_requests += 1
                    logger.debug(f"[graphql] New guest token: {self._guest_token}")
                    return
                logger.warning(f"[graphql] Guest token failed: {resp.status_code}")
            except Exception as exc:
                logger.warning(f"[graphql] Guest token error: {exc}")
            time.sleep(2 ** attempt)

        raise RuntimeError("Failed to obtain guest token after 3 attempts")

    # ------------------------------------------------------------------
    # GraphQL hash extraction
    # ------------------------------------------------------------------

    def _ensure_hashes(self) -> None:
        if self._hashes:
            return
        self._extract_hashes()

    def _extract_hashes(self) -> None:
        """Extract GraphQL query hashes from Twitter's JS bundles."""
        try:
            resp = requests.get("https://x.com", headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }, timeout=10)
            js_urls = re.findall(
                r'"(https://abs\.twimg\.com/responsive-web/client-web[^"]*\.js)"',
                resp.text,
            )
            for js_url in js_urls:
                js_resp = requests.get(js_url, headers={
                    "User-Agent": "Mozilla/5.0"
                }, timeout=15)
                for match in re.finditer(
                    r'queryId:"([^"]+)",operationName:"([^"]+)"', js_resp.text
                ):
                    self._hashes[match.group(2)] = match.group(1)
                if "UserTweets" in self._hashes:
                    break

            logger.info(f"[graphql] Extracted {len(self._hashes)} query hashes")
        except Exception as exc:
            raise RuntimeError(f"Failed to extract GraphQL hashes: {exc}")

    def _get_hash(self, operation: str) -> str:
        self._ensure_hashes()
        if operation not in self._hashes:
            raise ValueError(f"GraphQL hash not found for {operation}")
        return self._hashes[operation]

    # ------------------------------------------------------------------
    # API calls
    # ------------------------------------------------------------------

    def _graphql_get(
        self, operation: str, variables: dict, max_retries: int = 3
    ) -> Optional[dict]:
        """Make a GraphQL GET request with auto token refresh."""
        self._ensure_guest_token()
        self._ensure_hashes()

        query_hash = self._get_hash(operation)
        url = f"https://x.com/i/api/graphql/{query_hash}/{operation}"
        params = {
            "variables": json.dumps(variables),
            "features": _FEATURES_JSON,
        }

        for attempt in range(max_retries):
            self._request_count += 1
            try:
                resp = self._session.get(url, params=params, timeout=15)

                if resp.status_code == 200:
                    return resp.json()

                if resp.status_code in (401, 403):
                    logger.warning("[graphql] Token expired, refreshing...")
                    self._guest_token = None
                    self._refresh_guest_token()
                    continue

                if resp.status_code == 429:
                    wait = 60 * (attempt + 1)
                    logger.warning(f"[graphql] Rate limited, waiting {wait}s")
                    time.sleep(wait)
                    self._guest_token = None
                    self._refresh_guest_token()
                    continue

                if resp.status_code >= 500:
                    time.sleep(5)
                    continue

                logger.error(f"[graphql] HTTP {resp.status_code} for {operation}")
                return None

            except requests.RequestException as exc:
                logger.error(f"[graphql] Request failed: {exc}")
                if attempt < max_retries - 1:
                    time.sleep(3)

        return None

    # ------------------------------------------------------------------
    # High-level operations
    # ------------------------------------------------------------------

    def get_user_id(self, screen_name: str) -> Optional[str]:
        """Resolve a screen name to a user ID."""
        variables = {
            "screen_name": screen_name,
            "withSafetyModeUserFields": True,
        }
        data = self._graphql_get("UserByScreenName", variables)
        if not data:
            return None
        try:
            return data["data"]["user"]["result"]["rest_id"]
        except (KeyError, TypeError):
            logger.warning(f"[graphql] Could not resolve user: @{screen_name}")
            return None

    def get_user_tweets(
        self, user_id: str, count: int = 20, cursor: Optional[str] = None
    ) -> Optional[dict]:
        """Fetch tweets from a user's timeline."""
        variables: dict[str, Any] = {
            "userId": user_id,
            "count": count,
            "includePromotedContent": False,
            "withQuickPromoteEligibilityTweetFields": True,
            "withVoice": True,
            "withV2Timeline": True,
        }
        if cursor:
            variables["cursor"] = cursor

        return self._graphql_get("UserTweets", variables)
