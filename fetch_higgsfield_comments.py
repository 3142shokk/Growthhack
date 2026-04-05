#!/usr/bin/env python3
"""Fetch all comments for scraped Higgsfield Reddit posts via Arctic Shift."""
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone

import requests
import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)

BASE = "https://arctic-shift.photon-reddit.com"
MAX_RETRIES = 5
BACKOFF = 3.0
SAVE_EVERY = 50

POSTS_FILE = os.path.join(config.RAW_DIR, "higgsfield_reddit_progress.json")
OUTPUT_FILE = os.path.join(config.RAW_DIR, "higgsfield_reddit_comments.json")


def load_comments_progress():
    if not os.path.exists(OUTPUT_FILE):
        return {}, set()
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data, set(data.keys())


def save_comments(data):
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, default=str, ensure_ascii=False)
    total = sum(len(v) for v in data.values())
    logger.info(f"Saved: {len(data):,} posts, {total:,} comments -> {OUTPUT_FILE}")


def api_get(session, path, params):
    url = f"{BASE}{path}"
    for attempt in range(MAX_RETRIES):
        try:
            resp = session.get(url, params=params, timeout=30)
            if resp.status_code == 200:
                return resp.json()
            if resp.status_code in (429, 500, 502, 503):
                time.sleep(BACKOFF * (2 ** attempt))
                continue
            return None
        except requests.RequestException:
            if attempt < MAX_RETRIES - 1:
                time.sleep(BACKOFF * (2 ** attempt))
    return None


def fetch_comments(session, post_id):
    raw_id = post_id.replace("reddit_", "")
    params = {"link_id": f"t3_{raw_id}", "limit": 100, "sort": "asc"}
    all_comments = []

    while True:
        data = api_get(session, "/api/comments/search", params)
        if not data:
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
        if len(all_comments) >= 10:
            break
        if len(comments) < 100:
            break
        params["after"] = comments[-1].get("created_utc")
        time.sleep(1)

    all_comments.sort(key=lambda c: c["score"], reverse=True)
    return all_comments[:10]


# Main
logger.info(f"Loading posts from {POSTS_FILE}")
with open(POSTS_FILE, "r", encoding="utf-8") as f:
    posts = json.load(f)
post_ids = [p["id"] for p in posts]
logger.info(f"Loaded {len(post_ids):,} posts")

comments_by_post, done_ids = load_comments_progress()
remaining = [pid for pid in post_ids if pid not in done_ids]
logger.info(f"Already done: {len(done_ids):,}, remaining: {len(remaining):,}")

session = requests.Session()
total_comments = sum(len(v) for v in comments_by_post.values())

try:
    for i, post_id in enumerate(remaining):
        comments = fetch_comments(session, post_id)
        comments_by_post[post_id] = comments
        total_comments += len(comments)

        if (i + 1) % 50 == 0:
            logger.info(f"Progress: {len(done_ids) + i + 1:,}/{len(post_ids):,} posts, {total_comments:,} comments")

        if (i + 1) % SAVE_EVERY == 0:
            save_comments(comments_by_post)

        time.sleep(1)
except KeyboardInterrupt:
    logger.info("Interrupted!")

save_comments(comments_by_post)
logger.info(f"Done: {len(comments_by_post):,}/{len(post_ids):,} posts, {total_comments:,} comments")
