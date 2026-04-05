#!/usr/bin/env python3
"""X (Twitter) scraper for Higgsfield — separate output from Claude data."""
import logging
import config
from workers.x_scraper.x_worker import XTimelineWorker, CLAUDE_KEYWORDS, ANTHROPIC_ACCOUNTS, STATE_FILE, ACCOUNTS_FILE

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)

# Override discovery queries to search for Higgsfield
import workers.x_scraper.account_discovery as discovery
discovery.DISCOVERY_QUERIES = [
    "higgsfield",
    "higgsfield.ai",
    "higgsfield ai",
    "higgsfield app",
    "higgsfield video",
    "higgsfield ai video generation",
    "higgsfield demo",
    "higgsfield text to video",
]

# Override output paths so we don't mix with Claude data
OUTPUT_DIR = "data/x_tweets_higgsfield"

# Override filter keywords
import workers.x_scraper.x_worker as x_mod
x_mod.CLAUDE_KEYWORDS = ["higgsfield", "higgsfield.ai"]
x_mod.ANTHROPIC_ACCOUNTS = set()  # no special "keep all" accounts
x_mod.STATE_FILE = f"{OUTPUT_DIR}/state.json"
x_mod.ACCOUNTS_FILE = f"{OUTPUT_DIR}/discovered_accounts.json"

worker = XTimelineWorker(
    accounts=["higaboroslab"],  # seed with known Higgsfield account if any
    target_total=10_000,
    output_dir=OUTPUT_DIR,
    filter_claude=True,  # filters for "higgsfield" now (we overrode keywords)
    request_delay=1.0,
    discover=True,
)
total = worker.scrape()
print(f"X (Higgsfield): {total:,} tweets -> {OUTPUT_DIR}/")
