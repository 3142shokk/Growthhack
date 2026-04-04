"""
Module 5 — Amplifier Network Analysis
Charts:
  - Top X amplifiers ranked by views (Anthropic vs. community)
  - Author type breakdown by views
  - HN: who submits the highest-performing stories?
  - Reddit: top 20 authors by total score
"""
from __future__ import annotations
import warnings
warnings.filterwarnings("ignore")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from data_loader import load_reddit, load_hn, load_x, CHARTS

ANTHROPIC_ACCOUNTS = {"AnthropicAI", "DarioAmodei", "AmandaAskell", "alexalbert__", "claudeai", "ClaudeCodeLog"}

AMPLIFIER_TYPES = {
    "AI Researchers":    {"karpathy", "ylecun", "goodfellow", "sama", "ilyasut", "drfeifei"},
    "Indie Hackers":     {"levelsio", "skirano", "mattshumer_", "hqmank", "trq212"},
    "Tech Journalists":  {"TechCrunch", "verge", "wired", "arstechnica", "techreview"},
    "Politicians/Public":{"SenSanders", "RoundtableSpace"},
    "Other Influencers": {"rubenhassid", "ns123abc", "dani_avila7", "tishtishart", "perplexity_ai"},
}

def _author_type(author):
    if author in ANTHROPIC_ACCOUNTS:
        return "Anthropic Official"
    for t, accounts in AMPLIFIER_TYPES.items():
        if author.lower() in {a.lower() for a in accounts}:
            return t
    return "Community / Other"


# ── Chart 1: Top 25 X accounts by total views ────────────────────────────────
def chart_x_amplifiers():
    x = load_x()
    x = x[x["views"].notna()].copy()
    x["type"] = x["author"].apply(_author_type)

    by_author = x.groupby(["author", "type"]).agg(
        total_views=("views", "sum"),
        total_likes=("likes", "sum"),
        tweet_count=("id", "count"),
        avg_views=("views", "mean"),
    ).reset_index().sort_values("total_views", ascending=False).head(25)

    type_colors = {
        "Anthropic Official":  "#e74c3c",
        "AI Researchers":      "#3498db",
        "Indie Hackers":       "#2ecc71",
        "Tech Journalists":    "#9b59b6",
        "Politicians/Public":  "#f39c12",
        "Other Influencers":   "#1abc9c",
        "Community / Other":   "#95a5a6",
    }
    colors = [type_colors.get(t, "#95a5a6") for t in by_author["type"]]

    fig, ax = plt.subplots(figsize=(13, 9))
    bars = ax.barh(by_author["author"], by_author["total_views"] / 1e6,
                   color=colors, edgecolor="white", height=0.65)

    for bar, (_, row) in zip(bars, by_author.iterrows()):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                f"  {row['tweet_count']} tweets  avg {row['avg_views']/1e6:.1f}M",
                va="center", fontsize=8)

    ax.set_xlabel("Total Views (millions)", fontsize=11)
    ax.set_title("Top 25 X Accounts by Total Claude-related Views\n(colour = account type)",
                 fontsize=12, fontweight="bold")
    ax.invert_yaxis()
    ax.set_xlim(0, by_author["total_views"].max() / 1e6 * 1.4)
    ax.grid(axis="x", alpha=0.3)

    # legend
    from matplotlib.patches import Patch
    legend_handles = [Patch(color=c, label=t) for t, c in type_colors.items()]
    ax.legend(handles=legend_handles, fontsize=8, loc="lower right")

    plt.tight_layout()
    out = CHARTS / "5a_x_amplifiers_by_views.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out}")


# ── Chart 2: Anthropic official vs community share of views ──────────────────
def chart_official_vs_community():
    x = load_x()
    x = x[x["views"].notna()].copy()
    x["is_official"] = x["author"].isin(ANTHROPIC_ACCOUNTS)

    official    = x[x["is_official"]]["views"].sum()
    community   = x[~x["is_official"]]["views"].sum()
    off_likes   = x[x["is_official"]]["likes"].sum()
    comm_likes  = x[~x["is_official"]]["likes"].sum()

    fig, axes = plt.subplots(1, 2, figsize=(12, 6))

    # Views
    axes[0].pie([official, community],
                labels=["Anthropic Official", "Community / Influencers"],
                colors=["#e74c3c", "#3498db"],
                autopct="%1.1f%%", startangle=90,
                textprops={"fontsize": 11})
    axes[0].set_title(f"Total Views Share\n({(official+community)/1e6:.0f}M total views)", fontsize=11, fontweight="bold")

    # Likes
    axes[1].pie([off_likes, comm_likes],
                labels=["Anthropic Official", "Community / Influencers"],
                colors=["#e74c3c", "#3498db"],
                autopct="%1.1f%%", startangle=90,
                textprops={"fontsize": 11})
    axes[1].set_title(f"Total Likes Share\n({(off_likes+comm_likes)/1e3:.0f}k total likes)", fontsize=11, fontweight="bold")

    plt.suptitle("X: Anthropic Official Accounts vs. Community Amplifiers",
                 fontsize=13, fontweight="bold")
    plt.tight_layout()
    out = CHARTS / "5b_official_vs_community_views.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out}")


# ── Chart 3: HN top submitters ───────────────────────────────────────────────
def chart_hn_submitters():
    hn = load_hn()
    hn = hn[hn["likes"].notna()].copy()

    top = hn.groupby("author").agg(
        total_points=("likes", "sum"),
        story_count=("id",    "count"),
        avg_points=("likes",  "mean"),
    ).sort_values("total_points", ascending=False).head(20)

    fig, ax = plt.subplots(figsize=(12, 7))
    bars = ax.barh(top.index, top["total_points"], color="#6aa84f", alpha=0.8, height=0.65)

    for bar, (_, row) in zip(bars, top.iterrows()):
        ax.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2,
                f"  {row['story_count']} stories  avg {row['avg_points']:.0f} pts",
                va="center", fontsize=8.5)

    ax.set_xlabel("Total HN Points", fontsize=11)
    ax.set_title("HN: Top 20 Submitters by Total Points\n(these accounts reliably surface Claude to tech audience)",
                 fontsize=11, fontweight="bold")
    ax.invert_yaxis()
    ax.set_xlim(0, top["total_points"].max() * 1.35)
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    out = CHARTS / "5c_hn_top_submitters.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out}")


# ── Chart 4: Engagement efficiency (likes per tweet) by author type ──────────
def chart_engagement_efficiency():
    x = load_x()
    x = x[x["views"].notna() & x["likes"].notna()].copy()
    x["type"] = x["author"].apply(_author_type)
    x["eng_rate"] = (x["likes"] + x["reposts"].fillna(0) + x["comments"].fillna(0)) / x["views"].replace(0, np.nan)

    stats = x.groupby("type").agg(
        avg_eng_rate=("eng_rate", "mean"),
        avg_views=("views", "mean"),
        count=("id", "count"),
    ).sort_values("avg_eng_rate", ascending=True)

    fig, ax = plt.subplots(figsize=(11, 6))
    colors = plt.cm.RdYlGn(np.linspace(0.2, 0.9, len(stats)))
    bars = ax.barh(stats.index, stats["avg_eng_rate"] * 100, color=colors, height=0.55)

    for bar, (_, row) in zip(bars, stats.iterrows()):
        ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2,
                f"  {row['avg_eng_rate']*100:.2f}%  avg {row['avg_views']/1e6:.1f}M views  n={row['count']}",
                va="center", fontsize=8.5)

    ax.set_xlabel("Avg Engagement Rate (likes+reposts+replies / views) %", fontsize=10)
    ax.set_title("X: Engagement Rate by Account Type\n(rate = audience that actively engages, not just scrolls)",
                 fontsize=11, fontweight="bold")
    ax.set_xlim(0, stats["avg_eng_rate"].max() * 100 * 1.5)
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    out = CHARTS / "5d_engagement_efficiency_by_type.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out}")


if __name__ == "__main__":
    print("=== Module 5: Amplifier Network ===")
    chart_x_amplifiers()
    chart_official_vs_community()
    chart_hn_submitters()
    chart_engagement_efficiency()
    print("Done.")
