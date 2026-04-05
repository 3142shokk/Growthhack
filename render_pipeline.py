#!/usr/bin/env python3
"""Render Stage 3 pipeline diagram as a high-res PNG."""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe
import numpy as np

# ── colour tokens ──────────────────────────────────────────────────
BG       = "#07070f"
BG2      = "#0a0a16"
BORDER   = "#1a1a2e"
MUTED    = "#4a4a6a"
DIM      = "#2a2a4a"
TEXT     = "#c4c4d0"
SUBTEXT  = "#6a6a8a"

C_INGEST  = "#00b4d8"
C_PROCESS = "#a855f7"
C_ROUTER  = "#f59e0b"
C_RT      = "#ef4444"
C_SCHED   = "#22c55e"
C_MEASURE = "#818cf8"

FIG_W, FIG_H = 28, 42
DPI = 200

fig, ax = plt.subplots(figsize=(FIG_W, FIG_H), dpi=DPI)
ax.set_facecolor(BG)
fig.patch.set_facecolor(BG)
ax.set_xlim(0, 1)
ax.set_ylim(0.27, 1.01)  # crop to content
ax.axis("off")

# ── dot-grid background ────────────────────────────────────────────
for x in np.arange(0.01, 1.0, 0.025):
    for y in np.arange(0.01, 1.0, 0.018):
        ax.plot(x, y, ".", color="#6366f1", alpha=0.07, markersize=1.2)

# ── helpers ────────────────────────────────────────────────────────
def rbox(ax, x, y, w, h, color, alpha=0.07, radius=0.008):
    """Draw a rounded box."""
    fc = list(plt.matplotlib.colors.to_rgb(color)) + [alpha]
    ec = list(plt.matplotlib.colors.to_rgb(color)) + [0.5]
    box = FancyBboxPatch((x, y), w, h,
                         boxstyle=f"round,pad=0",
                         facecolor=fc, edgecolor=ec, linewidth=1.2,
                         transform=ax.transAxes, zorder=3)
    ax.add_patch(box)

def label(ax, x, y, txt, color, size=9, bold=False, ha="left", va="center", alpha=1.0):
    weight = "bold" if bold else "normal"
    ax.text(x, y, txt, color=color, fontsize=size, fontweight=weight,
            ha=ha, va=va, transform=ax.transAxes, zorder=5, alpha=alpha,
            fontfamily="monospace")

def layer_header(ax, y, n, title, color):
    ax.axhline(y=y + 0.001, xmin=0.03, xmax=0.97, color=color, alpha=0.15, linewidth=0.8, zorder=2)
    rbox(ax, 0.03, y - 0.008, 0.025, 0.018, color, alpha=0.2)
    label(ax, 0.035, y + 0.002, n, color, size=7, bold=True)
    label(ax, 0.062, y + 0.002, title.upper(), color, size=6.5, alpha=0.7)

def varrow(ax, x, y_top, y_bot, color, dashed=False, label_txt=None):
    ls = "--" if dashed else "-"
    ax.annotate("", xy=(x, y_bot), xytext=(x, y_top),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1,
                                connectionstyle="arc3,rad=0",
                                mutation_scale=8),
                xycoords="axes fraction", textcoords="axes fraction", zorder=4)
    if label_txt:
        mid = (y_top + y_bot) / 2
        label(ax, x + 0.01, mid, label_txt, MUTED, size=5.5, ha="left")

def node(ax, x, y, w, h, title, color, lines, status="running", freq=None, vol=None):
    rbox(ax, x, y, w, h, color, alpha=0.08)
    status_color = C_SCHED if status == "running" else C_ROUTER if status == "triggered" else MUTED
    # status dot
    ax.plot(x + 0.012, y + h - 0.012, "o", color=status_color, markersize=3.5,
            transform=ax.transAxes, zorder=6)
    # title
    label(ax, x + 0.025, y + h - 0.012, title, color, size=6, bold=True)
    # status text
    label(ax, x + w - 0.01, y + h - 0.012, status.upper(), status_color, size=4.5, ha="right")
    # freq/vol
    if freq or vol:
        info = []
        if freq: info.append(f"freq {freq}")
        if vol:  info.append(f"vol {vol}")
        label(ax, x + 0.025, y + h - 0.024, "  ".join(info), MUTED, size=4.8)
    # detail lines
    for i, ln in enumerate(lines):
        label(ax, x + 0.025, y + h - 0.036 - i * 0.011, ln, SUBTEXT, size=5)


# ════════════════════════════════════════════════════════════════════
# LAYOUT — top to bottom
# ════════════════════════════════════════════════════════════════════

# ── HERO TEXT ──────────────────────────────────────────────────────
ax.text(0.5, 0.978, "AUTOMATED GROWTH INTELLIGENCE PIPELINE",
        color="white", fontsize=14, fontweight="bold", ha="center", va="center",
        transform=ax.transAxes, fontfamily="monospace", zorder=5)
ax.text(0.5, 0.971, "Stage 3  ·  HackNU 2026  ·  Growth Engineering Track",
        color=MUTED, fontsize=7, ha="center", va="center",
        transform=ax.transAxes, fontfamily="monospace", zorder=5)

# status pill
rbox(ax, 0.35, 0.962, 0.3, 0.013, C_SCHED, alpha=0.08)
ax.plot(0.365, 0.9685, "o", color=C_SCHED, markersize=3, transform=ax.transAxes, zorder=6)
label(ax, 0.372, 0.9685, "SYSTEM ONLINE  ·  5 sources  ·  ~2,400 posts/hr  ·  4 exec tracks  ·  4 KPI signals",
      C_SCHED, size=5.5, ha="left")

# stats row
for i, (val, lbl) in enumerate([("5","sources"),("~2,400","posts/hr"),("9","archetypes"),
                                  ("4","platforms"),("2","exec tracks"),("4","kpi signals")]):
    xi = 0.05 + i * 0.155
    label(ax, xi, 0.954, val, "white", size=9, bold=True, ha="left")
    label(ax, xi, 0.947, lbl, MUTED, size=5, ha="left")

# ── L0: SOURCES ────────────────────────────────────────────────────
L0_Y = 0.898
layer_header(ax, L0_Y + 0.025, "L0", "Data Sources", C_INGEST)

sources = [
    ("REDDIT_SCRAPER",  "60min",  "200/run",  ["r/ClaudeAI · r/HiggsfieldAI", "PRAW · read-only auth", "title·score·flair·author"]),
    ("HN_WATCHER",      "real-time","top-30", ["Algolia HN API /search_by_date", "trigger: keyword match", "objectID·points·num_comments"]),
    ("X_SCRAPER",       "60min",  "50/run",   ["GraphQL keyword search", "claude · higgsfield", "id·text·view_count"]),
    ("YOUTUBE_API",     "daily",  "channel+search", ["YouTube Data v3", "queries: 'claude AI' etc.", "videoId·viewCount·likeCount"]),
    ("GTRENDS_POLLER",  "weekly", "comparison", ["pytrends · geo: US+GB+IN", "claude vs chatgpt vs higgsfield", "date·interest·index"]),
]
node_w = 0.175
node_h = 0.065
gap = (1 - 0.06 - node_w * 5) / 4
for i, (title, freq, vol, lines) in enumerate(sources):
    nx = 0.03 + i * (node_w + gap)
    node(ax, nx, L0_Y - 0.045, node_w, node_h, title, C_INGEST, lines, "running", freq, vol)

# arrow L0→L1
varrow(ax, 0.5, L0_Y - 0.045, L0_Y - 0.072, C_INGEST, label_txt="POST[] → normalize → Post schema")

# ── L1: UNIFIED COLLECTOR ──────────────────────────────────────────
L1_Y = L0_Y - 0.072
layer_header(ax, L1_Y + 0.026, "L1", "Unified Collector", C_INGEST)
rbox(ax, 0.03, L1_Y - 0.048, 0.94, 0.058, C_INGEST, alpha=0.07)
ax.plot(0.042, L1_Y + 0.013, "o", color=C_SCHED, markersize=3.5, transform=ax.transAxes, zorder=6)
label(ax, 0.055, L1_Y + 0.013, "UNIFIED_COLLECTOR", C_INGEST, size=7, bold=True)
label(ax, 0.97, L1_Y + 0.013, "RUNNING", C_SCHED, size=4.5, ha="right")
label(ax, 0.055, L1_Y + 0.003, "freq continuous   vol ~2,400 posts/hr", MUTED, size=5)
cols = [
    "input:  raw platform objects from all 5 scrapers",
    "output: Post[] — pydantic-validated · deduplicated by (platform, id)",
    "store:  SQLite → posts.db · indexed on (platform, created_at, score)",
    "dedup:  upsert on primary key · update score + comments on re-scrape",
]
for i, c in enumerate(cols):
    label(ax, 0.055, L1_Y - 0.008 - i * 0.01, c, SUBTEXT, size=5)

# arrow L1→L2
varrow(ax, 0.5, L1_Y - 0.048, L1_Y - 0.073, C_PROCESS,
       label_txt="Post{id, platform, text, score, timestamp}")

# ── L2: SIGNAL PROCESSING ──────────────────────────────────────────
L2_Y = L1_Y - 0.073
layer_header(ax, L2_Y + 0.026, "L2", "Signal Processing", C_PROCESS)
procs = [
    ("SPIKE_DETECTOR",       "hourly",    "per-platform",  ["z-score vs 4-week rolling avg", "threshold: 2σ above baseline", "output: spike_flag=True + delta%"]),
    ("ARCHETYPE_CLASSIFIER", "on-ingest", "every post",    ["regex ruleset → 9 classes", "Insider·Controversy·Demo·Story…", "fallback: 'other' if no match"]),
    ("CASCADE_DETECTOR",     "hourly",    "cross-platform",["compare first-post timestamp", "X_first → top_down", "Reddit_first → bottom_up"]),
    ("NARRATIVE_MONITOR",    "hourly",    "HN+X trending", ["scan HN front page + X trends", "match: keyword overlap", "flag: 'deepseek'|'regulation'|etc"]),
]
node_w2 = 0.22
gap2 = (1 - 0.06 - node_w2 * 4) / 3
for i, (title, freq, vol, lines) in enumerate(procs):
    nx = 0.03 + i * (node_w2 + gap2)
    node(ax, nx, L2_Y - 0.045, node_w2, node_h, title, C_PROCESS, lines, "running", freq, vol)

# arrow L2→L3
varrow(ax, 0.5, L2_Y - 0.045, L2_Y - 0.073, C_ROUTER,
       label_txt="Signal{archetype, spike, cascade_dir, narrative}")

# ── L3: ROUTING ENGINE ─────────────────────────────────────────────
L3_Y = L2_Y - 0.073
layer_header(ax, L3_Y + 0.026, "L3", "Routing Engine", C_ROUTER)
rbox(ax, 0.03, L3_Y - 0.08, 0.94, 0.09, C_ROUTER, alpha=0.07)
label(ax, 0.055, L3_Y + 0.010, "● PLATFORM × ARCHETYPE ROUTER", C_ROUTER, size=7, bold=True)
label(ax, 0.97, L3_Y + 0.010, "decision engine · 9 archetypes × 4 platforms", MUTED, size=5, ha="right")

rules_l = [
    ("archetype = capability_demo",  "→ HN first, then YouTube",         ["HN","YT"]),
    ("archetype = insider_reveal",   "→ cascade trigger: all platforms",  ["X","HN","R"]),
    ("archetype = controversy",      "→ X + Reddit simultaneous",         ["X","R"]),
    ("archetype = model_release",    "→ HN priority (242 avg pts)",       ["HN","X"]),
]
rules_r = [
    ("archetype = personal_story",   "→ X first (395k avg views)",        ["X"]),
    ("archetype = third_party",      "→ X priority (533k avg views)",     ["X","HN"]),
    ("spike_flag = True",            "→ real-time track + amplifier DM",  ["A"]),
    ("narrative != None",            "→ insert into live news cycle",     ["X"]),
]
for i, (cond, out, plat) in enumerate(rules_l):
    y = L3_Y - 0.002 - i * 0.018
    label(ax, 0.05, y, "IF", MUTED, size=5)
    label(ax, 0.065, y, cond, SUBTEXT, size=5.2)
    label(ax, 0.28, y, out, TEXT, size=5.2)
    for j, p in enumerate(plat):
        rbox(ax, 0.47 + j * 0.025, y - 0.006, 0.022, 0.013, C_MEASURE, alpha=0.25)
        label(ax, 0.481 + j * 0.025, y + 0.0005, p, C_MEASURE, size=4.5, ha="left")
for i, (cond, out, plat) in enumerate(rules_r):
    y = L3_Y - 0.002 - i * 0.018
    label(ax, 0.55, y, "IF", MUTED, size=5)
    label(ax, 0.565, y, cond, SUBTEXT, size=5.2)
    label(ax, 0.77, y, out, TEXT, size=5.2)
    for j, p in enumerate(plat):
        rbox(ax, 0.955 + j * 0.025 - len(plat)*0.025 + j*0.001, y - 0.006, 0.022, 0.013, C_MEASURE, alpha=0.25)
        label(ax, 0.966 + j * 0.025 - len(plat)*0.025 + j*0.001, y + 0.0005, p, C_MEASURE, size=4.5, ha="left")

label(ax, 0.05, L3_Y - 0.074, "ELSE → scheduled_track · add to weekly content calendar · assign copy formula (opening_word + length_target)",
      MUTED, size=4.8)

# ── TRACK SPLIT ────────────────────────────────────────────────────
split_y = L3_Y - 0.08
# center line down
ax.plot([0.5, 0.5], [split_y, split_y - 0.012], color=DIM, lw=1, transform=ax.transAxes, zorder=4)
# horizontal bar
ax.plot([0.22, 0.78], [split_y - 0.012, split_y - 0.012], color=DIM, lw=1, transform=ax.transAxes, zorder=4)
# left branch
ax.annotate("", xy=(0.22, split_y - 0.028), xytext=(0.22, split_y - 0.012),
            arrowprops=dict(arrowstyle="-|>", color=C_RT, lw=1, mutation_scale=7),
            xycoords="axes fraction", textcoords="axes fraction", zorder=4)
# right branch
ax.annotate("", xy=(0.78, split_y - 0.028), xytext=(0.78, split_y - 0.012),
            arrowprops=dict(arrowstyle="-|>", color=C_SCHED, lw=1, mutation_scale=7),
            xycoords="axes fraction", textcoords="axes fraction", zorder=4)
label(ax, 0.22, split_y - 0.006, "SPIKE RESPONSE", C_RT, size=5.5, ha="center")
label(ax, 0.78, split_y - 0.006, "SCHEDULED INTEL", C_SCHED, size=5.5, ha="center")

# ── L4: TWO TRACKS ─────────────────────────────────────────────────
L4_Y = split_y - 0.028
layer_header(ax, L4_Y + 0.026, "L4", "Execution Tracks", "#6b7280")

track_h = 0.125
# Track A box
rbox(ax, 0.03, L4_Y - track_h, 0.44, track_h, C_RT, alpha=0.07)
ax.plot(0.042, L4_Y + 0.011, "o", color=C_RT, markersize=3.5, transform=ax.transAxes, zorder=6)
label(ax, 0.055, L4_Y + 0.011, "Track A  ·  Spike Response", C_RT, size=6.5, bold=True)
steps_a = [
    ("T+0min",  "BRIEF_GEN",       "generate brief: platform, archetype, copy formula (70–130 chars)"),
    ("T+15min", "AMPLIFIER_ALERT", "Slack/DM to active creators + 4 film creators · include asset"),
    ("T+30min", "OFFICIAL_POST",   "X post · optimal time: Tue–Thu 14:00–19:00 UTC"),
    ("T+90min", "HN_SUBMIT",       "DM adocomplete / meetpateltech · 1-sentence pitch + link"),
    ("T+4hr",   "REDDIT_SEED",     "personal-story version to r/HiggsfieldAI first · r/aivideo day+1"),
    ("T+8hr",   "X_WAVE_2",        "thread replies · quote-tweets · engagement monitoring"),
]
for i, (step, lbl, detail) in enumerate(steps_a):
    y = L4_Y - 0.004 - i * 0.019
    label(ax, 0.05, y, step, C_RT, size=5, ha="left")
    label(ax, 0.115, y, lbl, TEXT, size=5.5, bold=True)
    label(ax, 0.115, y - 0.01, detail, SUBTEXT, size=4.8)

# Track B box
rbox(ax, 0.53, L4_Y - track_h, 0.44, track_h, C_SCHED, alpha=0.07)
ax.plot(0.542, L4_Y + 0.011, "o", color=C_SCHED, markersize=3.5, transform=ax.transAxes, zorder=6)
label(ax, 0.555, L4_Y + 0.011, "Track B  ·  Scheduled Intelligence", C_SCHED, size=6.5, bold=True)
steps_b = [
    ("Sun", "WEEKLY_DIGEST",    "top archetypes · score dist · competitor mentions · trend deltas"),
    ("Mon", "CONTENT_CALENDAR", "5 content briefs for the week · platform assignments · openers"),
    ("Mon", "ARCHETYPE_AUDIT",  "% Insider + Controversy in 30d · alert if below 20% target"),
    ("Tue", "COMMUNITY_SEED",   "3 posts to r/HiggsfieldAI · weekly challenge · filmmaker spotlight"),
    ("Thu", "HN_OPPORTUNITY",   "scan Claude HN stories without Higgsfield counterpart"),
    ("Fri", "FLYWHEEL_REPORT",  "owned ratio · amplifier idx · archetype mix · view floor · Slack"),
]
for i, (step, lbl, detail) in enumerate(steps_b):
    y = L4_Y - 0.004 - i * 0.019
    label(ax, 0.545, y, step, C_SCHED, size=5, ha="left")
    label(ax, 0.59, y, lbl, TEXT, size=5.5, bold=True)
    label(ax, 0.59, y - 0.01, detail, SUBTEXT, size=4.8)

# ── TRACK MERGE ────────────────────────────────────────────────────
merge_y = L4_Y - track_h
ax.plot([0.22, 0.22], [merge_y, merge_y - 0.012], color=C_RT, lw=1, ls="--", transform=ax.transAxes, zorder=4)
ax.plot([0.78, 0.78], [merge_y, merge_y - 0.012], color=C_SCHED, lw=1, ls="--", transform=ax.transAxes, zorder=4)
ax.plot([0.22, 0.78], [merge_y - 0.012, merge_y - 0.012], color=DIM, lw=1, transform=ax.transAxes, zorder=4)
ax.annotate("", xy=(0.5, merge_y - 0.028), xytext=(0.5, merge_y - 0.012),
            arrowprops=dict(arrowstyle="-|>", color=DIM, lw=1, mutation_scale=7),
            xycoords="axes fraction", textcoords="axes fraction", zorder=4)

# ── L5: FLYWHEEL MEASUREMENT ───────────────────────────────────────
L5_Y = merge_y - 0.028
layer_header(ax, L5_Y + 0.026, "L5", "Flywheel Measurement", C_MEASURE)
metrics = [
    ("OWNED_RATIO",     "weekly",  "per platform",  ["r/HiggsfieldAI ÷ total Reddit", "current: ~3% · target: >50%", "alert: if ratio drops WoW"]),
    ("AMPLIFIER_INDEX", "weekly",  "X accounts",    ["# voices with >100k followers", "current: 1 · target: ≥5", "decay: weight recent posts higher"]),
    ("ARCHETYPE_MIX",   "weekly",  "30d window",    ["% Insider + Controversy total", "current: ~0% · target: >20%", "source: classifier output"]),
    ("VIEW_FLOOR",      "monthly", "trailing 3mo",  ["lowest monthly X view total", "current: ~5M · target: >20M", "floor not peak — structural reach"]),
]
node_w5 = 0.22
gap5 = (1 - 0.06 - node_w5 * 4) / 3
for i, (title, freq, vol, lines) in enumerate(metrics):
    nx = 0.03 + i * (node_w5 + gap5)
    node(ax, nx, L5_Y - 0.065, node_w5, node_h, title, C_MEASURE, lines, "idle", freq, vol)

# feedback loop annotation
fb_y = L5_Y - 0.065 - 0.01
rbox(ax, 0.03, fb_y - 0.022, 0.94, 0.022, C_MEASURE, alpha=0.05)
# recycl icon (simple circle arrow text)
label(ax, 0.05, fb_y - 0.010, "↺", C_MEASURE, size=9, bold=True)
label(ax, 0.07, fb_y - 0.009,
      "feedback loop — L5 metrics update L2 baselines weekly. rising owned_ratio lowers spike_threshold for r/HiggsfieldAI.",
      C_MEASURE, size=5.2)
label(ax, 0.07, fb_y - 0.018,
      "rising view_floor raises cascade priority score. the pipeline self-calibrates.",
      C_MEASURE, size=5.2)

# ── FOOTER ─────────────────────────────────────────────────────────
ax.axhline(y=0.015, xmin=0.03, xmax=0.97, color=BORDER, linewidth=0.7, zorder=2)
label(ax, 0.05, 0.008, "HackNU 2026  ·  Stage 3  ·  Automated Intelligence Pipeline",
      MUTED, size=5.5)
label(ax, 0.97, 0.008, "L0 → L1 → L2 → L3 → L4a | L4b → L5 → ↺",
      MUTED, size=5.5, ha="right")

# ── SAVE ───────────────────────────────────────────────────────────
out = "/Users/alemzhanakhmetzhanov/Desktop/projects/growthhack/dashboard/public/pipeline_diagram.png"
plt.tight_layout(pad=0)
plt.savefig(out, dpi=DPI, bbox_inches="tight", facecolor=BG, edgecolor="none")
plt.close()
print(f"Saved → {out}")
