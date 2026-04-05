export type ComparisonChart = {
  file: string;
  title: string;
  subtitle: string;
  insight: string;
  category: "scale" | "engagement" | "content" | "amplifiers" | "platforms";
};

export const comparisonCharts: ComparisonChart[] = [
  {
    file: "cmp_01_community_scale.png",
    title: "Community Scale",
    subtitle: "Total content volume by platform",
    insight: "Claude has 84k Reddit posts vs Higgsfield's 2,094 (r/HiggsfieldAI) — a 40× gap. But Higgsfield has no Hacker News presence at all, which is Claude's single largest platform (107k posts). Higgsfield is missing the highest-credibility distribution channel entirely.",
    category: "scale",
  },
  {
    file: "cmp_02_reddit_growth.png",
    title: "Reddit Growth Trajectory",
    subtitle: "Monthly post volume comparison",
    insight: "Claude's Reddit grew 11.5× in 12 months. Higgsfield's Reddit is flat — no visible growth curve. Higgsfield lacks the self-sustaining community flywheel that Claude built. The subreddits Higgsfield posts to (r/generativeAI, r/aivideo) are shared with competitors, not owned.",
    category: "scale",
  },
  {
    file: "cmp_03_avg_engagement.png",
    title: "Average Engagement by Platform",
    subtitle: "Mean likes, views per post across platforms",
    insight: "Higgsfield's X avg views (171k) are roughly half of Claude's (352k). But Higgsfield's YouTube avg likes (988) are competitive with Claude's (2,038) relative to its smaller audience. YouTube is Higgsfield's most efficient platform per post.",
    category: "engagement",
  },
  {
    file: "cmp_04_score_distribution.png",
    title: "Engagement Score Distribution",
    subtitle: "Box plot — median and spread per platform",
    insight: "Claude's Reddit median score is higher but both have heavy right skew — most posts are low, a few are massive. Higgsfield's X distribution shows more variance: the top tweets (EHuanglu, 5M views) are outliers that pull the mean far above the median. Higgsfield is a one-amplifier business on X.",
    category: "engagement",
  },
  {
    file: "cmp_05_platform_mix.png",
    title: "Platform Mix",
    subtitle: "Where each brand's content lives",
    insight: "Claude: 54% Hacker News, 43% Reddit, 1% X. Higgsfield: 63% Reddit, 16% YouTube, 15% Google Trends, 6% X. The platform mixes are structurally different — Claude is developer-heavy (HN), Higgsfield is consumer/creator-heavy (Reddit + YouTube). Neither has cracked the other's dominant channel.",
    category: "platforms",
  },
  {
    file: "cmp_06_top_amplifiers.png",
    title: "Top X Amplifiers",
    subtitle: "Who drives reach on Twitter/X",
    insight: "EHuanglu alone accounts for the majority of Higgsfield's top-10 X views — a single account generating 5M, 4.1M, 3.1M, 2.5M view posts. Claude's top 10 is more distributed (AnthropicAI, claudeai, DarioAmodei, karpathy). Single-amplifier dependency is Higgsfield's biggest X risk.",
    category: "amplifiers",
  },
  {
    file: "cmp_07_official_vs_community.png",
    title: "Official vs. Community Split",
    subtitle: "Share of X views and likes by account type",
    insight: "Higgsfield's community split on X is more extreme than Claude's — one or two non-official accounts drive a disproportionate share. Claude has built a deeper ecosystem of mid-tier amplifiers (karpathy, levelsio, mattshumer) that Higgsfield has not yet cultivated.",
    category: "amplifiers",
  },
  {
    file: "cmp_08_archetype_mix.png",
    title: "Content Archetype Mix",
    subtitle: "What types of content each brand's community creates",
    insight: "Higgsfield Reddit is dominated by Capability Demo posts ('look what I made'). Claude Reddit has more Personal Story and Comparison content. From the Claude data: Capability Demo averages score 24, while Personal Story and Controversy average 16–102. Higgsfield is over-indexed on the middle-performing archetype.",
    category: "content",
  },
  {
    file: "cmp_09_viral_ceiling.png",
    title: "Viral Ceiling",
    subtitle: "Top-N posts ranked — how high does each brand's best go?",
    insight: "Claude's top Reddit post scores 6,167; Higgsfield's tops at 276 — a 22× gap. The gap is larger than expected: Higgsfield's subreddit avg is 4.8 and most content clusters at score 1–5. On X, however, Higgsfield's #1 post (5.2M views) is within striking distance of Claude's non-controversy peaks — video content has a higher viral ceiling on X than text, and Higgsfield's format advantage is real there.",
    category: "engagement",
  },
  {
    file: "cmp_10_x_views_timeline.png",
    title: "X Views Over Time",
    subtitle: "Monthly X view totals — trajectory comparison",
    insight: "Higgsfield's X trajectory shows spikes tied to specific EHuanglu posts rather than a rising baseline. Claude's X is also event-driven but has a higher floor. Higgsfield needs to raise the floor (consistent mid-tier amplifiers) not just chase peaks.",
    category: "platforms",
  },
  {
    file: "cmp_11_youtube_scatter.png",
    title: "YouTube: Views vs. Likes",
    subtitle: "Each dot = one video",
    insight: "Higgsfield has YouTube outliers with very high like-to-view ratios (Pawzu Clips: 59k likes / 913k views = 6.5% like rate). Claude's YouTube cluster shows lower like rates. High like rate = highly engaged niche audience. Higgsfield's YouTube audience is more passionate per viewer than Claude's.",
    category: "platforms",
  },
  {
    file: "cmp_12_wordclouds.png",
    title: "Content Keywords",
    subtitle: "Most frequent words in top posts",
    insight: "Claude's wordcloud: code, limit, opus, sonnet, job, built. Higgsfield's wordcloud: actor, film, replace, shot, face, Hollywood. The narrative frames are completely different — Claude's community talks about productivity and constraints; Higgsfield's talks about creative disruption and industry replacement.",
    category: "content",
  },
  {
    file: "cmp_13_engagement_rate.png",
    title: "Engagement Rate",
    subtitle: "(likes + reposts + comments) / views %",
    insight: "Higgsfield's YouTube engagement rate significantly outperforms Claude's — viewers who find Higgsfield content are more likely to interact. This is consistent with a passionate early-adopter creative audience. High engagement rate with lower reach = strong product-community fit waiting for distribution.",
    category: "engagement",
  },
  {
    file: "cmp_14_top_posts_table.png",
    title: "Top Reddit Posts",
    subtitle: "Top 10 posts by score for each brand",
    insight: "Claude's top posts are primarily text-based personal stories and controversy. Higgsfield's top posts are almost entirely video showcase posts ('AI generations are getting insanely realistic', 'Face Punching Iconic Characters'). The content type that goes viral for each brand is structurally different.",
    category: "content",
  },
  {
    file: "cmp_15_subreddit_breakdown.png",
    title: "Subreddit Breakdown",
    subtitle: "Where Reddit posts are made per brand",
    insight: "Claude posts almost entirely to r/ClaudeAI and r/Anthropic — owned communities. Higgsfield posts to r/generativeAI, r/aivideo, r/StableDiffusion — shared communities it does not own. Owned community = controlled quality and narrative. Shared community = competing with Runway, Sora, Kling for the same audience.",
    category: "platforms",
  },
];

export const categoryLabels: Record<ComparisonChart["category"], string> = {
  scale:      "Community Scale",
  engagement: "Engagement",
  content:    "Content",
  amplifiers: "Amplifiers",
  platforms:  "Platforms",
};

export const categoryColors: Record<ComparisonChart["category"], string> = {
  scale:      "bg-blue-950 text-blue-300 border-blue-800",
  engagement: "bg-green-950 text-green-300 border-green-800",
  content:    "bg-purple-950 text-purple-300 border-purple-800",
  amplifiers: "bg-orange-950 text-orange-300 border-orange-800",
  platforms:  "bg-slate-800 text-slate-300 border-slate-600",
};
