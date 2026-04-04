"""
X (Twitter) scraper — all Claude/Anthropic mentions, no login required.

Pipeline
--------
1. DISCOVER: DDG finds tweet URLs -> extract author screen names
2. SEED: Combine discovered accounts with curated seed list
3. SCRAPE: GraphQL UserTweets paginates each account's full timeline
4. FILTER: Keep only tweets mentioning Claude/Anthropic
5. WRITE: JSONL with 50k file rotation + dedup + resume

Strategy for 50k+
------------------
- Anthropic accounts: scrape ALL tweets (they're all relevant context)
- Other accounts: filter for Claude/Anthropic keywords
- Broad keyword list to catch more mentions
- DDG discovery to find hundreds of accounts
"""

from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime, timezone
from typing import Optional

from workers.x_scraper.graphql_client import GraphQLClient
from workers.x_scraper.json_writer import JSONWriter
from workers.x_scraper.parser import parse_user_tweets_response

logger = logging.getLogger(__name__)

# Broad keyword list to catch more mentions
from workers.x_scraper.seed_accounts import SEED_ACCOUNTS

CLAUDE_KEYWORDS = [
    "claude", "anthropic",
]

# Accounts where we keep ALL tweets (no filter) — they're contextually relevant
ANTHROPIC_ACCOUNTS = {
    "anthropicai", "claudeai", "darioamodei", "amandaaskell",
    "alexalbert__", "jackclarksf",
}

STATE_FILE = "data/x_tweets/state.json"
ACCOUNTS_FILE = "data/x_tweets/discovered_accounts.json"


class XTimelineWorker:
    """Scrapes user timelines via GraphQL guest tokens, filtered for Claude mentions."""

    def __init__(
        self,
        accounts: list[str] | None = None,
        target_total: int = 50_000,
        output_dir: str = "data/x_tweets",
        filter_claude: bool = True,
        request_delay: float = 1.0,
        tweets_per_page: int = 20,
        discover: bool = True,
    ):
        self.seed_accounts = accounts or SEED_ACCOUNTS
        self.target_total = target_total
        self.output_dir = output_dir
        self.filter_claude = filter_claude
        self.request_delay = request_delay
        self.tweets_per_page = tweets_per_page
        self.discover = discover

        self.client = GraphQLClient()
        self.writer = JSONWriter(output_dir=output_dir)

        self._seen_ids: set[str] = set()
        self._total_collected = 0
        self._accounts_done: set[str] = set()
        self._all_accounts: list[str] = []
        self._state: dict = {}

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def scrape(self) -> int:
        """Run the scraper. Returns total tweets collected."""
        self._load_state()
        self._load_seen_ids()

        # Build full account list: seed + discovered
        self._all_accounts = list(self.seed_accounts)
        if self.discover:
            self._run_discovery()

        # Deduplicate account list
        seen = set()
        deduped = []
        for acc in self._all_accounts:
            if acc.lower() not in seen:
                seen.add(acc.lower())
                deduped.append(acc)
        self._all_accounts = deduped

        logger.info(
            f"[x] Starting scraper: {len(self._all_accounts)} accounts, "
            f"target={self.target_total:,}, already have={self._total_collected:,}"
        )

        self.writer.start()

        try:
            for i, account in enumerate(self._all_accounts):
                if account.lower() in self._accounts_done:
                    continue

                self._scrape_account(account)
                self._accounts_done.add(account.lower())

                if (i + 1) % 5 == 0:
                    self._save_state()
                    logger.info(
                        f"[x] Progress: {i+1}/{len(self._all_accounts)} accounts, "
                        f"{self._total_collected:,} tweets, "
                        f"{self.client.request_count} requests"
                    )

                if self._total_collected >= self.target_total:
                    logger.info(f"[x] Target reached: {self._total_collected:,}")
                    break

        except KeyboardInterrupt:
            logger.info(f"[x] Interrupted! Saving state...")
        finally:
            self.writer.stop()
            self._save_state()

        logger.info(
            f"[x] Scrape complete: {self._total_collected:,} tweets, "
            f"{self.client.request_count} API requests, "
            f"{len(self._accounts_done)} accounts scraped"
        )
        return self._total_collected

    # ------------------------------------------------------------------
    # Account discovery
    # ------------------------------------------------------------------

    def _run_discovery(self) -> None:
        """Discover additional accounts via DDG."""
        discovered = self._load_discovered_accounts()

        if discovered:
            existing = {a.lower() for a in self._all_accounts}
            new_count = 0
            for acc in discovered:
                if acc.lower() not in existing:
                    self._all_accounts.append(acc)
                    existing.add(acc.lower())
                    new_count += 1
            logger.info(f"[x] Loaded {new_count} previously discovered accounts")
            return

        logger.info("[x] Running DDG account discovery...")
        try:
            from workers.x_scraper.account_discovery import discover_accounts

            existing = {a.lower() for a in self._all_accounts}
            new_accounts = discover_accounts(existing_accounts=existing)

            for acc in new_accounts:
                if acc.lower() not in existing:
                    self._all_accounts.append(acc)
                    existing.add(acc.lower())

            self._save_discovered_accounts(new_accounts)
            logger.info(f"[x] Discovery added {len(new_accounts)} accounts")

        except Exception as exc:
            logger.warning(f"[x] Discovery failed: {exc}. Continuing with seed list.")

    def _save_discovered_accounts(self, accounts: list[str]) -> None:
        os.makedirs(os.path.dirname(ACCOUNTS_FILE), exist_ok=True)
        with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
            json.dump(accounts, f, indent=2)

    def _load_discovered_accounts(self) -> list[str]:
        if not os.path.exists(ACCOUNTS_FILE):
            return []
        try:
            with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    # ------------------------------------------------------------------
    # Per-account scraping
    # ------------------------------------------------------------------

    def _scrape_account(self, screen_name: str) -> None:
        """Scrape all tweets from a user's timeline."""
        user_id = self.client.get_user_id(screen_name)
        if not user_id:
            logger.debug(f"[x] Could not resolve @{screen_name}")
            return

        # Anthropic accounts: keep ALL tweets (no filter)
        skip_filter = screen_name.lower() in ANTHROPIC_ACCOUNTS

        cursor: Optional[str] = self._state.get(f"cursor_{screen_name.lower()}")
        page = 0
        account_tweets = 0
        empty_pages = 0

        while True:
            data = self.client.get_user_tweets(
                user_id, count=self.tweets_per_page, cursor=cursor
            )
            if not data:
                break

            tweets, next_cursor = parse_user_tweets_response(data)

            if not tweets:
                empty_pages += 1
                if empty_pages >= 3:
                    break
                if next_cursor:
                    cursor = next_cursor
                    time.sleep(self.request_delay)
                    continue
                break

            empty_pages = 0

            for tweet in tweets:
                tid = tweet["tweet_id"]
                if tid in self._seen_ids:
                    continue

                if not skip_filter and self.filter_claude and not self._is_claude_related(tweet):
                    continue

                self._seen_ids.add(tid)
                tweet["query"] = f"timeline:@{screen_name}"
                self.writer.write(tweet)
                self._total_collected += 1
                account_tweets += 1

            page += 1
            cursor = next_cursor

            if not cursor:
                break

            self._state[f"cursor_{screen_name.lower()}"] = cursor

            if self._total_collected >= self.target_total:
                break

            time.sleep(self.request_delay)

        if account_tweets > 0:
            logger.info(
                f"[x] @{screen_name}: {account_tweets} tweets "
                f"({page} pages, {'all' if skip_filter else 'claude-only'})"
            )

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    @staticmethod
    def _is_claude_related(tweet: dict) -> bool:
        """Check if a tweet mentions Claude/Anthropic."""
        text = tweet.get("text", "").lower()
        return any(kw in text for kw in CLAUDE_KEYWORDS)

    # ------------------------------------------------------------------
    # State management
    # ------------------------------------------------------------------

    def _save_state(self) -> None:
        self._state["total_collected"] = self._total_collected
        self._state["accounts_done"] = list(self._accounts_done)
        self._state["timestamp"] = datetime.now(tz=timezone.utc).isoformat()

        os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(self._state, f, indent=2)

    def _load_state(self) -> None:
        if not os.path.exists(STATE_FILE):
            return
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                self._state = json.load(f)
            self._accounts_done = set(self._state.get("accounts_done", []))
            self._total_collected = self._state.get("total_collected", 0)
            logger.info(
                f"[x] Resumed from state: {self._total_collected:,} tweets, "
                f"{len(self._accounts_done)} accounts done"
            )
        except Exception as exc:
            logger.warning(f"[x] Could not load state: {exc}")

    def _load_seen_ids(self) -> None:
        """Load seen tweet IDs from existing JSONL files."""
        if not os.path.exists(self.output_dir):
            return
        for fname in os.listdir(self.output_dir):
            if not fname.endswith(".jsonl"):
                continue
            path = os.path.join(self.output_dir, fname)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        tweet = json.loads(line)
                        self._seen_ids.add(tweet.get("tweet_id", ""))
            except Exception:
                continue
        if self._seen_ids:
            logger.info(f"[x] Loaded {len(self._seen_ids):,} seen tweet IDs")
