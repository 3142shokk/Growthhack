import os

# ---------------------------------------------------------------------------
# Threads — hashtag-based scraping
# ---------------------------------------------------------------------------
THREADS_HASHTAGS = [
    "claudeai",
    "claude3",
    "claude35",
    "claude4",
    "claudecode",
    "claudesonnet",
    "claudeopus",
    "claudehaiku",
    "anthropicai",
    "anthropic",
]

THREADS_MAX_POSTS_PER_HASHTAG = 80   # posts to collect per hashtag (via scrolling)
THREADS_SCROLL_ROUNDS = 12           # scrolls per hashtag page (more = more posts)
THREADS_PARALLEL_HASHTAGS = 4        # concurrent browser contexts

# Keywords used to filter posts on any platform
CLAUDE_KEYWORDS = [
    "claude", "anthropic", "claude ai",
    "claude 3", "claude 3.5", "claude 3.7", "claude 4",
    "claude opus", "claude sonnet", "claude haiku",
    "claude code", "claude.ai",
]

COMPETITOR_KEYWORDS = ["chatgpt", "gemini", "copilot", "llama", "gpt-4", "openai"]

# ---------------------------------------------------------------------------
# Reddit — Arctic Shift API (no auth required)
# ---------------------------------------------------------------------------
REDDIT_SUBREDDITS = [
    "ClaudeAI",
    "anthropic",
]

REDDIT_SEARCH_QUERIES = [
    "Claude",
    "Anthropic",
    "Claude AI",
    "Claude Anthropic",
    "Claude Opus",
    "Claude Sonnet",
    "Claude Haiku",
    "Claude Code",
    "Claude 3",
    "Claude 3.5",
    "Claude 4",
    "claude.ai",
    "Anthropic Claude",
    "Anthropic AI",
    "Claude artifacts",
    "Claude projects",
    "Claude API",
]

REDDIT_SAVE_EVERY = 500          # save progress every N new posts

# ---------------------------------------------------------------------------
# X (Twitter) — DuckDuckGo discovery + syndication API (no auth)
# ---------------------------------------------------------------------------
X_SEARCH_QUERIES = [
    "Claude AI",
    "Claude Anthropic",
    "Claude Code",
    "Claude Opus",
    "Claude Sonnet",
    "Claude Haiku",
    "Claude 3",
    "Claude 3.5",
    "Claude 4",
    "Anthropic Claude",
    "Anthropic AI",
    "Claude artifacts",
    "Claude projects",
    "Claude API",
    "Claude computer use",
    # People / accounts
    "AnthropicAI",
    "DarioAmodei",
    "AmandaAskell",
    # Viral
    "switched to Claude",
    "Claude blew my mind",
    "Claude just",
]

X_DDG_DELAY = 2.0           # seconds between DDG queries
X_SYNDICATION_DELAY = 0.5   # seconds between syndication API calls
X_MAX_RETRIES = 3

# ---------------------------------------------------------------------------
# Output paths
# ---------------------------------------------------------------------------
DATA_DIR = "data"
RAW_DIR = f"{DATA_DIR}/raw"
PROCESSED_DIR = f"{DATA_DIR}/processed"
CHARTS_DIR = f"{DATA_DIR}/charts"
SCRAPE_LOG = f"{DATA_DIR}/scrape_log.json"

# ---------------------------------------------------------------------------
# Rate limiting defaults
# ---------------------------------------------------------------------------
REQUEST_DELAY_SECONDS = 3     # polite delay between profile requests
PLAYWRIGHT_TIMEOUT_MS = 30000
SELECTOR_TIMEOUT_MS = 15000
