"""
google_trends_worker.py — fetches all available Google Trends data for
"Claude" and "Anthropic" since their public launch in January 2024.

Data collected
--------------
1. Interest over time   — weekly search interest (0-100) per keyword
2. Interest by region   — per-country interest scores (normalised 0-100)
3. Related queries      — top + rising queries people search alongside the keyword
4. Related topics       — top + rising broader topic categories

Timeframe: 2024-01-01 → today (weekly granularity for a ~2-year window).
pytrends allows max 5 keywords per payload; we have 2 so one request each.

API docs: https://pypi.org/project/pytrends/
Rate limit: unofficial — polite 2 s delay between calls avoids 429s.
"""

import hashlib
import logging
import time
from datetime import datetime, timezone

import pandas as pd

# urllib3 2.x renamed method_whitelist → allowed_methods; patch for pytrends compatibility
try:
    import urllib3.util.retry as _retry_mod
    if not hasattr(_retry_mod.Retry, "_orig_init"):
        _orig_retry_init = _retry_mod.Retry.__init__

        def _patched_retry_init(self, *args, method_whitelist=None, **kwargs):
            if method_whitelist is not None and "allowed_methods" not in kwargs:
                kwargs["allowed_methods"] = method_whitelist
            _orig_retry_init(self, *args, **kwargs)

        _retry_mod.Retry._orig_init = _orig_retry_init
        _retry_mod.Retry.__init__ = _patched_retry_init
except Exception:
    pass

from pytrends.request import TrendReq

import config
from models.post import Post
from workers.base import BaseWorker

logger = logging.getLogger(__name__)

# Only Claude and Anthropic — the two entities we care about
TRENDS_KEYWORDS = ["Claude", "Anthropic"]

# Full period since Claude's public availability
TIMEFRAME = "2024-01-01 2026-04-04"
GEO = ""  # worldwide
_DELAY = 5.0        # base delay between API calls
_REGION_DELAY = 15.0  # longer pause before interest_by_region (most rate-limited)


class GoogleTrendsWorker(BaseWorker):
    platform = "google_trends"

    def __init__(self, keywords: list[str] | None = None):
        self.keywords = keywords or TRENDS_KEYWORDS
        self.pytrends = TrendReq(hl="en-US", tz=0, timeout=(10, 30), retries=3, backoff_factor=1.5)

    def scrape(self) -> list[Post]:
        posts: list[Post] = []
        now = datetime.now(timezone.utc)

        # 1. Interest over time (weekly, worldwide)
        logger.info("[trends] Fetching interest over time …")
        for keyword, date, score in self._fetch_interest_over_time():
            posts.append(self._make_post(
                keyword=keyword,
                title=f"[Trend] {keyword}",
                trend_score=score,
                url=self._trends_url(keyword),
                scraped_at=now,
                published_at=date,
            ))

        # 2. Interest by region (country-level breakdown)
        logger.info(f"[trends] Waiting {_REGION_DELAY}s before region fetch …")
        time.sleep(_REGION_DELAY)
        logger.info("[trends] Fetching interest by region …")
        for keyword, country_code, country_name, score in self._fetch_interest_by_region():
            posts.append(self._make_post(
                keyword=keyword,
                title=f"[Region] {keyword} — {country_name}",
                trend_score=score,
                url=self._trends_url(keyword),
                scraped_at=now,
                description=f"Country: {country_code}  |  Interest score: {score}",
                hashtags=[keyword.lower(), country_code.lower()],
            ))

        # 3. Related queries (top + rising)
        logger.info("[trends] Fetching related queries …")
        for keyword in self.keywords:
            for row in self._fetch_related_queries(keyword, kind="rising"):
                posts.append(self._make_post(
                    keyword=keyword,
                    title=f"[Rising query] {row['query']}",
                    trend_score=None,
                    url=self._trends_url(row["query"]),
                    scraped_at=now,
                    description=f"Rising related query for '{keyword}': value={row['value']}",
                    hashtags=[keyword.lower(), "rising"],
                ))
            for row in self._fetch_related_queries(keyword, kind="top"):
                posts.append(self._make_post(
                    keyword=keyword,
                    title=f"[Top query] {row['query']}",
                    trend_score=int(row["value"]) if str(row["value"]).isdigit() else None,
                    url=self._trends_url(row["query"]),
                    scraped_at=now,
                    description=f"Top related query for '{keyword}': value={row['value']}",
                    hashtags=[keyword.lower(), "top"],
                ))
            time.sleep(_DELAY)

        # 4. Related topics (top + rising)
        logger.info("[trends] Fetching related topics …")
        for keyword in self.keywords:
            for row in self._fetch_related_topics(keyword, kind="rising"):
                posts.append(self._make_post(
                    keyword=keyword,
                    title=f"[Rising topic] {row['topic_title']}",
                    trend_score=None,
                    url=self._trends_url(row["topic_title"]),
                    scraped_at=now,
                    description=f"Rising topic for '{keyword}': type={row.get('topic_type','')}  value={row.get('value','')}",
                    hashtags=[keyword.lower(), "rising_topic"],
                ))
            for row in self._fetch_related_topics(keyword, kind="top"):
                posts.append(self._make_post(
                    keyword=keyword,
                    title=f"[Top topic] {row['topic_title']}",
                    trend_score=int(row["value"]) if str(row.get("value", "")).isdigit() else None,
                    url=self._trends_url(row["topic_title"]),
                    scraped_at=now,
                    description=f"Top topic for '{keyword}': type={row.get('topic_type','')}  value={row.get('value','')}",
                    hashtags=[keyword.lower(), "top_topic"],
                ))
            time.sleep(_DELAY)

        logger.info(f"[trends] Total collected: {len(posts)} data points")
        return posts

    # ------------------------------------------------------------------
    # Fetchers
    # ------------------------------------------------------------------

    def _fetch_interest_over_time(self) -> list[tuple[str, datetime, int]]:
        rows: list[tuple[str, datetime, int]] = []
        try:
            self.pytrends.build_payload(self.keywords, cat=0, timeframe=TIMEFRAME, geo=GEO)
            df: pd.DataFrame = self.pytrends.interest_over_time()
            if df.empty:
                return rows
            for ts, row in df.iterrows():
                date = ts.to_pydatetime().replace(tzinfo=timezone.utc)
                for kw in self.keywords:
                    if kw in df.columns:
                        rows.append((kw, date, int(row[kw])))
        except Exception as e:
            logger.warning(f"[trends] interest_over_time failed: {e}")
        time.sleep(_DELAY)
        return rows

    def _fetch_interest_by_region(self) -> list[tuple[str, str, str, int]]:
        """Returns (keyword, country_code, country_name, score) for each country."""
        results: list[tuple[str, str, str, int]] = []
        for attempt in range(4):
            wait = _DELAY * (2 ** attempt)  # 5 → 10 → 20 → 40 s
            try:
                self.pytrends.build_payload(self.keywords, cat=0, timeframe=TIMEFRAME, geo=GEO)
                df: pd.DataFrame = self.pytrends.interest_by_region(resolution="COUNTRY", inc_low_vol=True)
                if df.empty:
                    return results
                for country_code, row in df.iterrows():
                    for kw in self.keywords:
                        if kw in df.columns:
                            score = int(row[kw])
                            if score > 0:
                                results.append((kw, country_code, country_code, score))
                time.sleep(_DELAY)
                return results
            except Exception as e:
                if "429" in str(e) and attempt < 3:
                    logger.warning(f"[trends] interest_by_region rate-limited, retrying in {wait}s (attempt {attempt+1}/4)")
                    time.sleep(wait)
                else:
                    logger.warning(f"[trends] interest_by_region failed after {attempt+1} attempts: {e}")
                    return results
        return results

    def _fetch_related_queries(self, keyword: str, kind: str = "rising") -> list[dict]:
        for attempt in range(3):
            wait = _DELAY * (2 ** attempt)
            try:
                self.pytrends.build_payload([keyword], cat=0, timeframe=TIMEFRAME, geo=GEO)
                related = self.pytrends.related_queries()
                df = related.get(keyword, {}).get(kind)
                time.sleep(_DELAY)
                if df is None or df.empty:
                    return []
                return df.head(25).to_dict(orient="records")
            except Exception as e:
                if "429" in str(e) and attempt < 2:
                    logger.warning(f"[trends] related_queries({keyword},{kind}) rate-limited, retrying in {wait}s")
                    time.sleep(wait)
                else:
                    logger.warning(f"[trends] related_queries({keyword},{kind}) failed: {e}")
                    return []
        return []

    def _fetch_related_topics(self, keyword: str, kind: str = "rising") -> list[dict]:
        for attempt in range(3):
            wait = _DELAY * (2 ** attempt)
            try:
                self.pytrends.build_payload([keyword], cat=0, timeframe=TIMEFRAME, geo=GEO)
                related = self.pytrends.related_topics()
                df = related.get(keyword, {}).get(kind)
                time.sleep(_DELAY)
                if df is None or df.empty:
                    return []
                records = df.head(25).to_dict(orient="records")
                out = []
                for r in records:
                    out.append({
                        "topic_title": r.get("topic_title") or r.get("title") or str(r),
                        "topic_type": r.get("topic_type") or r.get("type") or "",
                        "value": r.get("value") or r.get("formattedValue") or "",
                    })
                return out
            except Exception as e:
                if "429" in str(e) and attempt < 2:
                    logger.warning(f"[trends] related_topics({keyword},{kind}) rate-limited, retrying in {wait}s")
                    time.sleep(wait)
                else:
                    logger.warning(f"[trends] related_topics({keyword},{kind}) failed: {e}")
                    return []
        return []

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _trends_url(query: str) -> str:
        encoded = query.replace(" ", "+")
        return f"https://trends.google.com/trends/explore?q={encoded}&geo=&hl=en"

    @staticmethod
    def _make_post(
        keyword: str,
        title: str,
        trend_score: int | None,
        url: str,
        scraped_at: datetime,
        published_at: datetime | None = None,
        description: str | None = None,
        hashtags: list[str] | None = None,
    ) -> Post:
        uid = hashlib.md5(f"{title}{url}{published_at}".encode()).hexdigest()[:16]
        return Post(
            id=uid,
            platform="google_trends",
            post_title=title,
            author="google_trends",
            url=url,
            trend_score=trend_score,
            hashtags=hashtags or [keyword.lower()],
            description=description,
            published_at=published_at,
            scraped_at=scraped_at,
            raw_data={
                "keyword": keyword,
                "title": title,
                "trend_score": trend_score,
                "date": published_at.isoformat() if published_at else None,
            },
        )
