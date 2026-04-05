# GrowthHack — HackNU 2026 · Growth Engineering Track

Reverse-engineer Claude's viral growth playbook, then build a counter-playbook and automation pipeline for a competing AI product (Higgsfield AI).

**Team:** Alemzhan-A  
**Track:** Growth Engineering (async, 24 hours)

---

## What Was Built

| Part | Deliverable | Status |
|------|-------------|--------|
| 1 | Multi-platform scrapers + structured dataset (197k rows) | Done |
| 2 | Viral pattern analysis — archetypes, mechanics, channels | Done |
| 3 | Automated intelligence pipeline with architecture diagram | Done |
| 4 | Counter-playbook for Higgsfield AI (DOCX) | Done |

Dashboard: `dashboard/` — Next.js app with 4 pages (Claude Insights, Compare, Pipeline, Playbook).  
Counter-playbook doc: `docs/Higgsfield_Counter_Playbook.docx`

---

## Dataset

| Platform | Records | Notes |
|----------|---------|-------|
| Hacker News | ~107k | Posts + comments via Algolia API |
| Reddit (Claude) | ~74k | r/ClaudeAI, r/Anthropic via PRAW |
| Reddit (Higgsfield) | ~2,094 | r/HiggsfieldAI via PRAW |
| YouTube | ~3k | YouTube Data API v3 |
| Google Trends | ~500 | pytrends, weekly index |
| X (Twitter) | 0 | See note below |
| Threads | 0 | See note below |

**Total: ~197k rows** — `data/processed/full_dataset (1).csv`

### X (Twitter) — Not Collected

Multiple approaches were attempted:

- `snscrape` — deprecated; no longer returns results for search queries
- `tweepy` v2 Free tier — search endpoint requires Basic tier ($100/mo); free tier only allows posting, not search
- Unofficial scraper (playwright cookie session) — blocked by X bot detection after a few requests
- `x_scraper/` directory contains the abandoned attempt

X data was not included in the final dataset. Top X posts (EHuanglu, AnthropicAI) were manually identified and referenced in the analysis.

### Threads — Not Collected

- Official Threads API (Meta) requires app review and is not available for scraping public content from third-party accounts
- `threads-api` unofficial library — returns empty results for non-authenticated public search since Meta's 2024 API lockdown
- Playwright session scraping — login wall blocks unauthenticated access

Threads was dropped entirely. No data collected.

---

## Project Structure

```
growthhack/
├── main.py                        # CLI entrypoint
├── config.py                      # Keywords, API keys, rate limits
├── requirements.txt
│
├── workers/
│   ├── base.py                    # BaseWorker abstract class
│   ├── reddit_worker.py           # PRAW — r/ClaudeAI, r/Anthropic
│   ├── hackernews_worker.py       # Algolia HN Search API
│   ├── youtube_worker.py          # YouTube Data API v3
│   ├── google_trends_worker.py    # pytrends
│   ├── x_worker.py                # tweepy — FAILED (rate limits / tier)
│   ├── threads_worker.py          # playwright — FAILED (login wall)
│   └── x_scraper/                 # Abandoned X scraping attempt
│
├── models/
│   └── post.py                    # Unified Post schema (pydantic)
│
├── storage/
│   ├── database.py                # SQLite abstraction
│   └── exporter.py                # CSV / JSON export
│
├── analysis/
│   ├── analyzer.py                # Pattern detection
│   └── visualizer.py             # Chart generation
│
├── scrape_higgsfield_reddit.py    # Higgsfield-specific Reddit scraper
├── scrape_higgsfield_youtube.py   # Higgsfield YouTube scraper
├── scrape_higgsfield_x.py         # Higgsfield X scraper — FAILED
├── scrape_higgsfield_trends.py    # Higgsfield Google Trends
├── fetch_comments.py              # HN comment fetcher
├── fetch_higgsfield_comments.py   # Higgsfield comment fetcher
├── process_data.py                # Data cleaning and normalization
├── process_higgsfield.py          # Higgsfield-specific processing
├── render_pipeline.py             # Pipeline diagram renderer (Playwright)
├── generate_playbook_doc.py       # Counter-playbook DOCX generator
│
├── data/
│   ├── raw/                       # Raw JSON per scrape run
│   ├── processed/                 # Cleaned CSVs, unified dataset
│   └── charts/                    # Generated visualizations
│
├── dashboard/                     # Next.js 16 app (4 pages)
│   ├── app/
│   │   ├── page.tsx               # 01 · Claude Insights
│   │   ├── compare/page.tsx       # 02 · Claude vs Higgsfield
│   │   ├── pipeline/page.tsx      # 03 · Automation Pipeline
│   │   └── playbook/page.tsx      # 04 · Counter-Playbook
│   ├── lib/
│   │   ├── analysis.ts            # 6 gap findings
│   │   └── comparisons.ts         # 15 comparison charts
│   └── public/
│       ├── pipeline_diagram.png   # Full-page pipeline screenshot
│       └── charts/                # Comparison chart PNGs (cmp_01..15)
│
└── docs/
    ├── Higgsfield_Counter_Playbook.docx
    └── VIRAL_PLAYBOOK.md
```

---

## Setup

```bash
# Python dependencies
pip install -r requirements.txt

# Playwright (for pipeline diagram rendering)
playwright install chromium

# Dashboard
cd dashboard
npm install
npm run dev        # http://localhost:3000
```

**Required env / API keys** (set in `config.py` or environment):

| Variable | Used by | Required |
|----------|---------|----------|
| `REDDIT_CLIENT_ID` | reddit_worker, scrape_higgsfield_reddit | Yes |
| `REDDIT_CLIENT_SECRET` | same | Yes |
| `YOUTUBE_API_KEY` | youtube_worker, scrape_higgsfield_youtube | Yes |
| `TWITTER_BEARER_TOKEN` | x_worker | Not needed (scraping failed) |

---

## Running the Scrapers

```bash
# Full Claude dataset
python main.py

# Higgsfield-specific
python scrape_higgsfield_reddit.py
python scrape_higgsfield_youtube.py
python scrape_higgsfield_trends.py

# Process and export
python process_data.py
python process_higgsfield.py
```

---

## Key Findings (summary)

1. **"just" opener** — posts beginning with "just" average 638× higher engagement than baseline
2. **Insider Reveal archetype** — avg score 102 (n=230) vs Capability Demo avg 24 (n=1,208)
3. **Hacker News is Claude's #1 channel** — 107k posts; Higgsfield has zero HN presence
4. **Higgsfield's own subreddit is infiltrated** — KLING competitor content (153 posts, avg 6.6) outscores Higgsfield's own video model posts (46 posts, avg 2.6) inside r/HiggsfieldAI
5. **Single-amplifier risk** — EHuanglu alone drives the majority of Higgsfield's top-10 X views; Claude has 8+ independent amplifiers
6. **YouTube engagement rate** — Higgsfield beats Claude (5.12% vs ~2%) despite lower reach; strong product-audience fit, missing distribution

Full analysis: dashboard `/compare` and `/analysis` pages, or `docs/Higgsfield_Counter_Playbook.docx`.

---

## Tech Stack

| Layer | Tool |
|-------|------|
| Scraping | PRAW, Algolia HN API, YouTube Data API v3, pytrends |
| Data model | pydantic v2 |
| Processing | pandas |
| Visualization | matplotlib |
| Dashboard | Next.js 16, TypeScript, Tailwind CSS |
| Document generation | python-docx |
| Diagram rendering | Playwright (headless Chromium) |
| Storage | SQLite (dev) |

---

## Tradeoffs

- **Monolith over microservices** — 24-hour constraint; one repo, one process
- **No X data** — Free API tier blocks search; manual reference used instead
- **No Threads data** — API access requires Meta app review; not feasible in hackathon timeframe
- **SQLite not PostgreSQL** — Dev-only; `storage/database.py` has a Postgres migration path documented
- **Static dashboard** — Data is embedded in TypeScript constants, not served from a live database; fast to ship, not real-time
