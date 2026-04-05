#!/usr/bin/env python3
"""
Process raw Reddit and X (Twitter) data into clean, analysis-ready CSVs.

Outputs (in data/processed/):
  - reddit_posts.csv          — all Reddit posts, cleaned & filtered
  - reddit_comments.csv       — all fetched comments, linked to posts
  - reddit_combined.csv       — posts with their top comments merged
  - x_tweets.csv              — all X tweets, cleaned
  - all_platforms.csv         — unified Reddit + X dataset

Usage:
    python process_data.py
"""

import csv
import json
import logging
import os
import re
import sys
from datetime import datetime, timezone

import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

OUT_DIR = config.PROCESSED_DIR


# ── helpers ──────────────────────────────────────────────────────────────

def clean_text(text: str | None) -> str:
    """Strip control chars, collapse whitespace, trim."""
    if not text:
        return ""
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def safe_int(val) -> int | None:
    if val is None:
        return None
    try:
        return int(val)
    except (ValueError, TypeError):
        return None


def engagement_rate(likes, reposts, comments, views) -> float | None:
    likes = likes or 0
    reposts = reposts or 0
    comments = comments or 0
    if views and views > 0:
        return round((likes + reposts + comments) / views, 6)
    return None


def write_csv(rows: list[dict], path: str) -> None:
    if not rows:
        logger.warning(f"No rows to write for {path}")
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    logger.info(f"Wrote {len(rows):,} rows -> {path}")


# ── Reddit processing ────────────────────────────────────────────────────

def process_reddit_posts() -> list[dict]:
    path = os.path.join(config.RAW_DIR, "reddit_progress.json")
    logger.info(f"Loading Reddit posts from {path}")
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    rows = []
    for p in raw:
        title = clean_text(p.get("post_title"))
        description = clean_text(p.get("description"))
        likes = safe_int(p.get("likes"))
        reposts = safe_int(p.get("reposts"))
        comments = safe_int(p.get("comments"))
        hashtags = p.get("hashtags") or []
        subreddit = hashtags[0] if hashtags else ""

        rows.append({
            "id": p.get("id", ""),
            "platform": "reddit",
            "subreddit": subreddit,
            "title": title,
            "body": description[:2000] if description else "",
            "author": p.get("author", ""),
            "url": p.get("url", ""),
            "score": likes,
            "comments_count": comments,
            "crossposts": reposts,
            "flair": hashtags[1] if len(hashtags) > 1 else "",
            "published_at": p.get("published_at", ""),
            "engagement_rate": engagement_rate(likes, reposts, comments, None),
        })

    logger.info(f"Processed {len(rows):,} Reddit posts")
    return rows


def process_reddit_comments() -> list[dict]:
    path = os.path.join(config.RAW_DIR, "reddit_comments.json")
    if not os.path.exists(path):
        logger.warning("No reddit_comments.json found, skipping")
        return []

    logger.info(f"Loading Reddit comments from {path}")
    with open(path, "r", encoding="utf-8") as f:
        by_post = json.load(f)

    rows = []
    for post_id, comments in by_post.items():
        for c in comments:
            body = clean_text(c.get("body"))
            if not body or body == "[deleted]" or body == "[removed]":
                continue
            created = c.get("created_utc")
            if created:
                try:
                    created = datetime.fromtimestamp(created, tz=timezone.utc).isoformat()
                except (ValueError, OSError):
                    created = ""

            rows.append({
                "comment_id": c.get("id", ""),
                "post_id": post_id,
                "author": c.get("author", ""),
                "body": body[:2000],
                "score": safe_int(c.get("score")),
                "parent_id": c.get("parent_id", ""),
                "published_at": created,
            })

    logger.info(f"Processed {len(rows):,} Reddit comments")
    return rows


def build_reddit_combined(posts: list[dict], comments: list[dict]) -> list[dict]:
    """Merge posts with their top comments into a single row per post."""
    # Group comments by post_id
    comments_by_post: dict[str, list[dict]] = {}
    for c in comments:
        pid = c["post_id"]
        comments_by_post.setdefault(pid, []).append(c)

    rows = []
    for p in posts:
        post_id = p["id"]
        post_comments = comments_by_post.get(post_id, [])
        # Sort by score desc, take top 10
        post_comments.sort(key=lambda c: c.get("score") or 0, reverse=True)
        top = post_comments[:10]

        # Build comment text block
        comment_texts = []
        for i, c in enumerate(top, 1):
            comment_texts.append(f"[{c.get('score', 0)}pts] {c['body'][:300]}")

        rows.append({
            **p,
            "top_comments_count": len(top),
            "top_comments": " ||| ".join(comment_texts),
        })

    logger.info(f"Built {len(rows):,} combined Reddit rows")
    return rows


# ── X (Twitter) processing ───────────────────────────────────────────────

def process_x_tweets() -> list[dict]:
    path = "data/x_tweets/tweets_0001.jsonl"
    if not os.path.exists(path):
        logger.warning("No X tweets file found, skipping")
        return []

    logger.info(f"Loading X tweets from {path}")
    raw = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                raw.append(json.loads(line))

    rows = []
    seen_ids = set()
    for t in raw:
        tid = str(t.get("tweet_id", ""))
        if tid in seen_ids:
            continue
        seen_ids.add(tid)

        text = clean_text(t.get("text"))
        likes = safe_int(t.get("likes"))
        reposts = safe_int(t.get("reposts"))
        replies = safe_int(t.get("replies"))
        views = safe_int(t.get("views"))
        hashtags = t.get("hashtags") or []

        rows.append({
            "id": f"x_{tid}",
            "platform": "x",
            "author": t.get("author", ""),
            "text": text,
            "likes": likes,
            "reposts": reposts,
            "replies": replies,
            "views": views,
            "hashtags": "|".join(hashtags),
            "query": t.get("query", ""),
            "published_at": t.get("created_at", ""),
            "engagement_rate": engagement_rate(likes, reposts, replies, views),
        })

    logger.info(f"Processed {len(rows):,} X tweets")
    return rows


# ── Unified dataset ──────────────────────────────────────────────────────

def build_unified(reddit_posts: list[dict], x_tweets: list[dict]) -> list[dict]:
    """Merge Reddit and X into a single comparable dataset."""
    unified = []

    for p in reddit_posts:
        unified.append({
            "id": p["id"],
            "platform": "reddit",
            "author": p["author"],
            "title": p["title"],
            "body": p["body"][:500],
            "url": p["url"],
            "likes": p["score"],
            "reposts": p["crossposts"],
            "comments": p["comments_count"],
            "views": None,
            "hashtags": p["subreddit"],
            "published_at": p["published_at"],
            "engagement_rate": p["engagement_rate"],
        })

    for t in x_tweets:
        unified.append({
            "id": t["id"],
            "platform": "x",
            "author": t["author"],
            "title": t["text"][:200],
            "body": t["text"],
            "url": "",
            "likes": t["likes"],
            "reposts": t["reposts"],
            "comments": t["replies"],
            "views": t["views"],
            "hashtags": t["hashtags"],
            "published_at": t["published_at"],
            "engagement_rate": t["engagement_rate"],
        })

    logger.info(f"Unified dataset: {len(unified):,} rows ({len(reddit_posts):,} reddit + {len(x_tweets):,} x)")
    return unified


# ── Main ─────────────────────────────────────────────────────────────────

def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # Reddit
    reddit_posts = process_reddit_posts()
    write_csv(reddit_posts, os.path.join(OUT_DIR, "reddit_posts.csv"))

    reddit_comments = process_reddit_comments()
    write_csv(reddit_comments, os.path.join(OUT_DIR, "reddit_comments.csv"))

    reddit_combined = build_reddit_combined(reddit_posts, reddit_comments)
    write_csv(reddit_combined, os.path.join(OUT_DIR, "reddit_combined.csv"))

    # X
    x_tweets = process_x_tweets()
    write_csv(x_tweets, os.path.join(OUT_DIR, "x_tweets.csv"))

    # Unified
    unified = build_unified(reddit_posts, x_tweets)
    write_csv(unified, os.path.join(OUT_DIR, "all_platforms.csv"))

    # Summary
    print(f"\n{'='*50}")
    print("Processing complete:")
    print(f"  Reddit posts:    {len(reddit_posts):,}")
    print(f"  Reddit comments: {len(reddit_comments):,}")
    print(f"  X tweets:        {len(x_tweets):,}")
    print(f"  Unified total:   {len(unified):,}")
    print(f"\nOutput: {OUT_DIR}/")
    print(f"  reddit_posts.csv")
    print(f"  reddit_comments.csv")
    print(f"  reddit_combined.csv")
    print(f"  x_tweets.csv")
    print(f"  all_platforms.csv")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
