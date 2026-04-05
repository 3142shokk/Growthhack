"""
compare_charts.py — Claude vs Higgsfield comparison charts.

Generates cmp_*.png files in data/charts/.
"""
from __future__ import annotations
import warnings
warnings.filterwarnings("ignore")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import pandas as pd
import numpy as np
import re
from collections import Counter
from pathlib import Path
from compare_loader import load_claude, load_higgsfield, load_both, BRAND_COLORS, CHARTS

try:
    from wordcloud import WordCloud
    HAS_WC = True
except ImportError:
    HAS_WC = False

BG     = "#09090f"
PANEL  = "#0e0e18"
BORDER = "#1e1e2e"
TEXT   = "#e2e2ea"
MUTED  = "#6b6b7b"

C_COLOR = BRAND_COLORS["Claude"]["primary"]       # orange
H_COLOR = BRAND_COLORS["Higgsfield"]["primary"]   # indigo

STOPWORDS = {
    "the","a","an","and","or","but","in","on","at","to","for","of","with",
    "is","it","its","this","that","my","i","you","we","he","she","they",
    "be","been","have","has","had","do","does","did","will","would","can",
    "could","should","from","by","as","are","was","were","so","if","not",
    "no","what","when","how","why","which","who","up","out","about","just",
    "more","than","like","get","got","all","any","one","new","s","t","using",
    "after","before","into","over","also","here","there","some","now","use",
    "make","made","best","ai","video","model","image","generate","generation"
}

def _style(fig, axes):
    fig.patch.set_facecolor(BG)
    for ax in (axes if hasattr(axes, '__iter__') else [axes]):
        ax.set_facecolor(PANEL)
        ax.tick_params(colors=MUTED, labelsize=8)
        ax.grid(axis="y", alpha=0.12, color="#ffffff")
        for spine in ax.spines.values():
            spine.set_edgecolor(BORDER)
        ax.xaxis.label.set_color(MUTED)
        ax.yaxis.label.set_color(MUTED)
        ax.title.set_color(TEXT)

def _save(fig, name):
    out = CHARTS / name
    plt.tight_layout()
    plt.savefig(out, dpi=155, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"Saved: {out}")


# ── 1. Community scale — total posts per platform ────────────────────────────
def chart_community_scale():
    cl = load_claude()
    hf = load_higgsfield()

    platforms = ["reddit", "x", "youtube", "hacker_news"]
    labels    = ["Reddit", "X / Twitter", "YouTube", "Hacker News"]
    cl_counts = [len(cl[cl["platform"] == p]) for p in platforms]
    hf_counts = [len(hf[hf["platform"] == p]) for p in platforms]

    x = np.arange(len(labels))
    w = 0.35
    fig, ax = plt.subplots(figsize=(12, 6))
    _style(fig, [ax])
    b1 = ax.bar(x - w/2, cl_counts, w, label="Claude",     color=C_COLOR, alpha=0.85)
    b2 = ax.bar(x + w/2, hf_counts, w, label="Higgsfield", color=H_COLOR, alpha=0.85)
    ax.set_xticks(x); ax.set_xticklabels(labels, color=TEXT, fontsize=10)
    ax.set_ylabel("Number of posts / items", color=MUTED)
    ax.set_title("Community Scale: Total Content Volume by Platform", color=TEXT, fontweight="bold", fontsize=12)
    ax.legend(facecolor=PANEL, edgecolor=BORDER, labelcolor=TEXT, fontsize=9)
    for bar in list(b1) + list(b2):
        h = bar.get_height()
        if h > 0:
            ax.text(bar.get_x() + bar.get_width()/2, h + max(cl_counts)*0.01,
                    f"{int(h):,}", ha="center", fontsize=7.5, color=MUTED)
    _save(fig, "cmp_01_community_scale.png")


# ── 2. Reddit monthly growth comparison ──────────────────────────────────────
def chart_reddit_growth():
    cl = load_claude()
    hf = load_higgsfield()

    cl_r = cl[(cl["platform"] == "reddit") & (cl["published_at"].dt.year >= 2025)].copy()
    hf_r = hf[(hf["platform"] == "reddit") & (hf["published_at"].dt.year >= 2025)].copy()

    cl_r["month"] = cl_r["published_at"].dt.to_period("M").dt.to_timestamp()
    hf_r["month"] = hf_r["published_at"].dt.to_period("M").dt.to_timestamp()

    cl_m = cl_r.groupby("month").size().rename("Claude")
    hf_m = hf_r.groupby("month").size().rename("Higgsfield")
    df = pd.concat([cl_m, hf_m], axis=1).fillna(0)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
    _style(fig, [ax1, ax2])

    ax1.fill_between(df.index, df["Claude"],     alpha=0.6, color=C_COLOR)
    ax1.plot(df.index, df["Claude"], color=C_COLOR, lw=2)
    ax1.set_ylabel("Posts / month", color=MUTED)
    ax1.set_title("Claude Reddit — Monthly Post Volume", color=TEXT, fontweight="bold")

    ax2.fill_between(df.index, df["Higgsfield"], alpha=0.6, color=H_COLOR)
    ax2.plot(df.index, df["Higgsfield"], color=H_COLOR, lw=2)
    ax2.set_ylabel("Posts / month", color=MUTED)
    ax2.set_title("Higgsfield Reddit — Monthly Post Volume", color=TEXT, fontweight="bold")
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.xticks(rotation=25, ha="right", color=MUTED)

    fig.suptitle("Reddit Growth Trajectory: Claude vs. Higgsfield", color=TEXT, fontsize=13, fontweight="bold", y=1.01)
    _save(fig, "cmp_02_reddit_growth.png")


# ── 3. Avg engagement per platform ───────────────────────────────────────────
def chart_avg_engagement():
    cl = load_claude()
    hf = load_higgsfield()

    metrics = {
        "Reddit\navg score": ("reddit", "likes"),
        "X avg\nlikes": ("x", "likes"),
        "X avg\nviews (k)": ("x", "views"),
        "YouTube\navg views (k)": ("youtube", "views"),
        "YouTube\navg likes": ("youtube", "likes"),
    }

    cl_vals, hf_vals = [], []
    for label, (plat, col) in metrics.items():
        cl_v = cl[(cl["platform"] == plat)][col].mean()
        hf_v = hf[(hf["platform"] == plat)][col].mean()
        scale = 1000 if "k)" in label else 1
        cl_vals.append(cl_v / scale)
        hf_vals.append(hf_v / scale)

    x = np.arange(len(metrics))
    w = 0.35
    fig, ax = plt.subplots(figsize=(13, 6))
    _style(fig, [ax])
    ax.bar(x - w/2, cl_vals, w, label="Claude",     color=C_COLOR, alpha=0.85)
    ax.bar(x + w/2, hf_vals, w, label="Higgsfield", color=H_COLOR, alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels(list(metrics.keys()), color=TEXT, fontsize=9)
    ax.set_ylabel("Average value", color=MUTED)
    ax.set_title("Average Engagement Metrics by Platform", color=TEXT, fontweight="bold", fontsize=12)
    ax.legend(facecolor=PANEL, edgecolor=BORDER, labelcolor=TEXT, fontsize=9)
    for bars, vals in [(ax.containers[0], cl_vals), (ax.containers[1], hf_vals)]:
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(max(cl_vals), max(hf_vals)) * 0.01,
                    f"{v:.0f}", ha="center", fontsize=8, color=MUTED)
    _save(fig, "cmp_03_avg_engagement.png")


# ── 4. Top posts — score distribution (box plot) ─────────────────────────────
def chart_score_distribution():
    cl = load_claude()
    hf = load_higgsfield()

    fig, axes = plt.subplots(1, 3, figsize=(15, 6))
    _style(fig, axes)

    for ax, plat, ylabel in zip(axes,
                                 ["reddit",    "x",           "youtube"],
                                 ["Score",     "Views",       "Views"]):
        col = "likes" if plat == "reddit" else "views"
        cl_v = cl[(cl["platform"] == plat)][col].dropna()
        hf_v = hf[(hf["platform"] == plat)][col].dropna()

        # cap at 99th percentile for readability
        cap = max(cl_v.quantile(0.99), hf_v.quantile(0.99)) if len(cl_v) and len(hf_v) else 1

        bp = ax.boxplot([cl_v[cl_v <= cap], hf_v[hf_v <= cap]],
                        patch_artist=True, widths=0.4,
                        medianprops=dict(color="white", lw=2),
                        whiskerprops=dict(color=MUTED),
                        capprops=dict(color=MUTED),
                        flierprops=dict(marker="o", markersize=2, alpha=0.3, color=MUTED))

        bp["boxes"][0].set_facecolor(C_COLOR); bp["boxes"][0].set_alpha(0.7)
        if len(bp["boxes"]) > 1:
            bp["boxes"][1].set_facecolor(H_COLOR); bp["boxes"][1].set_alpha(0.7)

        ax.set_xticklabels(["Claude", "Higgsfield"], color=TEXT, fontsize=10)
        ax.set_title(plat.upper(), color=TEXT, fontweight="bold")
        ax.set_ylabel(ylabel, color=MUTED)

        # annotate median
        for i, data in enumerate([cl_v, hf_v]):
            if len(data):
                ax.text(i + 1, data.median() * 1.05, f"med={data.median():.0f}",
                        ha="center", fontsize=8, color=TEXT)

    fig.suptitle("Engagement Score Distribution (capped at 99th pct)\nWider box = more consistent performance",
                 color=TEXT, fontsize=12, fontweight="bold")
    _save(fig, "cmp_04_score_distribution.png")


# ── 5. Platform mix (pie) ─────────────────────────────────────────────────────
def chart_platform_mix():
    cl = load_claude()
    hf = load_higgsfield()

    plat_order = ["reddit", "x", "youtube", "hacker_news", "google_trends"]
    plat_labels = ["Reddit", "X", "YouTube", "Hacker News", "Google Trends"]
    colors_list = ["#e07b39", "#4a90d9", "#e74c3c", "#6aa84f", "#f39c12"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    _style(fig, [ax1, ax2])

    for ax, df, title in [(ax1, cl, "Claude"), (ax2, hf, "Higgsfield")]:
        counts = [len(df[df["platform"] == p]) for p in plat_order]
        total  = sum(counts)
        non_zero = [(c, l, col) for c, l, col in zip(counts, plat_labels, colors_list) if c > 0]
        vals, lbls, cols = zip(*non_zero)
        wedges, texts, autotexts = ax.pie(
            vals, labels=lbls, colors=cols,
            autopct=lambda p: f"{p:.1f}%" if p > 2 else "",
            startangle=90, textprops={"color": TEXT, "fontsize": 9},
        )
        for at in autotexts:
            at.set_color(TEXT); at.set_fontsize(8)
        ax.set_facecolor(BG)
        ax.set_title(f"{title}\n({total:,} total items)", color=TEXT, fontweight="bold", fontsize=11)

    fig.suptitle("Platform Mix: Where Each Brand's Content Lives", color=TEXT, fontsize=13, fontweight="bold")
    _save(fig, "cmp_05_platform_mix.png")


# ── 6. X: top amplifiers (non-official) side by side ─────────────────────────
def chart_top_amplifiers():
    cl = load_claude()
    hf = load_higgsfield()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    _style(fig, [ax1, ax2])

    for ax, df, brand, color in [
        (ax1, cl, "Claude",     C_COLOR),
        (ax2, hf, "Higgsfield", H_COLOR),
    ]:
        xdf = df[(df["platform"] == "x") & df["views"].notna()].copy()
        by_author = xdf.groupby("author").agg(
            total_views=("views", "sum"),
            tweet_count=("id",    "count"),
            avg_views=("views",   "mean"),
        ).sort_values("total_views", ascending=False).head(12)

        bars = ax.barh(by_author.index[::-1], by_author["total_views"][::-1] / 1e6,
                       color=color, alpha=0.8, height=0.6)
        for bar, (_, row) in zip(bars, by_author[::-1].iterrows()):
            ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
                    f" {row['tweet_count']} tweets  avg {row['avg_views']/1e6:.1f}M",
                    va="center", fontsize=7.5, color=MUTED)
        ax.set_xlabel("Total views (millions)", color=MUTED)
        ax.set_title(f"{brand} — Top X Amplifiers by Total Views", color=TEXT, fontweight="bold")
        ax.set_xlim(0, by_author["total_views"].max() / 1e6 * 1.5)
        ax.tick_params(axis="y", colors=TEXT, labelsize=8)

    fig.suptitle("Who Drives X Reach? Top Amplifiers Comparison", color=TEXT, fontsize=13, fontweight="bold")
    _save(fig, "cmp_06_top_amplifiers.png")


# ── 7. Official vs community split on X ──────────────────────────────────────
CLAUDE_OFFICIAL     = {"AnthropicAI", "DarioAmodei", "claudeai", "AmandaAskell", "alexalbert__", "ClaudeCodeLog"}
HIGGSFIELD_OFFICIAL = {"higgsfield", "HiggsfieldAI", "higgsfield_ai"}

def chart_official_vs_community():
    cl = load_claude()
    hf = load_higgsfield()

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    _style(fig, axes.flatten())

    for row_idx, (df, brand, official_set, color) in enumerate([
        (cl, "Claude",     CLAUDE_OFFICIAL,     C_COLOR),
        (hf, "Higgsfield", HIGGSFIELD_OFFICIAL, H_COLOR),
    ]):
        xdf = df[(df["platform"] == "x") & df["views"].notna()].copy()
        xdf["is_official"] = xdf["author"].isin(official_set)

        off_views = xdf[xdf["is_official"]]["views"].sum()
        com_views = xdf[~xdf["is_official"]]["views"].sum()
        off_likes = xdf[xdf["is_official"]]["likes"].sum()
        com_likes = xdf[~xdf["is_official"]]["likes"].sum()

        ax_v = axes[row_idx][0]
        ax_l = axes[row_idx][1]

        for ax, off, com, metric in [
            (ax_v, off_views, com_views, "Views"),
            (ax_l, off_likes, com_likes, "Likes"),
        ]:
            total = off + com
            if total == 0:
                continue
            ax.pie([off, com], labels=["Official", "Community"],
                   colors=[color, "#4b5563"],
                   autopct="%1.1f%%", startangle=90,
                   textprops={"color": TEXT, "fontsize": 9})
            ax.set_facecolor(BG)
            ax.set_title(f"{brand} — {metric} Share\n({total/1e6:.1f}M total)", color=TEXT, fontweight="bold", fontsize=10)

    fig.suptitle("Official Accounts vs. Community: Share of X Reach", color=TEXT, fontsize=13, fontweight="bold")
    _save(fig, "cmp_07_official_vs_community.png")


# ── 8. Content archetype comparison ──────────────────────────────────────────
ARCHETYPES = {
    "Controversy":       [r"\battack\b", r"\bstatement\b", r"\bwar\b", r"\bban\b", r"\brisks?\b", r"\bcontroversy\b"],
    "Personal Story":    [r"\bi (made|built|tried|used|got|created|tested)\b", r"\bmy (first|workflow|result)\b"],
    "Capability Demo":   [r"\b(watch|look|see) (what|how)\b", r"\bcan (now|do|generate|create)\b", r"\busing .{0,20}(ai|model)\b"],
    "Comparison":        [r"\bvs\.?\b", r"\bversus\b", r"\bcompare\b", r"\bbetter than\b", r"\bbeat\b"],
    "Tutorial / Guide":  [r"\bhow to\b", r"\btutorial\b", r"\bguide\b", r"\btips?\b", r"\bworkflow\b"],
    "Model Release":     [r"\bintroducing\b", r"\bnew .{0,20}(model|version|update)\b", r"\bjust (dropped|released|launched)\b"],
    "Humor / Meme":      [r"\blol\b", r"\bfunny\b", r"\bmeme\b", r"\blmao\b", r"\bpov\b"],
}

def _classify(title: str) -> str:
    t = str(title).lower()
    for arch, pats in ARCHETYPES.items():
        if any(re.search(p, t) for p in pats):
            return arch
    return "Other"

def chart_archetype_comparison():
    cl = load_claude()
    hf = load_higgsfield()

    cl_r = cl[(cl["platform"] == "reddit") & cl["post_title"].notna()].copy()
    hf_r = hf[(hf["platform"] == "reddit") & hf["post_title"].notna()].copy()

    cl_r["arch"] = cl_r["post_title"].apply(_classify)
    hf_r["arch"] = hf_r["post_title"].apply(_classify)

    archs = list(ARCHETYPES.keys()) + ["Other"]
    cl_pct = [(cl_r["arch"] == a).sum() / len(cl_r) * 100 for a in archs]
    hf_pct = [(hf_r["arch"] == a).sum() / len(hf_r) * 100 for a in archs]

    x = np.arange(len(archs))
    w = 0.35
    fig, ax = plt.subplots(figsize=(14, 6))
    _style(fig, [ax])
    ax.bar(x - w/2, cl_pct, w, label="Claude",     color=C_COLOR, alpha=0.85)
    ax.bar(x + w/2, hf_pct, w, label="Higgsfield", color=H_COLOR, alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels(archs, color=TEXT, fontsize=9, rotation=15, ha="right")
    ax.set_ylabel("% of Reddit posts", color=MUTED)
    ax.set_title("Reddit Content Archetype Mix: Claude vs. Higgsfield", color=TEXT, fontweight="bold", fontsize=12)
    ax.legend(facecolor=PANEL, edgecolor=BORDER, labelcolor=TEXT, fontsize=9)
    _save(fig, "cmp_08_archetype_mix.png")


# ── 9. Viral ceiling — top-N post scores ─────────────────────────────────────
def chart_viral_ceiling():
    cl = load_claude()
    hf = load_higgsfield()

    fig, axes = plt.subplots(1, 3, figsize=(16, 6))
    _style(fig, axes)

    configs = [
        ("reddit",  "likes",  "Reddit Score",   20),
        ("x",       "views",  "X Views",        15),
        ("youtube", "views",  "YouTube Views",  15),
    ]

    for ax, (plat, col, ylabel, topn) in zip(axes, configs):
        cl_top = cl[cl["platform"] == plat][col].dropna().nlargest(topn).values
        hf_top = hf[hf["platform"] == plat][col].dropna().nlargest(topn).values

        ranks = np.arange(1, topn + 1)
        ax.plot(ranks, cl_top[:topn] if len(cl_top) >= topn else np.pad(cl_top, (0, topn - len(cl_top))),
                "o-", color=C_COLOR, lw=2, ms=5, label="Claude")
        ax.plot(ranks, hf_top[:topn] if len(hf_top) >= topn else np.pad(hf_top, (0, topn - len(hf_top))),
                "s-", color=H_COLOR, lw=2, ms=5, label="Higgsfield")

        ax.set_xlabel(f"Rank (1 = top post)", color=MUTED)
        ax.set_ylabel(ylabel, color=MUTED)
        ax.set_title(plat.upper(), color=TEXT, fontweight="bold")
        ax.legend(facecolor=PANEL, edgecolor=BORDER, labelcolor=TEXT, fontsize=8)
        ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))

    fig.suptitle("Viral Ceiling: Top Posts Ranked — How High Does Each Brand's Best Content Go?",
                 color=TEXT, fontsize=12, fontweight="bold")
    _save(fig, "cmp_09_viral_ceiling.png")


# ── 10. Monthly X views timeline ─────────────────────────────────────────────
def chart_x_timeline():
    cl = load_claude()
    hf = load_higgsfield()

    cl_x = cl[(cl["platform"] == "x") & cl["views"].notna() & (cl["published_at"].dt.year >= 2024)].copy()
    hf_x = hf[(hf["platform"] == "x") & hf["views"].notna() & (hf["published_at"].dt.year >= 2024)].copy()

    cl_x["month"] = cl_x["published_at"].dt.to_period("M").dt.to_timestamp()
    hf_x["month"] = hf_x["published_at"].dt.to_period("M").dt.to_timestamp()

    cl_m = cl_x.groupby("month")["views"].sum().rename("Claude") / 1e6
    hf_m = hf_x.groupby("month")["views"].sum().rename("Higgsfield") / 1e6

    df = pd.concat([cl_m, hf_m], axis=1).fillna(0)

    fig, ax = plt.subplots(figsize=(14, 6))
    _style(fig, [ax])
    ax.fill_between(df.index, df.get("Claude", 0),     alpha=0.5, color=C_COLOR, label="Claude")
    ax.fill_between(df.index, df.get("Higgsfield", 0), alpha=0.5, color=H_COLOR, label="Higgsfield")
    ax.plot(df.index, df.get("Claude", 0),     color=C_COLOR, lw=2)
    ax.plot(df.index, df.get("Higgsfield", 0), color=H_COLOR, lw=2)
    ax.set_ylabel("Total X views (millions)", color=MUTED)
    ax.set_title("Monthly X Views: Claude vs. Higgsfield", color=TEXT, fontweight="bold", fontsize=12)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.xticks(rotation=25, ha="right", color=MUTED)
    ax.legend(facecolor=PANEL, edgecolor=BORDER, labelcolor=TEXT, fontsize=10)
    _save(fig, "cmp_10_x_views_timeline.png")


# ── 11. YouTube: views vs likes scatter ──────────────────────────────────────
def chart_youtube_scatter():
    cl = load_claude()
    hf = load_higgsfield()

    fig, ax = plt.subplots(figsize=(12, 7))
    _style(fig, [ax])

    for df, brand, color in [(cl, "Claude", C_COLOR), (hf, "Higgsfield", H_COLOR)]:
        yt = df[(df["platform"] == "youtube") & df["views"].notna() & df["likes"].notna()]
        ax.scatter(yt["views"] / 1e3, yt["likes"] / 1e3,
                   alpha=0.45, s=30, color=color, label=brand)

    ax.set_xlabel("Views (thousands)", color=MUTED)
    ax.set_ylabel("Likes (thousands)", color=MUTED)
    ax.set_title("YouTube: Views vs. Likes\n(each dot = one video)", color=TEXT, fontweight="bold", fontsize=12)
    ax.legend(facecolor=PANEL, edgecolor=BORDER, labelcolor=TEXT, fontsize=10)
    _save(fig, "cmp_11_youtube_scatter.png")


# ── 12. Word cloud side by side ───────────────────────────────────────────────
def chart_wordclouds():
    if not HAS_WC:
        print("wordcloud not installed, skipping cmp_12")
        return

    cl = load_claude()
    hf = load_higgsfield()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))
    fig.patch.set_facecolor(BG)

    for ax, df, brand, color in [
        (ax1, cl, "Claude",     C_COLOR),
        (ax2, hf, "Higgsfield", H_COLOR),
    ]:
        top = df[df["post_title"].notna()].nlargest(min(500, len(df)), "likes")
        text = " ".join(str(t) for t in top["post_title"])
        text = re.sub(r"http\S+", "", text)
        text = re.sub(r"[^\w\s]", " ", text)
        words = [w for w in text.lower().split() if w not in STOPWORDS and len(w) > 2]
        # remove brand name itself
        words = [w for w in words if w not in {brand.lower(), "claude", "higgsfield", "anthropic"}]
        wc = WordCloud(width=800, height=400, background_color="#0e0e18",
                       colormap="Oranges" if brand == "Claude" else "Purples",
                       max_words=80, collocations=False).generate(" ".join(words))
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        ax.set_facecolor(PANEL)
        ax.set_title(f"{brand} — Top Content Keywords\n(from top-500 posts by score)",
                     color=TEXT, fontweight="bold", fontsize=11, pad=10)

    fig.suptitle("What Do People Talk About? Word Cloud Comparison", color=TEXT, fontsize=13, fontweight="bold")
    _save(fig, "cmp_12_wordclouds.png")


# ── 13. Engagement rate comparison (per platform) ────────────────────────────
def chart_engagement_rate():
    cl = load_claude()
    hf = load_higgsfield()

    rows = []
    for df, brand in [(cl, "Claude"), (hf, "Higgsfield")]:
        for plat in ["x", "youtube"]:
            sub = df[(df["platform"] == plat) & df["views"].notna() & (df["views"] > 0)].copy()
            sub["eng_rate"] = (sub["likes"].fillna(0) + sub["reposts"].fillna(0) + sub["comments"].fillna(0)) / sub["views"]
            rows.append({"brand": brand, "platform": plat.upper(), "eng_rate": sub["eng_rate"].mean() * 100})

    res = pd.DataFrame(rows)
    fig, ax = plt.subplots(figsize=(10, 6))
    _style(fig, [ax])

    platforms = res["platform"].unique()
    x = np.arange(len(platforms))
    w = 0.35
    for i, (brand, color) in enumerate([("Claude", C_COLOR), ("Higgsfield", H_COLOR)]):
        vals = [res[(res["brand"] == brand) & (res["platform"] == p)]["eng_rate"].values[0]
                if len(res[(res["brand"] == brand) & (res["platform"] == p)]) else 0
                for p in platforms]
        bars = ax.bar(x + i * w - w/2, vals, w, label=brand, color=color, alpha=0.85)
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                    f"{v:.2f}%", ha="center", fontsize=9, color=MUTED)

    ax.set_xticks(x)
    ax.set_xticklabels(platforms, color=TEXT, fontsize=11)
    ax.set_ylabel("Avg engagement rate\n(likes+reposts+comments / views) %", color=MUTED)
    ax.set_title("Engagement Rate: How Much of the Audience Actively Engages?", color=TEXT, fontweight="bold", fontsize=12)
    ax.legend(facecolor=PANEL, edgecolor=BORDER, labelcolor=TEXT, fontsize=10)
    _save(fig, "cmp_13_engagement_rate.png")


# ── 14. Top Reddit posts side by side table ───────────────────────────────────
def chart_top_posts_table():
    cl = load_claude()
    hf = load_higgsfield()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
    fig.patch.set_facecolor(BG)

    for ax, df, brand, header_color in [
        (ax1, cl, "Claude",     C_COLOR),
        (ax2, hf, "Higgsfield", H_COLOR),
    ]:
        ax.set_facecolor(PANEL)
        ax.axis("off")
        top = df[(df["platform"] == "reddit") & df["post_title"].notna()].nlargest(10, "likes")
        data = [[str(row["post_title"])[:70] + ("…" if len(str(row["post_title"])) > 70 else ""),
                 f"{int(row['likes'] or 0):,}",
                 str(row["published_at"])[:10] if pd.notna(row["published_at"]) else ""]
                for _, row in top.iterrows()]
        col_labels = ["Title", "Score", "Date"]
        table = ax.table(cellText=data, colLabels=col_labels, loc="center", cellLoc="left")
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 1.7)
        for j in range(len(col_labels)):
            table[0, j].set_facecolor(header_color)
            table[0, j].set_text_props(color="white", fontweight="bold")
        for i in range(1, len(data) + 1):
            for j in range(len(col_labels)):
                table[i, j].set_facecolor("#12121e")
                table[i, j].set_text_props(color="#c4c4d0")
        ax.set_title(f"{brand} — Top 10 Reddit Posts", color=TEXT, fontweight="bold", fontsize=11, pad=15)

    fig.suptitle("Top Reddit Posts: Claude vs. Higgsfield", color=TEXT, fontsize=13, fontweight="bold")
    _save(fig, "cmp_14_top_posts_table.png")


# ── 15. Reddit subreddit breakdown ────────────────────────────────────────────
def chart_subreddit_breakdown():
    cl = load_claude()
    hf = load_higgsfield()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    _style(fig, [ax1, ax2])

    for ax, df, brand, color in [
        (ax1, cl, "Claude",     C_COLOR),
        (ax2, hf, "Higgsfield", H_COLOR),
    ]:
        r = df[df["platform"] == "reddit"].copy()
        sub_col = "hashtags" if "hashtags" in r.columns else "subreddit"
        counts = r[sub_col].value_counts().head(10)
        bars = ax.barh(counts.index[::-1], counts.values[::-1], color=color, alpha=0.8, height=0.6)
        for bar, v in zip(bars, counts.values[::-1]):
            ax.text(bar.get_width() + counts.max() * 0.01, bar.get_y() + bar.get_height()/2,
                    f" {v:,}", va="center", fontsize=8.5, color=MUTED)
        ax.set_title(f"{brand} — Top Subreddits / Communities", color=TEXT, fontweight="bold")
        ax.set_xlabel("Posts", color=MUTED)
        ax.tick_params(axis="y", colors=TEXT, labelsize=8)
        ax.set_xlim(0, counts.max() * 1.25)

    fig.suptitle("Where Does Each Brand's Community Live on Reddit?", color=TEXT, fontsize=13, fontweight="bold")
    _save(fig, "cmp_15_subreddit_breakdown.png")


# ── runner ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))

    print("=== Claude vs. Higgsfield Comparison Charts ===")
    chart_community_scale()
    chart_reddit_growth()
    chart_avg_engagement()
    chart_score_distribution()
    chart_platform_mix()
    chart_top_amplifiers()
    chart_official_vs_community()
    chart_archetype_comparison()
    chart_viral_ceiling()
    chart_x_timeline()
    chart_youtube_scatter()
    chart_wordclouds()
    chart_engagement_rate()
    chart_top_posts_table()
    chart_subreddit_breakdown()
    print("\nAll comparison charts done.")
