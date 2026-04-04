#!/usr/bin/env python3
"""
main.py — CLI entrypoint for the Claude Viral Growth Machine scrapers.

Usage
-----
# Run all workers
python main.py

# Run Threads only, no keyword filter
python main.py --workers threads --no-filter

# Run Threads with custom accounts
python main.py --workers threads --accounts anthropic alexalbert__
"""

import argparse
import logging
import sys
from datetime import datetime

import config
from storage.exporter import export_csv, export_json, export_raw
from workers.threads_worker import ThreadsWorker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

WORKER_MAP = {
    "threads": ThreadsWorker,
}


def run_threads(args) -> None:
    accounts = args.accounts or config.THREADS_TARGET_ACCOUNTS
    keywords = None if args.no_filter else config.CLAUDE_KEYWORDS

    mode = "profile" if args.profile_only else ("discover" if args.discover_only else "both")
    logger.info(f"Starting Threads scraper — mode={mode}, filter={'off' if keywords is None else 'on'}")
    worker = ThreadsWorker(usernames=accounts, filter_keywords=keywords, mode=mode, max_discover=args.max_discover)
    posts = worker.scrape()

    if not posts:
        logger.warning("No posts collected.")
        return

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_raw([p.raw_data for p in posts], "threads", config.RAW_DIR)
    export_csv(posts, f"{config.PROCESSED_DIR}/threads_{ts}.csv")
    export_json(posts, f"{config.PROCESSED_DIR}/threads_{ts}.json")

    # Quick summary
    print(f"\n{'='*50}")
    print(f"Threads scrape complete: {len(posts)} posts")
    print(f"Accounts scraped: {', '.join(accounts)}")
    top = sorted(posts, key=lambda p: (p.likes or 0) + (p.reposts or 0) + (p.comments or 0), reverse=True)[:3]
    print("\nTop 3 posts by engagement:")
    for i, p in enumerate(top, 1):
        print(f"  {i}. @{p.author} | likes={p.likes} reposts={p.reposts} replies={p.comments}")
        print(f"     {p.post_title[:120]!r}")
    print(f"{'='*50}\n")


def main():
    parser = argparse.ArgumentParser(description="Claude Growth Machine Scraper")
    parser.add_argument(
        "--workers",
        nargs="+",
        choices=list(WORKER_MAP.keys()),
        default=list(WORKER_MAP.keys()),
        help="Which workers to run (default: all)",
    )
    parser.add_argument(
        "--accounts",
        nargs="+",
        default=None,
        help="Threads: override target accounts list",
    )
    parser.add_argument(
        "--no-filter",
        action="store_true",
        help="Threads: collect all posts, not just Claude-keyword matches",
    )
    parser.add_argument(
        "--discover-only",
        action="store_true",
        help="Threads: only use DDG discovery (posts mentioning Claude from anyone)",
    )
    parser.add_argument(
        "--profile-only",
        action="store_true",
        help="Threads: only scrape curated profile list",
    )
    parser.add_argument(
        "--max-discover",
        type=int,
        default=60,
        help="Threads: max posts to scrape in discover mode (default: 60)",
    )
    args = parser.parse_args()

    if "threads" in args.workers:
        run_threads(args)


if __name__ == "__main__":
    main()
