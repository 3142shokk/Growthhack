"""
youtube_worker.py — YouTube scraper via official Data API v3.

Uses search.list to find videos, then videos.list to get full stats.
Quota: 10,000 units/day. search.list = 100 units, videos.list = 1 unit.

Reads API key from .env file (youtube_API=...).
"""

from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime, timezone
from typing import Any, Optional

from dotenv import load_dotenv
from googleapiclient.discovery import build

from models.post import Post
from workers.base import BaseWorker

load_dotenv()

logger = logging.getLogger(__name__)

SEARCH_QUERIES = [
    # Core
    "claude ai",
    "anthropic claude",
    "anthropic ai",
    "claude sonnet",
    "claude opus",
    "claude haiku",
    "claude 3",
    "claude 3.5",
    "claude 3.7",
    "claude 4",
    # Features
    "claude code",
    "claude computer use",
    "claude artifacts",
    "claude mcp",
    "claude api",
    "claude projects",
    "claude canvas",
    "claude prompt engineering",
    "claude system prompt",
    "claude extended thinking",
    "claude max plan",
    "claude pro",
    # Comparisons
    "claude vs chatgpt",
    "claude vs gpt4",
    "claude vs gemini",
    "claude vs deepseek",
    "claude vs copilot",
    "claude vs cursor",
    "chatgpt vs claude coding",
    "best ai for coding claude",
    "best ai assistant claude",
    # Tutorials / reviews
    "claude ai tutorial",
    "claude ai review",
    "claude ai beginner",
    "how to use claude",
    "claude ai tips",
    "claude ai for developers",
    "claude ai for writing",
    # People / company
    "anthropic ai model",
    "dario amodei",
    "anthropic safety",
    "anthropic funding",
    # Use cases
    "claude ai coding",
    "claude ai data analysis",
    "claude ai automation",
    "build app with claude",
    "claude ai workflow",
    "claude cursor ide",
    "claude windsurf",
    "claude cline",
]

MAX_RESULTS_PER_QUERY = 50  # max allowed by API per page
MAX_PAGES_PER_SEARCH = 1    # limit pagination to save quota (1 page = 50 results)


class YouTubeWorker(BaseWorker):
    platform = "youtube"

    def __init__(
        self,
        queries: list[str] | None = None,
        channel_urls: list[str] | None = None,  # kept for interface compat
        max_search_per_query: int = 200,
        fetch_comments: bool = False,
    ):
        self.queries = queries or SEARCH_QUERIES
        self.max_search_per_query = max_search_per_query
        api_key = os.getenv("youtube_API")
        if not api_key:
            raise RuntimeError("youtube_API not found in .env")
        self._youtube = build("youtube", "v3", developerKey=api_key)

    def scrape(self, raw_path: str | None = None) -> list[Post]:
        progress_path = os.path.join(
            os.path.dirname(raw_path or "data/raw/yt.json"),
            "youtube_progress.json",
        )

        # Load previous progress
        videos: list[Post] = []
        done_ids: set[str] = set()
        if os.path.exists(progress_path):
            try:
                with open(progress_path, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                for item in saved:
                    done_ids.add(item.get("id", "").replace("yt_video_", ""))
                    videos.append(Post(**item))
                logger.info(f"[yt] Resuming: {len(done_ids)} already fetched")
            except Exception:
                pass

        # 1. Collect video IDs via search
        all_video_ids: list[str] = []
        seen: set[str] = set(done_ids)

        for order in ("relevance", "date"):
            for query in self.queries:
                ids = self._search_videos(query, order=order)
                added = 0
                for vid_id in ids:
                    if vid_id not in seen:
                        seen.add(vid_id)
                        all_video_ids.append(vid_id)
                        added += 1
                if added > 0:
                    logger.info(f"[yt] {order} '{query}' → +{added} new (total queue: {len(all_video_ids)})")

        logger.info(f"[yt] New videos to fetch details: {len(all_video_ids)}")

        # 2. Fetch video details in batches of 50
        raw_file = None
        first_entry = len(done_ids) == 0
        if raw_path:
            os.makedirs(os.path.dirname(raw_path), exist_ok=True)
            mode = "a" if done_ids else "w"
            raw_file = open(raw_path, mode, encoding="utf-8")
            if not done_ids:
                raw_file.write("[\n")

        try:
            for i in range(0, len(all_video_ids), 50):
                batch = all_video_ids[i:i + 50]
                batch_posts = self._fetch_video_details(batch)

                for post in batch_posts:
                    videos.append(post)
                    if raw_file and post.raw_data:
                        if not first_entry:
                            raw_file.write(",\n")
                        json.dump(post.raw_data, raw_file, ensure_ascii=False, default=str)
                        raw_file.flush()
                        first_entry = False

                # Save progress every 200 videos
                if len(videos) % 200 < 50:
                    self._save_progress(videos, progress_path)

                logger.info(
                    f"[yt] Fetched {min(i + 50, len(all_video_ids))}/{len(all_video_ids)} "
                    f"— {len(videos)} total videos"
                )
                time.sleep(0.5)

        except KeyboardInterrupt:
            logger.info(f"[yt] Interrupted! Saving {len(videos)} videos...")

        self._save_progress(videos, progress_path)

        if raw_file:
            raw_file.write("\n]")
            raw_file.close()

        logger.info(f"[yt] Done: {len(videos)} videos")
        return videos

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def _search_videos(self, query: str, order: str = "relevance") -> list[str]:
        """Search YouTube and return video IDs. Pages through results."""
        video_ids: list[str] = []
        page_token = None
        pages = 0

        while len(video_ids) < self.max_search_per_query and pages < MAX_PAGES_PER_SEARCH:
            try:
                request = self._youtube.search().list(
                    q=query,
                    part="id",
                    type="video",
                    maxResults=min(MAX_RESULTS_PER_QUERY, self.max_search_per_query - len(video_ids)),
                    pageToken=page_token,
                    order=order,
                )
                response = request.execute()

                for item in response.get("items", []):
                    vid_id = item.get("id", {}).get("videoId")
                    if vid_id:
                        video_ids.append(vid_id)

                page_token = response.get("nextPageToken")
                pages += 1
                if not page_token:
                    break

                time.sleep(0.2)

            except Exception as e:
                logger.warning(f"[yt] Search error for '{query}': {e}")
                break

        return video_ids

    # ------------------------------------------------------------------
    # Video details (batch)
    # ------------------------------------------------------------------

    def _fetch_video_details(self, video_ids: list[str]) -> list[Post]:
        """Fetch full details for up to 50 videos in one API call (1 quota unit)."""
        posts: list[Post] = []
        try:
            request = self._youtube.videos().list(
                id=",".join(video_ids),
                part="snippet,statistics,contentDetails",
            )
            response = request.execute()

            for item in response.get("items", []):
                post = self._parse_video(item)
                if post:
                    posts.append(post)

        except Exception as e:
            logger.warning(f"[yt] Video details error: {e}")

        return posts

    # ------------------------------------------------------------------
    # Parser
    # ------------------------------------------------------------------

    def _parse_video(self, item: dict) -> Optional[Post]:
        try:
            vid_id = item["id"]
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})
            content = item.get("contentDetails", {})

            title = snippet.get("title", "")
            channel = snippet.get("channelTitle", "unknown")
            desc = (snippet.get("description") or "")[:2000]
            tags = snippet.get("tags") or []
            published = snippet.get("publishedAt", "")

            views = int(stats.get("viewCount", 0))
            likes = int(stats.get("likeCount", 0))
            n_cmts = int(stats.get("commentCount", 0))
            duration = content.get("duration", "")

            published_at = None
            if published:
                try:
                    published_at = datetime.fromisoformat(published.replace("Z", "+00:00"))
                except ValueError:
                    pass

            return Post(
                id=f"yt_video_{vid_id}",
                platform="youtube",
                post_title=title[:500],
                author=channel,
                url=f"https://www.youtube.com/watch?v={vid_id}",
                views=views,
                likes=likes,
                comments=n_cmts,
                hashtags=tags[:20],
                description=desc,
                duration=duration,
                published_at=published_at,
                scraped_at=datetime.now(tz=timezone.utc),
                raw_data={
                    "type": "video",
                    "video_id": vid_id,
                    "title": title,
                    "channel": channel,
                    "views": views,
                    "likes": likes,
                    "comment_count": n_cmts,
                    "duration": duration,
                    "upload_date": published,
                    "tags": tags[:20],
                    "description": desc[:500],
                    "url": f"https://www.youtube.com/watch?v={vid_id}",
                },
            )
        except Exception as e:
            logger.debug(f"[yt] parse_video failed: {e}")
            return None

    # ------------------------------------------------------------------
    # Progress
    # ------------------------------------------------------------------

    def _save_progress(self, videos: list[Post], path: str) -> None:
        data = [v.model_dump(mode="json") for v in videos]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, default=str, ensure_ascii=False)
        logger.info(f"[yt] Progress saved: {len(videos)} videos -> {path}")
