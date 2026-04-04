"""
Module 7 — Competitive Comparison Context
Charts:
  - Bar: avg score of Claude-only vs. comparison posts
  - Timeline: competitor mentions over time
  - Scatter: competitor context vs. engagement
  - Bar: which competitor mentioned most in viral posts
"""
from __future__ import annotations
import warnings
warnings.filterwarnings("ignore")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import re
from data_loader import load_reddit, load_hn, load_x, CHARTS

COMPETITORS = {
    "ChatGPT / GPT": [r"\bchatgpt\b", r"\bgpt-?[34]\b", r"\bgpt-?4o\b", r"\bopenai\b"],
    "Gemini":        [r"\bgemini\b"],
    "Copilot":       [r"\bcopilot\b", r"\bbing (ai|chat)\b"],
    "Grok":          [r"\bgrok\b", r"\bxai\b"],
    "Llama / Meta":  [r"\bllama\b", r"\bmeta ai\b"],
    "DeepSeek":      [r"\bdeepseek\b"],
    "Mistral":       [r"\bmistral\b"],
    "Perplexity":    [r"\bperplexity\b"],
}


def _competitor_flags(title: str) -> dict:
    t = str(title).lower()
    return {comp: int(any(re.search(p, t) for p in patterns))
            for comp, patterns in COMPETITORS.items()}


# ── Chart 1: Comparison posts vs. standalone Claude posts ─────────────────────
def chart_comparison_lift():
    reddit = load_reddit()
    reddit = reddit[reddit["likes"].notna()].copy()
    reddit["has_competitor"] = reddit["post_title"].apply(
        lambda t: int(any(any(re.search(p, str(t).lower()) for p in pats)
                          for pats in COMPETITORS.values()))
    )

    stats = reddit.groupby("has_competitor").agg(
        avg_score=("likes", "mean"),
        median_score=("likes", "median"),
        count=("id", "count"),
    )
    stats.index = ["Claude-only", "Contains competitor"]

    fig, ax = plt.subplots(figsize=(9, 5))
    colors = ["#3498db", "#e74c3c"]
    bars = ax.bar(stats.index, stats["avg_score"], color=colors, alpha=0.85, width=0.4)
    for bar, (_, row) in zip(bars, stats.iterrows()):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f"avg={row['avg_score']:.0f}\nn={row['count']:,}", ha="center", fontsize=10)

    ax.set_ylabel("Average Reddit Score", fontsize=11)
    ax.set_title("Does Mentioning a Competitor Boost Viral Performance?\n(Reddit posts)", fontsize=11, fontweight="bold")
    ax.grid(axis="y", alpha=0.3)
    ax.set_ylim(0, stats["avg_score"].max() * 1.3)
    plt.tight_layout()
    out = CHARTS / "7a_competitor_mention_lift.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out}")


# ── Chart 2: Competitor mentions in top-10% posts ─────────────────────────────
def chart_competitor_frequency():
    reddit = load_reddit()
    reddit = reddit[reddit["likes"].notna()].copy()
    top = reddit[reddit["likes"] >= reddit["likes"].quantile(0.90)]
    all_posts = reddit

    def _comp_counts(df):
        flags = pd.DataFrame([_competitor_flags(t) for t in df["post_title"]])
        return flags.sum()

    top_counts = _comp_counts(top)
    all_counts = _comp_counts(all_posts)

    # normalise to % of posts
    top_pct = top_counts / len(top) * 100
    all_pct = all_counts / len(all_posts) * 100

    x = np.arange(len(top_counts))
    width = 0.35

    fig, ax = plt.subplots(figsize=(12, 6))
    bars1 = ax.bar(x - width/2, top_pct.values, width, label=f"Top 10% viral (n={len(top):,})",
                   color="#e74c3c", alpha=0.85)
    bars2 = ax.bar(x + width/2, all_pct.values, width, label=f"All posts (n={len(all_posts):,})",
                   color="#95a5a6", alpha=0.85)

    ax.set_xticks(x)
    ax.set_xticklabels(top_counts.index, fontsize=10, rotation=15, ha="right")
    ax.set_ylabel("% of posts mentioning competitor", fontsize=10)
    ax.set_title("Competitor Mentions in Viral vs. All Posts (Reddit)\n(higher bar in red = competitor appears more in viral content)",
                 fontsize=11, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(axis="y", alpha=0.3)

    # lift
    for xi, (v, a) in enumerate(zip(top_pct.values, all_pct.values)):
        if a > 0:
            lift = v / a
            ax.text(xi - width/2, v + 0.1, f"{lift:.1f}×", ha="center", fontsize=8, color="#c0392b")

    plt.tight_layout()
    out = CHARTS / "7b_competitor_frequency_viral_vs_all.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out}")


# ── Chart 3: Competitor mention timeline ─────────────────────────────────────
def chart_competitor_timeline():
    reddit = load_reddit()
    reddit = reddit[reddit["published_at"].dt.year >= 2025].copy()
    reddit["month"] = reddit["published_at"].dt.to_period("M").dt.start_time

    for comp, patterns in COMPETITORS.items():
        reddit[comp] = reddit["post_title"].apply(
            lambda t: int(any(re.search(p, str(t).lower()) for p in patterns))
        )

    monthly = reddit.groupby("month")[list(COMPETITORS.keys())].sum()

    fig, ax = plt.subplots(figsize=(14, 6))
    colors_list = plt.cm.tab10(np.linspace(0, 1, len(COMPETITORS)))
    for comp, color in zip(COMPETITORS.keys(), colors_list):
        ax.plot(monthly.index, monthly[comp], marker="o", ms=4, lw=1.8,
                label=comp, color=color, alpha=0.85)

    ax.set_xlabel("Month")
    ax.set_ylabel("Number of Reddit posts mentioning competitor")
    ax.set_title("Competitor Mentions in r/ClaudeAI Over Time\n(showing which competitors are top-of-mind for Claude community)",
                 fontsize=11, fontweight="bold")
    ax.legend(fontsize=9, loc="upper left")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.xticks(rotation=30, ha="right")
    ax.grid(alpha=0.3)
    plt.tight_layout()
    out = CHARTS / "7c_competitor_timeline.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out}")


# ── Chart 4: X — competitor context in viral tweets ─────────────────────────
def chart_x_competitor_context():
    x = load_x()
    x = x[x["views"].notna()].copy()

    for comp, patterns in COMPETITORS.items():
        x[comp] = x["post_title"].apply(
            lambda t: int(any(re.search(p, str(t).lower()) for p in patterns))
        )

    comp_cols = list(COMPETITORS.keys())
    avg_views = {}
    for comp in comp_cols:
        with_comp    = x[x[comp] == 1]["views"].mean()
        without_comp = x[x[comp] == 0]["views"].mean()
        avg_views[comp] = {"with": with_comp or 0, "without": without_comp or 0}

    df = pd.DataFrame(avg_views).T / 1e6  # millions

    fig, ax = plt.subplots(figsize=(12, 6))
    x_pos = np.arange(len(df))
    width = 0.35
    ax.bar(x_pos - width/2, df["with"],    width, label="Tweet mentions competitor", color="#e74c3c", alpha=0.85)
    ax.bar(x_pos + width/2, df["without"], width, label="Tweet does not mention",    color="#95a5a6", alpha=0.85)

    ax.set_xticks(x_pos)
    ax.set_xticklabels(df.index, rotation=15, ha="right", fontsize=10)
    ax.set_ylabel("Average Views (millions)", fontsize=10)
    ax.set_title("X: Does Mentioning a Specific Competitor Boost View Count?\n(avg views per tweet)",
                 fontsize=11, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    out = CHARTS / "7d_x_competitor_view_boost.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out}")


if __name__ == "__main__":
    print("=== Module 7: Competitive Comparison ===")
    chart_comparison_lift()
    chart_competitor_frequency()
    chart_competitor_timeline()
    chart_x_competitor_context()
    print("Done.")
