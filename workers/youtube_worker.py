"""
youtube_worker.py — comprehensive YouTube scraper via yt-dlp (no API key).

Three-pronged strategy to capture every video about Claude:
  1. Search queries (relevance-sorted)
  2. Search queries (date-sorted)
  3. Channel scraping — Anthropic's official channel

Cookie handling: tries Chrome cookies first, falls back to no cookies
if macOS blocks access. For best results grant Terminal Full Disk Access
in System Settings → Privacy & Security → Full Disk Access.

Writes raw data progressively to disk as each video is processed.
"""

from __future__ import annotations

import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Any, Optional
from urllib.parse import quote

import yt_dlp

from models.post import Post
from workers.base import BaseWorker

logger = logging.getLogger(__name__)

SEARCH_QUERIES = [
    "claude ai",
    "anthropic claude",
    "claude sonnet",
    "claude opus",
    "claude haiku",
    "claude 3",
    "claude 3.5",
    "claude 3.7",
    "claude 4",
    "claude code",
    "claude computer use",
    "claude artifacts",
    "claude mcp",
    "claude api",
    "claude projects",
    "claude vs chatgpt",
    "claude vs gpt4",
    "claude vs gemini",
    "best ai coding assistant claude",
    "claude ai tutorial",
    "claude ai review",
    "anthropic ai model",
    "claude prompt engineering",
    "claude canvas",
]

CHANNEL_URLS = [
    "https://www.youtube.com/@AnthropicAI/videos",
]

MAX_SEARCH_PER_QUERY = 1000
WORKERS = 10


class YouTubeWorker(BaseWorker):
    platform = "youtube"

    def __init__(
        self,
        queries: list[str] | None = None,
        channel_urls: list[str] | None = None,
        max_search_per_query: int = MAX_SEARCH_PER_QUERY,
        fetch_comments: bool = False,
    ):
        self.queries = queries or SEARCH_QUERIES
        self.channel_urls = channel_urls or CHANNEL_URLS
        self.max_search_per_query = max_search_per_query
        self.fetch_comments = fetch_comments

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def scrape(self, raw_path: str | None = None) -> list[Post]:
        seen: set[str] = set()
        videos: list[Post] = []
        done = 0

        raw_file = None
        if raw_path:
            os.makedirs(os.path.dirname(raw_path), exist_ok=True)
            raw_file = open(raw_path, "w", encoding="utf-8")
            logger.info(f"[yt] Streaming raw data (NDJSON) → {raw_path}")

        def _process_batch(ids: list[str], label: str, pool: ThreadPoolExecutor) -> None:
            nonlocal done
            new_ids = []
            for vid_id in ids:
                if vid_id not in seen:
                    seen.add(vid_id)
                    new_ids.append(vid_id)
            logger.info(f"[yt] {label} → +{len(new_ids)} new (total seen: {len(seen)})")
            futures = {pool.submit(self._fetch_video, vid_id): vid_id for vid_id in new_ids}
            for future in as_completed(futures):
                done += 1
                try:
                    v = future.result()
                except Exception as e:
                    logger.debug(f"[yt] future error: {e}")
                    continue
                if v:
                    videos.append(v)
                    if raw_file and v.raw_data:
                        raw_file.write(json.dumps(v.raw_data, ensure_ascii=False, default=str) + "\n")
                        raw_file.flush()
                if done % 100 == 0:
                    logger.info(f"[yt] {done} processed — {len(videos)} videos saved")

        try:
            with ThreadPoolExecutor(max_workers=WORKERS) as pool:
                for query in self.queries:
                    _process_batch(self._search_relevance(query), f"relevance '{query}'", pool)
                for query in self.queries:
                    _process_batch(self._search_by_date(query), f"date '{query}'", pool)
                for ch_url in self.channel_urls:
                    _process_batch(self._scrape_channel(ch_url), ch_url, pool)
        finally:
            if raw_file:
                raw_file.close()
                logger.info(f"[yt] Raw file finalised: {raw_path}")

        logger.info(f"[yt] Done: {len(videos)} videos")
        return videos

    # ------------------------------------------------------------------
    # ID collection (no cookies needed for search)
    # ------------------------------------------------------------------

    def _search_relevance(self, query: str) -> list[str]:
        return self._extract_ids(f"ytsearch{self.max_search_per_query}:{query}")

    def _search_by_date(self, query: str) -> list[str]:
        url = f"https://www.youtube.com/results?search_query={quote(query)}&sp=CAI%3D"
        return self._extract_ids(url)

    def _scrape_channel(self, channel_url: str) -> list[str]:
        return self._extract_ids(channel_url)

    def _extract_ids(self, url: str) -> list[str]:
        ydl_opts: dict[str, Any] = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": True,
            "skip_download": True,
            "playlistend": self.max_search_per_query,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if not info:
                    return []
                if info.get("id") and "entries" not in info:
                    return [info["id"]]
                return [e["id"] for e in (info.get("entries") or []) if e and e.get("id")]
        except Exception as e:
            logger.warning(f"[yt] ID extraction failed for {url}: {e}")
            return []

    # ------------------------------------------------------------------
    # Video details — tries Chrome cookies, falls back to no cookies
    # ------------------------------------------------------------------

    def _fetch_video(self, video_id: str) -> Optional[Post]:
        url = f"https://www.youtube.com/watch?v={video_id}"
        base_opts: dict[str, Any] = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
        }
        # No cookies — avoids macOS keychain prompts
        for extra in ({},):
            try:
                with yt_dlp.YoutubeDL({**base_opts, **extra}) as ydl:
                    info = ydl.extract_info(url, download=False)
                if info:
                    return self._parse_video(info)
                return None
            except PermissionError:
                continue  # macOS blocked cookie access, try without
            except yt_dlp.utils.DownloadError as e:
                msg = str(e).lower()
                if any(x in msg for x in ("private", "unavailable", "removed", "sign in")):
                    return None
                logger.debug(f"[yt] DownloadError {video_id}: {e}")
                return None
            except Exception as e:
                logger.debug(f"[yt] Error {video_id}: {e}")
                return None
        return None

    # ------------------------------------------------------------------
    # Parser
    # ------------------------------------------------------------------

    def _parse_video(self, info: dict) -> Optional[Post]:
        try:
            vid_id   = info.get("id", "")
            title    = info.get("title", "")
            channel  = info.get("uploader") or info.get("channel") or "unknown"
            desc     = (info.get("description") or "")[:2000]
            tags     = info.get("tags") or []
            views    = int(info.get("view_count")    or 0)
            likes    = int(info.get("like_count")    or 0)
            n_cmts   = int(info.get("comment_count") or 0)
            duration = info.get("duration_string") or info.get("duration")
            ud       = info.get("upload_date")  # "YYYYMMDD"

            published_at = None
            if ud and len(ud) == 8:
                try:
                    published_at = datetime(
                        int(ud[:4]), int(ud[4:6]), int(ud[6:]), tzinfo=timezone.utc
                    )
                except ValueError:
                    pass

            now = datetime.now(tz=timezone.utc)
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
                duration=str(duration) if duration else None,
                published_at=published_at,
                scraped_at=now,
                raw_data={
                    "type": "video",
                    "video_id": vid_id,
                    "title": title,
                    "channel": channel,
                    "views": views,
                    "likes": likes,
                    "comment_count": n_cmts,
                    "duration": str(duration) if duration else None,
                    "upload_date": ud,
                    "tags": tags[:20],
                    "description": desc[:500],
                    "url": f"https://www.youtube.com/watch?v={vid_id}",
                },
            )
        except Exception as e:
            logger.debug(f"[yt] parse_video failed: {e}")
            return None
