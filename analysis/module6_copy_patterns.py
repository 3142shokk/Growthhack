"""
Module 6 — Title & Copy Pattern Analysis
Charts:
  - Opening word frequency for top vs. bottom posts
  - Title length vs. score scatter
  - Emotional trigger word presence in viral vs. non-viral posts
  - Word cloud of top post titles
  - HN comment sentiment themes (top stories)
"""
from __future__ import annotations
import warnings
warnings.filterwarnings("ignore")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import re
from collections import Counter
from data_loader import load_reddit, load_hn, load_x, load_hn_comments, load_reddit_comments, CHARTS

try:
    from wordcloud import WordCloud
    HAS_WORDCLOUD = True
except ImportError:
    HAS_WORDCLOUD = False

STOPWORDS = {
    "the","a","an","and","or","but","in","on","at","to","for","of","with",
    "is","it","its","this","that","my","i","you","we","he","she","they",
    "be","been","have","has","had","do","does","did","will","would","can",
    "could","should","from","by","as","are","was","were","so","if","not",
    "no","what","when","how","why","which","who","up","out","about","just",
    "more","than","like","get","got","all","any","one","new","s","t",
    "after","before","into","over","also","here","there","some","now"
}

EMOTIONAL_TRIGGERS = {
    "Curiosity":    ["secret", "leaked", "hidden", "nobody", "no one", "found out", "revealed",
                     "discovered", "insider", "how i", "dug through", "unhinged"],
    "Amazement":    ["incredible", "insane", "unbelievable", "mind", "blew", "wild",
                     "shocked", "amazing", "absolutely", "wow"],
    "Pride/Social": ["#1", "overtook", "beats", "top", "best in the world", "world's best",
                     "first ever", "milestone", "record"],
    "Outrage/Fear": ["attack", "distillation", "war", "banned", "supply chain",
                     "risk", "danger", "threat", "exposed", "steal"],
    "Relatability": ["we've all", "every", "anyone else", "am i the only",
                     "this is me", "can we talk about", "pov"],
    "BREAKING":     ["breaking", "just announced", "just released", "just dropped"],
}


def _trigger_score(title: str) -> dict:
    t = str(title).lower()
    return {cat: int(any(w in t for w in words)) for cat, words in EMOTIONAL_TRIGGERS.items()}


# ── Chart 1: Emotional triggers in viral vs. baseline posts ──────────────────
def chart_emotional_triggers():
    reddit = load_reddit()
    reddit = reddit[reddit["likes"].notna()].copy()

    threshold = reddit["likes"].quantile(0.90)
    viral    = reddit[reddit["likes"] >= threshold]
    baseline = reddit[reddit["likes"] <  threshold]

    v_scores = pd.DataFrame([_trigger_score(t) for t in viral["post_title"]]).mean()
    b_scores = pd.DataFrame([_trigger_score(t) for t in baseline["post_title"]]).mean()

    x = np.arange(len(v_scores))
    width = 0.35

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(x - width/2, v_scores.values * 100, width, label=f"Top 10% viral (n={len(viral):,})",
           color="#e74c3c", alpha=0.8)
    ax.bar(x + width/2, b_scores.values * 100, width, label=f"Remaining 90% (n={len(baseline):,})",
           color="#95a5a6", alpha=0.8)

    ax.set_xticks(x)
    ax.set_xticklabels(v_scores.index, fontsize=10)
    ax.set_ylabel("% of posts containing trigger", fontsize=10)
    ax.set_title("Emotional Triggers: Viral Posts vs. Baseline (Reddit)\n(% of posts in each group containing the trigger)",
                 fontsize=11, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(axis="y", alpha=0.3)

    # lift labels
    for xi, (v, b) in enumerate(zip(v_scores.values, b_scores.values)):
        if b > 0:
            lift = v / b
            ax.text(xi - width/2, v * 100 + 0.3, f"{lift:.1f}×", ha="center", fontsize=8.5, color="#c0392b")

    plt.tight_layout()
    out = CHARTS / "6a_emotional_triggers.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out}")


# ── Chart 2: Title length vs. score ──────────────────────────────────────────
def chart_title_length():
    reddit = load_reddit()
    reddit = reddit[reddit["likes"].notna() & (reddit["likes"] > 0)].copy()
    reddit["title_len"] = reddit["post_title"].str.len()

    # bin by title length
    bins = [0, 30, 50, 70, 90, 110, 130, 200]
    labels = ["<30", "30-50", "50-70", "70-90", "90-110", "110-130", ">130"]
    reddit["len_bin"] = pd.cut(reddit["title_len"], bins=bins, labels=labels)

    stats = reddit.groupby("len_bin", observed=True).agg(
        avg_score=("likes", "mean"),
        count=("id", "count"),
    )

    fig, ax1 = plt.subplots(figsize=(11, 5))
    ax2 = ax1.twinx()

    colors = plt.cm.RdYlGn(np.linspace(0.2, 0.9, len(stats)))
    bars = ax1.bar(stats.index, stats["avg_score"], color=colors, alpha=0.8)
    ax2.plot(stats.index, stats["count"], "o--", color="#2c3e50", lw=2, ms=8)

    ax1.set_xlabel("Title Character Length", fontsize=11)
    ax1.set_ylabel("Avg Score", color="green", fontsize=10)
    ax2.set_ylabel("Post Count", color="#2c3e50", fontsize=10)
    ax1.set_title("Reddit: Title Length vs. Average Score\n(sweet spot around 70-130 chars)",
                  fontsize=11, fontweight="bold")
    ax1.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    out = CHARTS / "6b_title_length_vs_score.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out}")


# ── Chart 3: Opening word analysis ───────────────────────────────────────────
def chart_opening_words():
    reddit = load_reddit()
    reddit = reddit[reddit["likes"].notna()].copy()
    reddit["first_word"] = reddit["post_title"].str.lower().str.split().str[0].str.strip(".,!?\"'")

    viral    = reddit[reddit["likes"] >= reddit["likes"].quantile(0.90)]
    baseline = reddit[reddit["likes"] <  reddit["likes"].quantile(0.90)]

    v_words  = Counter(viral["first_word"].dropna()).most_common(20)
    b_words  = Counter(baseline["first_word"].dropna()).most_common(20)

    v_dict = dict(v_words)
    b_dict = dict(b_words)
    all_words = list({w for w, _ in v_words} | {w for w, _ in b_words})

    # compute lift: viral_share / baseline_share
    v_total = len(viral)
    b_total = len(baseline)
    lifts = {}
    for w in all_words:
        v_share = v_dict.get(w, 0) / v_total
        b_share = b_dict.get(w, 1) / b_total  # avoid div0
        lifts[w] = v_share / b_share if b_share > 0 else 0

    # top 15 by lift (with minimum 5 viral uses)
    top_lifts = {w: l for w, l in lifts.items() if v_dict.get(w, 0) >= 5}
    top_lifts = sorted(top_lifts.items(), key=lambda x: x[1], reverse=True)[:15]

    words  = [w for w, _ in top_lifts]
    values = [l for _, l in top_lifts]

    fig, ax = plt.subplots(figsize=(11, 7))
    colors = ["#e74c3c" if v > 1.5 else "#3498db" for v in values]
    bars = ax.barh(words[::-1], values[::-1], color=colors[::-1], alpha=0.8)
    ax.axvline(1.0, color="grey", ls="--", alpha=0.6, label="No lift (=1.0)")
    ax.set_xlabel("Lift (viral rate / baseline rate)", fontsize=11)
    ax.set_title("Opening Words with Highest Viral Lift (Reddit)\n(lift > 1 = appears more often in top-10% posts)",
                 fontsize=11, fontweight="bold")
    ax.legend(fontsize=9)
    ax.grid(axis="x", alpha=0.3)
    for bar, val in zip(bars, values[::-1]):
        ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2,
                f" {val:.2f}×", va="center", fontsize=9)
    plt.tight_layout()
    out = CHARTS / "6c_opening_word_lift.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out}")


# ── Chart 4: Word cloud of top post titles ────────────────────────────────────
def chart_wordcloud():
    if not HAS_WORDCLOUD:
        print("wordcloud not installed, skipping chart 6d")
        return

    reddit = load_reddit()
    top    = reddit.nlargest(500, "likes")

    text = " ".join(str(t) for t in top["post_title"].dropna())
    # clean
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^\w\s]", " ", text)
    words = [w for w in text.lower().split() if w not in STOPWORDS and len(w) > 2]
    clean_text = " ".join(words)

    wc = WordCloud(width=1400, height=700, background_color="white",
                   colormap="RdYlGn", max_words=120,
                   collocations=False).generate(clean_text)

    fig, ax = plt.subplots(figsize=(16, 8))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    ax.set_title("Word Cloud: Top 500 Reddit Posts by Score\n(most frequent meaningful words)", fontsize=13, fontweight="bold")
    plt.tight_layout()
    out = CHARTS / "6d_top_posts_wordcloud.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out}")


# ── Chart 5: HN comment themes for top stories ───────────────────────────────
def chart_hn_comment_themes():
    hn_comments = load_hn_comments()
    hn_stories  = load_hn()

    # join to get story title
    hn_stories["story_id"] = hn_stories["id"].str.replace("hn_story_", "")
    merged = hn_comments.merge(
        hn_stories[["story_id", "post_title", "likes"]],
        on="story_id", how="left"
    )
    # top 10 stories by points
    top_story_ids = hn_stories.nlargest(10, "likes")["story_id"].tolist()
    merged = merged[merged["story_id"].isin(top_story_ids)]

    # word frequency in post_title (comments) — use post_title as comment content
    text = " ".join(str(t) for t in merged["post_title_x"].dropna())
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"\[comment on\]", "", text)
    text = re.sub(r"[^\w\s]", " ", text)
    words = [w for w in text.lower().split() if w not in STOPWORDS and len(w) > 3]
    freq  = Counter(words).most_common(30)

    words_list  = [w for w, _ in freq]
    counts_list = [c for _, c in freq]

    fig, ax = plt.subplots(figsize=(13, 7))
    colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(words_list)))
    ax.barh(words_list[::-1], counts_list[::-1], color=colors[::-1], edgecolor="white")
    ax.set_xlabel("Frequency in HN comments on top-10 stories", fontsize=11)
    ax.set_title("HN Comment Themes: What Do People Talk About Under Top Claude Stories?\n(top-10 viral stories by HN points)",
                 fontsize=11, fontweight="bold")
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    out = CHARTS / "6e_hn_comment_themes.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out}")


if __name__ == "__main__":
    print("=== Module 6: Copy Pattern Analysis ===")
    chart_emotional_triggers()
    chart_title_length()
    chart_opening_words()
    chart_wordcloud()
    chart_hn_comment_themes()
    print("Done.")
