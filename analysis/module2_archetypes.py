"""
Module 2 — Content Archetype Taxonomy
Charts:
  - Bar chart: avg engagement per archetype per platform
  - Heatmap: archetype × platform engagement matrix
  - Horizontal bar: top viral templates ranked
"""
from __future__ import annotations
import warnings
warnings.filterwarnings("ignore")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import pandas as pd
import numpy as np
import re
from data_loader import load_reddit, load_hn, load_x, CHARTS

# ── Archetype classifier ───────────────────────────────────────────────────────
ARCHETYPES = {
    "Controversy / Stance": [
        r"\bdow\b", r"\bhegseth\b", r"\bdeepseek\b", r"\bdistillation\b",
        r"\bcontroversy\b", r"\bstatement\b", r"\bresponse to\b",
        r"\banthropics? (ceo|stand|stance)\b", r"\bwar\b.*\banthrop",
        r"supply.chain risk", r"\bpolitical\b", r"\bripped?\b.*\banthrop"
    ],
    "Personal Breakthrough": [
        r"\b(i|my|me)\b.{0,40}\b(solved|fixed|cracked|built|made|got|helped|found)\b",
        r"\b(years?|months?|weeks?).{0,30}\b(finally|solved|cracked|no answer)\b",
        r"(medical|doctor|specialist|diagnosis)",
        r"nobody had solved", r"reprogrammed", r"reverse engin",
        r"(changed|saves?) my (life|career|business)"
    ],
    "Insider Leak / Reveal": [
        r"\bleak(ed)?\b", r"\bsource code\b", r"\bexposed?\b",
        r"\binternal\b.*\b(doc|code|data)\b", r"\bnpm\b.*\bmap file\b",
        r"\bdug through\b", r"\bdiscovered?\b.*\bhidden\b",
        r"codebase is (absolutely|completely|totally)"
    ],
    "Third-Party Validation": [
        r"\bceo\b.*\buse[sd]?\b", r"\bsays?\b.{0,30}\b(best|top|prefer|choose|switch)\b",
        r"\b(apple|google|meta|microsoft|nvidia|openai)\b.*\bclaud",
        r"\b(researcher|professor|scientist|expert)\b",
        r"\bkarpathy\b", r"\banda[rm]\b", r"\beveryone (is|should|should be)\b"
    ],
    "Capability Demo": [
        r"\bgave (claude|it) access\b", r"\bclaude (can|could|did|does|built|wrote|solved)\b",
        r"\b(autonomous|agentic|agent)\b.*\bclaud",
        r"\bclaud.{0,20}(macbook|computer|terminal|system)",
        r"\bbuilt.{0,30}(in|with|using) claude\b",
        r"\bclaude code\b.{0,50}(built|solved|wrote|created)"
    ],
    "Comparison / Competition": [
        r"\bvs\.?\b", r"\bversus\b", r"\b(better|worse|beats?|outperforms?)\b.{0,30}\b(gpt|chatgpt|gemini|copilot|llama|mistral|deepseek|grok)\b",
        r"\b(gpt|chatgpt|gemini|copilot)\b.{0,30}\b(better|worse|vs)\b",
        r"\bapp store\b.{0,30}(#?1|top|overtook|number one)",
        r"\bswitched? (from|to)\b"
    ],
    "Model Release": [
        r"\bclaude (opus|sonnet|haiku|3\.5|3\.7|4|code)\b.{0,30}(launch|release|introduc|announc|new|out now)",
        r"\bintroducing claude\b", r"\bnew claude\b",
        r"\bclaude (3\.5|3\.7|4\.0|opus 4|sonnet 4|haiku 3)\b",
        r"\banthropics? new model\b"
    ],
    "Humor / Meme": [
        r"\bmeme\b", r"\blol\b", r"\blmao\b", r"\bfunny\b", r"\bjoke\b",
        r"\brelatable\b", r"\b(caught|watching) (me|you|him|her|them)\b",
        r"\bbrother\b$", r"🤣|😂|💀", r"\bpov\b",
        r"\bblursed\b", r"\bslay\b"
    ],
    "Tips / Prompts / Guides": [
        r"\b(tip|trick|prompt|hack|guide|tutorial|how to|howto)\b",
        r"\b(best|top) (prompt|way|method|technique)\b",
        r"\b(use|try) (this|these) prompt\b",
        r"\bsystem prompt\b", r"\bprompt engineering\b",
        r"\bworkflow\b.{0,30}(claude|ai)", r"\bcheat sheet\b"
    ],
}

def classify(title: str) -> str:
    t = str(title).lower()
    for archetype, patterns in ARCHETYPES.items():
        if any(re.search(p, t) for p in patterns):
            return archetype
    return "Other"


# ── Chart 1: Avg engagement per archetype (Reddit) ───────────────────────────
def chart_reddit_archetypes():
    reddit = load_reddit()
    reddit["archetype"] = reddit["post_title"].apply(classify)

    stats = reddit.groupby("archetype").agg(
        count=("id", "count"),
        avg_score=("likes", "mean"),
        total_score=("likes", "sum"),
    ).sort_values("avg_score", ascending=True)

    fig, ax = plt.subplots(figsize=(12, 8))
    colors = cm.RdYlGn(np.linspace(0.2, 0.9, len(stats)))
    bars = ax.barh(stats.index, stats["avg_score"], color=colors, edgecolor="white", height=0.6)

    for bar, (idx, row) in zip(bars, stats.iterrows()):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                f"  n={row['count']:,}  avg={row['avg_score']:.0f}",
                va="center", fontsize=9)

    ax.set_xlabel("Average Reddit Score", fontsize=11)
    ax.set_title("Reddit: Average Score by Content Archetype\n(higher = more viral per post)", fontsize=12, fontweight="bold")
    ax.grid(axis="x", alpha=0.3)
    ax.set_xlim(0, stats["avg_score"].max() * 1.3)
    plt.tight_layout()
    out = CHARTS / "2a_reddit_archetype_avg_score.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out}")


# ── Chart 2: Archetype breakdown across all platforms ────────────────────────
def chart_cross_platform_archetypes():
    reddit = load_reddit()
    hn     = load_hn()
    x      = load_x()

    reddit["archetype"] = reddit["post_title"].apply(classify)
    hn["archetype"]     = hn["post_title"].apply(classify)
    x["archetype"]      = x["post_title"].apply(classify)

    reddit_stats = reddit.groupby("archetype")["likes"].mean().rename("Reddit avg score")
    hn_stats     = hn.groupby("archetype")["likes"].mean().rename("HN avg points")
    x_stats      = x.groupby("archetype")["views"].mean().div(1000).rename("X avg views (k)")

    matrix = pd.concat([reddit_stats, hn_stats, x_stats], axis=1).fillna(0)
    # normalize each column to 0–100 for comparability
    norm = matrix.copy()
    for col in norm.columns:
        mx = norm[col].max()
        if mx > 0:
            norm[col] = norm[col] / mx * 100

    fig, ax = plt.subplots(figsize=(12, 8))
    im = ax.imshow(norm.values, cmap="YlOrRd", aspect="auto")

    ax.set_xticks(range(len(norm.columns)))
    ax.set_xticklabels(norm.columns, fontsize=10)
    ax.set_yticks(range(len(norm.index)))
    ax.set_yticklabels(norm.index, fontsize=10)

    for i in range(len(norm.index)):
        for j in range(len(norm.columns)):
            raw_val = matrix.iloc[i, j]
            ax.text(j, i, f"{raw_val:.0f}", ha="center", va="center",
                    fontsize=8.5, color="black" if norm.iloc[i, j] < 70 else "white")

    plt.colorbar(im, ax=ax, label="Normalised score (0–100 within platform)")
    ax.set_title("Content Archetype Performance Across Platforms\n(raw values shown; colour = relative rank within platform)",
                 fontsize=11, fontweight="bold")
    plt.tight_layout()
    out = CHARTS / "2b_archetype_cross_platform_heatmap.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out}")


# ── Chart 3: Top 5 examples per archetype ────────────────────────────────────
def print_archetype_examples():
    reddit = load_reddit()
    reddit["archetype"] = reddit["post_title"].apply(classify)

    print("\n=== TOP EXAMPLES PER ARCHETYPE (Reddit) ===")
    for arch in sorted(ARCHETYPES.keys()):
        subset = reddit[reddit["archetype"] == arch].nlargest(3, "likes")
        print(f"\n-- {arch} --")
        for _, row in subset.iterrows():
            print(f"  score={int(row['likes'] or 0):,}  {str(row['post_title'])[:110]}")


# ── Chart 4: Archetype volume vs. avg score scatter ──────────────────────────
def chart_archetype_scatter():
    reddit = load_reddit()
    reddit["archetype"] = reddit["post_title"].apply(classify)

    stats = reddit.groupby("archetype").agg(
        count=("id", "count"),
        avg_score=("likes", "mean"),
    )

    fig, ax = plt.subplots(figsize=(11, 7))
    scatter = ax.scatter(stats["count"], stats["avg_score"],
                         s=stats["avg_score"] * 3, alpha=0.7,
                         c=range(len(stats)), cmap="tab10")

    for arch, row in stats.iterrows():
        ax.annotate(arch, (row["count"], row["avg_score"]),
                    xytext=(6, 4), textcoords="offset points", fontsize=8.5)

    ax.set_xlabel("Number of Posts (volume)", fontsize=11)
    ax.set_ylabel("Average Score (virality per post)", fontsize=11)
    ax.set_title("Content Archetype: Volume vs. Virality\n(bubble size = avg score)", fontsize=12, fontweight="bold")
    ax.grid(alpha=0.3)
    plt.tight_layout()
    out = CHARTS / "2c_archetype_volume_vs_virality.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out}")


if __name__ == "__main__":
    print("=== Module 2: Content Archetype Taxonomy ===")
    chart_reddit_archetypes()
    chart_cross_platform_archetypes()
    chart_archetype_scatter()
    print_archetype_examples()
    print("Done.")
