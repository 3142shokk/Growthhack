"""
google_trends_worker.py — fetches interest-over-time and rising/top related
queries from Google Trends for Claude/Anthropic keywords.

Interest-over-time: one Post per (keyword, week) with published_at = week date.
Related queries: one Post per query, published_at = None (aggregated period).
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

TRENDS_KEYWORDS = [
    "Claude AI",
    "Anthropic",
    "claude.ai",
    "Claude Opus",
    "Claude Sonnet",
    "Claude Haiku",
    "Claude 3",
    "Claude 3.5",
    "Claude 4",
    "Claude Code",
]

# pytrends allows max 5 keywords per request
BATCH_SIZE = 5
# timeframe: past 90 days
TIMEFRAME = "today 3-m"
GEO = ""  # worldwide


class GoogleTrendsWorker(BaseWorker):
    platform = "google_trends"

    def __init__(self, keywords: list[str] | None = None):
        self.keywords = keywords or TRENDS_KEYWORDS
        self.pytrends = TrendReq(hl="en-US", tz=0, timeout=(10, 30), retries=3, backoff_factor=1.5)

    def scrape(self) -> list[Post]:
        posts: list[Post] = []
        now = datetime.now(timezone.utc)

        # --- 1. Interest over time — one record per (keyword, week) ---
        for keyword, date, score in self._fetch_interest_over_time():
            posts.append(self._make_post(
                keyword=keyword,
                title=f"[Trend] {keyword}",
                trend_score=score,
                url=self._trends_url(keyword),
                scraped_at=now,
                published_at=date,
            ))

        # --- 2. Related rising queries for each keyword ---
        for keyword in self.keywords:
            rising = self._fetch_related_queries(keyword, kind="rising")
            top = self._fetch_related_queries(keyword, kind="top")
            for row in rising:
                posts.append(self._make_post(
                    keyword=keyword,
                    title=f"[Rising] {row['query']}",
                    trend_score=None,
                    url=self._trends_url(row["query"]),
                    scraped_at=now,
                    description=f"Rising related to '{keyword}': value={row['value']}",
                    hashtags=[keyword.lower().replace(" ", "")],
                ))
            for row in top:
                posts.append(self._make_post(
                    keyword=keyword,
                    title=f"[Top] {row['query']}",
                    trend_score=int(row["value"]) if str(row["value"]).isdigit() else None,
                    url=self._trends_url(row["query"]),
                    scraped_at=now,
                    description=f"Top related to '{keyword}': value={row['value']}",
                    hashtags=[keyword.lower().replace(" ", "")],
                ))
            time.sleep(1.5)  # polite delay between keyword requests

        logger.info(f"Google Trends: collected {len(posts)} data points")
        return posts

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fetch_interest_over_time(self) -> list[tuple[str, datetime, int]]:
        """Yields (keyword, week_date, score) for every row in the time series."""
        rows: list[tuple[str, datetime, int]] = []
        for i in range(0, len(self.keywords), BATCH_SIZE):
            batch = self.keywords[i : i + BATCH_SIZE]
            try:
                self.pytrends.build_payload(batch, cat=0, timeframe=TIMEFRAME, geo=GEO)
                df: pd.DataFrame = self.pytrends.interest_over_time()
                if df.empty:
                    continue
                for ts, row in df.iterrows():
                    date = ts.to_pydatetime().replace(tzinfo=timezone.utc)
                    for kw in batch:
                        if kw in df.columns:
                            rows.append((kw, date, int(row[kw])))
            except Exception as e:
                logger.warning(f"interest_over_time failed for batch {batch}: {e}")
            time.sleep(2)
        return rows

    def _fetch_related_queries(self, keyword: str, kind: str = "rising") -> list[dict]:
        """Returns list of {query, value} dicts for rising or top related queries."""
        try:
            self.pytrends.build_payload([keyword], cat=0, timeframe=TIMEFRAME, geo=GEO)
            related = self.pytrends.related_queries()
            df = related.get(keyword, {}).get(kind)
            if df is None or df.empty:
                return []
            return df.head(10).to_dict(orient="records")
        except Exception as e:
            logger.warning(f"related_queries({keyword}, {kind}) failed: {e}")
            return []

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
            hashtags=hashtags or [keyword.lower().replace(" ", "")],
            description=description,
            published_at=published_at,
            scraped_at=scraped_at,
            raw_data={"keyword": keyword, "title": title, "trend_score": trend_score, "date": published_at.isoformat() if published_at else None},
        )
