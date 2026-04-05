#!/usr/bin/env python3
"""Render automation architecture diagram as a high-res PNG."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

# ── palette ────────────────────────────────────────────────────────
BG        = "#0d1117"
CARD_BG   = "#161b22"
BORDER    = "#30363d"

WHITE     = "#f0f6fc"
MUTED     = "#8b949e"
DIM       = "#484f58"

C_SOURCE  = "#58a6ff"   # blue  — data sources
C_STORE   = "#3fb950"   # green — storage
C_PROCESS = "#d2a8ff"   # purple — processing / analysis
C_DASH    = "#ffa657"   # orange — dashboard / output
C_ARROW   = "#6e7681"

FIG_W, FIG_H = 26, 20
DPI = 200

fig, ax = plt.subplots(figsize=(FIG_W, FIG_H), dpi=DPI)
ax.set_facecolor(BG)
fig.patch.set_facecolor(BG)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")

# ── helpers ────────────────────────────────────────────────────────

def box(x, y, w, h, color, alpha_fill=0.12, lw=1.4, radius=0.01):
    """Rounded rectangle."""
    import matplotlib.colors as mc
    rgb = mc.to_rgb(color)
    fc = (*rgb, alpha_fill)
    ec = (*rgb, 0.8)
    p = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0",
        facecolor=fc, edgecolor=ec,
        linewidth=lw,
        transform=ax.transAxes, clip_on=False, zorder=3,
    )
    ax.add_patch(p)

def txt(x, y, s, color=WHITE, size=9, bold=False, ha="left", va="center", alpha=1.0, zorder=5):
    ax.text(x, y, s,
            color=color, fontsize=size,
            fontweight="bold" if bold else "normal",
            ha=ha, va=va, alpha=alpha,
            transform=ax.transAxes, clip_on=False, zorder=zorder,
            fontfamily="monospace")

def arrow(x0, y0, x1, y1, color=C_ARROW, label=""):
    ax.annotate(
        "", xy=(x1, y1), xytext=(x0, y0),
        xycoords="axes fraction", textcoords="axes fraction",
        arrowprops=dict(
            arrowstyle="-|>", color=color, lw=1.4,
            mutation_scale=10,
            connectionstyle="arc3,rad=0.0",
        ), zorder=4,
    )
    if label:
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        txt(mx + 0.01, my, label, MUTED, size=7, ha="left")

def section_label(x, y, tag, title, color):
    """Section header badge + title."""
    box(x, y - 0.006, 0.038, 0.022, color, alpha_fill=0.3, lw=1)
    txt(x + 0.019, y + 0.005, tag, color, size=8, bold=True, ha="center")
    txt(x + 0.044, y + 0.005, title.upper(), color, size=8, alpha=0.75)

def node_card(x, y, w, h, color, title, lines, tag=None):
    """Draw a node card with title + detail lines."""
    box(x, y, w, h, color, alpha_fill=0.10, lw=1.2)
    # title bar
    import matplotlib.colors as mc
    rgb = mc.to_rgb(color)
    fc_title = (*rgb, 0.20)
    p = FancyBboxPatch(
        (x, y + h - 0.033), w, 0.033,
        boxstyle="round,pad=0",
        facecolor=fc_title, edgecolor="none",
        transform=ax.transAxes, clip_on=False, zorder=4,
    )
    ax.add_patch(p)
    # dot
    ax.plot(x + 0.012, y + h - 0.0165, "o", color=color,
            markersize=4, transform=ax.transAxes, zorder=6, clip_on=False)
    # title text
    txt(x + 0.026, y + h - 0.0165, title, color, size=7.5, bold=True)
    if tag:
        txt(x + w - 0.008, y + h - 0.0165, tag, MUTED, size=6, ha="right")
    # detail lines
    for i, line in enumerate(lines):
        txt(x + 0.014, y + h - 0.044 - i * 0.018, line, MUTED, size=6.5, va="top")

# ════════════════════════════════════════════════════════════════════
# TITLE
# ════════════════════════════════════════════════════════════════════
txt(0.5, 0.965, "AUTOMATED GROWTH INTELLIGENCE PIPELINE",
    WHITE, size=15, bold=True, ha="center")
txt(0.5, 0.943, "HackNU 2026  ·  Growth Engineering Track  ·  5 sources  ·  7 analysis modules  ·  Next.js dashboard",
    MUTED, size=8.5, ha="center")

# divider
ax.axhline(0.930, xmin=0.03, xmax=0.97, color=BORDER, lw=1, zorder=2)

# ════════════════════════════════════════════════════════════════════
# LAYER 0 — DATA SOURCES
# ════════════════════════════════════════════════════════════════════
L0_TOP = 0.895
section_label(0.03, L0_TOP + 0.017, "L0", "Data Sources", C_SOURCE)

sources = [
    ("REDDIT",        "reddit_worker.py",    ["Arctic Shift API", "r/ClaudeAI, r/anthropic", "score · comments · flair"]),
    ("HACKER NEWS",   "hackernews_worker.py",["Algolia HN API", "keyword search + comments", "points · comment depth"]),
    ("X / TWITTER",   "x_worker.py",         ["DuckDuckGo + syndication", "17 search queries", "views · likes · reposts"]),
    ("YOUTUBE",       "youtube_worker.py",   ["YouTube Data API v3", "channel + keyword search", "views · likes · comments"]),
    ("GOOGLE TRENDS", "google_trends_worker",["pytrends", "interest over time", "region · related queries"]),
]

card_w = 0.166
card_h = 0.098
gap = (0.94 - card_w * 5) / 4
for i, (title, sub, lines) in enumerate(sources):
    nx = 0.03 + i * (card_w + gap)
    node_card(nx, L0_TOP - card_h, card_w, card_h, C_SOURCE, title, lines, tag=sub)

# arrows L0 → L1 (5 arrows converging to center)
arrow_y_top = L0_TOP - card_h
arrow_y_bot = L0_TOP - card_h - 0.044
for i in range(5):
    cx = 0.03 + i * (card_w + gap) + card_w / 2
    ax.annotate("", xy=(0.5, arrow_y_bot),
                xytext=(cx, arrow_y_top),
                xycoords="axes fraction", textcoords="axes fraction",
                arrowprops=dict(arrowstyle="-|>", color=C_SOURCE, lw=1.1,
                                mutation_scale=8,
                                connectionstyle="arc3,rad=0.0"), zorder=4)

# ════════════════════════════════════════════════════════════════════
# LAYER 1 — STORAGE / RAW DATA
# ════════════════════════════════════════════════════════════════════
L1_TOP = L0_TOP - card_h - 0.044
section_label(0.03, L1_TOP + 0.015, "L1", "Storage", C_STORE)

box(0.03, L1_TOP - 0.068, 0.94, 0.068, C_STORE, alpha_fill=0.07, lw=1.3)

# store sub-boxes
stores = [
    ("data/raw/",          ["reddit_progress.json", "hacker_news_*.json", "youtube_*.json", "google_trends_*.json"]),
    ("data/x_tweets/",    ["tweets_*.jsonl", "DuckDuckGo + syndication", "scraped per query"]),
    ("data/processed/",   ["reddit_posts.csv", "reddit_comments.csv", "hacker_news_*.csv", "youtube_*.csv"]),
    ("storage/exporter.py",["export_csv()", "export_json()", "export_raw()", "unified model → Post"]),
]
sw = (0.94 - 0.06 - 0.03 * 3) / 4
for i, (title, lines) in enumerate(stores):
    sx = 0.045 + i * (sw + 0.03)
    node_card(sx, L1_TOP - 0.062, sw, 0.055, C_STORE, title, lines)

arrow(0.5, L1_TOP - 0.068, 0.5, L1_TOP - 0.068 - 0.038, C_STORE, "normalize · deduplicate · Post schema")

# ════════════════════════════════════════════════════════════════════
# LAYER 2 — PROCESSING
# ════════════════════════════════════════════════════════════════════
L2_TOP = L1_TOP - 0.068 - 0.038
section_label(0.03, L2_TOP + 0.015, "L2", "Data Processing", C_PROCESS)

procs = [
    ("process_data.py",      ["Reddit posts + comments", "X tweets cleaner", "Unified all_platforms.csv", "engagement_rate calc"]),
    ("process_higgsfield.py",["Higgsfield-specific", "YouTube + Reddit + X", "competitor baseline", "scoring normalisation"]),
    ("fetch_comments.py",    ["Top 10 comments/post", "Reddit comment tree", "score · author · body", "linked to post_id"]),
    ("models/post.py",       ["Pydantic Post model", "platform · id · title", "likes · views · comments", "published_at · url"]),
]
pw = (0.94 - 0.03 * 3) / 4
for i, (title, lines) in enumerate(procs):
    px = 0.03 + i * (pw + 0.03)
    node_card(px, L2_TOP - 0.098, pw, 0.090, C_PROCESS, title, lines)

arrow(0.5, L2_TOP - 0.098, 0.5, L2_TOP - 0.098 - 0.036, C_PROCESS, "clean CSVs  →  analysis-ready datasets")

# ════════════════════════════════════════════════════════════════════
# LAYER 3 — ANALYSIS
# ════════════════════════════════════════════════════════════════════
L3_TOP = L2_TOP - 0.098 - 0.036
section_label(0.03, L3_TOP + 0.015, "L3", "Analysis Engine  (analysis/run_all.py)", C_PROCESS)

modules = [
    ("M1 Timeline",      ["Weekly engagement", "Reddit growth curve", "Viral moment spikes"]),
    ("M2 Archetypes",    ["9 content classes", "regex classifier", "avg score per archetype"]),
    ("M3 Engagement",    ["Flair breakdown", "X views vs likes", "Timing heatmap"]),
    ("M4 Cascade",       ["Cross-platform lag", "X→HN→Reddit order", "event windows"]),
    ("M5 Amplifiers",    ["Top X accounts", "Official vs community", "Engagement efficiency"]),
    ("M6 Copy Patterns", ["Emotional triggers", "Title length lift", "Opening word lift"]),
    ("M7 Competition",   ["Competitor mention lift", "Timeline vs rivals", "View boost"]),
]

mw = (0.94 - 0.03 * 6) / 7
for i, (title, lines) in enumerate(modules):
    mx = 0.03 + i * (mw + 0.03)
    node_card(mx, L3_TOP - 0.092, mw, 0.085, C_PROCESS, title, lines)

# arrows from analysis to outputs (fan out)
ana_y_bot = L3_TOP - 0.092
output_y = ana_y_bot - 0.045
# left arrow to charts
ax.annotate("", xy=(0.20, output_y),
            xytext=(0.35, ana_y_bot),
            xycoords="axes fraction", textcoords="axes fraction",
            arrowprops=dict(arrowstyle="-|>", color=C_DASH, lw=1.2,
                            mutation_scale=9,
                            connectionstyle="arc3,rad=0.0"), zorder=4)
# center arrow to playbook
ax.annotate("", xy=(0.50, output_y),
            xytext=(0.50, ana_y_bot),
            xycoords="axes fraction", textcoords="axes fraction",
            arrowprops=dict(arrowstyle="-|>", color=C_DASH, lw=1.2,
                            mutation_scale=9), zorder=4)
# right arrow to dashboard
ax.annotate("", xy=(0.80, output_y),
            xytext=(0.65, ana_y_bot),
            xycoords="axes fraction", textcoords="axes fraction",
            arrowprops=dict(arrowstyle="-|>", color=C_DASH, lw=1.2,
                            mutation_scale=9,
                            connectionstyle="arc3,rad=0.0"), zorder=4)

# ════════════════════════════════════════════════════════════════════
# LAYER 4 — OUTPUTS
# ════════════════════════════════════════════════════════════════════
L4_TOP = output_y
section_label(0.03, L4_TOP + 0.012, "L4", "Outputs", C_DASH)

outputs = [
    (0.03,  0.30, "data/charts/  (28 PNGs)",
     ["1a weekly_engagement_timeline", "2a archetype_avg_score", "3d viral_timing_heatmap",
      "4b lead_lag_correlation", "5a x_amplifiers", "6a emotional_triggers", "7a competitor_lift"]),
    (0.38,  0.24, "VIRAL_PLAYBOOK.md",
     ["Executive summary", "8 viral templates + examples", "Platform sequencing strategy",
      "Amplifier tier list", "Copy formula + timing rules"]),
    (0.67,  0.30, "Next.js Dashboard  (dashboard/)",
     ["/ Home · findings summary", "/analysis  · 7-module charts", "/compare  · competitor grids",
      "/pipeline · architecture view", "/playbook  · rendered playbook"]),
]

for ox, ow, title, lines in outputs:
    node_card(ox, L4_TOP - 0.095, ow, 0.088, C_DASH, title, lines)

# ════════════════════════════════════════════════════════════════════
# LEGEND
# ════════════════════════════════════════════════════════════════════
lx, ly = 0.03, 0.030
legend_items = [
    (C_SOURCE,  "Data Sources / Scrapers"),
    (C_STORE,   "Storage / Raw & Processed"),
    (C_PROCESS, "Processing & Analysis"),
    (C_DASH,    "Outputs & Dashboard"),
]
for i, (color, label) in enumerate(legend_items):
    ex = lx + i * 0.20
    ax.plot(ex, ly, "s", color=color, markersize=8,
            transform=ax.transAxes, zorder=5, clip_on=False)
    txt(ex + 0.016, ly, label, MUTED, size=7, va="center")

# footer line
ax.axhline(0.048, xmin=0.03, xmax=0.97, color=BORDER, lw=0.8, zorder=2)
txt(0.97, 0.030, "growthhack  ·  HackNU 2026  ·  L0→L1→L2→L3→L4",
    DIM, size=7, ha="right")

# ── SAVE ───────────────────────────────────────────────────────────
out = "/Users/alemzhanakhmetzhanov/Desktop/projects/growthhack/dashboard/public/pipeline_diagram.png"
plt.tight_layout(pad=0.5)
plt.savefig(out, dpi=DPI, bbox_inches="tight", facecolor=BG, edgecolor="none")
plt.close()
print(f"Saved → {out}")
