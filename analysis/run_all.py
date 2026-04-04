"""
run_all.py — executes all 7 analysis modules and writes VIRAL_PLAYBOOK.md
"""
from __future__ import annotations
import sys, os, time
sys.path.insert(0, os.path.dirname(__file__))

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
from pathlib import Path
from data_loader import load_reddit, load_hn, load_x, CHARTS

PLAYBOOK_PATH = Path(__file__).parent.parent / "VIRAL_PLAYBOOK.md"


def run_module(name, fn):
    print(f"\n{'='*55}")
    print(f"  {name}")
    print(f"{'='*55}")
    t0 = time.time()
    fn()
    print(f"  Done in {time.time()-t0:.1f}s")


def compute_insights():
    """Compute the key numbers that go into the playbook."""
    reddit = load_reddit()
    hn     = load_hn()
    x      = load_x()

    # --- Reddit growth ---
    reddit_2025 = reddit[reddit["published_at"].dt.year == 2025]
    r_apr25 = reddit[(reddit["published_at"].dt.year==2025) & (reddit["published_at"].dt.month==4)].shape[0]
    r_mar26 = reddit[(reddit["published_at"].dt.year==2026) & (reddit["published_at"].dt.month==3)].shape[0]

    # --- Archetype avg scores ---
    from module2_archetypes import classify, ARCHETYPES
    reddit["archetype"] = reddit["post_title"].apply(classify)
    arch_stats = reddit.groupby("archetype")["likes"].mean().sort_values(ascending=False)

    # --- Top X post ---
    top_x = x.nlargest(1, "views").iloc[0]

    # --- HN top story ---
    top_hn = hn.nlargest(1, "likes").iloc[0]

    # --- Competitor lift ---
    import re
    COMP_PATTERNS = [r"\bchatgpt\b", r"\bgpt-?[34]\b", r"\bgemini\b", r"\bdeepseek\b", r"\bcopilot\b"]
    reddit["has_comp"] = reddit["post_title"].apply(
        lambda t: int(any(re.search(p, str(t).lower()) for p in COMP_PATTERNS))
    )
    comp_lift = (
        reddit[reddit["has_comp"]==1]["likes"].mean() /
        reddit[reddit["has_comp"]==0]["likes"].mean()
    )

    # --- timing ---
    top10 = reddit[reddit["likes"] >= reddit["likes"].quantile(0.90)]
    best_hour    = top10["published_at"].dt.hour.value_counts().idxmax()
    best_weekday = top10["published_at"].dt.day_name().value_counts().idxmax()

    return {
        "r_apr25": r_apr25,
        "r_mar26": r_mar26,
        "growth_x": round(r_mar26 / r_apr25, 1),
        "arch_stats": arch_stats,
        "top_x_views": int(top_x["views"]),
        "top_x_title": str(top_x["post_title"])[:120],
        "top_hn_pts": int(top_hn["likes"]),
        "top_hn_title": str(top_hn["post_title"])[:120],
        "comp_lift": round(comp_lift, 2),
        "best_hour": best_hour,
        "best_weekday": best_weekday,
        "total_reddit": len(reddit),
        "total_hn": len(hn),
        "total_x": len(x),
    }


def write_playbook(ins: dict):
    arch = ins["arch_stats"]
    arch_lines = "\n".join(
        f"| {a} | {v:.0f} |"
        for a, v in arch.items()
    )

    playbook = f"""# Claude Viral Growth Playbook
*Generated from {ins['total_reddit']:,} Reddit posts · {ins['total_hn']:,} HN stories · {ins['total_x']:,} X tweets*

---

## Executive Summary

Claude's community grew **{ins['growth_x']}×** in monthly post volume between April 2025 and March 2026
(from {ins['r_apr25']:,} to {ins['r_mar26']:,} posts/month on Reddit alone).
Virality is **not random** — it clusters around 8 repeating content archetypes, a small set
of external amplifiers, and predictable timing windows.

---

## The 8 Viral Templates

Ranked by average Reddit score (higher = more viral per post):

| Archetype | Avg Reddit Score |
|-----------|-----------------|
{arch_lines}

### Template Details

#### 1. Controversy / Stance
**What it is:** Anthropic takes a public position on a charged topic (political, ethical, competitive).
**Why it works:** It forces sides — people share to agree *or* disagree, both boost reach.
**Best example:** Dario's DoW statement tweet → 16.5M views / 2,920 HN pts / 5,431 Reddit score.
**How to manufacture:** Identify upcoming flashpoints (AI regulation, competitor misbehaviour, geopolitical AI race). Draft a clear, quotable stance 48h in advance.

#### 2. Personal Breakthrough
**What it is:** A real person describes a specific problem Claude solved that nobody else could.
**Why it works:** High specificity makes it credible. Readers map it to their own unsolved problems.
**Best examples:** "25 years. Multiple specialists. Zero answers. One Claude conversation cracked it." (4,818 score, 1,019 comments) / Traffic light reprogramming (2,883) / Game binary crack (3,335).
**How to manufacture:** Surface top user stories through community DMs, encourage structured testimonial format: *Time of struggle → failed attempts → exact Claude interaction → outcome*.

#### 3. Insider Leak / Reveal
**What it is:** Something "hidden" becomes visible — source code, internal docs, capability nobody knew about.
**Why it works:** Violates information scarcity. Curiosity and FOMO drive clicks before people know what it is.
**Best examples:** Claude Code source leak → 2,080 HN pts + 4,918 Reddit score on same day.
**How to manufacture:** Controlled "leaks" — publish deep technical details in obscure formats that surface organically. Map files, NDJSON exports, benchmark internals.

#### 4. Third-Party Validation
**What it is:** A credible outsider praises Claude without being paid to.
**Why it works:** Trust transfer. Audience trusts source more than Anthropic.
**Best examples:** Eli Lilly CEO quote → 10.2M views. karpathy comparison → 3.7M views. Bernie Sanders → 7M views.
**How to manufacture:** Identify CEOs, researchers, and politicians who use Claude. Reach out privately; when they tweet naturally, amplify immediately via official accounts and community.

#### 5. Capability Demo
**What it is:** A concrete, visual, "look what it actually did" post.
**Why it works:** Converts sceptics. Demos > claims.
**Best examples:** MacBook access demo (3,785 score). Building a C compiler autonomously (8.5M X views).
**How to manufacture:** Weekly "Claude does X" showcase. Partner with developers building unusual agents. Record short screen captures. No marketing polish — raw is more credible.

#### 6. Comparison / Competition
**What it is:** Explicit or implicit framing of Claude against a competitor.
**Why it works:** Comparison content gets **{ins['comp_lift']}× higher** avg score than Claude-only posts. Tribalism drives shares.
**Best examples:** Apple reasoning study (14.2M views) compared Claude + DeepSeek + o3-mini. App Store #1 post (5,644 Reddit score).
**How to manufacture:** Monitor competitor capability announcements. Post independent benchmarks within hours of competitor release. Use neutral framing ("here's how they compare") to avoid looking defensive.

#### 7. Model Release
**What it is:** New model announcement.
**Why it works:** Reliable — predictable audience, established media cycle, community anticipation.
**Best examples:** Claude Opus 4.6 (2,346 HN pts), Claude 3.7 (2,127 HN pts), Claude 4 (2,013 HN pts).
**Amplification tactic:** Seed HN with the link within minutes of announcement. The HN spike drives X coverage which feeds Reddit. Target 48h cascade, not just launch day.

#### 8. Humor / Meme
**What it is:** Relatable, shareable content about Claude's behaviour or AI culture.
**Why it works:** Low friction to share. Reaches people outside the core AI audience.
**Best examples:** "Brother" post (4,312 score). "Caught red handed" (4,789 score).
**How to manufacture:** Don't force it. React to community-created memes by boosting signal (upvote, repost). Anthropic official meme attempts reliably underperform community memes.

---

## Platform Sequencing Strategy

Based on cross-platform cascade analysis:

```
X (seed) ──→ HN (tech amplification) ──→ Reddit (mass sustain) ──→ X (second wave)
  Day 0         Day 0–1                     Day 1–3               Day 3–5
```

1. **X first** — official Anthropic tweet or coordinated amplifier tweet within the first hour of any event.
2. **HN within 2h** — submit the primary source link. Do not submit the tweet; submit the blog post / paper.
3. **Reddit within 6h** — post in r/ClaudeAI and r/Anthropic with different framings (technical vs. use-case).
4. **X second wave on Day 3** — as Reddit discussion peaks, screenshot the top comments and tweet them to restart the X cycle.

---

## The Amplifier List

**Tier 1 — Official (Anthropic-controlled):**
- @AnthropicAI (core announcements)
- @DarioAmodei (narrative / thought leadership)
- @claudeai (product demos)

**Tier 2 — High-reach, Claude-adjacent (cultivate, don't control):**
- @karpathy — AI researcher, 3.7M views/post, tech credibility
- @levelsio — indie hacker, 3.9M views, builder audience
- @rubenhassid — contrarian AI takes, 14M views when Claude is subject
- @mattshumer_ — 28 Claude-related tweets, avg high engagement

**Tier 3 — Opportunistic (react when they engage):**
- Politicians (SenSanders): unexpected reach to non-AI audience
- Fortune 500 CEOs: quote amplification (Eli Lilly format)
- Tech journalists: TechCrunch, The Verge — surface to mainstream

**Rule:** Don't pitch Tier 2/3. Monitor their feeds. When they mention Claude positively, reply + RT within 30 minutes to ride their algorithm window.

---

## Copy Playbook

### Titles that outperform (Reddit)

| Pattern | Example | Why |
|---------|---------|-----|
| Specific numbers + zero resolution | "25 years. Multiple specialists. Zero answers." | Specificity creates credibility |
| "I dug through / I reverse-engineered" | "i dug through claude code's leaked source..." | Signals insider knowledge |
| Outcome-first, no build-up | "Claude just gave me access to another user's legal documents" | Instant stakes |
| Short declarative + emoji hook | "Outside Anthropic Office in SF "Thank You"" | Curiosity gap |

### What to avoid
- Questions as titles: avg score **12.0** (lowest archetype)
- Complaint framing: avg score **9.9** (second lowest)
- Title > 150 chars: engagement drops sharply above 130 chars
- Generic superlatives: "amazing", "incredible" without specific evidence

### Best posting time (UTC)
- **Best day:** {ins['best_weekday']}
- **Best hour:** {ins['best_hour']:02d}:00–{ins['best_hour']+2:02d}:00 UTC
- Avoid weekends for technical/news content (lower initial velocity)

---

## The Anthropic-Manufactured Virality Formula

**For product launches:**
```
Announcement + technical depth post (blog)
→ X thread with 3 concrete demos (not features)
→ HN submission of blog post within 2h
→ Reddit post framing the user benefit (not the product spec)
→ Day 3: community showcase thread ("show us what you built")
```

**For controversy moments:**
```
Identify flashpoint 24–48h in advance
→ Prepare 2–3 quotable lines (not paragraphs)
→ Publish on X at peak-hour (10:00–14:00 UTC Mon–Wed)
→ Monitor HN for organic submission; upvote/comment if it appears
→ Let community carry Reddit; do not astroturf
```

**For competitive positioning:**
```
Competitor releases model / makes mistake
→ Within 6h: neutral comparison post from non-official account
→ Within 12h: official benchmark data (let data speak)
→ Do NOT mock — "here's the data" outperforms "we're better"
```

---

## Charts Reference

All charts are saved in `data/charts/`:

| File | Description |
|------|-------------|
| `1a_weekly_engagement_timeline.png` | Weekly engagement per platform with event markers |
| `1b_reddit_growth.png` | Reddit monthly growth curve |
| `1c_top_viral_moments.png` | Top 20 all-platform viral posts |
| `2a_reddit_archetype_avg_score.png` | Avg score by content archetype |
| `2b_archetype_cross_platform_heatmap.png` | Archetype performance heatmap across platforms |
| `2c_archetype_volume_vs_virality.png` | Volume vs. virality scatter |
| `3a_reddit_flair_engagement.png` | Engagement by Reddit flair |
| `3b_x_views_vs_likes_archetype.png` | X views vs. likes by archetype |
| `3c_hn_discussion_depth.png` | HN comment/point ratio by archetype |
| `3d_viral_timing_heatmap.png` | Viral post timing heatmap |
| `4a_event_cascade_windows.png` | Per-event cascade windows |
| `4b_lead_lag_correlation.png` | Cross-platform lead/lag correlation |
| `4c_platform_volume_stack.png` | Monthly volume by platform |
| `5a_x_amplifiers_by_views.png` | Top X amplifiers |
| `5b_official_vs_community_views.png` | Official vs. community share |
| `5c_hn_top_submitters.png` | HN top submitters |
| `5d_engagement_efficiency_by_type.png` | Engagement rate by account type |
| `6a_emotional_triggers.png` | Emotional trigger lift |
| `6b_title_length_vs_score.png` | Title length vs. score |
| `6c_opening_word_lift.png` | Opening word viral lift |
| `6d_top_posts_wordcloud.png` | Word cloud of top posts |
| `6e_hn_comment_themes.png` | HN comment themes |
| `7a_competitor_mention_lift.png` | Competitor mention lift |
| `7b_competitor_frequency_viral_vs_all.png` | Competitor frequency viral vs. all |
| `7c_competitor_timeline.png` | Competitor mention timeline |
| `7d_x_competitor_view_boost.png` | X competitor view boost |
"""

    PLAYBOOK_PATH.write_text(playbook, encoding="utf-8")
    print(f"\nPlaybook written: {PLAYBOOK_PATH}")


if __name__ == "__main__":
    import module1_timeline   as m1
    import module2_archetypes as m2
    import module3_engagement_rate as m3
    import module4_cascade    as m4
    import module5_amplifiers as m5
    import module6_copy_patterns as m6
    import module7_competition as m7

    run_module("Module 1: Viral Moment Timeline",         lambda: (m1.chart_weekly_engagement(), m1.chart_reddit_growth(), m1.chart_spike_moments()))
    run_module("Module 2: Content Archetype Taxonomy",    lambda: (m2.chart_reddit_archetypes(), m2.chart_cross_platform_archetypes(), m2.chart_archetype_scatter(), m2.print_archetype_examples()))
    run_module("Module 3: Engagement Rate Analysis",      lambda: (m3.chart_flair_engagement(), m3.chart_x_views_vs_likes(), m3.chart_hn_discussion_depth(), m3.chart_timing_heatmap()))
    run_module("Module 4: Cross-Platform Cascade",        lambda: (m4.chart_event_cascades(), m4.chart_lead_lag(), m4.chart_platform_dominance()))
    run_module("Module 5: Amplifier Network",             lambda: (m5.chart_x_amplifiers(), m5.chart_official_vs_community(), m5.chart_hn_submitters(), m5.chart_engagement_efficiency()))
    run_module("Module 6: Copy Pattern Analysis",         lambda: (m6.chart_emotional_triggers(), m6.chart_title_length(), m6.chart_opening_words(), m6.chart_wordcloud(), m6.chart_hn_comment_themes()))
    run_module("Module 7: Competitive Comparison",        lambda: (m7.chart_comparison_lift(), m7.chart_competitor_frequency(), m7.chart_competitor_timeline(), m7.chart_x_competitor_context()))

    print("\n=== Computing insights for playbook ===")
    insights = compute_insights()
    write_playbook(insights)

    print(f"\n{'='*55}")
    print("  ALL MODULES COMPLETE")
    charts = list(Path(__file__).parent.parent.glob("data/charts/*.png"))
    print(f"  {len(charts)} charts saved to data/charts/")
    print(f"  Playbook: VIRAL_PLAYBOOK.md")
    print(f"{'='*55}")
