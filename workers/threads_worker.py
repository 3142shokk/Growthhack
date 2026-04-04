"""
Threads scraper — parallel hashtag page scraping.

Strategy
--------
1. Split hashtag list across N parallel workers (ThreadPoolExecutor).
2. Each worker spawns its own Playwright browser, loads the hashtag page,
   and scrolls aggressively to surface as many posts as possible.
3. DDG discovery runs after as a top-up for any posts not on hashtag pages.

Why parallel + scroll beats sequential:
- Hashtag pages lazy-load more posts on scroll — 12 scrolls yields ~50-80 posts
- 4 parallel contexts = 4x throughput on hashtag collection
- Each browser context is independent, no shared state issues

Ceiling without login: ~50-80 posts per hashtag page (Threads hard-limits
further scrolling without auth). With 18 hashtags × 80 posts = ~1,400 posts max.
"""

from __future__ import annotations

import logging
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Optional

from ddgs import DDGS
from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

import config
from models.post import Post
from workers.base import BaseWorker

logger = logging.getLogger(__name__)

_DDG_QUERIES = [
    'site:threads.net "claude ai"',
    'site:threads.net "claude anthropic"',
    'site:threads.net "claude code"',
    'site:threads.net "claude opus" OR "claude sonnet"',
]

_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


class ThreadsWorker(BaseWorker):
    platform = "threads"

    def __init__(
        self,
        hashtags: list[str] | None = None,
        max_per_hashtag: int = config.THREADS_MAX_POSTS_PER_HASHTAG,
        scroll_rounds: int = config.THREADS_SCROLL_ROUNDS,
        parallel: int = config.THREADS_PARALLEL_HASHTAGS,
        max_discover: int = 40,
        **kwargs,
    ):
        self.hashtags = hashtags or config.THREADS_HASHTAGS
        self.max_per_hashtag = max_per_hashtag
        self.scroll_rounds = scroll_rounds
        self.parallel = parallel
        self.max_discover = max_discover

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def scrape(self) -> list[Post]:
        all_posts: list[Post] = []
        seen_ids: set[str] = set()

        # Phase 1 — parallel hashtag scraping
        logger.info(
            f"[threads] Scraping {len(self.hashtags)} hashtags "
            f"({self.parallel} parallel, {self.scroll_rounds} scrolls each)"
        )
        hashtag_posts = self._scrape_hashtags_parallel()
        for p in hashtag_posts:
            if p.id not in seen_ids:
                seen_ids.add(p.id)
                all_posts.append(p)

        logger.info(f"[threads] Hashtags done: {len(all_posts)} unique posts")

        # Phase 2 — DDG top-up
        urls = self._find_post_urls()
        logger.info(f"[threads] DDG discovered {len(urls)} additional URLs")

        if urls:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)
                ctx = browser.new_context(user_agent=_UA, locale="en-US")
                total = min(len(urls), self.max_discover)
                for i, url in enumerate(urls[:total], 1):
                    m = re.search(r"/post/([A-Za-z0-9_-]+)", url)
                    if m and f"threads_{m.group(1)}" in seen_ids:
                        continue
                    try:
                        logger.info(f"[threads] DDG [{i}/{total}] {url}")
                        post = self._scrape_single_post(ctx, url)
                        if post and post.id not in seen_ids:
                            all_posts.append(post)
                            seen_ids.add(post.id)
                            logger.info(f"[threads]   ✓ likes={post.likes} views={post.views} @{post.author}")
                        time.sleep(1.5)
                    except Exception as exc:
                        logger.debug(f"[threads] DDG post failed: {exc}")
                browser.close()

        logger.info(f"[threads] Total: {len(all_posts)} unique posts")
        return all_posts

    # ------------------------------------------------------------------
    # Parallel hashtag scraping
    # ------------------------------------------------------------------

    def _scrape_hashtags_parallel(self) -> list[Post]:
        results: list[Post] = []
        with ThreadPoolExecutor(max_workers=self.parallel) as pool:
            futures = {
                pool.submit(self._scrape_one_hashtag, tag): tag
                for tag in self.hashtags
            }
            for future in as_completed(futures):
                tag = futures[future]
                try:
                    posts = future.result()
                    results.extend(posts)
                    logger.info(f"[threads] #{tag}: {len(posts)} posts")
                except Exception as exc:
                    logger.error(f"[threads] #{tag} failed: {exc}")
        return results

    def _scrape_one_hashtag(self, tag: str) -> list[Post]:
        """Runs in its own thread — each thread owns its Playwright instance."""
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            ctx = browser.new_context(user_agent=_UA, locale="en-US")
            page = ctx.new_page()
            try:
                url = f"https://www.threads.net/tag/{tag.lstrip('#').lower()}"
                page.goto(url, timeout=config.PLAYWRIGHT_TIMEOUT_MS)
                page.wait_for_load_state("domcontentloaded")
                time.sleep(2)

                body = page.evaluate("document.body.innerText")
                if "log in" in body.lower()[:300]:
                    logger.warning(f"[threads] #{tag} gated — skipping")
                    return []

                # Scroll to load more posts
                prev_count = 0
                for _ in range(self.scroll_rounds):
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(1.2)
                    links = page.query_selector_all("a[href*='/post/']")
                    if len(links) == prev_count:
                        break  # no new posts loaded, stop early
                    prev_count = len(links)

                posts = self._extract_posts_from_page(page, source_tag=tag)
                return posts[: self.max_per_hashtag]

            except PlaywrightTimeout:
                logger.warning(f"[threads] #{tag} timeout")
                return []
            finally:
                browser.close()

    # ------------------------------------------------------------------
    # DOM extraction
    # ------------------------------------------------------------------

    def _extract_posts_from_page(self, page, source_tag: str = "") -> list[Post]:
        links = page.query_selector_all("a[href*='/post/']")
        seen_codes: dict[str, str] = {}
        for link in links:
            href = link.get_attribute("href") or ""
            m = re.search(r"/post/([A-Za-z0-9_-]+)", href)
            if m and m.group(1) not in seen_codes:
                seen_codes[m.group(1)] = href

        time_els = page.query_selector_all("time[datetime]")
        datetimes = [t.get_attribute("datetime") or "" for t in time_els]

        posts: list[Post] = []
        for idx, (code, href) in enumerate(seen_codes.items()):
            post = self._extract_card(page, code, href, datetimes, idx, source_tag)
            if post:
                posts.append(post)
        return posts

    def _extract_card(self, page, code, href, datetimes, idx, source_tag) -> Optional[Post]:
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

            author_match = re.search(r"/@([^/]+)/post/", href)
            author = author_match.group(1) if author_match else "unknown"
            text, likes, replies, reposts = self._parse_card_text(container_text, author)

            published_at = None
            if idx < len(datetimes) and datetimes[idx]:
                try:
                    published_at = datetime.fromisoformat(datetimes[idx].replace("Z", "+00:00"))
                except ValueError:
                    pass

            url = f"https://www.threads.net{href}"
            hashtags = list({source_tag} | set(re.findall(r"#(\w+)", text)))

            return Post(
                id=f"threads_{code}",
                platform="threads",
                post_title=text,
                author=author,
                url=url,
                likes=likes,
                reposts=reposts,
                comments=replies,
                hashtags=[h for h in hashtags if h],
                published_at=published_at,
                scraped_at=datetime.now(tz=timezone.utc),
                raw_data={"code": code, "source": f"hashtag:{source_tag}"},
            )
        except Exception as exc:
            logger.debug(f"[threads] card parse failed {code}: {exc}")
            return None

    # ------------------------------------------------------------------
    # DDG discovery
    # ------------------------------------------------------------------

    def _find_post_urls(self) -> list[str]:
        seen: set[str] = set()
        urls: list[str] = []
        for query in _DDG_QUERIES:
            try:
                results = list(DDGS().text(query, max_results=20, backend="auto"))
                for r in results:
                    href = r.get("href", "")
                    m = re.search(r"(https://www\.threads\.net/@[^/]+/post/[A-Za-z0-9_-]+)", href)
                    if m and m.group(1) not in seen:
                        seen.add(m.group(1))
                        urls.append(m.group(1))
                time.sleep(1)
            except Exception as exc:
                logger.warning(f"[threads] DDG failed: {exc}")
        return urls

    def _scrape_single_post(self, ctx, url: str) -> Optional[Post]:
        page = ctx.new_page()
        try:
            page.goto(url, timeout=config.PLAYWRIGHT_TIMEOUT_MS)
            page.wait_for_load_state("domcontentloaded")
            time.sleep(3)

            body_text = page.evaluate("document.body.innerText")
            if "log in" in body_text.lower()[:100]:
                return None

            url_match = re.search(r"/@([^/]+)/post/([A-Za-z0-9_-]+)", url)
            if not url_match:
                return None
            username, code = url_match.group(1), url_match.group(2)

            views = None
            view_match = re.search(r"([\d,.]+[KMk]?)\s+views", body_text)
            if view_match:
                views = self._parse_number(view_match.group(1))

            time_el = page.query_selector("time[datetime]")
            published_at = None
            if time_el:
                dt_str = time_el.get_attribute("datetime") or ""
                try:
                    published_at = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
                except ValueError:
                    pass

            text, likes, replies, reposts = self._parse_post_page_text(
                body_text.split("\n"), username
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
                raw_data={"code": code, "source": "ddg_discover"},
            )
        except PlaywrightTimeout:
            return None
        finally:
            page.close()

    # ------------------------------------------------------------------
    # Parsers
    # ------------------------------------------------------------------

    def _parse_card_text(self, raw: str, username: str):
        lines = [l.strip() for l in raw.split("\n") if l.strip()]
        date_pat = re.compile(r"^\d{1,2}/\d{1,2}/\d{2,4}$")
        num_pat = re.compile(r"^[\d,.]+[KMk]?$")

        start = 0
        for i, line in enumerate(lines[:6]):
            if line.lower() == username.lower() or date_pat.match(line):
                start = i + 1

        text_end = len(lines)
        numbers: list[int] = []
        for i in range(start, len(lines)):
            if num_pat.match(lines[i]):
                run, j = [], i
                while j < len(lines) and num_pat.match(lines[j]):
                    run.append(self._parse_number(lines[j]))
                    j += 1
                if len(run) >= 2:
                    numbers, text_end = run, i
                    break

        text = " ".join(lines[start:text_end]).strip()
        return text, numbers[0] if numbers else None, numbers[1] if len(numbers) > 1 else None, numbers[2] if len(numbers) > 2 else None

    def _parse_post_page_text(self, lines: list[str], username: str):
        clean = [l.strip() for l in lines if l.strip()]
        num_pat = re.compile(r"^[\d,.]+[KMk]?$")
        date_pat = re.compile(r"^\d{1,2}/\d{1,2}/\d{2,4}$")
        skip = {"thread", "threads", "home"}
        views_pat = re.compile(r"^[\d,.]+[KMk]?\s+views$", re.I)

        start = 0
        for i, line in enumerate(clean[:8]):
            if line.lower() in skip or line.lower() == username.lower() or date_pat.match(line) or views_pat.match(line):
                start = i + 1

        text_end = len(clean)
        numbers: list[int] = []
        for i in range(start, len(clean)):
            if num_pat.match(clean[i]):
                run, j = [], i
                while j < len(clean) and num_pat.match(clean[j]):
                    run.append(self._parse_number(clean[j]))
                    j += 1
                if len(run) >= 2:
                    numbers, text_end = run, i
                    break

        text = " ".join(clean[start:text_end]).strip()
        return text, numbers[0] if numbers else None, numbers[1] if len(numbers) > 1 else None, numbers[2] if len(numbers) > 2 else None

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
