#!/usr/bin/env python3
"""YouTube scraper for Higgsfield — uses YouTube Data API v3."""
import json
import logging
import os
import time
from datetime import datetime, timezone

from dotenv import load_dotenv
from googleapiclient.discovery import build

import config
from models.post import Post
from storage.exporter import export_csv, export_json

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)

API_KEY = os.getenv("youtube_API")
PROGRESS_PATH = os.path.join(config.RAW_DIR, "higgsfield_youtube_progress.json")

QUERIES = [
    "higgsfield",
    "higgsfield ai",
    "higgsfield.ai",
    "higgsfield app",
    "higgsfield video generation",
    "higgsfield tutorial",
    "higgsfield review",
    "higgsfield demo",
    "higgsfield ai video",
    "higgsfield text to video",
]

yt = build("youtube", "v3", developerKey=API_KEY)


def search_videos(query, order="relevance"):
    ids = []
    try:
        resp = yt.search().list(q=query, part="id", type="video", maxResults=50, order=order).execute()
        for item in resp.get("items", []):
            vid = item.get("id", {}).get("videoId")
            if vid:
                ids.append(vid)
    except Exception as e:
        logger.warning(f"Search error '{query}': {e}")
    return ids


def fetch_details(video_ids):
    posts = []
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        try:
            resp = yt.videos().list(id=",".join(batch), part="snippet,statistics,contentDetails").execute()
            for item in resp.get("items", []):
                vid_id = item["id"]
                snippet = item.get("snippet", {})
                stats = item.get("statistics", {})
                content = item.get("contentDetails", {})
                published = snippet.get("publishedAt", "")
                published_at = None
                if published:
                    try:
                        published_at = datetime.fromisoformat(published.replace("Z", "+00:00"))
                    except ValueError:
                        pass

                posts.append(Post(
                    id=f"yt_video_{vid_id}",
                    platform="youtube",
                    post_title=snippet.get("title", "")[:500],
                    author=snippet.get("channelTitle", ""),
                    url=f"https://www.youtube.com/watch?v={vid_id}",
                    views=int(stats.get("viewCount", 0)),
                    likes=int(stats.get("likeCount", 0)),
                    comments=int(stats.get("commentCount", 0)),
                    hashtags=(snippet.get("tags") or [])[:20],
                    description=(snippet.get("description") or "")[:2000],
                    duration=content.get("duration", ""),
                    published_at=published_at,
                    scraped_at=datetime.now(tz=timezone.utc),
                    raw_data={"video_id": vid_id, "title": snippet.get("title", ""),
                              "channel": snippet.get("channelTitle", ""),
                              "views": int(stats.get("viewCount", 0)),
                              "likes": int(stats.get("likeCount", 0)),
                              "comment_count": int(stats.get("commentCount", 0))},
                ))
        except Exception as e:
            logger.warning(f"Details error: {e}")
        time.sleep(0.5)
    return posts


# Collect IDs
seen = set()
all_ids = []

for order in ("relevance", "date"):
    for q in QUERIES:
        ids = search_videos(q, order)
        added = 0
        for vid in ids:
            if vid not in seen:
                seen.add(vid)
                all_ids.append(vid)
                added += 1
        if added:
            logger.info(f"{order} '{q}' → +{added} new (total: {len(all_ids)})")

logger.info(f"Total unique videos: {len(all_ids)}")

# Fetch details
videos = fetch_details(all_ids)
logger.info(f"Fetched details: {len(videos)} videos")

# Save
if videos:
    os.makedirs(config.RAW_DIR, exist_ok=True)
    os.makedirs(config.PROCESSED_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    with open(PROGRESS_PATH, "w", encoding="utf-8") as f:
        json.dump([v.model_dump(mode="json") for v in videos], f, default=str, ensure_ascii=False)

    export_csv(videos, f"{config.PROCESSED_DIR}/higgsfield_youtube_{ts}.csv")
    export_json(videos, f"{config.PROCESSED_DIR}/higgsfield_youtube_{ts}.json")
    print(f"YouTube (Higgsfield): {len(videos)} videos")
else:
    print("No YouTube videos found.")
