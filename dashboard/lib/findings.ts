export type Finding = {
  id: string;
  number: number;
  title: string;
  subtitle: string;
  stat: string;
  statLabel: string;
  charts: { file: string; caption: string }[];
  body: string;
  higgsfield: string;
  tag: "dilution" | "cascade" | "mismatch" | "amplifier" | "constraint" | "copy" | "competitor" | "storm";
};

export const findings: Finding[] = [
  {
    id: "dilution",
    number: 1,
    title: "The community is growing faster than the signal can sustain",
    subtitle: "11.5× post growth, average score collapsed from 25 → 10",
    stat: "11.5×",
    statLabel: "post volume growth Apr'25 → Mar'26",
    tag: "dilution",
    charts: [
      { file: "1b_reddit_growth.png", caption: "Reddit monthly post volume vs. avg score per post" },
      { file: "1a_weekly_engagement_timeline.png", caption: "Weekly engagement volume by platform with event markers" },
    ],
    body: `Reddit post volume grew 11.5× between April 2025 and March 2026 (1,518 → 17,509 posts/month). Average score per post moved in the opposite direction — from ~25 in early 2025 to ~10 by March 2026.

This is textbook community dilution. As the subreddit became discoverable, the incoming cohort of lower-engagement users drowned out the high-signal early community. More posts, less attention per post.

The exception is December 2025 – January 2026: both metrics were simultaneously elevated — high volume and high avg score. That window represents the last moment the community was large enough to drive reach but tight enough to maintain quality.

At what community size does signal-to-noise flip permanently? Claude's data suggests the tipping point is somewhere between 5,000 and 10,000 posts/month. Before that threshold, rising volume lifts all boats. After it, quality posts get buried under volume.`,
    higgsfield: "You have not hit this wall yet. The time to seed high-quality content archetypes is before the community is large — because early posts set the quality standard that latecomers anchor to. If your first 1,000 community posts are capability showcases, your community identity becomes \"people who show off outputs.\" If your first 1,000 are personal breakthroughs and creative experiments, that's the floor future members aim for.",
  },
  {
    id: "cascade",
    number: 2,
    title: "There are two cascade architectures flowing in opposite directions",
    subtitle: "Official content: X → HN → Reddit. Community-discovered: Reddit → HN → X.",
    stat: "0.2–0.4",
    statLabel: "cross-platform Pearson correlation (mostly independent)",
    tag: "cascade",
    charts: [
      { file: "4a_event_cascade_windows.png", caption: "Activity around 6 key events — shows cascade direction per event type" },
      { file: "4b_lead_lag_correlation.png", caption: "Cross-platform lead/lag correlation (peak at lag=N means left platform leads by N days)" },
      { file: "4c_platform_volume_stack.png", caption: "Monthly content volume by platform" },
    ],
    body: `Every event in the dataset falls into one of two cascade patterns:

Pattern A — Top-down (official content): X spikes on day 0 → HN spikes same day → Reddit builds over 3–5 days. Seen in Claude 4 launch, Opus 4.6, Bun acquisition, DoW statement.

Pattern B — Bottom-up (community-discovered): Reddit spikes first → HN follows 1–2 days later → X picks it up last. Seen in the Claude Code source leak — the only clear example in the dataset. Reddit's bar is visibly larger and earlier than HN's spike.

The lead-lag correlation chart confirms this is not a universal cascade: overall cross-platform correlations are 0.2–0.4. Platforms operate mostly independently. Synchronized multi-platform spikes are rare, anomalous events — not the default state.

Most growth teams treat Reddit as a lagging indicator. The data says it is the leading indicator for organic content.`,
    higgsfield: "When a filmmaker discovers an unexpected capability in your model and posts about it — that will start on Reddit if they have < 5k followers. Your community manager needs to be watching Reddit first-post moments and escalating them to HN and the official X account within 24h. For product launches: publish the blog post, submit to HN immediately, post the X thread within the hour. Reddit will follow on its own.",
  },
  {
    id: "mismatch",
    number: 3,
    title: "The archetype-platform matrix reveals a systematic mismatch",
    subtitle: "Personal Breakthrough gets avg score 16 on Reddit — and 395k avg views on X",
    stat: "25×",
    statLabel: "more reach for Personal Breakthrough on X vs. Reddit",
    tag: "mismatch",
    charts: [
      { file: "2b_archetype_cross_platform_heatmap.png", caption: "Content archetype performance across platforms (normalized 0–100 within platform)" },
      { file: "2a_reddit_archetype_avg_score.png", caption: "Reddit avg score by content archetype" },
      { file: "2c_archetype_volume_vs_virality.png", caption: "Archetype volume vs. virality — scarcity drives per-post value" },
    ],
    body: `The heatmap shows where each content type actually performs best:

- Controversy / Stance: Reddit 102, HN 89, X 1,830k views
- Personal Breakthrough: Reddit 16, HN 23, X 395k views
- Capability Demo: Reddit 24, HN 70, X 408k views
- Model Release: Reddit 39, HN 242 pts, X 370k views
- Insider Leak: Reddit 102, HN 81, X 153k views
- Third-Party Validation: Reddit 51, HN 24, X 533k views

The community is posting Personal Breakthrough stories to Reddit — where they land with a score of 16 — when those exact same stories would generate 25× more reach on X.

Model Release content performs best on HN (242 avg pts) — far above Reddit (39). HN should be co-equal with X for technical launches, not an afterthought.

The volume-vs-virality scatter confirms the scarcity mechanism: Insider Leak has low volume and the highest per-post virality. Personal Breakthrough has high volume (4,635 posts) and low avg score. The more a type is produced, the less each individual post is worth.`,
    higgsfield: "Capability demos of your video model should be X-first (408k avg views). Technical write-ups about your architecture should be HN-first. User testimonials and personal creative breakthroughs should be X-first, not Instagram or TikTok-first. Reddit is for community discussion and workarounds — not for showcasing outputs.",
  },
  {
    id: "amplifier",
    number: 4,
    title: "The official account is a depth engine. Researchers are a reach engine.",
    subtitle: "Karpathy: 1.8M avg views / 6 tweets. AnthropicAI: 0.5M avg views / 580 tweets.",
    stat: "3.6×",
    statLabel: "more efficient per post: top researcher vs. official account",
    tag: "amplifier",
    charts: [
      { file: "5d_engagement_efficiency_by_type.png", caption: "Engagement rate by account type (rate = audience that actively engages, not just scrolls)" },
      { file: "5a_x_amplifiers_by_views.png", caption: "Top 25 X accounts by total Claude-related views" },
      { file: "5b_official_vs_community_views.png", caption: "Official accounts vs. community amplifiers: views and likes share" },
    ],
    body: `AnthropicAI: 580 tweets, 605% engagement rate, 0.5M avg views.
Karpathy: 6 tweets, 1.0% engagement rate, 1.8M avg views.

These describe two completely different mechanisms:

Official accounts produce depth — an engaged, loyal audience that clicks, reposts, and replies at extraordinary rates. The 605% engagement rate means for every 1,000 views, 6,050 engagement actions occur.

AI Researchers produce breadth — they distribute content to people who have never heard of Claude. Each tweet is an acquisition event.

One karpathy tweet (1.8M views, new audience) is worth more than three average AnthropicAI tweets (0.5M views, existing audience) if your goal is growth.

The chart also reveals a dead zone: Tech Journalists have 0.61% engagement rate and 0.1M avg views. They are neither deep nor broad — yet they are the most commonly pitched by PR teams.`,
    higgsfield: "Map your growth objectives to account types before spending influencer budget. Pre-launch: invest in researcher/practitioner equivalents (cinematographers, VFX supervisors, directors with 50k-500k Twitter followings) for breadth. Post-launch: invest in official account quality for depth. Stop pitching tech journalists for reach — their engagement rate is 0.61%.",
  },
  {
    id: "constraint",
    number: 5,
    title: "The community obsesses over constraints, not capabilities",
    subtitle: "\"Limit\" is one of the largest words in top-500 posts. Workarounds beat Showcases.",
    stat: "16.8",
    statLabel: "avg score for Workaround flair vs. 15.7 for Built_with_Claude",
    tag: "constraint",
    charts: [
      { file: "6d_top_posts_wordcloud.png", caption: "Word cloud: top 500 Reddit posts by score" },
      { file: "3a_reddit_flair_engagement.png", caption: "Reddit avg score by post flair (top 12 by volume)" },
      { file: "3c_hn_discussion_depth.png", caption: "HN discussion depth vs. points by archetype" },
    ],
    body: `"Limit" is one of the largest words in the top-500 Reddit posts by score. Not "capability", not "powerful", not "amazing." Limit.

The Workaround flair averages 16.8 — higher than Built_with_Claude at 15.7, Coding at 20.1, and dramatically higher than MCP at 7.8. Users sharing how to circumvent constraints slightly outperform users showcasing what they built.

This is the central behavioral insight of viral AI content: people engage more with what AI can't do than what it can.

There is a structural reason. Capability posts require the reader to believe the claim and imagine the application. Constraint posts confirm something the reader has already experienced — they have all hit limits — and offer relief. The emotional arc is: recognition → frustration → resolution. That arc is more engaging than demonstration → aspiration.

The word cloud also prominently features "token", "pro", "daily", "limit" — pricing and quota language dominating top posts is not coincidental. Discussions about value and pricing tiers generate high engagement because they are decision-relevant for the entire community.`,
    higgsfield: "Every time you impose a constraint (video length cap, style limitation, resolution tier), users will post workarounds. The question is whether that content will be frustration or ingenuity. Be transparent and specific about constraints early. Vague limits produce angry posts. Specific limits with stated reasons produce creative problem-solving posts — which outperform angry ones.",
  },
  {
    id: "copy",
    number: 6,
    title: "Longer titles win and almost nobody writes them. Your product name is nearly inert.",
    subtitle: "110–130 char titles score 30% higher. \"just\" has 636× viral lift. \"claude\" has 1.26×.",
    stat: "636×",
    statLabel: "viral lift for posts opening with \"just\" vs. baseline",
    tag: "copy",
    charts: [
      { file: "6c_opening_word_lift.png", caption: "Opening words with highest viral lift (lift > 1 = appears more in top-10% posts)" },
      { file: "6b_title_length_vs_score.png", caption: "Title length vs. average score — sweet spot at 110–130 chars" },
      { file: "6a_emotional_triggers.png", caption: "Emotional trigger presence in viral vs. baseline posts" },
    ],
    body: `Title length vs. score rises monotonically. Posts above 110 characters score ~30% higher than the median. But over 80% of posts are under 90 characters. The community has a systematic bias toward short titles — probably because short feels confident. The data says specificity wins, and specificity requires length.

Opening word viral lift:
- "just": 636×
- "new": 574×
- "when": 380×
- "we": 371×
- "i'm": 344×
- "anthropic": 3.87×
- "claude": 1.26×

"Claude" as the opening word has a lift of 1.26× — barely above baseline. Posts that open with "just" are narrating a moment. Posts that open with "Claude" are describing a product. The community responds to authenticity and immediacy above product claims.

Emotional triggers with highest lift: Amazement (2.8×), BREAKING (2.7×), Outrage/Fear (1.6×), Curiosity (1.8×). Pride/Social milestone posts: 0.9× — essentially no lift. The community does not care about Anthropic's growth milestones.`,
    higgsfield: "Brief your community, content team, and any seeded creators with a title framework: [Recency word] + [what happened] + [specific surprising outcome], targeting 90–130 characters. Never open with the product name. Seed user-generated content with first-person, past-tense prompts. \"Tell us what happened when you tried X\" produces better titles than \"Show us what you made with X.\"",
  },
  {
    id: "competitor",
    number: 7,
    title: "Competitor framing is a 55% score multiplier — but only for the right competitors",
    subtitle: "ChatGPT mention: 1.6× lift. Copilot mention: 0.8× (negative). MCP has the engagement of a complaint thread.",
    stat: "55%",
    statLabel: "avg score lift when post mentions a competitor (28 vs. 18)",
    tag: "competitor",
    charts: [
      { file: "7a_competitor_mention_lift.png", caption: "Does mentioning a competitor boost viral performance?" },
      { file: "7b_competitor_frequency_viral_vs_all.png", caption: "Competitor mentions in viral vs. all posts" },
      { file: "7c_competitor_timeline.png", caption: "Competitor mentions in r/ClaudeAI over time" },
      { file: "7d_x_competitor_view_boost.png", caption: "X: does mentioning a specific competitor boost view count?" },
    ],
    body: `Posts mentioning a competitor average 28 vs. 18 for Claude-only posts — a 55% lift across 74k posts.

But not all competitors are equal:
- ChatGPT / GPT: 1.6× lift
- Llama / Meta: 1.4× lift
- Grok: 1.2× lift
- Gemini: 1.3× lift
- Copilot: 0.8× (negative)
- Perplexity: 0.8× (negative)

Mentioning Copilot or Perplexity actually slightly depresses performance. ChatGPT and Llama comparisons reliably amplify.

The competitor timeline chart reveals the mechanism: ChatGPT mentions spiked 10× above baseline in March 2026 — not because Anthropic manufactured comparisons, but because when Claude released something significant, the community spontaneously started comparing. The comparison was community-driven, not engineered.

MCP has 1,383 posts and averages 7.8 — below complaints (8.2). The community has not been given a frame for why it matters to them personally.`,
    higgsfield: "Your comparison competitors are Runway and Sora. Posts comparing your outputs to theirs will outperform standalone showcases. You do not need to make those posts — seed the model outputs, let users compare. When you ship something strong, the comparison wave is the community's amplification mechanism. It works best when you do not visibly orchestrate it.",
  },
  {
    id: "storm",
    number: 8,
    title: "The February 2026 spike was a perfect storm, not a reproducible model",
    subtitle: "Five independent events in three weeks. Outside event clusters, platforms are mostly independent.",
    stat: "5×",
    statLabel: "larger than any prior event — caused by confluence, not strategy",
    tag: "storm",
    charts: [
      { file: "1c_top_viral_moments.png", caption: "Top 20 viral moments across all platforms" },
      { file: "5c_hn_top_submitters.png", caption: "HN top submitters by total points" },
      { file: "3d_viral_timing_heatmap.png", caption: "When do top-10% posts get posted? (UTC)" },
    ],
    body: `The February–March 2026 spike is 5× larger than any prior event. It was the collision of five independent events within three weeks:

- DeepSeek distillation attack disclosure (external threat narrative, 33.6M views on X)
- Dario's DoW statement (political controversy, 16.5M views)
- $30B funding / $380B valuation (milestone, 7.2M views)
- Claude Opus 4.6 launch (2,346 HN pts)
- Claude #1 App Store (5,644 Reddit score)

Any single one would have been a significant spike. All five in three weeks produced an event that cannot be reverse-engineered into a calendar.

The outrage/fear emotional trigger gives only 1.6× lift in the data — far below amazement (2.8×) or BREAKING framing (2.7×). Manufactured controversy without substance produces 1.6×, not 33M views. The DoW statement worked because it was genuine, unexpected, and high-stakes.

The timing heatmap reveals a counterintuitive pattern: the dark patches (highest scoring viral posts) cluster in early UTC hours — not the conventional "US morning" window of 13:00–17:00 UTC. Viral posts are either from non-US posters or from US late-night posts that find an audience in Asian and European mornings.`,
    higgsfield: "You cannot plan a February. What you can plan is the system that capitalizes on one when it arrives — fast response infrastructure, pre-written content formats, amplifier relationships already warm. The spike is luck. The capture rate is skill.",
  },
];

export const stats = [
  { value: "74,012", label: "Reddit posts" },
  { value: "3,355", label: "HN stories" },
  { value: "2,127", label: "X tweets" },
  { value: "26", label: "charts generated" },
  { value: "11.5×", label: "Reddit growth Apr'25–Mar'26" },
  { value: "33.6M", label: "views on single top tweet" },
];

export const tagColors: Record<Finding["tag"], string> = {
  dilution:   "bg-orange-100 text-orange-700 border-orange-200",
  cascade:    "bg-blue-100 text-blue-700 border-blue-200",
  mismatch:   "bg-purple-100 text-purple-700 border-purple-200",
  amplifier:  "bg-green-100 text-green-700 border-green-200",
  constraint: "bg-yellow-100 text-yellow-700 border-yellow-200",
  copy:       "bg-pink-100 text-pink-700 border-pink-200",
  competitor: "bg-red-100 text-red-700 border-red-200",
  storm:      "bg-slate-100 text-slate-700 border-slate-200",
};
