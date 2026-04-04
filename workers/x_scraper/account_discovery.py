"""
Account discovery — find Twitter accounts that tweet about Claude/Anthropic.

Uses DuckDuckGo to search for tweets mentioning Claude, then extracts
unique author screen names from the URLs. These accounts are then fed
into the timeline scraper.
"""

from __future__ import annotations

import logging
import re
import time
from typing import Optional

from ddgs import DDGS

logger = logging.getLogger(__name__)

_TWEET_AUTHOR_RE = re.compile(r"(?:x\.com|twitter\.com)/(\w+)/status/")

# Broad DDG queries to find accounts across all domains
DISCOVERY_QUERIES = [
    # Direct Claude mentions
    "Claude AI",
    "Claude Anthropic",
    "Claude Code",
    "Claude Opus",
    "Claude Sonnet",
    "Claude Haiku",
    "Anthropic AI",
    "Anthropic Claude",
    "claude.ai",
    "Claude API",
    "Claude artifacts",
    "Claude computer use",
    # Usage / reactions
    "using Claude",
    "switched to Claude",
    "Claude is amazing",
    "Claude helped me",
    "built with Claude",
    "Claude can now",
    "Claude update",
    "tried Claude",
    "love Claude AI",
    "Claude blew my mind",
    # Business / industry
    "Anthropic funding",
    "Anthropic valuation",
    "Anthropic partnership",
    "Anthropic Google",
    "Anthropic Amazon",
    "Dario Amodei",
    "Anthropic CEO",
    "Anthropic safety",
    # Media / news coverage
    "Claude AI review",
    "Claude AI news",
    "Anthropic news",
    "Anthropic announcement",
    "Claude launch",
    "Claude released",
    # Politics / regulation
    "AI regulation Claude",
    "AI safety Anthropic",
    "Senate AI Anthropic",
    "Congress AI Claude",
    "AI policy Anthropic",
    "Dario Amodei testimony",
    "Dario Amodei interview",
    # Education
    "Claude education",
    "Claude students",
    "Claude teaching",
    "Claude university",
    "Claude research",
    # Specific use cases
    "Claude coding",
    "Claude writing",
    "Claude legal",
    "Claude healthcare",
    "Claude finance",
    "Claude marketing",
    "Claude productivity",
    # Time-based (different results)
    "Claude AI 2024",
    "Claude AI 2025",
    "Claude AI 2026",
    "Anthropic 2024",
    "Anthropic 2025",
    "Anthropic 2026",
    # Controversy / opinions
    "Claude better than ChatGPT",
    "quit ChatGPT Claude",
    "Claude problem",
    "Claude down",
    "Claude outage",
    "Anthropic controversy",
    # Viral / meme
    "Claude just",
    "Claude literally",
    "Claude be like",
    "Anthropic just",
]


def discover_accounts(
    queries: list[str] | None = None,
    max_per_query: int = 200,
    delay: float = 2.0,
    existing_accounts: set[str] | None = None,
) -> list[str]:
    """
    Use DuckDuckGo to discover Twitter accounts that tweet about Claude.
    Returns a deduplicated list of screen names sorted by mention frequency.
    """
    queries = queries or DISCOVERY_QUERIES
    existing = {a.lower() for a in (existing_accounts or set())}
    found: dict[str, int] = {}  # screen_name -> mention count

    for qi, query in enumerate(queries):
        accounts_from_query = _search_query(query, max_per_query)
        for account in accounts_from_query:
            al = account.lower()
            if al not in existing:
                found[account] = found.get(account, 0) + 1

        logger.info(
            f"[discovery] Query {qi+1}/{len(queries)}: '{query}' "
            f"-> {len(found)} unique new accounts so far"
        )

        time.sleep(delay)

    # Sort by mention count (most frequently found = most relevant)
    sorted_accounts = sorted(found.keys(), key=lambda a: found[a], reverse=True)

    logger.info(
        f"[discovery] Discovery complete: {len(sorted_accounts)} new accounts found. "
        f"Top 10: {', '.join(f'@{a}({found[a]})' for a in sorted_accounts[:10])}"
    )

    return sorted_accounts


def _search_query(query: str, max_results: int) -> list[str]:
    """Run DDG search and extract Twitter account names from results."""
    accounts = []
    skip_names = {"i", "search", "explore", "home", "settings", "hashtag", "intent"}

    for site in ["x.com", "twitter.com"]:
        try:
            results = list(DDGS().text(f"{query} site:{site}", max_results=max_results))
            for r in results:
                href = r.get("href", "")
                match = _TWEET_AUTHOR_RE.search(href)
                if match:
                    screen_name = match.group(1)
                    if screen_name.lower() not in skip_names:
                        accounts.append(screen_name)
        except Exception as exc:
            logger.warning(f"[discovery] DDG search failed: {exc}")

    return accounts
