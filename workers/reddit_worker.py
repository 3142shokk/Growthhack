"""
Reddit scraper — public JSON API, no authentication required.

Strategy
--------
1. Hit Reddit's public JSON endpoints (append .json to any URL).
2. Search across relevant subreddits and site-wide for Claude-related posts.
3. For each post, extract title, score (upvotes), comments count, crossposts,
   author, flair, and selftext.
4. Paginate using the `after` token (Reddit returns 25-100 posts per page).

Rate Limiting
-------------
Reddit's public JSON API allows ~60 requests/minute without auth.
We use a 1.5s delay between requests and respect 429 responses with backoff.

Limitations
-----------
- Reddit does not expose view counts publicly → views is always None.
- Score = upvotes - downvotes (fuzzing applied by Reddit), not raw upvote count.
- Deleted/removed posts may appear with [deleted] author or [removed] body.
"""

from __future__ import annotations

import logging
import re
import time
from datetime import datetime, timezone
from typing import Any, Optional

import requests

import config
from models.post import Post
from workers.base import BaseWorker

logger = logging.getLogger(__name__)

# Public JSON API base
_BASE = "https://www.reddit.com"
_HEADERS = {
    "User-Agent": "ClaudeGrowthMachine/1.0 (HackNU 2026 research project)",
}


class RedditWorker(BaseWorker):
    platform = "reddit"

    def __init__(
        self,
        subreddits: list[str] | None = None,
        search_queries: list[str] | None = None,
        max_posts_per_query: int = 200,
        sort: str = "relevance",
        time_filter: str = "month",
        filter_keywords: list[str] | None = None,
    ):
        self.subreddits = subreddits or config.REDDIT_SUBREDDITS
        self.search_queries = search_queries or config.REDDIT_SEARCH_QUERIES
        self.max_posts_per_query = max_posts_per_query
        self.sort = sort
        self.time_filter = time_filter
        self.filter_keywords = (
            [k.lower() for k in filter_keywords] if filter_keywords else None
        )
        self._session = requests.Session()
        self._session.headers.update(_HEADERS)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def scrape(self) -> list[Post]:
        all_posts: list[Post] = []
        seen_ids: set[str] = set()

        # 1. Site-wide search for each query
        for query in self.search_queries:
            posts = self._search_site(query)
            for p in posts:
                if p.id not in seen_ids:
                    seen_ids.add(p.id)
                    all_posts.append(p)
            logger.info(f"[reddit] site search '{query}': {len(posts)} posts")

        # 2. Per-subreddit search
        for sub in self.subreddits:
            for query in self.search_queries:
                posts = self._search_subreddit(sub, query)
                for p in posts:
                    if p.id not in seen_ids:
                        seen_ids.add(p.id)
                        all_posts.append(p)
                logger.info(f"[reddit] r/{sub} search '{query}': {len(posts)} posts")

        # 3. Hot/top posts from target subreddits (catches posts without exact keyword match)
        for sub in self.subreddits:
            posts = self._fetch_listing(f"/r/{sub}/top.json", params={"t": self.time_filter})
            for p in posts:
                if p.id not in seen_ids and self._passes_filter(p):
                    seen_ids.add(p.id)
                    all_posts.append(p)
            logger.info(f"[reddit] r/{sub} top: {len(posts)} posts")

        logger.info(f"[reddit] Total: {len(all_posts)} unique posts")
        return all_posts

    # ------------------------------------------------------------------
    # Search methods
    # ------------------------------------------------------------------

    def _search_site(self, query: str) -> list[Post]:
        """Site-wide search via /search.json."""
        return self._fetch_listing(
            "/search.json",
            params={"q": query, "sort": self.sort, "t": self.time_filter},
        )

    def _search_subreddit(self, subreddit: str, query: str) -> list[Post]:
        """Subreddit-scoped search via /r/{sub}/search.json."""
        return self._fetch_listing(
            f"/r/{subreddit}/search.json",
            params={
                "q": query,
                "restrict_sr": "on",
                "sort": self.sort,
                "t": self.time_filter,
            },
        )

    # ------------------------------------------------------------------
    # Pagination + fetching
    # ------------------------------------------------------------------

    def _fetch_listing(self, path: str, params: dict | None = None) -> list[Post]:
        """Fetch a Reddit listing endpoint with pagination."""
        posts: list[Post] = []
        params = dict(params or {})
        params["limit"] = 100  # max per page
        after: Optional[str] = None

        while len(posts) < self.max_posts_per_query:
            if after:
                params["after"] = after

            data = self._get_json(path, params)
            if not data:
                break

            listing = data.get("data", {})
            children = listing.get("children", [])
            if not children:
                break

            for child in children:
                if child.get("kind") != "t3":  # t3 = link/post
                    continue
                post = self._parse_post(child["data"])
                if post:
                    posts.append(post)

            after = listing.get("after")
            if not after:
                break

            time.sleep(config.REDDIT_REQUEST_DELAY)

        return posts[: self.max_posts_per_query]

    def _get_json(self, path: str, params: dict | None = None) -> Optional[dict]:
        """Make a GET request to Reddit's JSON API with retry logic."""
        url = f"{_BASE}{path}"
        for attempt in range(config.REDDIT_MAX_RETRIES):
            try:
                resp = self._session.get(url, params=params, timeout=15)

                if resp.status_code == 200:
                    return resp.json()

                if resp.status_code == 429:
                    wait = 2 ** (attempt + 1)
                    logger.warning(f"[reddit] Rate limited, waiting {wait}s")
                    time.sleep(wait)
                    continue

                if resp.status_code >= 500:
                    logger.warning(f"[reddit] Server error {resp.status_code}, retrying")
                    time.sleep(2)
                    continue

                logger.error(f"[reddit] HTTP {resp.status_code} for {url}")
                return None

            except requests.RequestException as exc:
                logger.error(f"[reddit] Request failed: {exc}")
                if attempt < config.REDDIT_MAX_RETRIES - 1:
                    time.sleep(2)

        return None

    # ------------------------------------------------------------------
    # Post parsing
    # ------------------------------------------------------------------

    def _parse_post(self, data: dict[str, Any]) -> Optional[Post]:
        """Convert a Reddit post JSON object into a Post model."""
        try:
            post_id = data.get("id", "")
            subreddit = data.get("subreddit", "")
            title = data.get("title", "")
            selftext = data.get("selftext", "") or ""
            author = data.get("author", "[deleted]")
            permalink = data.get("permalink", "")
            score = data.get("score", 0)
            num_comments = data.get("num_comments", 0)
            num_crossposts = data.get("num_crossposts", 0)
            created_utc = data.get("created_utc", 0)
            link_flair = data.get("link_flair_text") or ""

            # Build URL
            url = f"https://www.reddit.com{permalink}" if permalink else ""

            # Extract hashtag-like tokens: subreddit name + flair
            hashtags = [subreddit]
            if link_flair:
                hashtags.append(link_flair.replace(" ", "_"))
            # Also extract any #tags from selftext (uncommon on Reddit but exists)
            hashtags.extend(re.findall(r"#(\w+)", selftext))

            # Timestamp
            published_at = None
            if created_utc:
                published_at = datetime.fromtimestamp(created_utc, tz=timezone.utc)

            return Post(
                id=f"reddit_{post_id}",
                platform="reddit",
                post_title=title,
                author=author,
                url=url,
                views=None,  # Reddit doesn't expose view counts publicly
                likes=score,
                reposts=num_crossposts,
                comments=num_comments,
                hashtags=hashtags,
                description=selftext[:2000] if selftext else None,
                published_at=published_at,
                scraped_at=datetime.now(tz=timezone.utc),
                engagement_rate=None,  # No views → can't compute
                raw_data=data,
            )
        except Exception as exc:
            logger.debug(f"[reddit] Failed to parse post: {exc}")
            return None

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def _passes_filter(self, post: Post) -> bool:
        """Filter posts by Claude-related keywords (used for top/hot listings)."""
        if self.filter_keywords is None:
            return True
        text = f"{post.post_title} {post.description or ''}".lower()
        return any(kw in text for kw in self.filter_keywords)
