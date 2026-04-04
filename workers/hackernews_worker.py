"""
hackernews_worker.py — scrapes Hacker News via the Algolia HN Search API.
No auth required. Free tier covers all our needs.

Strategy
--------
1. Search stories mentioning Claude/Anthropic keywords (relevance + date sort).
2. Search comments mentioning Claude/Anthropic — comment text reveals what
   practitioners actually think, ideal for sentiment + topic analysis.
3. Deduplicate by objectID across all queries.

API docs: https://hn.algolia.com/api
Rate limit: ~10k requests/hour (unauthenticated).

Data collected
--------------
Stories : title, url, points, num_comments, author, created_at, story_text
Comments: text, author, story_id, parent_id, created_at, story_title (if available)
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Any, Optional

import requests

import config
from models.post import Post
from workers.base import BaseWorker

logger = logging.getLogger(__name__)

_BASE = "https://hn.algolia.com/api/v1"
_HEADERS = {"User-Agent": "ClaudeGrowthMachine/1.0 (HackNU 2026 research)"}
_DELAY = 0.5  # seconds between requests

HN_QUERIES = [
    "Claude",
    "Anthropic",
]

MAX_PAGES_PER_QUERY = 10  # 10 pages × 200 hits = up to 2000 hits per query
HITS_PER_PAGE = 200


class HackerNewsWorker(BaseWorker):
    platform = "hacker_news"

    def __init__(
        self,
        queries: list[str] | None = None,
        fetch_comments: bool = True,
        max_pages: int = MAX_PAGES_PER_QUERY,
        story_comments_min_points: int = 0,
    ):
        self.queries = queries or HN_QUERIES
        self.fetch_comments = fetch_comments
        self.max_pages = max_pages
        self.story_comments_min_points = story_comments_min_points
        self._session = requests.Session()
        self._session.headers.update(_HEADERS)

    def scrape(self) -> list[Post]:
        posts: list[Post] = []
        seen: set[str] = set()

        for query in self.queries:
            # Relevance-ranked stories
            for p in self._search(query, tags="story", sort="search"):
                if p.id not in seen:
                    seen.add(p.id)
                    posts.append(p)

            # Date-sorted stories (catches recent ones relevance misses)
            for p in self._search(query, tags="story", sort="search_by_date"):
                if p.id not in seen:
                    seen.add(p.id)
                    posts.append(p)

            if self.fetch_comments:
                for p in self._search(query, tags="comment", sort="search"):
                    if p.id not in seen:
                        seen.add(p.id)
                        posts.append(p)

            logger.info(f"[hn] '{query}' → {len(posts)} total so far")

        logger.info(f"[hn] Total collected: {len(posts)}")
        return posts

    # Keywords that must appear in the story title to be considered on-topic
    _TITLE_KEYWORDS = ["claude", "anthropic"]

    def _story_is_on_topic(self, story: Post) -> bool:
        """Return True only if the story title actually mentions Claude/Anthropic."""
        title_lower = (story.post_title or "").lower()
        desc_lower = (story.description or "").lower()
        return any(kw in title_lower or kw in desc_lower for kw in self._TITLE_KEYWORDS)

    def scrape_story_comments(self, stories: list[Post]) -> list[Post]:
        """
        Given a list of already-scraped story Posts, fetch ALL comments for
        stories that meet the min_points threshold AND are actually about Claude.

        Uses Algolia tag filter: tags=comment,story_{id} — returns every comment
        in that thread regardless of whether it mentions Claude keywords.
        """
        targets = [
            s for s in stories
            if s.raw_data and s.raw_data.get("type") == "story"
            and (s.likes or 0) >= self.story_comments_min_points
        ]
        logger.info(
            f"[hn] Fetching all comments for {len(targets)} stories "
            f"(>={self.story_comments_min_points} pts)"
        )

        all_comments: list[Post] = []
        seen: set[str] = set()

        for i, story in enumerate(targets):
            story_id = story.raw_data.get("objectID") or story.id.replace("hn_story_", "")
            story_title = story.post_title
            comments = self._fetch_all_story_comments(story_id, story_title)
            for c in comments:
                if c.id not in seen:
                    seen.add(c.id)
                    all_comments.append(c)

            if (i + 1) % 20 == 0:
                logger.info(f"[hn] {i+1}/{len(targets)} stories processed, {len(all_comments)} comments so far")

        logger.info(f"[hn] story_comments total: {len(all_comments)}")
        return all_comments

    def _fetch_all_story_comments(self, story_id: str, story_title: str) -> list[Post]:
        """Fetch all comments for a single story via Algolia tag filter."""
        comments: list[Post] = []
        for page in range(20):  # up to 20 pages × 200 = 4000 comments per story
            data = self._get(
                "/search_by_date",
                params={
                    "tags": f"comment,story_{story_id}",
                    "hitsPerPage": HITS_PER_PAGE,
                    "page": page,
                },
            )
            if not data:
                break

            hits = data.get("hits", [])
            if not hits:
                break

            for hit in hits:
                # Inject story_title so _parse_hit can use it
                hit.setdefault("story_title", story_title)
                post = self._parse_hit(hit, item_type="comment")
                if post:
                    comments.append(post)

            nb_pages = data.get("nbPages", 0)
            if page >= nb_pages - 1:
                break

            time.sleep(_DELAY)

        return comments

    # ------------------------------------------------------------------

    def _search(self, query: str, tags: str, sort: str) -> list[Post]:
        results: list[Post] = []
        for page in range(self.max_pages):
            data = self._get(
                f"/{sort}",
                params={
                    "query": query,
                    "tags": tags,
                    "hitsPerPage": HITS_PER_PAGE,
                    "page": page,
                },
            )
            if not data:
                break

            hits = data.get("hits", [])
            if not hits:
                break

            for hit in hits:
                post = self._parse_hit(hit, item_type=tags)
                if post:
                    results.append(post)

            # Stop early if we've fetched all pages
            nb_pages = data.get("nbPages", 0)
            if page >= nb_pages - 1:
                break

            time.sleep(_DELAY)

        return results

    def _get(self, path: str, params: dict | None = None) -> Optional[dict]:
        url = f"{_BASE}{path}"
        for attempt in range(3):
            try:
                resp = self._session.get(url, params=params, timeout=15)
                if resp.status_code == 200:
                    return resp.json()
                if resp.status_code == 429:
                    wait = 2 ** (attempt + 2)
                    logger.warning(f"[hn] Rate limited, waiting {wait}s")
                    time.sleep(wait)
                    continue
                logger.warning(f"[hn] HTTP {resp.status_code} for {url}")
                return None
            except requests.RequestException as e:
                logger.warning(f"[hn] Request error: {e}")
                time.sleep(2)
        return None

    def _parse_hit(self, hit: dict[str, Any], item_type: str) -> Optional[Post]:
        try:
            obj_id = hit.get("objectID", "")
            author = hit.get("author") or "unknown"
            created_at_iso = hit.get("created_at")
            published_at = None
            if created_at_iso:
                try:
                    published_at = datetime.fromisoformat(
                        created_at_iso.replace("Z", "+00:00")
                    )
                except ValueError:
                    pass

            tags_list: list[str] = hit.get("_tags", [])

            if item_type == "story":
                title = hit.get("title") or ""
                url = hit.get("url") or f"https://news.ycombinator.com/item?id={obj_id}"
                points = hit.get("points") or 0
                num_comments = hit.get("num_comments") or 0
                story_text = hit.get("story_text") or ""

                return Post(
                    id=f"hn_story_{obj_id}",
                    platform="hacker_news",
                    post_title=title,
                    author=author,
                    url=url,
                    likes=points,
                    comments=num_comments,
                    hashtags=[t for t in tags_list if not t.startswith("author_")],
                    description=story_text[:2000] if story_text else None,
                    published_at=published_at,
                    scraped_at=datetime.now(tz=timezone.utc),
                    raw_data={
                        "objectID": obj_id,
                        "type": "story",
                        "points": points,
                        "num_comments": num_comments,
                        "title": title,
                        "url": hit.get("url"),
                        "story_text": story_text[:500] if story_text else None,
                    },
                )

            elif item_type == "comment":
                comment_text = hit.get("comment_text") or ""
                story_id = hit.get("story_id")
                story_title = hit.get("story_title") or ""
                parent_id = hit.get("parent_id")
                hn_url = f"https://news.ycombinator.com/item?id={obj_id}"

                # Use story title as post_title so we know what it's in response to
                title = f"[comment on] {story_title}" if story_title else "[comment]"

                return Post(
                    id=f"hn_comment_{obj_id}",
                    platform="hacker_news",
                    post_title=title[:500],
                    author=author,
                    url=hn_url,
                    hashtags=[t for t in tags_list if not t.startswith("author_")],
                    description=comment_text[:2000],
                    published_at=published_at,
                    scraped_at=datetime.now(tz=timezone.utc),
                    raw_data={
                        "objectID": obj_id,
                        "type": "comment",
                        "story_id": story_id,
                        "story_title": story_title,
                        "parent_id": parent_id,
                        "comment_text": comment_text[:1000],
                    },
                )

        except Exception as e:
            logger.debug(f"[hn] Failed to parse hit: {e}")
        return None
