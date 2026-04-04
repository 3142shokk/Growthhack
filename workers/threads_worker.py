"""
Threads scraper — two-mode DOM-based extraction using Playwright.

Modes
-----
1. DISCOVER mode (default for Claude-mentions)
   - Searches DuckDuckGo for site:threads.net + Claude keywords
   - Extracts Threads post URLs from search results
   - Scrapes each individual post page → gets views + full engagement
   - Finds posts from *anyone*, not just curated accounts

2. PROFILE mode
   - Scrapes a curated list of AI/tech accounts
   - Paginates through their recent posts
   - Optionally filters by Claude keywords

Why DOM, not embedded JSON
--------------------------
As of 2026, Threads no longer embeds post data in <script data-sjs> blobs
(they only contain React module definitions). Posts are rendered client-side
and are only accessible in the DOM after JavaScript executes.

Individual post pages (/post/CODE) also expose view counts, which profile
pages do not — so discovering URLs via DDG + scraping individually is the
best way to get complete data.
"""

from __future__ import annotations

import logging
import re
import time
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urlparse

from ddgs import DDGS
from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

import config
from models.post import Post
from workers.base import BaseWorker

logger = logging.getLogger(__name__)

# DDG search queries for Claude-related Threads posts
_SEARCH_QUERIES = [
    'site:threads.net "claude ai"',
    'site:threads.net "claude anthropic"',
    'site:threads.net "claude code"',
    'site:threads.net "claude opus" OR "claude sonnet"',
    'site:threads.net "anthropic" claude',
]


class ThreadsWorker(BaseWorker):
    platform = "threads"

    def __init__(
        self,
        usernames: list[str] | None = None,
        max_posts_per_user: int = config.THREADS_MAX_POSTS_PER_USER,
        filter_keywords: list[str] | None = None,
        mode: str = "discover",          # "discover" | "profile" | "both"
        max_discover: int = 60,          # max posts to discover via DDG
    ):
        self.usernames = usernames or config.THREADS_TARGET_ACCOUNTS
        self.max_posts_per_user = max_posts_per_user
        self.filter_keywords = (
            [k.lower() for k in filter_keywords] if filter_keywords else None
        )
        self.mode = mode
        self.max_discover = max_discover

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

            if self.mode in ("discover", "both"):
                discovered = self._discover_and_scrape(ctx)
                all_posts.extend(discovered)
                logger.info(f"[threads] discover mode: {len(discovered)} posts")

            if self.mode in ("profile", "both"):
                for username in self.usernames:
                    try:
                        posts = self._scrape_profile(ctx, username)
                        all_posts.extend(posts)
                        logger.info(f"[threads] @{username}: {len(posts)} posts")
                    except Exception as exc:
                        logger.error(f"[threads] @{username} failed: {exc}")
                    time.sleep(config.REQUEST_DELAY_SECONDS)

            browser.close()

        # Deduplicate by post ID
        seen: set[str] = set()
        unique = []
        for p in all_posts:
            if p.id not in seen:
                seen.add(p.id)
                unique.append(p)

        logger.info(f"[threads] Total unique posts: {len(unique)}")
        return unique

    # ------------------------------------------------------------------
    # Discover mode — DDG search → individual post scraping
    # ------------------------------------------------------------------

    def _discover_and_scrape(self, ctx) -> list[Post]:
        urls = self._find_post_urls()
        logger.info(f"[threads] DDG discovered {len(urls)} unique post URLs")

        posts: list[Post] = []
        total = min(len(urls), self.max_discover)
        for i, url in enumerate(urls[:total], 1):
            try:
                logger.info(f"[threads] [{i}/{total}] scraping {url}")
                post = self._scrape_single_post(ctx, url)
                if post and self._passes_filter(post):
                    posts.append(post)
                    logger.info(f"[threads]   ✓ collected — likes={post.likes} views={post.views} author=@{post.author}")
                else:
                    logger.debug(f"[threads]   ✗ skipped (filtered or empty)")
                time.sleep(1.5)
            except Exception as exc:
                logger.debug(f"[threads] Failed to scrape {url}: {exc}")
        return posts

    def _find_post_urls(self) -> list[str]:
        """Use DuckDuckGo to discover public Threads post URLs mentioning Claude."""
        seen: set[str] = set()
        urls: list[str] = []

        for query in _SEARCH_QUERIES:
            try:
                # backend="lite" uses DDG's lightweight HTML endpoint — much faster,
                # avoids the ~14min Google timeout that the default multi-backend mode hits
                results = list(DDGS().text(query, max_results=20, backend="lite"))
                for r in results:
                    href = r.get("href", "")
                    # Only keep direct post URLs (not profile or search pages)
                    if "/post/" in href:
                        # Normalize — strip trailing slug text after post code
                        match = re.search(r"(https://www\.threads\.net/@[^/]+/post/[A-Za-z0-9_-]+)", href)
                        if match:
                            clean = match.group(1)
                            if clean not in seen:
                                seen.add(clean)
                                urls.append(clean)
                time.sleep(1.5)  # polite DDG rate limit
            except Exception as exc:
                logger.warning(f"[threads] DDG search failed for '{query}': {exc}")

        return urls

    def _scrape_single_post(self, ctx, url: str) -> Optional[Post]:
        """Scrape an individual Threads post page."""
        page = ctx.new_page()
        try:
            page.goto(url, timeout=config.PLAYWRIGHT_TIMEOUT_MS)
            page.wait_for_load_state("domcontentloaded")
            time.sleep(3)  # let React render the post

            body_text = page.evaluate("document.body.innerText")
            if "log in" in body_text.lower()[:100]:
                return None

            # Extract post code and username from URL
            url_match = re.search(r"/@([^/]+)/post/([A-Za-z0-9_-]+)", url)
            if not url_match:
                return None
            username, code = url_match.group(1), url_match.group(2)

            # View count appears as "X views" or "X.XK views" at the top
            views = None
            view_match = re.search(r"([\d,.]+[KMk]?)\s+views", body_text)
            if view_match:
                views = self._parse_number(view_match.group(1))

            # Get time element for published_at
            time_el = page.query_selector("time[datetime]")
            published_at = None
            if time_el:
                dt_str = time_el.get_attribute("datetime") or ""
                try:
                    published_at = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
                except ValueError:
                    pass

            # Extract post text and engagement from the container
            container_text = body_text.split("\n")
            text, likes, replies, reposts = self._parse_post_page_text(
                container_text, username
            )

            hashtags = re.findall(r"#(\w+)", text)

            return Post(
                id=f"threads_{code}",
                platform="threads",
                post_title=text,
                author=username,
                url=url,
                views=views,
                likes=likes,
                reposts=reposts,
                comments=replies,
                hashtags=hashtags,
                published_at=published_at,
                scraped_at=datetime.now(tz=timezone.utc),
                raw_data={"code": code, "url": url},
            )
        except PlaywrightTimeout:
            logger.warning(f"[threads] Timeout on {url}")
            return None
        finally:
            page.close()

    def _parse_post_page_text(
        self, lines: list[str], username: str
    ) -> tuple[str, Optional[int], Optional[int], Optional[int]]:
        """
        Individual post page body (innerText) looks like:
            Thread
            150K views
            mengto
            11/28/24
            Post text here... (may be multi-line)
            1.8K   ← likes
            106    ← replies
            137    ← reposts
            390    ← quotes
            mengto        ← replies section starts here (ignore rest)
            11/28/24
            · Author
            Reply text...
        We find the engagement block by scanning for the first run of
        3+ consecutive pure-number lines after the header.
        """
        clean = [l.strip() for l in lines if l.strip()]
        num_pat = re.compile(r"^[\d,.]+[KMk]?$")
        date_pat = re.compile(r"^\d{1,2}/\d{1,2}/\d{2,4}$")
        skip = {"thread", "threads", "home"}
        views_pat = re.compile(r"^[\d,.]+[KMk]?\s+views$", re.I)

        # Skip header lines
        start = 0
        for i, line in enumerate(clean[:8]):
            if (
                line.lower() in skip
                or line.lower() == username.lower()
                or date_pat.match(line)
                or views_pat.match(line)
            ):
                start = i + 1

        # Scan forward to find the engagement number block (3-4 consecutive numbers)
        text_end = len(clean)
        numbers: list[int] = []
        for i in range(start, len(clean)):
            if num_pat.match(clean[i]):
                # Check if this starts a run of at least 2 numbers
                run = []
                j = i
                while j < len(clean) and num_pat.match(clean[j]):
                    run.append(self._parse_number(clean[j]))
                    j += 1
                if len(run) >= 2:
                    numbers = run
                    text_end = i
                    break

        text = " ".join(clean[start:text_end]).strip()
        likes   = numbers[0] if len(numbers) > 0 else None
        replies = numbers[1] if len(numbers) > 1 else None
        reposts = numbers[2] if len(numbers) > 2 else None
        return text, likes, replies, reposts

    # ------------------------------------------------------------------
    # Profile mode (unchanged from v1)
    # ------------------------------------------------------------------

    def _scrape_profile(self, ctx, username: str) -> list[Post]:
        url = f"https://www.threads.net/@{username}"
        page = ctx.new_page()
        try:
            page.goto(url, timeout=config.PLAYWRIGHT_TIMEOUT_MS)
            page.wait_for_load_state("networkidle", timeout=20000)
            time.sleep(2)

            body_text = page.evaluate("document.body.innerText")
            if "private" in body_text.lower() or "log in" in body_text.lower()[:200]:
                logger.warning(f"[threads] @{username} is private or gated — skipping")
                return []

            for _ in range(2):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1.5)

            return self._extract_posts_from_profile(page, username)[: self.max_posts_per_user]

        except PlaywrightTimeout:
            logger.warning(f"[threads] Timeout loading @{username}")
            return []
        finally:
            page.close()

    def _extract_posts_from_profile(self, page, username: str) -> list[Post]:
        links = page.query_selector_all("a[href*='/post/']")
        seen_codes: dict[str, str] = {}
        for link in links:
            href = link.get_attribute("href") or ""
            match = re.search(r"/post/([A-Za-z0-9_-]+)", href)
            if match:
                code = match.group(1)
                if code not in seen_codes:
                    seen_codes[code] = href

        time_els = page.query_selector_all("time[datetime]")
        datetimes = [t.get_attribute("datetime") or "" for t in time_els]

        posts: list[Post] = []
        for idx, (code, href) in enumerate(seen_codes.items()):
            post = self._extract_profile_post(page, username, code, href, datetimes, idx)
            if post and self._passes_filter(post):
                posts.append(post)
        return posts

    def _extract_profile_post(self, page, username, code, href, datetimes, idx) -> Optional[Post]:
        try:
            link_el = page.query_selector(f'a[href="{href}"]')
            if not link_el:
                return None

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

            text, likes, replies, reposts = self._parse_container_text(container_text, username)

            published_at = None
            if idx < len(datetimes) and datetimes[idx]:
                try:
                    published_at = datetime.fromisoformat(datetimes[idx].replace("Z", "+00:00"))
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
            logger.debug(f"[threads] Failed to parse profile post {code}: {exc}")
            return None

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    def _parse_container_text(self, raw: str, username: str) -> tuple[str, Optional[int], Optional[int], Optional[int]]:
        lines = [l.strip() for l in raw.split("\n") if l.strip()]
        date_pattern = re.compile(r"^\d{1,2}/\d{1,2}/\d{2,4}$")
        start = 0
        for i, line in enumerate(lines):
            if line.lower() == username.lower() or date_pattern.match(line):
                start = i + 1
            elif i > 3:
                break

        numbers: list[int] = []
        end = len(lines)
        for line in reversed(lines):
            if re.match(r"^\d[\d,KMk.]*$", line):
                numbers.insert(0, self._parse_number(line))
                end -= 1
            else:
                break

        text = " ".join(lines[start:end]).strip()
        likes   = numbers[0] if len(numbers) > 0 else None
        replies = numbers[1] if len(numbers) > 1 else None
        reposts = numbers[2] if len(numbers) > 2 else None
        return text, likes, replies, reposts

    @staticmethod
    def _parse_number(s: str) -> int:
        s = s.replace(",", "").strip()
        if s.upper().endswith("K"):
            return int(float(s[:-1]) * 1_000)
        if s.upper().endswith("M"):
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
