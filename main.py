#!/usr/bin/env python3
"""
main.py — CLI entrypoint for the Claude Viral Growth Machine scrapers.

Usage
-----
python main.py                          # run all workers
python main.py --workers threads        # Threads only
python main.py --workers reddit         # Reddit only
python main.py --workers threads --max-discover 100
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


def run_threads(args) -> None:
    from workers.threads_worker import ThreadsWorker

    logger.info(f"Starting Threads scraper — hashtags + DDG discover, max_discover={args.max_discover}")
    worker = ThreadsWorker(max_discover=args.max_discover)
    posts = worker.scrape()

    if not posts:
        logger.warning("No Threads posts collected.")
        return

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_raw([p.raw_data for p in posts], "threads", config.RAW_DIR)
    export_csv(posts, f"{config.PROCESSED_DIR}/threads_{ts}.csv")
    export_json(posts, f"{config.PROCESSED_DIR}/threads_{ts}.json")

    print(f"\n{'='*50}")
    print(f"Threads: {len(posts)} posts collected")
    top = sorted(posts, key=lambda p: (p.likes or 0) + (p.reposts or 0) + (p.comments or 0), reverse=True)[:5]
    print("\nTop 5 by engagement:")
    for i, p in enumerate(top, 1):
        print(f"  {i}. @{p.author} | likes={p.likes} views={p.views}")
        print(f"     {p.post_title[:120]!r}")
    print(f"{'='*50}\n")


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


def main():
    parser = argparse.ArgumentParser(description="Claude Growth Machine Scraper")
    parser.add_argument(
        "--workers", nargs="+", choices=["threads", "reddit"],
        default=["threads", "reddit"],
        help="Which workers to run (default: all)",
    )
    parser.add_argument(
        "--max-discover", type=int, default=60,
        help="Threads: max posts from DDG discovery (default: 60)",
    )
    args = parser.parse_args()

    if "threads" in args.workers:
        run_threads(args)

    if "reddit" in args.workers:
        try:
            run_reddit(args)
        except ImportError:
            logger.warning("Reddit worker not available, skipping.")


if __name__ == "__main__":
    main()
