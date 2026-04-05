export type AnalysisFinding = {
  id: string;
  number: number;
  title: string;
  subtitle: string;
  stat: string;
  statLabel: string;
  charts: { file: string; caption: string }[];
  body: string;
  action: string;
  tag: "fragility" | "community" | "efficiency" | "brand" | "distribution" | "narrative";
};

export const analysisFindings: AnalysisFinding[] = [
  {
    id: "single-amplifier",
    number: 1,
    title: "EHuanglu IS Higgsfield's X presence. That's not a feature — it's a liability.",
    subtitle: "69.4% of Higgsfield X views are community-driven. The community is mostly one person.",
    stat: "69.4%",
    statLabel: "of Higgsfield X views from community — concentrated in one creator",
    tag: "fragility",
    charts: [
      { file: "cmp_06_top_amplifiers.png", caption: "Top X amplifiers for Claude and Higgsfield — total views by account" },
      { file: "cmp_07_official_vs_community.png", caption: "Official vs. community share of X views and likes" },
    ],
    body: `The top amplifiers chart shows the gap clearly. Claude's top X amplifiers: AnthropicAI (580M total views, 923 tweets), claudeai, alexalbert_, ns123abc (17 tweets avg 2.4M), rubenhassid, karpathy (6 tweets avg 1.8M), DarioAmodei, SenSanders, andrewchen. Eight meaningful, independent voices.

Higgsfield's top amplifiers: EHuanglu (dominates the chart), then a steep cliff. One creator generating the majority of Higgsfield's top-10 X posts. The bar chart tells the whole story — EHuanglu's bar is visually 3–4× the next account.

The official vs. community split (cmp_07) makes this structural: 69.4% of Higgsfield X views come from community accounts vs. 30.6% from official. For Claude, the split is 38% community / 62% official. Higgsfield's X presence is MORE community-dependent than Claude's — which sounds healthy, but the community is one person.

If EHuanglu pivots to Sora, takes a month off, or loses interest, Higgsfield's X monthly views likely halve. The X timeline chart (cmp_10) shows Higgsfield's X spikes are event-driven bumps, not a rising floor — exactly what single-amplifier dependency looks like at scale. Claude's floor, even in quiet months, is 20–30M monthly views. Higgsfield's is 5–10M.

Claude built its amplifier stack over time: AnthropicAI as the depth engine, then researchers (karpathy, rubenhassid) for breadth, then cross-industry voices (SenSanders, andrewchen) for credibility. Each type serves a different distribution function. Higgsfield currently only has community volume from EHuanglu.`,
    action: "Identify 5 film/VFX professionals with 100k–500k followers who post technical creative content. Not influencers — producers. Give them early access, a direct line to the team, and exclusives on upcoming features. The goal is 5 independent X voices for Higgsfield by the end of the quarter. Each one is an insurance policy against EHuanglu moving on.",
  },
  {
    id: "community-capture",
    number: 2,
    title: "r/HiggsfieldAI has 2,094 posts. KLING content (153 posts) scores 2.5× higher than Higgsfield's own video model (46 posts).",
    subtitle: "Competitors have colonised Higgsfield's own subreddit. KLING flair avg 6.6 vs 'Video Model - HIGGSFIELD' avg 2.6.",
    stat: "2.5×",
    statLabel: "KLING avg score (6.6) vs Higgsfield video model avg score (2.6) inside r/HiggsfieldAI",
    tag: "community",
    charts: [
      { file: "cmp_15_subreddit_breakdown.png", caption: "Where each brand's Reddit posts live — owned vs. shared communities" },
      { file: "cmp_02_reddit_growth.png", caption: "Reddit growth trajectory: Claude vs. Higgsfield (monthly post volume)" },
    ],
    body: `r/HiggsfieldAI exists — 2,094 posts scraped from Apr 2025 to Apr 2026. That's the good news. The bad news is in the flair breakdown.

Flair distribution and avg scores (n=2,094):
— Showcase: 826 posts, avg 4.6 — 39% of all posts, low engagement per post
— Discussion: 322 posts, avg 5.0
— Video Model - KLING: 153 posts, avg 6.6 ← competitor
— Tips / Tutorials: 146 posts, avg 6.0
— Feedback: 181 posts, avg 5.2
— Video Model - HIGGSFIELD: 46 posts, avg 2.6 ← Higgsfield's own model
— Video Model - SORA 2: 18 posts, avg 4.7 ← competitor
— CONTEST posts (38+16): 54 posts, avg 2.4 — worst non-zero category

The subreddit has become a general AI video tool forum. Members post Kling videos (153 posts), Sora videos (18 posts), and WAN/Seedance content — all flaired and indexed inside Higgsfield's own community space. When someone searches r/HiggsfieldAI, they're served competitor content.

The engagement gap makes it worse: community members engage more with Kling posts (6.6 avg) than with Higgsfield's own video model posts (2.6 avg). Contest content ranks last at 2.4 avg — the "free credits" strategy is actively suppressing the subreddit's quality signal.

Peak activity: December 2025 (543 posts) and January 2026 (528 posts), declining to 266 in March 2026 and 14 in the first 4 days of April. The community grew then started contracting — the classic pattern when there's no content strategy holding a community together.

Claude's r/ClaudeAI (60,132 posts) has no competitor flair. Every post is about Claude. The algorithm learns that r/ClaudeAI users want Claude content. This is the compounding effect: 11.5× Reddit growth in 12 months vs. Higgsfield's declining trajectory after a Dec 2025 peak.`,
    action: "Two distinct actions: (1) Establish a flair policy — competitor model flairs (KLING, SORA, WAN) should be removed or replaced with 'AI Video Comparison' and deprioritised in the feed. The subreddit should not be a free distribution channel for competitors. (2) Create a 'Higgsfield Insider' flair for posts from creators with early access, team updates, and feature previews — announcements already avg 13.2, the highest in the subreddit. Feed that archetype, not showcase content that averages 4.6.",
  },
  {
    id: "youtube-moat",
    number: 3,
    title: "Higgsfield beats Claude on YouTube engagement rate. Nobody knows — because nobody finds it.",
    subtitle: "Higgsfield YouTube engagement: 5.12%. Claude: 3.02%. But 55% fewer views on average.",
    stat: "5.12%",
    statLabel: "Higgsfield YouTube engagement rate vs Claude's 3.02% — 70% higher",
    tag: "efficiency",
    charts: [
      { file: "cmp_13_engagement_rate.png", caption: "Engagement rate comparison: (likes + reposts + comments) / views %" },
      { file: "cmp_11_youtube_scatter.png", caption: "YouTube: views vs. likes — each dot = one video" },
    ],
    body: `The engagement rate chart (cmp_13) contains the most counter-intuitive finding in the comparison dataset. YouTube engagement rate: Higgsfield 5.12% vs. Claude 3.02%. People who find Higgsfield's YouTube content interact with it more than Claude's viewers do.

The scatter plot (cmp_11) explains the structure. Claude has one massive outlier — approximately 21M views / 850k likes — that pulls the average up dramatically. Remove that one video and Claude's YouTube average drops substantially. Most Claude videos cluster in the 200k–2M views range.

Higgsfield's scatter is dense at low view counts with no breakout outliers yet. But the engagement rate within that cluster is genuinely better. This pattern has one explanation: the content quality is there, and the audience that finds it is passionate and engaged. The problem is distribution — not enough people are finding it.

High engagement rate with low reach is the classic pattern for a brand that hasn't solved YouTube discovery. It means the content earns its views when they happen — but it's not being surfaced by YouTube's recommendation algorithm or ranking in search.

Claude's YouTube growth came from tutorials about specific use cases ("how to use Claude for X") that rank in YouTube search and get recommended alongside other AI tool tutorials. Higgsfield's content leans showcase-heavy — beautiful output videos that perform well when found but don't rank for intent-based searches like "AI filmmaking workflow" or "how to create consistent AI characters."`,
    action: "Produce 10 YouTube videos with titles optimized for YouTube search: \"AI filmmaking workflow for indie directors,\" \"How to maintain character consistency in AI video,\" \"Replace green screen with AI: step-by-step.\" The current showcase content will keep getting 5.12% engagement — the problem is reaching the filmmaker audience that hasn't discovered Higgsfield yet. YouTube SEO is the missing piece, not content quality.",
  },
  {
    id: "vocabulary-rot",
    number: 4,
    title: "Higgsfield's top posts build a 'free contest' brand. Claude's build a 'build with AI' brand.",
    subtitle: "\"contest\" and \"free\" appear prominently in Higgsfield's top-content wordcloud. Claude's wordcloud: code, build, agent.",
    stat: "56%",
    statLabel: "Reddit score boost from competitor comparisons — which Higgsfield is already triggering (kling in their wordcloud)",
    tag: "brand",
    charts: [
      { file: "cmp_12_wordclouds.png", caption: "Top-500 post keywords: Claude vs. Higgsfield — what each brand's community actually talks about" },
      { file: "cmp_14_top_posts_table.png", caption: "Top 10 Reddit posts by score for each brand" },
    ],
    body: `The wordcloud comparison (cmp_12) tells you what the market thinks each brand is for.

Claude top-500 keywords: code, build, agent, chatgpt, gemini, opus, sonnet, mcp, tutorial, research, skills. Every word reinforces "professional AI tool for builders." The competitor mentions (chatgpt, gemini) reinforce "serious market player worth comparing."

Higgsfield top-500 keywords: create, action, full, cinematic, tutorial, contest, cinema, film, studio, free, kling, seedance, higgsfield_ai. The presence of "contest" and "free" signals a significant portion of top-performing Higgsfield content is giveaway-driven — posts that get engagement because they're offering something, not because of genuine community interest.

The top posts table (cmp_14) confirms: Higgsfield's highest-scoring posts are "AI generations are getting insanely realistic" (capability demo) and "Face Punching Iconic Characters" (capability demo). But note position #7: "stay away from Higgsfield" — a negative post — scored higher than most capability demos. Controversy outperforms polish.

Two signals from "kling" in Higgsfield's wordcloud: the community is already comparing Higgsfield to competitors, which is a 56% engagement boost opportunity (from Claude competitor mention data). But it also means Higgsfield is positioned as "one of the AI video tools" rather than the destination for serious filmmakers.

Contest-driven engagement inflates metrics while building the wrong brand associations. The posts getting the most score from contests are teaching the algorithm and the community that Higgsfield's highest-value content is about getting free credits — not about making something remarkable.`,
    action: "Audit your top 50 Reddit posts. Tag each as contest-driven or organic. Track them separately — contest posts should never set your engagement baseline. Separately: lean into the competitor comparison that's already happening. \"Higgsfield vs Kling on cinematic action sequences\" is a post your community is already writing — seeding one authoritative version captures the 56% score boost while controlling the narrative.",
  },
  {
    id: "hn-gap",
    number: 5,
    title: "HN is Claude's largest platform at 107k posts. Higgsfield has never appeared on HN.",
    subtitle: "One HN front-page story drives tech press pickup within 24 hours. Higgsfield hasn't tried once.",
    stat: "0",
    statLabel: "Higgsfield HN posts vs Claude's 107,000",
    tag: "distribution",
    charts: [
      { file: "cmp_05_platform_mix.png", caption: "Platform mix: where each brand's content lives" },
      { file: "cmp_01_community_scale.png", caption: "Community scale: total content volume by platform" },
    ],
    body: `The platform mix charts (cmp_05, cmp_01) show the structural asymmetry. Claude: 58.3% Hacker News, 42.8% Reddit — a developer-heavy, two-platform brand. Higgsfield: 93.2% Reddit, 9.4% X, 15.8% YouTube, 18.8% Google Trends — a consumer/creator-heavy, multi-platform brand.

The HN absence is not just a volume gap — it's a credibility gap. HN is where Claude's developer reputation is built and sustained. 107k HN posts means Claude discourse is permanently indexed in HN's archive, where engineers search for information years later. Zero Higgsfield HN presence means no developer credibility infrastructure exists.

The mechanism of HN distribution: a front-page story is read by 300k–500k highly-engaged technical users. Those readers share to engineering Slack channels, developer Discords, and newsletters like TLDR and Morning Brew. Tech journalists monitor HN front page for story ideas. The "HN-to-press" pipeline is how technical products get covered in TechCrunch and The Verge without a dedicated PR campaign.

From the Claude data (Finding 6): the top submitters show selectivity beats volume. adocomplete submits 10 Claude stories and averages 947 HN points. The HN network is accessible — it's enthusiasts who surface things they find genuinely interesting, not PR gatekeepers.

Higgsfield's content mix is structurally incompatible with HN right now: showcase videos and contest posts don't belong on HN. But technical content — architecture writeups, open-source evaluation tools, research findings about character consistency or motion transfer — does. That content doesn't exist in Higgsfield's current output.`,
    action: "Create one piece of technical content worth submitting to HN: a detailed writeup of how Higgsfield maintains character identity across shots, a benchmark methodology for AI video quality, or an open-source evaluation tool for cinematic AI. Submit it as Show HN. DM adocomplete and meetpateltech (Claude's top HN submitters, who clearly follow AI closely) with the link and one sentence of context. One front-page HN story = TechCrunch coverage + developer community credibility that persists for years.",
  },
  {
    id: "deepseek-lesson",
    number: 6,
    title: "DeepSeek gave Claude a 9.3× X view boost by being in the right conversation at the right time.",
    subtitle: "Claude tweets mentioning DeepSeek got 2.8M avg views vs 0.3M baseline. The mechanism: narrative surfing.",
    stat: "9.3×",
    statLabel: "X view boost from DeepSeek mentions in Jan–Feb 2026 — highest competitor boost in dataset",
    tag: "narrative",
    charts: [
      { file: "7d_x_competitor_view_boost.png", caption: "X: does mentioning a specific competitor boost view count? — by competitor" },
      { file: "7c_competitor_timeline.png", caption: "Competitor mentions in r/ClaudeAI over time — showing which are durable vs. spike-and-fade" },
    ],
    body: `The X competitor view boost chart (7d) is one of the most instructive charts in the dataset. Every competitor listed shows roughly similar avg views for mention vs. non-mention tweets — ChatGPT, Gemini, Copilot, Llama/Meta all hover around 0.4–0.6M views with minor variation. Then DeepSeek: mention tweets averaged 2.8M views vs. 0.3M for non-DeepSeek tweets. Nearly 10×.

This is not about the quality of the comparison content. It's a timing artifact. DeepSeek became a major news story in January 2026 around "China AI threat" and "open-source vs. proprietary AI." Every major outlet was running DeepSeek coverage. Claude tweets mentioning DeepSeek were algorithmically surfaced into that entire news feed — they appeared alongside DeepSeek news for every user following the story.

This is narrative surfing: your content gets carried by a larger story's momentum. The DeepSeek effect disappeared completely by March 2026 (visible in the competitor timeline, chart 7c). Once the DeepSeek news cycle ended, so did the view boost.

The ChatGPT mention timeline shows the opposite pattern: steady, durable, rising. ChatGPT mentions in r/ClaudeAI spiked in March 2026 but maintained a consistent baseline since May 2025. ChatGPT is Claude's reference competitor in the community's mind — the comparison that never fades because it's always relevant.

The lesson for Higgsfield: the Hollywood AI disruption narrative is already the DeepSeek of the creative industry. WGA, SAG-AFTRA, and major studios are actively negotiating AI policies. That story is in every entertainment trade outlet and climbing into mainstream press. A Higgsfield post with something credible to say inside that conversation would be surfaced to audiences who are actively consuming Hollywood-AI news — audiences far larger than Higgsfield's current follower base.`,
    action: "Monitor when Hollywood AI news spikes on r/movies, r/VFX, and entertainment trade outlets. Have 2–3 pieces of content pre-drafted that Higgsfield can deploy into those conversations authentically: a filmmaker's perspective on responsible use, data on what AI video actually costs vs. traditional production, a clear policy on disclosure and attribution. The narrative moment arrives unpredictably — the preparation needs to happen before it does.",
  },
];

export const analysisTagColors: Record<AnalysisFinding["tag"], string> = {
  fragility:    "bg-red-950 text-red-300 border-red-800",
  community:    "bg-blue-950 text-blue-300 border-blue-800",
  efficiency:   "bg-green-950 text-green-300 border-green-800",
  brand:        "bg-orange-950 text-orange-300 border-orange-800",
  distribution: "bg-purple-950 text-purple-300 border-purple-800",
  narrative:    "bg-yellow-950 text-yellow-300 border-yellow-800",
};
