#!/usr/bin/env python3
"""Reddit scraper for Higgsfield."""
import logging
from datetime import datetime
import config
from storage.exporter import export_csv, export_json, export_raw
from workers.reddit_worker import RedditWorker

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)

KEYWORDS = ["higgsfield", "higgsfield.ai", "higgsfield ai", "higgs field ai"]
QUERIES = ["higgsfield", "higgsfield.ai", "higgsfield ai", "higgs field ai", "higgsfield video", "higgsfield app"]
TS = datetime.now().strftime("%Y%m%d_%H%M%S")

worker = RedditWorker(
    subreddits=["Higgsfield_AI", "aivideo", "generativeAI", "singularity", "StableDiffusion", "AItools"],
    search_queries=QUERIES,
    target_total=100_000,
    weeks_back=104,
    filter_keywords=KEYWORDS,
    progress_name="higgsfield_reddit_progress.json",
)
posts = worker.scrape()

if posts:
    export_raw([p.raw_data for p in posts], "higgsfield_reddit", config.RAW_DIR)
    export_csv(posts, f"{config.PROCESSED_DIR}/higgsfield_reddit_{TS}.csv")
    export_json(posts, f"{config.PROCESSED_DIR}/higgsfield_reddit_{TS}.json")
    print(f"Reddit (Higgsfield): {len(posts):,} posts")
else:
    print("No Reddit posts found.")
