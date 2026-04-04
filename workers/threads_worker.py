"""
Threads scraper — DOM-based extraction using Playwright.

Why DOM, not embedded JSON
--------------------------
The scrapfly guide describes extracting data from <script data-sjs> blobs,
but as of 2026 Threads no longer embeds post data there (blobs only contain
React module definitions). Posts are rendered client-side and are accessible
in the DOM after JavaScript executes.

Strategy
---------
1. Load each target profile page with Playwright (headless Chromium).
2. Wait for <time datetime="..."> elements — their presence means posts rendered.
3. For each unique post link (href contains /post/), extract:
   - Post code + URL from href
   - ISO timestamp from <time datetime> attribute
   - Post text from the rendered container text
   - Engagement counts (likes, replies, reposts) parsed from numeric tokens
4. Filter results by Claude-related keywords (optional).

Limitations
-----------
- Private accounts (e.g. @anthropic on Threads) return no posts — logged.
- Keyword search requires login → we target known AI/tech accounts instead.
- Engagement number order in the DOM: likes, replies, reposts, quotes (Threads UI order).
"""

from __future__ import annotations

import logging
import re
import time
from datetime import datetime, timezone
from typing import Optional

from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

import config
from models.post import Post
from workers.base import BaseWorker

logger = logging.getLogger(__name__)

# Engagement numbers appear in this order in the Threads DOM
_ENGAGEMENT_ORDER = ["likes", "replies", "reposts", "quotes"]


class ThreadsWorker(BaseWorker):
    platform = "threads"

    def __init__(
        self,
        usernames: list[str] | None = None,
        max_posts_per_user: int = config.THREADS_MAX_POSTS_PER_USER,
        filter_keywords: list[str] | None = None,
    ):
        self.usernames = usernames or config.THREADS_TARGET_ACCOUNTS
        self.max_posts_per_user = max_posts_per_user
        self.filter_keywords = (
            [k.lower() for k in filter_keywords] if filter_keywords else None
        )

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def scrape(self) -> list[Post]:
        all_posts: list[Post] = []

        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            ctx = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                ),
                locale="en-US",
            )

            for username in self.usernames:
                try:
                    posts = self._scrape_profile(ctx, username)
                    all_posts.extend(posts)
                    logger.info(f"[threads] @{username}: {len(posts)} posts")
                except Exception as exc:
                    logger.error(f"[threads] @{username} failed: {exc}")
                time.sleep(config.REQUEST_DELAY_SECONDS)

            browser.close()

        logger.info(f"[threads] Total: {len(all_posts)} posts from {len(self.usernames)} accounts")
        return all_posts

    # ------------------------------------------------------------------
    # Per-profile scraping
    # ------------------------------------------------------------------

    def _scrape_profile(self, ctx, username: str) -> list[Post]:
        url = f"https://www.threads.net/@{username}"
        page = ctx.new_page()
        try:
            page.goto(url, timeout=config.PLAYWRIGHT_TIMEOUT_MS)
            page.wait_for_load_state("networkidle", timeout=20000)
            time.sleep(2)  # let React finish rendering

            # Check if account is private / login-gated
            body_text = page.evaluate("document.body.innerText")
            if "private" in body_text.lower() or "log in" in body_text.lower()[:200]:
                logger.warning(f"[threads] @{username} is private or requires login — skipping")
                return []

            # Scroll to load more posts
            for _ in range(2):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1.5)

            posts = self._extract_posts(page, username)
            return posts[: self.max_posts_per_user]

        except PlaywrightTimeout:
            logger.warning(f"[threads] Timeout loading @{username}")
            return []
        finally:
            page.close()

    # ------------------------------------------------------------------
    # DOM extraction
    # ------------------------------------------------------------------

    def _extract_posts(self, page, username: str) -> list[Post]:
        """Pull post data from rendered DOM elements."""
        # Collect unique post codes (deduplicate /post/CODE and /post/CODE/media)
        links = page.query_selector_all("a[href*='/post/']")
        seen_codes: dict[str, str] = {}  # code -> full href
        for link in links:
            href = link.get_attribute("href") or ""
            match = re.search(r"/post/([A-Za-z0-9_-]+)", href)
            if match:
                code = match.group(1)
                if code not in seen_codes:
                    seen_codes[code] = href

        # Map datetime elements by position (they align with post links)
        time_els = page.query_selector_all("time[datetime]")
        datetimes: list[str] = [
            t.get_attribute("datetime") or "" for t in time_els
        ]

        posts: list[Post] = []
        for idx, (code, href) in enumerate(seen_codes.items()):
            post = self._extract_single(page, username, code, href, datetimes, idx)
            if post and self._passes_filter(post):
                posts.append(post)

        return posts

    def _extract_single(
        self,
        page,
        username: str,
        code: str,
        href: str,
        datetimes: list[str],
        idx: int,
    ) -> Optional[Post]:
        try:
            # Find the post link element and walk up to get container text
            link_el = page.query_selector(f'a[href="{href}"]')
            if not link_el:
                return None

            # Walk up the DOM to find a container with enough text
            container_text: str = page.evaluate(
                """el => {
                    let node = el;
                    for (let i = 0; i < 20; i++) {
                        node = node.parentElement;
                        if (!node) break;
                        const lines = node.innerText.split('\\n').filter(l => l.trim());
                        if (lines.length >= 3) return node.innerText;
                    }
                    return el.parentElement ? el.parentElement.innerText : '';
                }""",
                link_el,
            )

            text, likes, replies, reposts = self._parse_container_text(
                container_text, username
            )

            # Get datetime from the aligned time element
            published_at: Optional[datetime] = None
            if idx < len(datetimes) and datetimes[idx]:
                try:
                    published_at = datetime.fromisoformat(
                        datetimes[idx].replace("Z", "+00:00")
                    )
                except ValueError:
                    pass

            url = f"https://www.threads.net{href}"
            hashtags = re.findall(r"#(\w+)", text)

            return Post(
                id=f"threads_{code}",
                platform="threads",
                post_title=text,
                author=username,
                url=url,
                likes=likes,
                reposts=reposts,
                comments=replies,
                hashtags=hashtags,
                published_at=published_at,
                scraped_at=datetime.now(tz=timezone.utc),
                raw_data={"code": code, "container_text": container_text},
            )
        except Exception as exc:
            logger.debug(f"[threads] Failed to parse post {code}: {exc}")
            return None

    # ------------------------------------------------------------------
    # Text parsing
    # ------------------------------------------------------------------

    def _parse_container_text(
        self, raw: str, username: str
    ) -> tuple[str, Optional[int], Optional[int], Optional[int]]:
        """
        Container innerText typically looks like:
            username
            MM/DD/YY
            Post text here... possibly multi-line
            hashtag1 hashtag2
            195          ← likes
            27           ← replies
            7            ← reposts
            1            ← quotes

        We strip the username/date header and trailing numbers.
        """
        lines = [l.strip() for l in raw.split("\n") if l.strip()]

        # Drop leading username lines and date lines
        date_pattern = re.compile(r"^\d{1,2}/\d{1,2}/\d{2,4}$")
        start = 0
        for i, line in enumerate(lines):
            if line.lower() == username.lower() or date_pattern.match(line):
                start = i + 1
            elif i > 3:
                break

        # Collect trailing pure-number lines (engagement counts)
        numbers: list[int] = []
        end = len(lines)
        for line in reversed(lines):
            if re.match(r"^\d[\d,KMk.]*$", line):
                numbers.insert(0, self._parse_number(line))
                end -= 1
            else:
                break

        # Remaining lines = post text
        text = " ".join(lines[start:end]).strip()

        # Assign engagement values in Threads DOM order
        likes = numbers[0] if len(numbers) > 0 else None
        replies = numbers[1] if len(numbers) > 1 else None
        reposts = numbers[2] if len(numbers) > 2 else None

        return text, likes, replies, reposts

    @staticmethod
    def _parse_number(s: str) -> int:
        """Parse '1.2K' → 1200, '4.5M' → 4500000, '195' → 195."""
        s = s.replace(",", "").strip()
        if s.endswith("K") or s.endswith("k"):
            return int(float(s[:-1]) * 1_000)
        if s.endswith("M") or s.endswith("m"):
            return int(float(s[:-1]) * 1_000_000)
        try:
            return int(s)
        except ValueError:
            return 0

    def _passes_filter(self, post: Post) -> bool:
        if self.filter_keywords is None:
            return True
        text = post.post_title.lower()
        return any(kw in text for kw in self.filter_keywords)
