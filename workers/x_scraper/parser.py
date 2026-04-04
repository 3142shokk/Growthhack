"""
Tweet parser — extracts structured tweet data from GraphQL responses.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Optional


def parse_user_tweets_response(data: dict) -> tuple[list[dict], Optional[str]]:
    """
    Parse a UserTweets GraphQL response.
    Returns (list of parsed tweet dicts, next cursor or None).
    """
    tweets: list[dict] = []
    cursor: Optional[str] = None

    try:
        user_result = data["data"]["user"]["result"]
        timeline = user_result.get("timeline_v2") or user_result.get("timeline", {})
        instructions = timeline["timeline"]["instructions"]
    except (KeyError, TypeError):
        return [], None

    for inst in instructions:
        entries = inst.get("entries", [])
        for entry in entries:
            content = entry.get("content", {})

            # Handle single tweet items
            tweet_result = (
                content.get("itemContent", {})
                .get("tweet_results", {})
                .get("result")
            )
            if tweet_result:
                parsed = _parse_tweet(tweet_result)
                if parsed:
                    tweets.append(parsed)

            # Handle conversation modules (thread items)
            items = content.get("items", [])
            for item in items:
                tweet_result = (
                    item.get("item", {})
                    .get("itemContent", {})
                    .get("tweet_results", {})
                    .get("result")
                )
                if tweet_result:
                    parsed = _parse_tweet(tweet_result)
                    if parsed:
                        tweets.append(parsed)

            # Extract cursor
            cursor_type = content.get("cursorType", "")
            if cursor_type == "Bottom":
                cursor = content.get("value")

    return tweets, cursor


def _parse_tweet(result: dict[str, Any]) -> Optional[dict]:
    """Parse a single tweet result into a flat dict."""
    try:
        # Handle tweet with tombstone (deleted/unavailable)
        typename = result.get("__typename", "")
        if typename == "TweetTombstone":
            return None

        # Handle TweetWithVisibilityResults wrapper
        if typename == "TweetWithVisibilityResults":
            result = result.get("tweet", {})

        legacy = result.get("legacy", {})
        if not legacy:
            return None

        # User info — screen_name moved to core.user_results.result.core in 2026
        user_result = result.get("core", {}).get("user_results", {}).get("result", {})
        user_core = user_result.get("core", {})
        screen_name = (
            user_core.get("screen_name")
            or user_result.get("legacy", {}).get("screen_name")
            or "unknown"
        )

        # Views
        views_str = result.get("views", {}).get("count")
        views = int(views_str) if views_str else None

        # Tweet text — prefer note_tweet for long tweets
        text = legacy.get("full_text", "")
        note = result.get("note_tweet", {}).get("note_tweet_results", {}).get("result", {})
        if note:
            note_text = note.get("text", "")
            if len(note_text) > len(text):
                text = note_text

        # Hashtags
        entities = legacy.get("entities", {})
        hashtags = [h.get("text", "") for h in entities.get("hashtags", [])]
        # Also from text
        text_hashtags = re.findall(r"#(\w+)", text)
        seen = {h.lower() for h in hashtags}
        for h in text_hashtags:
            if h.lower() not in seen:
                hashtags.append(h)
                seen.add(h.lower())

        # Timestamp
        created_at = legacy.get("created_at", "")
        published_at = None
        if created_at:
            try:
                published_at = datetime.strptime(
                    created_at, "%a %b %d %H:%M:%S %z %Y"
                ).isoformat()
            except ValueError:
                pass

        tweet_id = legacy.get("id_str", result.get("rest_id", ""))

        return {
            "tweet_id": tweet_id,
            "author": screen_name,
            "text": text,
            "created_at": published_at,
            "likes": legacy.get("favorite_count", 0),
            "reposts": legacy.get("retweet_count", 0),
            "replies": legacy.get("reply_count", 0),
            "views": views,
            "hashtags": hashtags,
            "query": "",  # filled by the worker
        }
    except Exception:
        return None
