import os

# ---------------------------------------------------------------------------
# Threads — target accounts (search requires login, so we target known accounts)
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
# Reddit — public JSON API (no auth required)
# ---------------------------------------------------------------------------
REDDIT_SUBREDDITS = [
    "ClaudeAI",       # Dedicated Claude subreddit
    "Anthropic",      # Anthropic company subreddit
]

REDDIT_REQUEST_DELAY = 1.5   # seconds between paginated requests
REDDIT_MAX_RETRIES = 3

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
