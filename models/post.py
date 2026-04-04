from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, field_validator


class Post(BaseModel):
    id: str
    platform: str                        # "threads", "x", "youtube", "google_trends"
    post_title: str                      # tweet text / thread text / video title
    author: str
    url: str
    views: Optional[int] = None
    likes: Optional[int] = None
    reposts: Optional[int] = None
    comments: Optional[int] = None
    hashtags: list[str] = []
    description: Optional[str] = None   # YouTube only
    duration: Optional[str] = None      # YouTube only (ISO 8601)
    trend_score: Optional[int] = None   # Google Trends only (0-100)
    published_at: Optional[datetime] = None
    scraped_at: datetime
    engagement_rate: Optional[float] = None
    raw_data: Optional[Any] = None

    @field_validator("engagement_rate", mode="before")
    @classmethod
    def compute_engagement(cls, v, info):
        # Auto-compute if not provided
        if v is not None:
            return v
        data = info.data
        views = data.get("views")
        likes = data.get("likes") or 0
        reposts = data.get("reposts") or 0
        comments = data.get("comments") or 0
        if views and views > 0:
            return round((likes + reposts + comments) / views, 6)
        return None

    def to_csv_row(self) -> dict:
        return {
            "id": self.id,
            "platform": self.platform,
            "post_title": self.post_title[:500],  # truncate for CSV readability
            "author": self.author,
            "url": self.url,
            "views": self.views,
            "likes": self.likes,
            "reposts": self.reposts,
            "comments": self.comments,
            "hashtags": "|".join(self.hashtags),
            "engagement_rate": self.engagement_rate,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "scraped_at": self.scraped_at.isoformat(),
        }
