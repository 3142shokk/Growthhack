#!/usr/bin/env python3
"""
main.py — CLI entrypoint for the Claude Viral Growth Machine scrapers.

Usage
-----
python main.py                          # run all workers
python main.py --workers reddit         # Reddit only
python main.py --workers hacker_news    # Hacker News only
python main.py --workers google_trends  # Google Trends only
"""

import argparse
import logging
from datetime import datetime

import config
from storage.exporter import export_csv, export_json, export_raw

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def run_reddit(args) -> None:
    from workers.reddit_worker import RedditWorker

    logger.info("Starting Reddit scraper")
    worker = RedditWorker()
    posts = worker.scrape()

    if not posts:
        logger.warning("No Reddit posts collected.")
        return

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_raw([p.raw_data for p in posts], "reddit", config.RAW_DIR)
    export_csv(posts, f"{config.PROCESSED_DIR}/reddit_{ts}.csv")
    export_json(posts, f"{config.PROCESSED_DIR}/reddit_{ts}.json")

    print(f"\n{'='*50}")
    print(f"Reddit: {len(posts)} posts collected")
    top = sorted(posts, key=lambda p: (p.likes or 0) + (p.comments or 0), reverse=True)[:5]
    print("\nTop 5 by score + comments:")
    for i, p in enumerate(top, 1):
        print(f"  {i}. r/{p.hashtags[0] if p.hashtags else '?'} | score={p.likes} comments={p.comments}")
        print(f"     {p.post_title[:120]!r}")
    print(f"{'='*50}\n")


def run_hackernews(args) -> None:
    from workers.hackernews_worker import HackerNewsWorker

    logger.info("Starting Hacker News scraper")
    worker = HackerNewsWorker()
    posts = worker.scrape()

    if not posts:
        logger.warning("No Hacker News data collected.")
        return

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_raw([p.raw_data for p in posts], "hacker_news", config.RAW_DIR)
    export_csv(posts, f"{config.PROCESSED_DIR}/hacker_news_{ts}.csv")
    export_json(posts, f"{config.PROCESSED_DIR}/hacker_news_{ts}.json")

    stories = [p for p in posts if "hn_story_" in p.id]
    comments = [p for p in posts if "hn_comment_" in p.id]

    # Fetch all comments for high-engagement stories
    story_comments = worker.scrape_story_comments(stories)
    if story_comments:
        export_raw([p.raw_data for p in story_comments], "hacker_news_story_comments", config.RAW_DIR)
        export_csv(story_comments, f"{config.PROCESSED_DIR}/hacker_news_story_comments_{ts}.csv")
        export_json(story_comments, f"{config.PROCESSED_DIR}/hacker_news_story_comments_{ts}.json")

    print(f"\n{'='*50}")
    print(f"Hacker News: {len(posts)} items ({len(stories)} stories, {len(comments)} keyword comments)")
    print(f"Story comments fetched: {len(story_comments)} (from all {len(stories)} stories)")
    top = sorted(stories, key=lambda p: p.likes or 0, reverse=True)[:5]
    print("\nTop 5 stories by points:")
    for i, p in enumerate(top, 1):
        print(f"  {i}. {p.likes}pts | {p.comments}cmts | {p.published_at.date() if p.published_at else '?'}")
        print(f"     {p.post_title[:100]!r}")
    print(f"{'='*50}\n")


def run_google_trends(args) -> None:
    from workers.google_trends_worker import GoogleTrendsWorker

    logger.info("Starting Google Trends scraper")
    worker = GoogleTrendsWorker()
    posts = worker.scrape()

    if not posts:
        logger.warning("No Google Trends data collected.")
        return

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_raw([p.raw_data for p in posts], "google_trends", config.RAW_DIR)
    export_csv(posts, f"{config.PROCESSED_DIR}/google_trends_{ts}.csv")
    export_json(posts, f"{config.PROCESSED_DIR}/google_trends_{ts}.json")

    print(f"\n{'='*50}")
    print(f"Google Trends: {len(posts)} data points collected")
    interest = [p for p in posts if p.post_title.startswith("[Trend]") and p.trend_score is not None]
    if interest:
        seen = set()
        print("\nPeak interest scores (last 90 days, 0-100):")
        for p in sorted(interest, key=lambda x: x.trend_score or 0, reverse=True):
            kw = p.post_title[8:]
            if kw not in seen:
                seen.add(kw)
                print(f"  {kw}: {p.trend_score}")
    print(f"{'='*50}\n")


def main():
    parser = argparse.ArgumentParser(description="Claude Growth Machine Scraper")
    parser.add_argument(
        "--workers", nargs="+", choices=["reddit", "google_trends", "hacker_news"],
        default=["reddit", "google_trends", "hacker_news"],
        help="Which workers to run (default: all)",
    )
    args = parser.parse_args()

    if "reddit" in args.workers:
        try:
            run_reddit(args)
        except ImportError:
            logger.warning("Reddit worker not available, skipping.")

    if "google_trends" in args.workers:
        try:
            run_google_trends(args)
        except ImportError:
            logger.warning("Google Trends worker not available, skipping.")

    if "hacker_news" in args.workers:
        try:
            run_hackernews(args)
        except ImportError:
            logger.warning("Hacker News worker not available, skipping.")


if __name__ == "__main__":
    main()
