"""
data_loader.py — loads and normalises all platform datasets into a single frame.
"""
from __future__ import annotations
import pandas as pd
from pathlib import Path

PROCESSED = Path(__file__).parent.parent / "data" / "processed"
CHARTS    = Path(__file__).parent.parent / "data" / "charts"
CHARTS.mkdir(parents=True, exist_ok=True)

# ── known external events to overlay on timelines ──────────────────────────────
EVENTS = [
    ("2024-10-22", "Computer Use + Claude 3.5 Haiku"),
    ("2025-02-24", "Claude 3.7 Sonnet + Claude Code"),
    ("2025-05-22", "Claude 4"),
    ("2025-09-29", "Claude Sonnet 4.5"),
    ("2025-11-13", "AI Cyberattack disclosure"),
    ("2025-12-02", "Bun acquisition"),
    ("2026-02-05", "Claude Opus 4.6"),
    ("2026-02-12", "$30B funding / $380B valuation"),
    ("2026-02-23", "DeepSeek distillation attack disclosure"),
    ("2026-02-26", "Dario DoW statement"),
    ("2026-02-28", "Claude #1 App Store"),
    ("2026-03-31", "Claude Code source leak"),
]

def load_reddit() -> pd.DataFrame:
    df = pd.read_csv(PROCESSED / "reddit_posts.csv", low_memory=False)
    df["published_at"] = pd.to_datetime(df["published_at"], utc=True, errors="coerce")
    df["platform"] = "reddit"
    df = df.rename(columns={"score": "likes", "comments_count": "comments", "title": "post_title"})
    return df

def load_hn() -> pd.DataFrame:
    df = pd.read_csv(PROCESSED / "hacker_news_20260404_181312.csv", low_memory=False)
    df = df[df["id"].str.contains("story", na=False)].copy()
    df["published_at"] = pd.to_datetime(df["published_at"], utc=True, errors="coerce")
    df["platform"] = "hacker_news"
    df["likes"] = pd.to_numeric(df["likes"], errors="coerce")
    df["comments"] = pd.to_numeric(df["comments"], errors="coerce")
    return df

def load_hn_comments() -> pd.DataFrame:
    df = pd.read_csv(PROCESSED / "hacker_news_story_comments_20260404_181312.csv", low_memory=False)
    df["published_at"] = pd.to_datetime(df["published_at"], utc=True, errors="coerce")
    # extract story_id from hashtags field e.g. "comment|story_46902223"
    df["story_id"] = df["hashtags"].str.extract(r"story_(\d+)")
    return df

def load_reddit_comments() -> pd.DataFrame:
    df = pd.read_csv(PROCESSED / "reddit_comments.csv", low_memory=False)
    df["published_at"] = pd.to_datetime(df["published_at"], utc=True, errors="coerce")
    return df

def load_x() -> pd.DataFrame:
    df = pd.read_csv(PROCESSED / "x_tweets.csv", low_memory=False)
    df["published_at"] = pd.to_datetime(df["published_at"], utc=True, errors="coerce")
    df["platform"] = "x"
    df["views"] = pd.to_numeric(df["views"], errors="coerce")
    df["likes"] = pd.to_numeric(df["likes"], errors="coerce")
    df["reposts"] = pd.to_numeric(df["reposts"], errors="coerce")
    df["replies"] = pd.to_numeric(df["replies"], errors="coerce")
    df = df.rename(columns={"text": "post_title", "replies": "comments"})
    return df

def load_google_trends() -> pd.DataFrame:
    df = pd.read_csv(PROCESSED / "google_trends_20260404_182735.csv", low_memory=False)
    df["scraped_at"] = pd.to_datetime(df["scraped_at"], utc=True, errors="coerce")
    return df

def load_all() -> pd.DataFrame:
    """Merged frame with columns: platform, post_title, likes, comments, views, published_at"""
    reddit = load_reddit()[["id", "platform", "post_title", "likes", "comments", "published_at", "subreddit", "flair"]]
    hn     = load_hn()[["id", "platform", "post_title", "likes", "comments", "published_at"]]
    x      = load_x()[["id", "platform", "post_title", "likes", "comments", "views", "reposts", "published_at", "author"]]
    combined = pd.concat([reddit, hn, x], ignore_index=True, sort=False)
    combined["likes"]    = pd.to_numeric(combined["likes"],    errors="coerce")
    combined["comments"] = pd.to_numeric(combined["comments"], errors="coerce")
    combined["views"]    = pd.to_numeric(combined["views"],    errors="coerce")
    combined["reposts"]  = pd.to_numeric(combined["reposts"],  errors="coerce")
    combined["date"]     = combined["published_at"].dt.date
    combined["week"]     = combined["published_at"].dt.to_period("W")
    combined["month"]    = combined["published_at"].dt.to_period("M")
    return combined
