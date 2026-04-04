"""
Module 1 — Viral Moment Timeline
Charts:
  - Weekly engagement volume per platform (stacked area)
  - Top spike moments labelled with event
  - Reddit monthly post volume growth
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
from data_loader import load_reddit, load_hn, load_x, CHARTS, EVENTS

# ── helpers ────────────────────────────────────────────────────────────────────
def _event_df():
    return pd.DataFrame(EVENTS, columns=["date", "label"]).assign(
        date=lambda d: pd.to_datetime(d["date"]).dt.tz_localize("UTC")
    )

# ── Previously unlabeled spikes — identified from tweet-level data ─────────────
IDENTIFIED_SPIKES = [
    # (date,  short label,  driver platform hint)
    ("2025-05-22", "Claude 4 launch\n+ deleted researcher tweet\n+ Rick Rubin collab"),
    ("2025-06-07", "Apple reasoning study\n(rubenhassid, 14.2M views)\n— 100% third-party"),
    ("2025-07-28", "Claude Opus 4.1\n+ @claudeai joins X\n+ rate-limit anger"),
    ("2025-11-11", "Eli Lilly CEO\nendorsement (10M)\n+ AI cyberattack disclosure"),
]

# ── Chart 1: Weekly engagement per platform ────────────────────────────────────
def chart_weekly_engagement():
    reddit = load_reddit()
    hn     = load_hn()
    x      = load_x()

    reddit["week"] = reddit["published_at"].dt.to_period("W").dt.start_time.dt.tz_localize("UTC")
    hn["week"]     = hn["published_at"].dt.to_period("W").dt.start_time.dt.tz_localize("UTC")
    x["week"]      = x["published_at"].dt.to_period("W").dt.start_time.dt.tz_localize("UTC")

    rw = reddit.groupby("week")["likes"].sum().rename("Reddit score")
    hw = hn.groupby("week")["likes"].sum().rename("HN points")
    xw = x.groupby("week")["views"].sum().div(1000).rename("X views (k)")

    df = pd.concat([rw, hw, xw], axis=1).fillna(0)
    df = df[df.index >= "2025-01-01"]

    known_events = _event_df()
    new_events = pd.DataFrame(IDENTIFIED_SPIKES, columns=["date", "label"]).assign(
        date=lambda d: pd.to_datetime(d["date"]).dt.tz_localize("UTC")
    )

    fig, axes = plt.subplots(3, 1, figsize=(20, 14), sharex=True)
    fig.patch.set_facecolor("#0e0e18")
    platform_colors = ["#e07b39", "#6aa84f", "#4a90d9"]
    bg_color = "#0e0e18"
    panel_bg = "#12121e"

    for ax, col, color in zip(axes, df.columns, platform_colors):
        ax.set_facecolor(panel_bg)
        ax.fill_between(df.index, df[col], alpha=0.55, color=color)
        ax.plot(df.index, df[col], color=color, lw=1.8)
        ax.set_ylabel(col, fontsize=10, color="#aaaacc")
        ax.tick_params(colors="#aaaacc", labelsize=8)
        ax.grid(axis="y", alpha=0.15, color="#ffffff")
        for spine in ax.spines.values():
            spine.set_edgecolor("#2a2a3a")

        # known events — red dashed
        for _, ev in known_events.iterrows():
            ax.axvline(ev["date"], color="#ff6b6b", alpha=0.5, lw=1.2, ls="--")

        # newly identified spikes — amber dashed
        for _, ev in new_events.iterrows():
            ax.axvline(ev["date"], color="#f5a623", alpha=0.6, lw=1.4, ls=":")

    # ── Labels on top axis (known events, red) ────────────────────────────────
    axes[0].set_ylim(bottom=0)
    y_top = axes[0].get_ylim()[1]

    for i, (_, ev) in enumerate(known_events.iterrows()):
        y_pos = y_top * (0.97 if i % 2 == 0 else 0.72)
        axes[0].text(
            ev["date"], y_pos, ev["label"],
            rotation=68, fontsize=6.2, ha="left", va="top",
            color="#ff8888", alpha=0.95,
            bbox=dict(boxstyle="round,pad=0.15", fc="#0e0e18", ec="none", alpha=0.7)
        )

    # ── Labels on X panel (new spikes, amber) — more room there ──────────────
    axes[2].set_ylim(bottom=0)
    y_top_x = axes[2].get_ylim()[1]

    for i, (_, ev) in enumerate(new_events.iterrows()):
        y_pos = y_top_x * (0.97 if i % 2 == 0 else 0.65)
        axes[2].text(
            ev["date"], y_pos, ev["label"],
            rotation=0, fontsize=6.5, ha="left", va="top",
            color="#f5c842", alpha=0.95,
            bbox=dict(boxstyle="round,pad=0.25", fc="#1a1400", ec="#f5a623", lw=0.6, alpha=0.88)
        )

    # ── Title + legend ─────────────────────────────────────────────────────────
    from matplotlib.lines import Line2D
    legend_handles = [
        Line2D([0], [0], color="#ff6b6b", ls="--", lw=1.5, label="Known events (Anthropic-announced)"),
        Line2D([0], [0], color="#f5a623", ls=":",  lw=1.8, label="Identified spikes (previously unlabeled)"),
    ]
    axes[0].legend(handles=legend_handles, loc="upper left", fontsize=8,
                   facecolor="#1a1a2a", edgecolor="#2a2a3a", labelcolor="#ddddee")

    axes[0].set_title(
        "Weekly Engagement Volume by Platform (2025–2026)\n"
        "Red dashes = known events  ·  Amber dots = newly identified spike causes",
        fontsize=13, fontweight="bold", color="#e8e8f0", pad=10
    )

    axes[2].xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    axes[2].tick_params(axis="x", colors="#aaaacc", labelsize=9, rotation=30)

    plt.tight_layout(rect=[0, 0, 1, 0.98])
    out = CHARTS / "1a_weekly_engagement_timeline.png"
    plt.savefig(out, dpi=160, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"Saved: {out}")


# ── Chart 2: Reddit monthly growth ────────────────────────────────────────────
def chart_reddit_growth():
    reddit = load_reddit()
    reddit = reddit[reddit["published_at"].dt.year >= 2025].copy()
    reddit["month"] = reddit["published_at"].dt.to_period("M")

    monthly = reddit.groupby("month").agg(
        posts=("id", "count"),
        total_score=("likes", "sum"),
        avg_score=("likes", "mean"),
    )
    monthly.index = monthly.index.to_timestamp()

    fig, ax1 = plt.subplots(figsize=(14, 6))
    ax2 = ax1.twinx()

    bars = ax1.bar(monthly.index, monthly["posts"], width=20, color="#e07b39", alpha=0.7, label="Post count")
    ax2.plot(monthly.index, monthly["avg_score"], color="#2c3e50", lw=2.5, marker="o", label="Avg score/post")

    ax1.set_xlabel("Month")
    ax1.set_ylabel("Number of Posts", color="#e07b39")
    ax2.set_ylabel("Avg Score per Post", color="#2c3e50")
    ax1.set_title("Reddit r/ClaudeAI: Monthly Post Volume vs. Average Engagement\n(11.5× growth Apr 2025 → Mar 2026)", fontsize=12, fontweight="bold")

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    out = CHARTS / "1b_reddit_growth.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out}")


# ── Chart 3: Top spike moments table ──────────────────────────────────────────
def chart_spike_moments():
    reddit = load_reddit()
    hn     = load_hn()
    x      = load_x()

    # top 15 viral posts across all platforms
    reddit_top = reddit.nlargest(50, "likes")[["platform","post_title","likes","comments","published_at"]].copy()
    reddit_top["engagement"] = reddit_top["likes"] + reddit_top["comments"].fillna(0)

    hn_top = hn.nlargest(50, "likes")[["platform","post_title","likes","comments","published_at"]].copy()
    hn_top["engagement"] = hn_top["likes"] + hn_top["comments"].fillna(0)

    x_top = x.nlargest(50, "views")[["platform","post_title","views","likes","published_at"]].copy()
    x_top = x_top.rename(columns={"views": "engagement"})
    x_top["likes"] = x_top["likes"].fillna(0)

    top = pd.concat([reddit_top[["platform","post_title","engagement","published_at"]],
                     hn_top[["platform","post_title","engagement","published_at"]],
                     x_top[["platform","post_title","engagement","published_at"]]],
                    ignore_index=True).nlargest(20, "engagement")

    fig, ax = plt.subplots(figsize=(18, 10))
    ax.axis("off")

    col_labels = ["Platform", "Title (truncated)", "Engagement", "Date"]
    data = [
        [
            row["platform"].upper(),
            str(row["post_title"])[:90] + ("…" if len(str(row["post_title"])) > 90 else ""),
            f"{int(row['engagement']):,}",
            str(row["published_at"])[:10] if pd.notna(row["published_at"]) else ""
        ]
        for _, row in top.iterrows()
    ]

    table = ax.table(cellText=data, colLabels=col_labels,
                     loc="center", cellLoc="left")
    table.auto_set_font_size(False)
    table.set_fontsize(8.5)
    table.scale(1, 1.6)

    # color header
    for j in range(len(col_labels)):
        table[0, j].set_facecolor("#2c3e50")
        table[0, j].set_text_props(color="white", fontweight="bold")
    # color rows by platform
    pcolor = {"REDDIT": "#fde8d8", "HACKER_NEWS": "#e8f4d8", "X": "#d8ecf8"}
    for i, (_, row) in enumerate(top.iterrows()):
        c = pcolor.get(row["platform"].upper(), "#f9f9f9")
        for j in range(len(col_labels)):
            table[i+1, j].set_facecolor(c)

    ax.set_title("Top 20 Viral Moments Across All Platforms\n(Reddit=score+comments, HN=points+comments, X=views)",
                 fontsize=12, fontweight="bold", pad=20)
    plt.tight_layout()
    out = CHARTS / "1c_top_viral_moments.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out}")


if __name__ == "__main__":
    print("=== Module 1: Viral Moment Timeline ===")
    chart_weekly_engagement()
    chart_reddit_growth()
    chart_spike_moments()
    print("Done.")
