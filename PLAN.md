# Claude Viral Growth Machine — Implementation Plan

## Architecture: Python Monolith with Worker-Based Scrapers

```
┌─────────────────────────────────────────────────────────────┐
│                        MONOLITH APP                         │
│                        (main.py)                            │
│                                                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌──────────────┐  │
│  │ X Worker│  │Threads  │  │YouTube  │  │Google Trends │  │
│  │         │  │ Worker  │  │ Worker  │  │   Worker     │  │
│  └────┬────┘  └────┬────┘  └────┬────┘  └──────┬───────┘  │
│       │            │            │               │          │
│       ▼            ▼            ▼               ▼          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Unified Data Pipeline                  │   │
│  │  normalize → deduplicate → validate → store         │   │
│  └──────────────────────┬──────────────────────────────┘   │
│                         │                                   │
│                         ▼                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                  Storage Layer                        │  │
│  │          SQLite (dev) / PostgreSQL (prod)             │  │
│  │              + JSON/CSV export                        │  │
│  └──────────────────────┬───────────────────────────────┘  │
│                         │                                   │
│                         ▼                                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │               Analysis Engine                        │  │
│  │     pandas + matplotlib/plotly visualizations        │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
hacknu/
├── main.py                  # CLI entrypoint — orchestrates all workers
├── config.py                # API keys, rate limits, search queries
├── requirements.txt
│
├── workers/
│   ├── __init__.py
│   ├── base.py              # BaseWorker abstract class
│   ├── x_worker.py          # X (Twitter) scraper
│   ├── threads_worker.py    # Threads scraper
│   ├── youtube_worker.py    # YouTube Data API v3
│   └── trends_worker.py     # Google Trends (pytrends)
│
├── models/
│   ├── __init__.py
│   └── post.py              # Unified data model for all platforms
│
├── storage/
│   ├── __init__.py
│   ├── database.py          # SQLite/PostgreSQL abstraction
│   └── exporter.py          # CSV / JSON export
│
├── analysis/
│   ├── __init__.py
│   ├── analyzer.py          # Growth pattern analysis
│   └── visualizer.py        # Charts and graphs
│
├── data/                    # Output directory
│   ├── raw/                 # Raw scraped JSON per platform
│   ├── processed/           # Cleaned, unified dataset
│   └── charts/              # Generated visualizations
│
└── docs/
    ├── PLAYBOOK_ANALYSIS.md # Part 2: Decoded playbook
    ├── ARCHITECTURE.md      # Part 3: Automation design
    └── COUNTER_PLAYBOOK.md  # Part 4: Counter-strategy
```

---

## Unified Data Model

Every scraped post, regardless of platform, gets normalized into this schema:

| Field             | Type      | Source Platforms    | Notes                                      |
| ----------------- | --------- | ------------------- | ------------------------------------------ |
| `id`              | str       | all                 | Platform-prefixed: `x_123`, `yt_abc`       |
| `platform`        | str       | all                 | `x`, `threads`, `youtube`, `google_trends` |
| `post_title`      | str       | all                 | Tweet text / thread text / video title     |
| `author`          | str       | X, Threads, YouTube | Username or channel name                   |
| `url`             | str       | X, Threads, YouTube | Direct link to the post                    |
| `views`           | int/null  | X, YouTube          | View count (null if unavailable)           |
| `likes`           | int/null  | X, Threads, YouTube | Like count                                 |
| `reposts`         | int/null  | X, Threads          | Retweet / repost count                     |
| `comments`        | int/null  | X, Threads, YouTube | Reply / comment count                      |
| `hashtags`        | list[str] | X, Threads, YouTube | Extracted from text + tags                 |
| `description`     | str/null  | YouTube             | Video description                          |
| `duration`        | str/null  | YouTube             | Video length (ISO 8601)                    |
| `trend_score`     | int/null  | Google Trends       | Relative interest 0-100                    |
| `published_at`    | datetime  | all                 | When the content was posted                |
| `scraped_at`      | datetime  | all                 | When we collected it                       |
| `engagement_rate` | float     | computed            | (likes + reposts + comments) / views       |
| `raw_data`        | json      | all                 | Original API response preserved            |

---

## Worker Specifications

### 1. X (Twitter) Worker — `x_worker.py`

**Approach:** Use [Nitter](https://github.com/zedeus/nitter) instances or `snscrape` for public tweet scraping (no API key needed for public data). Fallback: Twitter API v2 free tier (limited to 100 reads/month — use sparingly).

**Search queries:**

- `"Claude AI"`, `"Claude Anthropic"`, `"Claude 3"`, `"Claude Opus"`, `"Claude Sonnet"`
- `#ClaudeAI`, `#Anthropic`

**Data extracted:**
| Field | How |
|-------------|----------------------------------------|
| views | Tweet impression count (if public) |
| likes | `like_count` from API/scrape |
| reposts | `retweet_count` + `quote_count` |
| post_title | Full tweet text |
| hashtags | Parsed from `entities.hashtags` |
| author | `user.screen_name` |

**Rate limiting:** 1 request/second, exponential backoff on 429. Batch by date ranges to control volume.

**Library:** `tweepy` (API v2 free tier) or `snscrape` (no auth needed, more volume).

---

### 2. Threads Worker — `threads_worker.py`

**Approach:** Threads has a public API (as of 2025). Use the Threads API or browser automation with `playwright`/`selenium` for public posts.

**Search queries:**

- Search for posts mentioning "Claude", "Anthropic", "Claude AI"
- Scrape top posts from relevant hashtag pages

**Data extracted:**
| Field | How |
|------------|-------------------------------------|
| likes | Like count from post metadata |
| reposts | Repost/quote count |
| post_title | Full thread text |
| hashtags | Parsed from tex t (`#tag` pattern) |
| author | Username |
| comments | Reply count |

**Rate limiting:** Respect `Retry-After` headers. 2-second delay between requests. Rotate user-agents.

**Library:** `threads-api` package or `playwright` for browser automation.

---

### 3. YouTube Worker — `youtube_worker.py`

**Approach:** YouTube Data API v3 (free tier: 10,000 quota units/day). This is the most reliable and data-rich source.

**Search queries:**

- `"Claude AI"`, `"Claude vs ChatGPT"`, `"Anthropic Claude"`, `"Claude tutorial"`, `"Claude review"`

**API calls needed:**

1. `search.list` (100 units per call) — find videos
2. `videos.list` (1 unit per call) — get full stats for each video

**Data extracted:**
| Field | How |
|-------------|--------------------------------------------|
| views | `statistics.viewCount` |
| likes | `statistics.likeCount` |
| comments | `statistics.commentCount` |
| post_title | `snippet.title` |
| description | `snippet.description` |
| hashtags | Parsed from description + `snippet.tags` |
| duration | `contentDetails.duration` |
| author | `snippet.channelTitle` |
| published_at| `snippet.publishedAt` |

**Quota budget (10,000 units/day):**

- ~50 search calls = 5,000 units → ~250 video IDs
- ~250 video detail calls = 250 units
- Total: ~5,250 units/day → leaves headroom for retries

**Library:** `google-api-python-client`

---

### 4. Google Trends Worker — `trends_worker.py`

**Approach:** `pytrends` (unofficial Google Trends API). No auth needed.

**Search terms:**

- `"Claude AI"` vs `"ChatGPT"` vs `"Gemini AI"` vs `"Copilot AI"` (comparative)
- Individual: `"Claude"`, `"Anthropic"`

**Data extracted:**
| Field | How |
|--------------|---------------------------------------------|
| trend_score | Interest over time (0-100 relative scale) |
| region | Geographic breakdown |
| related | Related queries and rising topics |
| timeframe | Weekly data for past 12 months |

**Rate limiting:** pytrends is aggressive about rate limits. Use 10-second delays between requests. Retry with exponential backoff (max 3 retries).

**Library:** `pytrends`

---

## Implementation Order

### Phase 1 — Scaffolding (1-2 hours)

- [ ] Set up project structure, `requirements.txt`, `config.py`
- [ ] Implement `BaseWorker` abstract class with common interface
- [ ] Implement `Post` data model with validation (pydantic)
- [ ] Implement SQLite storage layer + CSV/JSON export

### Phase 2 — Workers (4-6 hours)

- [ ] **YouTube Worker** (highest priority — richest public data, most reliable API)
- [ ] **Google Trends Worker** (second — no auth, comparative data)
- [ ] **X Worker** (third — high volume but rate-limit challenges)
- [ ] **Threads Worker** (fourth — newer API, less certain availability)

### Phase 3 — Orchestration (1-2 hours)

- [ ] `main.py` CLI with argparse: run all workers or specific ones
- [ ] Concurrent execution with `concurrent.futures.ThreadPoolExecutor`
- [ ] Progress logging, error aggregation, retry summary
- [ ] Export unified dataset to `data/processed/`

### Phase 4 — Analysis & Visualization (3-4 hours)

- [ ] Engagement patterns over time (line charts)
- [ ] Platform comparison (bar charts)
- [ ] Top viral posts by engagement rate
- [ ] Hashtag frequency analysis (word cloud / bar chart)
- [ ] Posting time heatmap (when does Claude content go viral?)
- [ ] Sentiment distribution if time permits

### Phase 5 — Documentation (2-3 hours)

- [ ] `PLAYBOOK_ANALYSIS.md` — insights from the data
- [ ] `ARCHITECTURE.md` — automation pipeline design + diagram
- [ ] `COUNTER_PLAYBOOK.md` — actionable growth distribution plan
- [ ] `README.md` — setup, assumptions, tradeoffs

---

## Tech Stack

| Component     | Tool                     | Why                               |
| ------------- | ------------------------ | --------------------------------- |
| Language      | Python 3.11+             | Ecosystem for scraping/data       |
| Data model    | Pydantic                 | Validation, serialization         |
| HTTP          | httpx (async) / requests | Async support, connection pooling |
| Browser auto  | Playwright               | For Threads if API unavailable    |
| YouTube API   | google-api-python-client | Official, reliable                |
| Trends        | pytrends                 | Only option for Google Trends     |
| X scraping    | snscrape / tweepy        | Public data, no login needed      |
| Database      | SQLite (via sqlite3)     | Zero setup, good for hackathon    |
| Data analysis | pandas                   | Industry standard                 |
| Visualization | matplotlib + plotly      | Static charts + interactive       |
| CLI           | argparse                 | Simple, no extra dependency       |
| Concurrency   | concurrent.futures       | stdlib, simple thread pool        |

---

## Key Design Decisions

1. **Monolith over microservices** — 24-hour hackathon. One process, one repo, one deploy. Workers are classes, not services.

2. **Workers as plugins** — Each worker inherits `BaseWorker` with a standard interface (`scrape() -> list[Post]`). Easy to add new platforms without touching orchestration.

3. **YouTube first** — Richest data (views, likes, comments, description, tags), most reliable API, generous free tier. Best ROI for analysis quality.

4. **Store raw + processed** — Keep raw API responses in `raw_data` field. If we need to re-process or extract new fields later, we don't need to re-scrape.

5. **SQLite for dev, schema supports Postgres** — Use SQLAlchemy-compatible schema so migration to Postgres for "production" pipeline (Part 3) is trivial.

6. **Graceful degradation** — If one worker fails (rate limit, API down), others continue. Main orchestrator collects partial results and logs failures.

---

## Search Keywords (Shared Config)

```python
SEARCH_QUERIES = [
    "Claude AI",
    "Claude Anthropic",
    "Claude 3",
    "Claude Opus",
    "Claude Sonnet",
    "Claude vs ChatGPT",
    "Anthropic Claude",
    "Claude Code",
    "Claude tutorial",
    "Claude review",
]

HASHTAGS = [
    "#ClaudeAI",
    "#Anthropic",
    "#Claude3",
    "#AItools",
]

COMPETITORS = ["ChatGPT", "Gemini", "Copilot", "Llama"]  # For comparative analysis
```

---

## Error Handling Strategy

| Scenario                 | Handling                                                  |
| ------------------------ | --------------------------------------------------------- |
| Rate limit (429)         | Exponential backoff: 2s → 4s → 8s → 16s, max 3 retries    |
| API down (5xx)           | Skip platform, log error, continue with others            |
| Missing field            | Set to `null`, flag in data quality report                |
| Duplicate posts          | Deduplicate by platform + post ID before storage          |
| Quota exceeded (YouTube) | Stop YouTube worker, continue others, log remaining quota |
| Network timeout          | 30s timeout per request, retry once                       |

All errors are logged to `data/scrape_log.json` with timestamp, platform, error type, and request details. This log becomes part of the deliverable (documenting what broke).
