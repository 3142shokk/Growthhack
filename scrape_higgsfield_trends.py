#!/usr/bin/env python3
"""Google Trends scraper for Higgsfield."""
import logging
from datetime import datetime
import config
from storage.exporter import export_csv, export_json, export_raw
from workers.google_trends_worker import GoogleTrendsWorker

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)

TS = datetime.now().strftime("%Y%m%d_%H%M%S")

worker = GoogleTrendsWorker(keywords=["higgsfield", "higgsfield.ai"])
posts = worker.scrape()

if posts:
    export_raw([p.raw_data for p in posts], "higgsfield_trends", config.RAW_DIR)
    export_csv(posts, f"{config.PROCESSED_DIR}/higgsfield_trends_{TS}.csv")
    export_json(posts, f"{config.PROCESSED_DIR}/higgsfield_trends_{TS}.json")
    print(f"Google Trends (Higgsfield): {len(posts)} data points")
else:
    print("No Google Trends data found.")
