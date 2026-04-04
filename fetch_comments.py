#!/usr/bin/env python3
"""
Fetch all comments for previously scraped Reddit posts via Arctic Shift.

Reads post IDs from data/raw/reddit_progress.json, fetches comments for each
post via /api/comments/search, and saves results incrementally to
data/raw/reddit_comments.json.

Usage:
    python fetch_comments.py
    python fetch_comments.py --delay 0.5       # faster (risky)
    python fetch_comments.py --delay 2          # slower (safer)
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone

import requests

import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

_BASE = "https://arctic-shift.photon-reddit.com"
_MAX_RETRIES = 5
_BACKOFF_BASE = 3.0
_SAVE_EVERY = 50  # save progress every N posts processed


def load_posts(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_comment_progress(path: str) -> tuple[dict[str, list[dict]], set[str]]:
    """Load previously fetched comments. Returns (post_id -> comments, done_ids)."""
    if not os.path.exists(path):
        return {}, set()
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    done_ids = set(data.keys())
    return data, done_ids


def save_comments(comments_by_post: dict[str, list[dict]], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(comments_by_post, f, default=str, ensure_ascii=False)
    total = sum(len(v) for v in comments_by_post.values())
    logger.info(
        f"Saved comments: {len(comments_by_post):,} posts, "
        f"{total:,} total comments -> {path}"
    )


def fetch_comments_for_post(
    session: requests.Session, post_id: str, delay: float
) -> list[dict]:
    """Fetch all comments for a single post, paginating via created_utc."""
    # Arctic Shift expects link_id in t3_xxx format
    # Our post IDs are stored as "reddit_xxx", strip the prefix
    raw_id = post_id.replace("reddit_", "")
    link_id = f"t3_{raw_id}"

    all_comments: list[dict] = []
    params = {
        "link_id": link_id,
        "limit": 100,
        "sort": "asc",
    }

    while True:
        data = _api_get(session, "/api/comments/search", params)
        if data is None:
            break

        comments = data.get("data", [])
        if not comments:
            break

        for c in comments:
            all_comments.append({
                "id": c.get("id", ""),
                "post_id": raw_id,
                "author": c.get("author", "[deleted]"),
                "body": c.get("body", ""),
                "score": c.get("score", 0),
                "parent_id": c.get("parent_id", ""),
                "created_utc": c.get("created_utc", 0),
            })

        # If we already have 10+ comments, no need to paginate further
        if len(all_comments) >= 10:
            break

        if len(comments) < 100:
            break

        # Paginate using created_utc of last comment
        last_ts = comments[-1].get("created_utc")
        if last_ts is None:
            break
        params["after"] = last_ts
        time.sleep(delay)

    # Return top 10 by score (or fewer if the post has less)
    all_comments.sort(key=lambda c: c["score"], reverse=True)
    return all_comments[:10]


def _api_get(
    session: requests.Session, path: str, params: dict
) -> dict | None:
    url = f"{_BASE}{path}"
    for attempt in range(_MAX_RETRIES):
        try:
            resp = session.get(url, params=params, timeout=30)
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code == 429:
                wait = _BACKOFF_BASE * (2 ** attempt)
                logger.warning(f"Rate limited, waiting {wait:.0f}s")
                time.sleep(wait)
                continue
            if resp.status_code >= 500:
                wait = _BACKOFF_BASE * (2 ** attempt)
                logger.warning(f"Server error {resp.status_code}, waiting {wait:.0f}s")
                time.sleep(wait)
                continue
            logger.error(f"HTTP {resp.status_code} for {url}")
            return None
        except requests.RequestException as exc:
            logger.error(f"Request failed: {exc}")
            if attempt < _MAX_RETRIES - 1:
                time.sleep(_BACKOFF_BASE * (2 ** attempt))
    return None


def main():
    parser = argparse.ArgumentParser(description="Fetch Reddit comments for scraped posts")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between requests (default: 1.0s)")
    parser.add_argument("--posts-file", default=os.path.join(config.RAW_DIR, "reddit_progress.json"))
    parser.add_argument("--output", default=os.path.join(config.RAW_DIR, "reddit_comments.json"))
    args = parser.parse_args()

    # Load posts — only from r/ClaudeAI
    logger.info(f"Loading posts from {args.posts_file}")
    posts = load_posts(args.posts_file)
    posts = [p for p in posts if "ClaudeAI" in (p.get("hashtags") or [])]
    post_ids = [p["id"] for p in posts]
    logger.info(f"Loaded {len(post_ids):,} posts from r/ClaudeAI")

    # Load any previous progress
    comments_by_post, done_ids = load_comment_progress(args.output)
    remaining = [pid for pid in post_ids if pid not in done_ids]
    logger.info(
        f"Already fetched: {len(done_ids):,}, remaining: {len(remaining):,}"
    )

    session = requests.Session()
    request_count = 0
    total_comments = sum(len(v) for v in comments_by_post.values())

    try:
        for i, post_id in enumerate(remaining):
            comments = fetch_comments_for_post(session, post_id, args.delay)
            comments_by_post[post_id] = comments
            total_comments += len(comments)
            request_count += 1

            if (i + 1) % 100 == 0:
                logger.info(
                    f"Progress: {len(done_ids) + i + 1:,}/{len(post_ids):,} posts, "
                    f"{total_comments:,} total comments"
                )

            if (i + 1) % _SAVE_EVERY == 0:
                save_comments(comments_by_post, args.output)

            time.sleep(args.delay)

    except KeyboardInterrupt:
        logger.info("Interrupted! Saving progress...")

    # Final save
    save_comments(comments_by_post, args.output)

    logger.info(
        f"Done: {len(comments_by_post):,}/{len(post_ids):,} posts processed, "
        f"{total_comments:,} total comments fetched"
    )


if __name__ == "__main__":
    main()
