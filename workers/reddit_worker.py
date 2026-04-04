"""
Reddit scraper — uses Arctic Shift API for bulk historical Reddit data.

Arctic Shift (arctic-shift.photon-reddit.com) archives Reddit posts and
exposes them via a search API with no result caps. Pagination is done by
sliding the `after` parameter to the `created_utc` of the last returned post.

Strategy (targeting 1M+ posts)
-------------------------------
1. Per-subreddit full crawl: for each configured subreddit, paginate through
   ALL posts in the configured date range. This is the highest-yield approach.
2. Keyword search: search across all of Reddit for each configured query term.

Rate Limiting
-------------
Arctic Shift has no documented rate limit but is a community resource.
We use a 1s delay between requests and exponential backoff on errors.

Incremental Saves
-----------------
Posts are saved to disk every 500 new posts, so progress is never lost.
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import requests

import config
from models.post import Post
from workers.base import BaseWorker

logger = logging.getLogger(__name__)

_BASE = "https://arctic-shift.photon-reddit.com"
_REQUEST_DELAY = 1.0        # seconds between requests
_ERROR_BACKOFF_BASE = 3.0   # seconds base for exponential backoff
_MAX_RETRIES = 5


class RedditWorker(BaseWorker):
    platform = "reddit"

    def __init__(
        self,
        subreddits: list[str] | None = None,
        search_queries: list[str] | None = None,
        target_total: int = 1_000_000,
        weeks_back: int = 52,
        filter_keywords: list[str] | None = None,
    ):
        self.subreddits = subreddits or config.REDDIT_SUBREDDITS
        self.search_queries = search_queries or config.REDDIT_SEARCH_QUERIES
        self.target_total = target_total
        self.weeks_back = weeks_back
        self.filter_keywords = (
            [k.lower() for k in filter_keywords] if filter_keywords
            else [k.lower() for k in config.CLAUDE_KEYWORDS]
        )
        self._session = requests.Session()
        self._seen_ids: set[str] = set()
        self._posts: list[Post] = []
        self._request_count = 0
        self._error_count = 0
        self._last_save_count = 0

        # Compute date range
        self._end_date = datetime.now(tz=timezone.utc)
        self._start_date = self._end_date - timedelta(weeks=weeks_back)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def scrape(self) -> list[Post]:
        self._load_progress()

        logger.info(
            f"[reddit] Starting Arctic Shift scrape: "
            f"{len(self.subreddits)} subreddits, "
            f"{len(self.search_queries)} queries, "
            f"date range: {self._start_date.date()} to {self._end_date.date()}, "
            f"target={self.target_total:,}, already have={len(self._posts):,}"
        )

        try:
            # Phase 1: Full subreddit crawls (highest yield)
            self._phase_subreddit_crawl()
            if self._hit_target():
                return self._posts

            # Phase 2: Keyword searches across all of Reddit
            self._phase_keyword_search()
        except KeyboardInterrupt:
            logger.info(f"[reddit] Interrupted! Saving {len(self._posts):,} posts...")
            self._save_progress()
            raise

        self._save_progress()

        logger.info(
            f"[reddit] Scrape complete: {len(self._posts):,} unique posts "
            f"({self._request_count:,} API requests, "
            f"{self._error_count} errors)"
        )
        return self._posts

    def _hit_target(self) -> bool:
        if len(self._posts) >= self.target_total:
            logger.info(f"[reddit] Target reached: {len(self._posts):,} posts")
            self._save_progress()
            return True
        return False

    # ------------------------------------------------------------------
    # Phase 1: Full subreddit crawl
    # ------------------------------------------------------------------

    def _phase_subreddit_crawl(self) -> None:
        logger.info("[reddit] Phase 1: Full subreddit crawl via Arctic Shift")
        for si, sub in enumerate(self.subreddits):
            count_before = len(self._posts)
            self._crawl_all_posts(subreddit=sub)
            gained = len(self._posts) - count_before
            logger.info(
                f"[reddit] Phase 1: r/{sub} done ({si+1}/{len(self.subreddits)}), "
                f"+{gained:,} posts, total={len(self._posts):,}"
            )
            if self._hit_target():
                return

    # ------------------------------------------------------------------
    # Phase 2: Keyword search across all subreddits
    # ------------------------------------------------------------------

    def _phase_keyword_search(self) -> None:
        logger.info("[reddit] Phase 2: Keyword search across all of Reddit")
        for qi, query in enumerate(self.search_queries):
            count_before = len(self._posts)
            self._crawl_all_posts(query=query)
            gained = len(self._posts) - count_before
            logger.info(
                f"[reddit] Phase 2: query '{query}' done ({qi+1}/{len(self.search_queries)}), "
                f"+{gained:,} posts, total={len(self._posts):,}"
            )
            if self._hit_target():
                return

    # ------------------------------------------------------------------
    # Core crawl: paginate through Arctic Shift results
    # ------------------------------------------------------------------

    def _crawl_all_posts(
        self,
        subreddit: str | None = None,
        query: str | None = None,
    ) -> None:
        """Paginate through all matching posts using created_utc sliding."""
        params: dict[str, Any] = {
            "sort": "asc",
            "limit": 100,
            "after": int(self._start_date.timestamp()),
            "before": int(self._end_date.timestamp()),
        }
        if subreddit:
            params["subreddit"] = subreddit
        if query:
            params["query"] = query

        pages = 0
        while True:
            data = self._api_get("/api/posts/search", params)
            if data is None:
                break

            posts_raw = data.get("data", [])
            if not posts_raw:
                break

            parsed = []
            for raw in posts_raw:
                post = self._parse_post(raw)
                if post and self._passes_filter(post):
                    parsed.append(post)
            self._collect(parsed)

            pages += 1
            if pages % 50 == 0:
                sub_label = f"r/{subreddit}" if subreddit else f"q='{query}'"
                logger.info(
                    f"[reddit] {sub_label}: page {pages}, "
                    f"{len(self._posts):,} total unique posts"
                )

            if len(posts_raw) < 100:
                break

            # Slide the after parameter to the last post's created_utc
            last_ts = posts_raw[-1].get("created_utc")
            if last_ts is None:
                break
            params["after"] = last_ts

            if self._hit_target():
                return

            time.sleep(_REQUEST_DELAY)

    # ------------------------------------------------------------------
    # HTTP layer
    # ------------------------------------------------------------------

    def _api_get(self, path: str, params: dict) -> Optional[dict]:
        """GET request with retries and exponential backoff."""
        url = f"{_BASE}{path}"
        self._request_count += 1

        for attempt in range(_MAX_RETRIES):
            try:
                resp = self._session.get(url, params=params, timeout=30)

                if resp.status_code == 200:
                    return resp.json()

                if resp.status_code == 429:
                    self._error_count += 1
                    wait = _ERROR_BACKOFF_BASE * (2 ** attempt)
                    logger.warning(
                        f"[reddit] Rate limited, waiting {wait:.0f}s "
                        f"({len(self._posts):,} posts so far)"
                    )
                    self._save_progress()
                    time.sleep(wait)
                    continue

                if resp.status_code >= 500:
                    self._error_count += 1
                    wait = _ERROR_BACKOFF_BASE * (2 ** attempt)
                    logger.warning(
                        f"[reddit] Server error {resp.status_code}, waiting {wait:.0f}s"
                    )
                    time.sleep(wait)
                    continue

                logger.error(f"[reddit] HTTP {resp.status_code} for {url}")
                self._error_count += 1
                return None

            except requests.RequestException as exc:
                self._error_count += 1
                logger.error(f"[reddit] Request failed: {exc}")
                if attempt < _MAX_RETRIES - 1:
                    time.sleep(_ERROR_BACKOFF_BASE * (2 ** attempt))

        return None

    # ------------------------------------------------------------------
    # Collection + deduplication
    # ------------------------------------------------------------------

    def _collect(self, posts: list[Post]) -> None:
        for p in posts:
            if p.id not in self._seen_ids:
                self._seen_ids.add(p.id)
                self._posts.append(p)

        new_since_save = len(self._posts) - self._last_save_count
        if new_since_save >= config.REDDIT_SAVE_EVERY:
            self._save_progress()

    # ------------------------------------------------------------------
    # Progress persistence
    # ------------------------------------------------------------------

    def _progress_path(self) -> str:
        os.makedirs(config.RAW_DIR, exist_ok=True)
        return os.path.join(config.RAW_DIR, "reddit_progress.json")

    def _save_progress(self) -> None:
        if not self._posts:
            return
        path = self._progress_path()
        data = [p.model_dump(mode="json") for p in self._posts]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, default=str)
        self._last_save_count = len(self._posts)
        logger.info(f"[reddit] Progress saved: {len(self._posts):,} posts -> {path}")

    def _load_progress(self) -> None:
        path = self._progress_path()
        if not os.path.exists(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for item in data:
                pid = item.get("id", "")
                if pid not in self._seen_ids:
                    self._seen_ids.add(pid)
                    self._posts.append(Post(**item))
            logger.info(f"[reddit] Loaded {len(self._posts):,} posts from previous run")
        except Exception as exc:
            logger.warning(f"[reddit] Could not load progress: {exc}")

    # ------------------------------------------------------------------
    # Post parsing
    # ------------------------------------------------------------------

    def _parse_post(self, data: dict[str, Any]) -> Optional[Post]:
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

            url = f"https://www.reddit.com{permalink}" if permalink else ""

            hashtags = [subreddit]
            if link_flair:
                hashtags.append(link_flair.replace(" ", "_"))
            hashtags.extend(re.findall(r"#(\w+)", selftext))

            published_at = None
            if created_utc:
                published_at = datetime.fromtimestamp(created_utc, tz=timezone.utc)

            return Post(
                id=f"reddit_{post_id}",
                platform="reddit",
                post_title=title,
                author=author,
                url=url,
                views=None,
                likes=score,
                reposts=num_crossposts,
                comments=num_comments,
                hashtags=hashtags,
                description=selftext[:2000] if selftext else None,
                published_at=published_at,
                scraped_at=datetime.now(tz=timezone.utc),
                engagement_rate=None,
                raw_data=data,
            )
        except Exception as exc:
            logger.debug(f"[reddit] Failed to parse post: {exc}")
            return None

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    def _passes_filter(self, post: Post) -> bool:
        if self.filter_keywords is None:
            return True
        text = f"{post.post_title} {post.description or ''}".lower()
        return any(kw in text for kw in self.filter_keywords)
