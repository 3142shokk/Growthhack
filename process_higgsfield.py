#!/usr/bin/env python3
"""
Process all Higgsfield raw data into clean CSVs + one unified dataset.

Outputs (in data/processed/):
  - higgsfield_reddit_posts.csv
  - higgsfield_reddit_comments.csv
  - higgsfield_reddit_combined.csv
  - higgsfield_x_tweets.csv
  - higgsfield_youtube.csv
  - higgsfield_trends.csv
  - higgsfield_full_dataset.csv    <-- everything combined
"""

import csv
import json
import os
import re
import sys
from datetime import datetime, timezone

import config

sys.stdout.reconfigure(encoding="utf-8")

OUT = config.PROCESSED_DIR


def clean(text):
    if not text:
        return ""
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def safe_int(v):
    if not v or v == "":
        return ""
    try:
        return int(float(v))
    except (ValueError, TypeError):
        return ""


def eng_rate(likes, reposts, comments, views):
    likes = likes or 0
    reposts = reposts or 0
    comments = comments or 0
    if views and views > 0:
        return round((likes + reposts + comments) / views, 6)
    return ""


def write_csv(rows, path):
    if not rows:
        print(f"  (no data for {path})")
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    print(f"  {len(rows):,} rows -> {path}")


# ── Reddit posts ─────────────────────────────────────────────────────
print("Processing Reddit posts...")
with open("data/raw/higgsfield_reddit_progress.json", "r", encoding="utf-8") as f:
    raw_posts = json.load(f)

reddit_posts = []
for p in raw_posts:
    title = clean(p.get("post_title"))
    body = clean(p.get("description"))
    likes = safe_int(p.get("likes"))
    reposts = safe_int(p.get("reposts"))
    comments = safe_int(p.get("comments"))
    hashtags = p.get("hashtags") or []
    subreddit = hashtags[0] if hashtags else ""

    reddit_posts.append({
        "id": p.get("id", ""),
        "platform": "reddit",
        "subreddit": subreddit,
        "title": title,
        "body": body[:2000] if body else "",
        "author": p.get("author", ""),
        "url": p.get("url", ""),
        "score": likes,
        "comments_count": comments,
        "crossposts": reposts,
        "flair": hashtags[1] if len(hashtags) > 1 else "",
        "published_at": p.get("published_at", ""),
        "engagement_rate": eng_rate(likes, reposts, comments, None),
    })

write_csv(reddit_posts, os.path.join(OUT, "higgsfield_reddit_posts.csv"))

# ── Reddit comments ──────────────────────────────────────────────────
print("Processing Reddit comments...")
with open("data/raw/higgsfield_reddit_comments.json", "r", encoding="utf-8") as f:
    raw_comments = json.load(f)

reddit_comments = []
for post_id, clist in raw_comments.items():
    for c in clist:
        body = clean(c.get("body"))
        if not body or body in ("[deleted]", "[removed]"):
            continue
        created = c.get("created_utc")
        if created:
            try:
                created = datetime.fromtimestamp(created, tz=timezone.utc).isoformat()
            except (ValueError, OSError):
                created = ""
        reddit_comments.append({
            "comment_id": c.get("id", ""),
            "post_id": post_id,
            "author": c.get("author", ""),
            "body": body[:2000],
            "score": safe_int(c.get("score")),
            "parent_id": c.get("parent_id", ""),
            "published_at": created,
        })

write_csv(reddit_comments, os.path.join(OUT, "higgsfield_reddit_comments.csv"))

# ── Reddit combined ──────────────────────────────────────────────────
print("Building Reddit combined...")
comments_by_post = {}
for c in reddit_comments:
    comments_by_post.setdefault(c["post_id"], []).append(c)

reddit_combined = []
for p in reddit_posts:
    pc = comments_by_post.get(p["id"], [])
    pc.sort(key=lambda c: c.get("score") or 0, reverse=True)
    top = pc[:10]
    texts = [f"[{c.get('score', 0)}pts] {c['body'][:300]}" for c in top]
    reddit_combined.append({
        **p,
        "top_comments_count": len(top),
        "top_comments": " ||| ".join(texts),
    })

write_csv(reddit_combined, os.path.join(OUT, "higgsfield_reddit_combined.csv"))

# ── X tweets ─────────────────────────────────────────────────────────
print("Processing X tweets...")
x_tweets = []
seen_x = set()
tweets_path = "data/x_tweets_higgsfield/tweets_0001.jsonl"
if os.path.exists(tweets_path):
    with open(tweets_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            t = json.loads(line)
            tid = str(t.get("tweet_id", ""))
            if tid in seen_x:
                continue
            seen_x.add(tid)
            likes = safe_int(t.get("likes"))
            reposts = safe_int(t.get("reposts"))
            replies = safe_int(t.get("replies"))
            views = safe_int(t.get("views"))
            x_tweets.append({
                "id": f"x_{tid}",
                "platform": "x",
                "author": t.get("author", ""),
                "text": clean(t.get("text")),
                "likes": likes,
                "reposts": reposts,
                "replies": replies,
                "views": views,
                "hashtags": "|".join(t.get("hashtags") or []),
                "query": t.get("query", ""),
                "published_at": t.get("created_at", ""),
                "engagement_rate": eng_rate(likes, reposts, replies, views),
            })

write_csv(x_tweets, os.path.join(OUT, "higgsfield_x_tweets.csv"))

# ── YouTube ──────────────────────────────────────────────────────────
print("Processing YouTube...")
with open("data/raw/higgsfield_youtube_progress.json", "r", encoding="utf-8") as f:
    raw_yt = json.load(f)

yt_videos = []
for v in raw_yt:
    views = safe_int(v.get("views"))
    likes = safe_int(v.get("likes"))
    comments = safe_int(v.get("comments"))
    yt_videos.append({
        "id": v.get("id", ""),
        "platform": "youtube",
        "author": v.get("author", ""),
        "title": clean(v.get("post_title")),
        "description": clean(v.get("description", ""))[:500],
        "url": v.get("url", ""),
        "views": views,
        "likes": likes,
        "comments": comments,
        "duration": v.get("duration", ""),
        "published_at": v.get("published_at", ""),
        "engagement_rate": eng_rate(likes, 0, comments, views),
    })

write_csv(yt_videos, os.path.join(OUT, "higgsfield_youtube.csv"))

# ── Google Trends ────────────────────────────────────────────────────
# Already processed, just note it
print("Google Trends: already in higgsfield_trends_*.csv")

# ── Full unified dataset ─────────────────────────────────────────────
print("\nBuilding unified dataset...")

COLS = ["id", "platform", "type", "parent_id", "author", "title", "body",
        "url", "likes", "reposts", "comments", "views", "hashtags",
        "published_at", "engagement_rate"]

unified = []

for p in reddit_posts:
    unified.append({
        "id": p["id"], "platform": "reddit", "type": "post", "parent_id": "",
        "author": p["author"], "title": p["title"], "body": p["body"][:500],
        "url": p["url"], "likes": p["score"], "reposts": p["crossposts"],
        "comments": p["comments_count"], "views": "", "hashtags": p["subreddit"],
        "published_at": p["published_at"], "engagement_rate": p["engagement_rate"],
    })

for c in reddit_comments:
    unified.append({
        "id": f"reddit_comment_{c['comment_id']}", "platform": "reddit",
        "type": "comment", "parent_id": c["post_id"], "author": c["author"],
        "title": "", "body": c["body"][:500], "url": "", "likes": c["score"],
        "reposts": "", "comments": "", "views": "", "hashtags": "",
        "published_at": c["published_at"], "engagement_rate": "",
    })

for t in x_tweets:
    unified.append({
        "id": t["id"], "platform": "x", "type": "tweet", "parent_id": "",
        "author": t["author"], "title": t["text"][:200], "body": t["text"],
        "url": "", "likes": t["likes"], "reposts": t["reposts"],
        "comments": t["replies"], "views": t["views"], "hashtags": t["hashtags"],
        "published_at": t["published_at"], "engagement_rate": t["engagement_rate"],
    })

for v in yt_videos:
    unified.append({
        "id": v["id"], "platform": "youtube", "type": "video", "parent_id": "",
        "author": v["author"], "title": v["title"], "body": v["description"],
        "url": v["url"], "likes": v["likes"], "reposts": "",
        "comments": v["comments"], "views": v["views"], "hashtags": "",
        "published_at": v["published_at"], "engagement_rate": v["engagement_rate"],
    })

# Add trends
trends_files = [f for f in os.listdir(OUT) if f.startswith("higgsfield_trends_") and f.endswith(".csv")]
if trends_files:
    with open(os.path.join(OUT, sorted(trends_files)[-1]), "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            unified.append({
                "id": row.get("id", ""), "platform": "google_trends", "type": "trend",
                "parent_id": "", "author": "", "title": row.get("post_title", ""),
                "body": "", "url": "", "likes": safe_int(row.get("likes")),
                "reposts": "", "comments": "", "views": "",
                "hashtags": row.get("hashtags", ""),
                "published_at": row.get("published_at", ""),
                "engagement_rate": row.get("engagement_rate", ""),
            })

out_path = os.path.join(OUT, "higgsfield_full_dataset.csv")
write_csv(unified, out_path)

# Summary
from collections import Counter
by_platform = Counter(r["platform"] for r in unified)
by_type = Counter(r["type"] for r in unified)

print(f"\n{'='*50}")
print(f"Higgsfield full dataset: {len(unified):,} rows")
print(f"\nBy platform:")
for p, c in by_platform.most_common():
    print(f"  {p:15s} {c:>8,}")
print(f"\nBy type:")
for t, c in by_type.most_common():
    print(f"  {t:15s} {c:>8,}")
print(f"{'='*50}")
