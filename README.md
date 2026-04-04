# Claude Viral Growth Machine

**HackNU 2026 — Growth Engineering Track**
**Challenge:** Reverse-engineer Claude's viral growth playbook, then build a system to replicate it for a competing AI product.
**Format:** Async, 24 hours.

---

## Challenge Summary

4-part deliverable:

1. **Scrape the Discourse** — Build scrapers collecting public conversation about Claude across X, Reddit, YouTube, Instagram, LinkedIn, TikTok. Output clean structured dataset.
2. **Decode the Playbook** — Analyze scraped data to find growth patterns. Original insights only — must be data-backed.
3. **Build the Machine** — Design (+ prototype) automated recurring intelligence pipeline with architecture diagram, orchestration plan, alert design, and cost estimates.
4. **The Counter-Playbook** — Concrete distribution plan for a competing AI product, directly grounded in findings from Parts 1–2.

Scoring: Data extraction (25%), Analytical depth (30%), Automation design (15%), Counter-playbook (20%), Communication (10%).

---

## Architecture

Python monolith with worker-based scrapers. See [PLAN.md](PLAN.md) for full architecture diagram and design decisions.

```
main.py → [X Worker, Threads Worker, YouTube Worker, Google Trends Worker]
        → Unified Data Pipeline (normalize → deduplicate → validate → store)
        → SQLite (dev) / PostgreSQL (prod) + CSV/JSON export
        → Analysis Engine (pandas + matplotlib/plotly)
```

**Output directories:**
- `data/raw/` — Raw scraped JSON per platform
- `data/processed/` — Cleaned, unified dataset
- `data/charts/` — Generated visualizations
- `data/scrape_log.json` — Error log (what broke and why)

---

## Project Structure

```
growthhack/
├── main.py                  # CLI entrypoint — orchestrates all workers
├── config.py                # API keys, rate limits, search queries
├── requirements.txt
├── workers/
│   ├── base.py              # BaseWorker abstract class
│   ├── x_worker.py          # X (Twitter) scraper — snscrape / tweepy
│   ├── threads_worker.py    # Threads scraper — threads-api / playwright
│   ├── youtube_worker.py    # YouTube Data API v3
│   └── trends_worker.py     # Google Trends — pytrends
├── models/
│   └── post.py              # Unified Post data model (pydantic)
├── storage/
│   ├── database.py          # SQLite/PostgreSQL abstraction
│   └── exporter.py          # CSV / JSON export
├── analysis/
│   ├── analyzer.py          # Growth pattern analysis
│   └── visualizer.py        # Charts and graphs
├── data/
│   ├── raw/
│   ├── processed/
│   └── charts/
└── docs/
    ├── PLAYBOOK_ANALYSIS.md
    ├── ARCHITECTURE.md
    └── COUNTER_PLAYBOOK.md
```

---

## Platform Priorities & Rationale

| Priority | Platform | Why |
|----------|----------|-----|
| 1 | YouTube | Richest data (views/likes/comments/tags), most reliable API, 10k free quota/day |
| 2 | Google Trends | No auth, comparative data vs competitors, broad signal |
| 3 | X (Twitter) | High volume, high signal — rate limits are the challenge |
| 4 | Threads | Newer API, less certain availability |

Reddit, Instagram, TikTok: deprioritized — login walls or no viable free scraping.

---

## Unified Data Model

All platforms normalize into a single `Post` schema:

| Field | Type | Notes |
|-------|------|-------|
| `id` | str | Platform-prefixed: `x_123`, `yt_abc` |
| `platform` | str | `x`, `threads`, `youtube`, `google_trends` |
| `post_title` | str | Tweet text / thread text / video title |
| `author` | str | Username or channel name |
| `url` | str | Direct link |
| `views` | int/null | |
| `likes` | int/null | |
| `reposts` | int/null | |
| `comments` | int/null | |
| `hashtags` | list[str] | |
| `trend_score` | int/null | Google Trends 0–100 |
| `published_at` | datetime | |
| `scraped_at` | datetime | |
| `engagement_rate` | float | (likes + reposts + comments) / views |
| `raw_data` | json | Original API response preserved |

---

## Tech Stack

| Component | Tool | Why |
|-----------|------|-----|
| Language | Python 3.11+ | Ecosystem for scraping/data |
| Data model | Pydantic | Validation, serialization |
| HTTP | httpx / requests | Async support |
| Browser auto | Playwright | For Threads if API unavailable |
| YouTube API | google-api-python-client | Official, reliable |
| Trends | pytrends | Only option for Google Trends |
| X scraping | snscrape / tweepy | Public data, no login |
| Database | SQLite | Zero setup, hackathon-appropriate |
| Data analysis | pandas | |
| Visualization | matplotlib + plotly | Static + interactive |
| CLI | argparse | No extra deps |
| Concurrency | concurrent.futures | stdlib thread pool |

---

## Search Keywords

```python
SEARCH_QUERIES = [
    "Claude AI", "Claude Anthropic", "Claude 3",
    "Claude Opus", "Claude Sonnet", "Claude vs ChatGPT",
    "Anthropic Claude", "Claude Code", "Claude tutorial", "Claude review",
]
HASHTAGS = ["#ClaudeAI", "#Anthropic", "#Claude3", "#AItools"]
COMPETITORS = ["ChatGPT", "Gemini", "Copilot", "Llama"]  # for comparative analysis
```

---

## Error Handling

| Scenario | Strategy |
|----------|----------|
| Rate limit (429) | Exponential backoff: 2s → 4s → 8s → 16s, max 3 retries |
| API down (5xx) | Skip platform, log error, continue others |
| Missing field | Set null, flag in quality report |
| Duplicate posts | Deduplicate by platform + post ID |
| YouTube quota exceeded | Stop YouTube worker, continue others |
| Network timeout | 30s per request, retry once |

---

## Implementation Phases

1. **Scaffolding** — BaseWorker, Post model, SQLite storage, CSV/JSON export
2. **Workers** — YouTube → Google Trends → X → Threads
3. **Orchestration** — `main.py` CLI, ThreadPoolExecutor, progress logging
4. **Analysis & Visualization** — Engagement patterns, platform comparison, hashtag analysis, posting time heatmap
5. **Documentation** — PLAYBOOK_ANALYSIS.md, ARCHITECTURE.md, COUNTER_PLAYBOOK.md

---

## Key Design Decisions

- **Monolith over microservices** — 24-hour constraint. One process, one repo.
- **Workers as plugins** — Each inherits `BaseWorker` with `scrape() -> list[Post]`. Adding platforms doesn't touch orchestration.
- **YouTube first** — Best data quality + most reliable free API.
- **Store raw + processed** — `raw_data` field preserves original response for re-processing without re-scraping.
- **Graceful degradation** — One worker failing doesn't stop others. Partial results are still valuable.

---

## Deliverables Checklist

- [ ] Working scrapers + code (GitHub repo)
- [ ] Structured dataset (CSV or JSON)
- [ ] Playbook analysis with supporting data (README or doc)
- [ ] Automation architecture diagram
- [ ] Counter-playbook / distribution plan (written doc)
- [ ] README (setup, assumptions, tradeoffs)
- [ ] Video walkthrough 5–10 min (bonus)
