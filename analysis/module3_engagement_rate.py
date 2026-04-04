"""
Module 3 — Engagement Rate vs. Content Type
Charts:
  - Box plot: engagement rate distribution by Reddit flair
  - Scatter: views vs likes coloured by archetype (X)
  - Bar: HN comment-to-point ratio by story type
  - Heatmap: posting hour vs weekday for viral posts
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
from module2_archetypes import classify


# ── Chart 1: Reddit flair engagement ─────────────────────────────────────────
def chart_flair_engagement():
    reddit = load_reddit()
    reddit = reddit[reddit["likes"].notna() & (reddit["likes"] > 0)].copy()

    # top 12 flairs by post count
    top_flairs = reddit["flair"].value_counts().head(12).index
    subset = reddit[reddit["flair"].isin(top_flairs)].copy()

    flair_stats = subset.groupby("flair").agg(
        avg_score=("likes", "mean"),
        median_score=("likes", "median"),
        count=("id", "count"),
    ).sort_values("avg_score", ascending=True)

    fig, ax = plt.subplots(figsize=(12, 7))
    colors = plt.cm.RdYlGn(np.linspace(0.2, 0.9, len(flair_stats)))
    bars = ax.barh(flair_stats.index, flair_stats["avg_score"], color=colors, height=0.65)

    for bar, (idx, row) in zip(bars, flair_stats.iterrows()):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                f"  avg={row['avg_score']:.1f}  med={row['median_score']:.0f}  n={row['count']:,}",
                va="center", fontsize=8.5)

    ax.set_xlabel("Average Score", fontsize=11)
    ax.set_title("Reddit: Average Score by Post Flair\n(top 12 flairs by volume)", fontsize=12, fontweight="bold")
    ax.set_xlim(0, flair_stats["avg_score"].max() * 1.45)
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    out = CHARTS / "3a_reddit_flair_engagement.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out}")


# ── Chart 2: X — views vs likes by archetype ─────────────────────────────────
def chart_x_views_vs_likes():
    x = load_x()
    x = x[x["views"].notna() & x["likes"].notna()].copy()
    x["archetype"] = x["post_title"].apply(classify)
    x["engagement_rate"] = (x["likes"] + x["reposts"].fillna(0) + x["comments"].fillna(0)) / x["views"].replace(0, np.nan)

    archetypes = x["archetype"].unique()
    color_map  = {a: plt.cm.tab10(i / len(archetypes)) for i, a in enumerate(archetypes)}

    fig, ax = plt.subplots(figsize=(13, 8))
    for arch in archetypes:
        sub = x[x["archetype"] == arch]
        ax.scatter(sub["views"] / 1e6, sub["likes"] / 1e3,
                   label=arch, alpha=0.65, s=50, color=color_map[arch])

    ax.set_xlabel("Views (millions)", fontsize=11)
    ax.set_ylabel("Likes (thousands)", fontsize=11)
    ax.set_title("X: Views vs. Likes by Content Archetype\n(each dot = one tweet)", fontsize=12, fontweight="bold")
    ax.legend(fontsize=8, loc="upper left", framealpha=0.7)
    ax.grid(alpha=0.25)
    plt.tight_layout()
    out = CHARTS / "3b_x_views_vs_likes_archetype.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out}")


# ── Chart 3: HN discussion depth (comments/points ratio) ─────────────────────
def chart_hn_discussion_depth():
    hn = load_hn()
    hn = hn[hn["likes"].notna() & hn["comments"].notna() & (hn["likes"] > 0)].copy()
    hn["discussion_ratio"] = hn["comments"] / hn["likes"]
    hn["archetype"] = hn["post_title"].apply(classify)

    stats = hn.groupby("archetype").agg(
        avg_ratio=("discussion_ratio", "mean"),
        avg_points=("likes", "mean"),
        count=("id", "count"),
    ).sort_values("avg_ratio", ascending=True)

    fig, ax1 = plt.subplots(figsize=(12, 7))
    ax2 = ax1.twinx()

    y = range(len(stats))
    bars = ax1.barh(list(y), stats["avg_ratio"], color="#4a90d9", alpha=0.7, height=0.5, label="Avg comments/points")
    ax2.plot(stats["avg_points"], list(y), "o-", color="#e07b39", lw=2, ms=8, label="Avg points")

    ax1.set_yticks(list(y))
    ax1.set_yticklabels(stats.index, fontsize=10)
    ax1.set_xlabel("Avg Comments per Point (discussion depth)", color="#4a90d9", fontsize=10)
    ax2.set_xlabel("Avg Points", color="#e07b39", fontsize=10)
    ax1.set_title("HN: Discussion Depth vs. Points by Content Archetype\n(high ratio = controversial / debated)", fontsize=11, fontweight="bold")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="lower right", fontsize=9)
    ax1.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    out = CHARTS / "3c_hn_discussion_depth.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out}")


# ── Chart 4: Viral post timing heatmap (Reddit) ───────────────────────────────
def chart_timing_heatmap():
    reddit = load_reddit()
    top = reddit[reddit["likes"] >= reddit["likes"].quantile(0.90)].copy()
    top["hour"]    = top["published_at"].dt.hour
    top["weekday"] = top["published_at"].dt.day_name()

    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    pivot = top.pivot_table(index="weekday", columns="hour", values="likes",
                            aggfunc="mean").reindex(order)

    fig, ax = plt.subplots(figsize=(16, 5))
    im = ax.imshow(pivot.values, cmap="hot_r", aspect="auto")

    ax.set_xticks(range(24))
    ax.set_xticklabels([f"{h:02d}:00" for h in range(24)], rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(7))
    ax.set_yticklabels(order, fontsize=10)

    plt.colorbar(im, ax=ax, label="Avg score of top-10% posts")
    ax.set_title("Reddit: When Do Top-10% Posts Get Posted? (UTC)\nDarker = higher average score at that hour/day",
                 fontsize=11, fontweight="bold")
    plt.tight_layout()
    out = CHARTS / "3d_viral_timing_heatmap.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out}")


if __name__ == "__main__":
    print("=== Module 3: Engagement Rate Analysis ===")
    chart_flair_engagement()
    chart_x_views_vs_likes()
    chart_hn_discussion_depth()
    chart_timing_heatmap()
    print("Done.")
