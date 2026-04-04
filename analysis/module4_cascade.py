"""
Module 4 — Cross-Platform Cascade Analysis
For each major viral event, shows which platform spiked first and
how activity spread across Reddit / HN / X in the days following.
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

WINDOW_DAYS = 14   # days around each event to plot

COLORS = {"reddit": "#e07b39", "hacker_news": "#6aa84f", "x": "#4a90d9"}


def _daily_engagement(reddit, hn, x):
    reddit["date"] = reddit["published_at"].dt.floor("D")
    hn["date"]     = hn["published_at"].dt.floor("D")
    x["date"]      = x["published_at"].dt.floor("D")

    rd = reddit.groupby("date")["likes"].sum().rename("reddit")
    hd = hn.groupby("date")["likes"].sum().rename("hacker_news")
    xd = x.groupby("date")["views"].sum().div(1000).rename("x_views_k")

    return pd.concat([rd, hd, xd], axis=1).fillna(0)


# ── Chart 1: Per-event cascade windows ───────────────────────────────────────
def chart_event_cascades():
    reddit = load_reddit()
    hn     = load_hn()
    x      = load_x()
    daily  = _daily_engagement(reddit, hn, x)

    # pick 6 events with most obvious spikes
    key_events = [
        ("2026-02-23", "DeepSeek distillation\nattack disclosure"),
        ("2026-02-26", "Dario DoW statement"),
        ("2026-02-05", "Claude Opus 4.6 launch"),
        ("2026-03-31", "Claude Code source leak"),
        ("2025-05-22", "Claude 4 launch"),
        ("2025-12-02", "Bun acquisition"),
    ]

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    axes = axes.flatten()

    for ax, (ev_date, label) in zip(axes, key_events):
        center = pd.Timestamp(ev_date, tz="UTC")
        start  = center - pd.Timedelta(days=5)
        end    = center + pd.Timedelta(days=WINDOW_DAYS)

        window = daily[(daily.index >= start) & (daily.index <= end)].copy()
        if window.empty:
            ax.set_title(f"{label}\n(no data)")
            continue

        ax2 = ax.twinx()

        ax.fill_between(window.index, window["reddit"],  alpha=0.5, color=COLORS["reddit"],      label="Reddit score")
        ax.fill_between(window.index, window["hacker_news"], alpha=0.5, color=COLORS["hacker_news"], label="HN points")
        ax2.plot(window.index, window["x_views_k"], color=COLORS["x"], lw=2.5, marker="o", ms=4, label="X views (k)")

        ax.axvline(center, color="red", lw=2, ls="--", alpha=0.8)
        ax.set_title(label, fontsize=9, fontweight="bold")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
        ax.tick_params(axis="x", labelsize=7, rotation=30)
        ax.set_ylabel("Reddit/HN", fontsize=7, color="grey")
        ax2.set_ylabel("X views k", fontsize=7, color=COLORS["x"])

        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        if ax == axes[0]:
            ax.legend(lines1 + lines2, labels1 + labels2, fontsize=6.5, loc="upper right")

    plt.suptitle("Cross-Platform Cascade: Activity Around Key Events\n(red dashes = event day)",
                 fontsize=12, fontweight="bold")
    plt.tight_layout()
    out = CHARTS / "4a_event_cascade_windows.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out}")


# ── Chart 2: Lead/lag correlation between platforms ──────────────────────────
def chart_lead_lag():
    reddit = load_reddit()
    hn     = load_hn()
    x      = load_x()
    daily  = _daily_engagement(reddit, hn, x)

    # filter to 2025+
    daily = daily[daily.index >= "2025-01-01"]

    # cross-correlation: does X lead Reddit?
    lags   = range(-7, 8)
    corr_x_reddit = [daily["x_views_k"].corr(daily["reddit"].shift(lag)) for lag in lags]
    corr_x_hn     = [daily["x_views_k"].corr(daily["hacker_news"].shift(lag)) for lag in lags]
    corr_hn_reddit= [daily["hacker_news"].corr(daily["reddit"].shift(lag)) for lag in lags]

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(list(lags), corr_x_reddit,  marker="o", color=COLORS["reddit"],      label="X leads Reddit (lag X→R)")
    ax.plot(list(lags), corr_x_hn,      marker="s", color=COLORS["hacker_news"], label="X leads HN (lag X→HN)")
    ax.plot(list(lags), corr_hn_reddit, marker="^", color="#9b59b6",             label="HN leads Reddit (lag HN→R)")

    ax.axvline(0, color="grey", ls="--", alpha=0.5)
    ax.axhline(0, color="grey", ls="--", alpha=0.3)
    ax.set_xlabel("Lag (days) — positive = left platform leads right platform", fontsize=10)
    ax.set_ylabel("Pearson Correlation", fontsize=10)
    ax.set_title("Cross-Platform Lead/Lag Correlation\n(peak at lag=N means left platform spikes N days before right platform)",
                 fontsize=11, fontweight="bold")
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)
    ax.set_xticks(list(lags))
    plt.tight_layout()
    out = CHARTS / "4b_lead_lag_correlation.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out}")


# ── Chart 3: Platform share of weekly top posts ──────────────────────────────
def chart_platform_dominance():
    reddit = load_reddit()
    hn     = load_hn()
    x      = load_x()

    reddit = reddit[reddit["published_at"].dt.year >= 2025].copy()
    hn     = hn[hn["published_at"].dt.year >= 2025].copy()
    x      = x[x["published_at"].dt.year >= 2025].copy()

    reddit["month"] = reddit["published_at"].dt.to_period("M")
    hn["month"]     = hn["published_at"].dt.to_period("M")
    x["month"]      = x["published_at"].dt.to_period("M")

    r_vol = reddit.groupby("month").size().rename("Reddit posts")
    h_vol = hn.groupby("month").size().rename("HN stories")
    x_vol = x.groupby("month").size().rename("X tweets")

    vol = pd.concat([r_vol, h_vol, x_vol], axis=1).fillna(0)
    vol.index = vol.index.to_timestamp()

    fig, ax = plt.subplots(figsize=(14, 6))
    bottom = np.zeros(len(vol))
    palette = [COLORS["reddit"], COLORS["hacker_news"], COLORS["x"]]

    for col, color in zip(vol.columns, palette):
        ax.bar(vol.index, vol[col], bottom=bottom, label=col, color=color, alpha=0.85, width=22)
        bottom += vol[col].values

    ax.set_title("Monthly Content Volume by Platform (2025–2026)", fontsize=12, fontweight="bold")
    ax.set_ylabel("Number of posts / stories / tweets")
    ax.legend(fontsize=10)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.xticks(rotation=30, ha="right")
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    out = CHARTS / "4c_platform_volume_stack.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out}")


if __name__ == "__main__":
    print("=== Module 4: Cross-Platform Cascade ===")
    chart_event_cascades()
    chart_lead_lag()
    chart_platform_dominance()
    print("Done.")
