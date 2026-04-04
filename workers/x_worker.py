"""
X (Twitter) scraper — DuckDuckGo discovery + Twitter syndication API.

Strategy
--------
No login or API keys required. Two-phase approach:
1. DISCOVER: Use DuckDuckGo to find tweet URLs mentioning Claude/Anthropic.
   DDG returns up to ~250 results per query. We use many query variations,
   time-based filtering, and site:x.com to maximize coverage.
2. ENRICH: Hit Twitter's public syndication API to get structured data for
   each discovered tweet (likes, replies, text, hashtags, author).

Syndication API
---------------
Endpoint: https://cdn.syndication.twimg.com/tweet-result?id={tweet_id}&lang=en&token=x
- No auth required (used by Twitter's embed feature)
- Returns: text, favorite_count, conversation_count, entities, user info
- Does NOT return: view_count, retweet_count (not in this endpoint)
- Rate limit: generous, ~100 req/min with polite delays

Limitations
-----------
- Views not available via syndication API -> views is always None.
- Retweet count not in syndication response -> reposts is always None.
- DuckDuckGo may not return all tweets (search engine coverage varies).
- Deleted tweets return 404 from syndication API -> skipped.
"""

from __future__ import annotations

import logging
import re
import time
from datetime import datetime, timezone
from typing import Any, Optional

import requests
from ddgs import DDGS

import config
from models.post import Post
from workers.base import BaseWorker

logger = logging.getLogger(__name__)

_SYNDICATION_URL = "https://cdn.syndication.twimg.com/tweet-result"
_SYNDICATION_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Referer": "https://platform.twitter.com/",
}

# Tweet ID regex: numeric string of 15-20 digits at end of URL path
_TWEET_ID_RE = re.compile(r"/status/(\d{15,20})")


class XWorker(BaseWorker):
    platform = "x"

    def __init__(
        self,
        search_queries: list[str] | None = None,
        target_total: int = 10_000,
        filter_keywords: list[str] | None = None,
        enrich: bool = True,
        ddg_max_per_query: int = 250,
    ):
        self.search_queries = search_queries or config.X_SEARCH_QUERIES
        self.target_total = target_total
        self.filter_keywords = (
            [k.lower() for k in filter_keywords] if filter_keywords else None
        )
        self.enrich = enrich
        self.ddg_max_per_query = ddg_max_per_query
        self._session = requests.Session()
        self._session.headers.update(_SYNDICATION_HEADERS)
        self._seen_ids: set[str] = set()
        self._posts: list[Post] = []
        self._request_count = 0
        self._enrich_failures = 0

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def scrape(self) -> list[Post]:
        logger.info(
            f"[x] Starting X scraper: {len(self.search_queries)} queries, "
            f"target={self.target_total:,}, enrich={self.enrich}"
        )

        # Phase 1: Discover tweet URLs via DuckDuckGo
        tweet_ids = self._discover_tweets()
        logger.info(f"[x] Discovered {len(tweet_ids):,} unique tweet IDs")

        if not tweet_ids:
            return []

        # Phase 2: Enrich with syndication API
        if self.enrich:
            self._enrich_tweets(tweet_ids)
        else:
            # If no enrichment, create minimal posts from DDG data
            for tid, ddg_data in tweet_ids.items():
                post = self._post_from_ddg(tid, ddg_data)
                if post:
                    self._posts.append(post)

        logger.info(
            f"[x] Scrape complete: {len(self._posts):,} posts "
            f"({self._request_count:,} syndication requests, "
            f"{self._enrich_failures} failures)"
        )
        return self._posts

    # ------------------------------------------------------------------
    # Phase 1: DuckDuckGo discovery
    # ------------------------------------------------------------------

    def _discover_tweets(self) -> dict[str, dict]:
        """Use DDG to find tweet URLs. Returns {tweet_id: ddg_result_dict}."""
        tweet_map: dict[str, dict] = {}

        for qi, query in enumerate(self.search_queries):
            # Search with site:x.com
            found = self._ddg_search(f"{query} site:x.com")
            for result in found:
                tid = self._extract_tweet_id(result.get("href", ""))
                if tid and tid not in tweet_map:
                    tweet_map[tid] = result

            # Also try site:twitter.com (older URLs still indexed)
            found = self._ddg_search(f"{query} site:twitter.com")
            for result in found:
                tid = self._extract_tweet_id(result.get("href", ""))
                if tid and tid not in tweet_map:
                    tweet_map[tid] = result

            logger.info(
                f"[x] DDG query {qi+1}/{len(self.search_queries)}: "
                f"'{query}' -> {len(tweet_map):,} total unique tweets"
            )

            if len(tweet_map) >= self.target_total:
                break

            time.sleep(config.X_DDG_DELAY)

        return tweet_map

    def _ddg_search(self, query: str) -> list[dict]:
        """Run a single DDG search and return results."""
        try:
            results = list(DDGS().text(query, max_results=self.ddg_max_per_query))
            return results
        except Exception as exc:
            logger.warning(f"[x] DDG search failed for '{query}': {exc}")
            return []

    @staticmethod
    def _extract_tweet_id(url: str) -> Optional[str]:
        """Extract tweet ID from an x.com or twitter.com URL."""
        match = _TWEET_ID_RE.search(url)
        return match.group(1) if match else None

    # ------------------------------------------------------------------
    # Phase 2: Syndication API enrichment
    # ------------------------------------------------------------------

    def _enrich_tweets(self, tweet_ids: dict[str, dict]) -> None:
        """Fetch full tweet data from Twitter's syndication API."""
        logger.info(f"[x] Enriching {len(tweet_ids):,} tweets via syndication API")
        total = len(tweet_ids)

        for i, (tid, ddg_data) in enumerate(tweet_ids.items()):
            post = self._fetch_tweet(tid, ddg_data)
            if post:
                if self._passes_filter(post):
                    self._posts.append(post)
            else:
                self._enrich_failures += 1

            if (i + 1) % 100 == 0:
                logger.info(
                    f"[x] Enrichment progress: {i+1}/{total}, "
                    f"{len(self._posts):,} posts collected, "
                    f"{self._enrich_failures} failures"
                )

            if len(self._posts) >= self.target_total:
                break

            time.sleep(config.X_SYNDICATION_DELAY)

    def _fetch_tweet(self, tweet_id: str, ddg_data: dict) -> Optional[Post]:
        """Fetch a single tweet from the syndication API."""
        self._request_count += 1

        for attempt in range(config.X_MAX_RETRIES):
            try:
                resp = self._session.get(
                    _SYNDICATION_URL,
                    params={"id": tweet_id, "lang": "en", "token": "x"},
                    timeout=10,
                )

                if resp.status_code == 200:
                    data = resp.json()
                    if data:
                        return self._parse_syndication(tweet_id, data, ddg_data)
                    return None

                if resp.status_code == 404:
                    # Tweet deleted or unavailable
                    return None

                if resp.status_code == 429:
                    wait = 2 ** (attempt + 1)
                    logger.warning(f"[x] Rate limited, waiting {wait}s")
                    time.sleep(wait)
                    continue

                if resp.status_code >= 500:
                    time.sleep(2)
                    continue

                return None

            except requests.RequestException as exc:
                logger.debug(f"[x] Request failed for tweet {tweet_id}: {exc}")
                if attempt < config.X_MAX_RETRIES - 1:
                    time.sleep(2)

        return None

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------

    def _parse_syndication(
        self, tweet_id: str, data: dict[str, Any], ddg_data: dict
    ) -> Optional[Post]:
        """Parse syndication API response into a Post."""
        try:
            text = data.get("text", "")
            user = data.get("user", {})
            author = user.get("screen_name", "unknown")
            entities = data.get("entities", {})

            # Likes
            likes = data.get("favorite_count")

            # Replies (conversation_count)
            comments = data.get("conversation_count")

            # Hashtags from entities
            hashtags = [
                h.get("text", "") for h in entities.get("hashtags", [])
            ]
            # Also extract from text
            hashtags.extend(re.findall(r"#(\w+)", text))
            # Deduplicate preserving order
            seen = set()
            unique_hashtags = []
            for h in hashtags:
                hl = h.lower()
                if hl not in seen:
                    seen.add(hl)
                    unique_hashtags.append(h)

            # Timestamp
            published_at = None
            created_at = data.get("created_at")
            if created_at:
                try:
                    published_at = datetime.fromisoformat(
                        created_at.replace("Z", "+00:00")
                    )
                except ValueError:
                    pass

            url = f"https://x.com/{author}/status/{tweet_id}"

            # Check for note_tweet (long tweets)
            note = data.get("note_tweet", {})
            if note:
                note_text = note.get("text", "")
                if len(note_text) > len(text):
                    text = note_text

            return Post(
                id=f"x_{tweet_id}",
                platform="x",
                post_title=text,
                author=author,
                url=url,
                views=None,  # Not available via syndication API
                likes=likes,
                reposts=None,  # Not available via syndication API
                comments=comments,
                hashtags=unique_hashtags,
                published_at=published_at,
                scraped_at=datetime.now(tz=timezone.utc),
                raw_data=data,
            )
        except Exception as exc:
            logger.debug(f"[x] Failed to parse tweet {tweet_id}: {exc}")
            return None

    def _post_from_ddg(self, tweet_id: str, ddg_data: dict) -> Optional[Post]:
        """Create a minimal Post from DDG search result (no enrichment)."""
        try:
            title = ddg_data.get("title", "")
            href = ddg_data.get("href", "")
            body = ddg_data.get("body", "")

            # Try to extract author from URL
            author_match = re.search(r"x\.com/(\w+)/status/", href)
            if not author_match:
                author_match = re.search(r"twitter\.com/(\w+)/status/", href)
            author = author_match.group(1) if author_match else "unknown"

            # Extract hashtags from title + body
            hashtags = list(set(re.findall(r"#(\w+)", f"{title} {body}")))

            return Post(
                id=f"x_{tweet_id}",
                platform="x",
                post_title=f"{title} {body}".strip(),
                author=author,
                url=href,
                views=None,
                likes=None,
                reposts=None,
                comments=None,
                hashtags=hashtags,
                published_at=None,
                scraped_at=datetime.now(tz=timezone.utc),
                raw_data=ddg_data,
            )
        except Exception as exc:
            logger.debug(f"[x] Failed to create DDG post: {exc}")
            return None

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def _passes_filter(self, post: Post) -> bool:
        if self.filter_keywords is None:
            return True
        text = post.post_title.lower()
        return any(kw in text for kw in self.filter_keywords)
