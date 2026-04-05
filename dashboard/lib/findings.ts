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
  tag: "narrative" | "archetypes" | "copy" | "product" | "distribution";
};

export const findings: Finding[] = [
  {
    id: "threat-over-launch",
    number: 1,
    title: "The #1 viral moment wasn't a product launch. It was a threat disclosure.",
    subtitle: "33.6M views from a security alert. Best product launch: 5M views. Six times less.",
    stat: "6.7×",
    statLabel: "more views from threat disclosure than from best product launch",
    tag: "narrative",
    charts: [
      { file: "1c_top_viral_moments.png", caption: "Top 20 viral moments from Anthropic's own posts — ranked by engagement" },
      { file: "1a_weekly_engagement_timeline.png", caption: "Weekly engagement volume by platform — event markers show what caused spikes" },
    ],
    body: `The top 20 viral moments table (scraped from Anthropic's own accounts and r/ClaudeAI) is a product roadmap in reverse:

#1: "We identified industrial-scale distillation attacks on our models" — 33.6M views
#2: Dario Amodei statement on DoW — 18.5M views
#3: Statement on Pete Hegseth comments — 17.6M views
#4: Apple reasoning study (third-party post) — 16.2M views
#5: Eli Lilly CEO does not use ChatGPT — 10.2M views

First product launch appears at #14: "Introducing Claude Sonnet 4.5" — 5M views.

The pattern is consistent: content about what Claude MEANS to the world — threats to AI, geopolitical stakes, endorsements from non-AI industries — consistently outperforms content about what Claude IS. The distillation attack disclosure worked not because of clever marketing, but because "state-level actors are targeting us" communicates scale more viscerally than any benchmark.

The weekly timeline confirms this: every major Reddit and HN spike follows a real-world event, not a product launch calendar. The community grows in response to moments, not campaigns. Claude's Reddit grew 11.5× in 12 months — but that growth is a staircase of event-driven ratchets, each spike landing on a permanently higher floor.

The lesson: position Claude (or Higgsfield) inside existing high-stakes conversations. Not by manufacturing controversy, but by having something credible to say when the conversation arrives.`,
    higgsfield: "\"AI is replacing Hollywood\" is already a live, high-stakes conversation in every entertainment trade outlet. WGA and actors' guilds are actively discussing AI video policy. Higgsfield doesn't need to create that narrative — it needs a credible position inside it. Not a PR announcement, but a real filmmaker voice, a real production outcome, a real data point about responsible use. That's the surface for a 10M+ view moment.",
  },
  {
    id: "archetype-trap",
    number: 2,
    title: "The community writes 5× more Capability Demos than Insider Leaks. Demos score 4× lower.",
    subtitle: "1,208 Capability Demo posts, avg score 24. 230 Insider Leak posts, avg score 102.",
    stat: "4.25×",
    statLabel: "score gap between the top-performing and the most-produced named archetype",
    tag: "archetypes",
    charts: [
      { file: "2a_reddit_archetype_avg_score.png", caption: "Reddit avg score by content archetype (higher = more viral per post)" },
      { file: "2c_archetype_volume_vs_virality.png", caption: "Archetype volume vs. virality — scarcity drives per-post value" },
      { file: "2b_archetype_cross_platform_heatmap.png", caption: "Same archetypes routed to different platforms produce very different results" },
    ],
    body: `The volume-virality scatter (2c) maps every content archetype by number of posts vs. average score. Insider Leak/Reveal sits isolated in the top-left: low volume, highest virality. Capability Demo is mid-right: high volume, mediocre virality. "Other" (61k+ posts) is the extreme-right with low virality.

Full archetype breakdown:
— Insider Leak / Reveal: n=230, avg score 102
— Controversy / Stance: n=266, avg score 102
— Humor / Meme: n=495, avg score 68
— Third-Party Validation: n=303, avg score 51
— Model Release: n=1,187, avg score 39
— Capability Demo: n=1,208, avg score 24
— Personal Breakthrough: n=4,635, avg score 16

4,635 Personal Breakthrough posts × avg 16 = 74k total score. 230 Insider Leak posts × avg 102 = 23k total score. You produce 20× more content to generate 3× more aggregate engagement. The ROI on Insider Leak per post is extraordinary — it's rare because it requires genuine access or timing luck, not because it's conceptually hard to produce.

But the heatmap (2b) adds the platform routing insight: Capability Demo gets Reddit score 24 — but HN avg points 70 and X avg views 408k. The archetype isn't wrong. It's being posted to the wrong platform. Reddit rewards story and emotion; HN rewards technical depth; X rewards reach and novelty.

The scarcity mechanism is self-reinforcing: Insider Leaks average 102 precisely because there are only 230 of them. As soon as everyone starts posting "insider reveals," the score converges toward the mean. The value is partly genuine scarcity of genuine information.`,
    higgsfield: "Higgsfield Reddit is almost entirely Capability Demo — the archetype that scores 24. The platform-archetype routing matrix from this data: video demos → HN and YouTube (HN scores 70, YouTube has Higgsfield's best engagement rate); filmmaker personal stories → Reddit (where story-format performs); industry insider posts → everywhere simultaneously. The current Higgsfield posting strategy is fighting Reddit's algorithm with the archetype Reddit scores lowest.",
  },
  {
    id: "copy-formula",
    number: 3,
    title: "Opening with your product name has 1.26× lift. Opening with 'just' has 638×.",
    subtitle: "Title length, first word, and emotional frame predict viral performance more than topic.",
    stat: "638×",
    statLabel: "viral lift for posts beginning with 'just' vs. baseline (1.0 = no effect)",
    tag: "copy",
    charts: [
      { file: "6c_opening_word_lift.png", caption: "Opening words with highest viral lift (lift = viral rate ÷ baseline rate)" },
      { file: "6b_title_length_vs_score.png", caption: "Title length vs. average score — sweet spot around 70–130 chars" },
      { file: "6a_emotional_triggers.png", caption: "Emotional trigger presence in viral vs. baseline posts" },
    ],
    body: `Opening word lift across 74k Reddit posts:

sonnet: 662× — specific model version = immediate context
just: 638× — recency + personal discovery
new: 574× — novelty signal
when: 380× — conditional narrative hook
we: 371× — team / collective voice
i'm: 344× — personal revelation

vs. weak performers:
anthropic: 3.87×
claude: 1.26× — barely above baseline
what: 1.17×
the: 1.57×

Posts that open with "sonnet" aren't viral because of the word — they follow a pattern: "Sonnet [just/finally] [did something specific] in [context]." Version specificity signals the post is about a concrete, recent, reproducible event. "Claude is amazing at coding" opens with the product name and says nothing specific.

The performing opening words are all story hooks. "Just" followed by a past-tense verb is the formula: something happened, to a person, right now, with a specific tool version. "Just had Sonnet rewrite my entire test suite in 40 minutes" — recency + personal + version + outcome + time frame.

Title length (6b): sweet spot at 70–130 characters. Most posts are under 70 characters. Longer titles perform better because they force specificity — you cannot write a 100-character title about "Claude is good." You're forced to describe what specifically happened.

Emotional triggers (6a): Amazement has 2.8× lift. BREAKING has 2.7×. But Pride/Social ("look at what I made") has 0.9× — below baseline. The community does not respond to self-congratulation. Posts framed as personal achievements underperform posts framed as discoveries.`,
    higgsfield: "Every Higgsfield post title should pass this filter: does it start with a story hook or a product claim? \"Higgsfield releases cinematic AI\" → 1.26× lift. \"Just tried to recreate a Spielberg tracking shot with AI for $0\" → potentially 638×. The second title forces the reader to ask \"what happened?\" — which is the only question that drives clicks. Brief your content team and seeded creators with this exact framework: [recency word] + [what happened] + [specific surprising outcome], 70–130 characters.",
  },
  {
    id: "mcp-signal",
    number: 4,
    title: "MCP has 1,383 posts averaging 7.8 score. The community scores Complaint threads higher.",
    subtitle: "Claude's biggest developer bet gets less engagement than a thread about billing issues.",
    stat: "7.8",
    statLabel: "avg MCP flair score — below Complaint threads (8.2) and above only Question (6.4)",
    tag: "product",
    charts: [
      { file: "3a_reddit_flair_engagement.png", caption: "Reddit avg score by post flair — top 12 by volume" },
      { file: "6e_hn_comment_themes.png", caption: "HN comment themes: what do people discuss under top Claude stories?" },
      { file: "6d_top_posts_wordcloud.png", caption: "Word cloud: top 500 Reddit posts by score — MCP notably absent" },
    ],
    body: `The flair engagement chart (3a) is an unintentional product health dashboard:

Humor: avg 79.4, n=2,521
Vibe_Coding: avg 24.5, n=2,228
Coding: avg 20.1, n=5,948
Workaround: avg 16.8, n=1,937
Built_with_Claude: avg 15.7, n=6,037
Complaint: avg 8.2, n=3,234
MCP: avg 7.8, n=1,383 ← below Complaint
Question: avg 6.4, n=18,267

MCP is Claude's flagship agentic protocol. The community finds complaint threads about Claude more interesting than MCP content.

Two explanations, both partially true. First: MCP discussion is primarily developer setup questions ("how do I connect X to MCP") which read as low-context tech questions and get question-level engagement. Technical configuration content scores low across every platform. Second: the community doesn't have a narrative for why MCP matters to them personally. The top-500 post wordcloud doesn't feature "MCP" — it features "limit," "code," "opus," "sonnet." Users discuss what Claude does, what it can't do, and which version. Not the protocol layer.

The 18,267 Question posts averaging 6.4 are the indicator of friction. High question volume means users are stuck more than they're succeeding. Workaround flair (avg 16.8) outperforming Built_with_Claude (15.7) tells the same story: hacking around constraints engages more than succeeding with the designed path.

This is not a criticism of MCP — it's a signal that the developer community is using MCP silently. They're not excited or frustrated, they're just working. That's fine for adoption but terrible for community momentum.`,
    higgsfield: "Developer features only generate community momentum when the community has a story for why they matter. Don't launch \"Higgsfield API\" — launch \"a filmmaker built a 10-episode YouTube series using Higgsfield's API to generate one new cinematic shot per episode, $500 total.\" The outcome story creates the narrative. The API announcement alone produces MCP-level engagement: 7.8 avg score, below complaints.",
  },
  {
    id: "hn-power-law",
    number: 5,
    title: "107k HN posts. Real distribution runs through 20 people deciding what the tech world hears.",
    subtitle: "adocomplete: 10 stories, avg 947 pts. meetpateltech: 27 stories, avg 368 pts. Selectivity beats volume.",
    stat: "947",
    statLabel: "avg HN points for adocomplete (10 stories) vs 368 for the most prolific submitter",
    tag: "distribution",
    charts: [
      { file: "5c_hn_top_submitters.png", caption: "HN top 20 submitters by total points — colour = account type" },
      { file: "4a_event_cascade_windows.png", caption: "Cross-platform cascade: activity around 6 key events" },
      { file: "4c_platform_volume_stack.png", caption: "Monthly content volume by platform (2025–2026)" },
    ],
    body: `Hacker News has 107k Claude-related items — Claude's single largest platform at 58% of total content. But the front-page placement that drives downstream press coverage runs through approximately 20 power submitters.

Top submitters ranked by avg pts per story:
— aarontrexel04: 1 story, avg 2,920 pts
— bafugo: 1 story, avg 2,127 pts
— adocomplete: 10 stories, avg 947 pts ← highest ROI regular submitter
— meetpateltech: 27 stories, avg 368 pts ← most prolific

adocomplete submits 10 stories and averages 947 pts. meetpateltech submits 27 and averages 368. Selectivity beats volume by 2.6×. Prolific submitters get noisier with volume; selective ones improve their batting average. The algorithm rewards stories that are genuinely novel to an engineering audience — and frequent submitters learn to lower their bar over time.

The event cascade windows (4a) show why HN placement matters downstream: every major Claude event — DoW statement, source code leak, Claude 4 launch — generates an HN spike within 24–48 hours, which then drives tech press coverage within 48 hours. HN is the credibility amplifier in Claude's distribution chain. Content that lands on the HN front page gets shared in engineering Slacks, developer Discords, and technical newsletters. The HN signal is what justifies a TechCrunch story.

The monthly volume stack (4c) shows HN as a stable, reliable stream. Reddit grew 11.5× in 12 months. HN stayed roughly constant. This stability makes HN predictable — lower variance, but the floor doesn't collapse.

HN is not Claude's top-of-funnel discovery platform (that's X). It's the credibility amplifier that turns an X spike into a lasting developer narrative.`,
    higgsfield: "Higgsfield has zero HN presence. To build it: submit a technical Show HN with a real architecture writeup (\"Show HN: How we built consistent actor identity across shots without per-person fine-tuning\"), and get it in front of the 20-person submission network. Direct DM to adocomplete and meetpateltech with a one-sentence pitch is a viable cold start — these are enthusiasts who surface things they find genuinely interesting to engineers, not gatekeepers. One front-page HN story = tech press pickup within 24 hours.",
  },
];

export const stats = [
  { value: "197k",    label: "total data items scraped" },
  { value: "84,088",  label: "Claude Reddit posts" },
  { value: "107k",    label: "Hacker News stories" },
  { value: "33.6M",   label: "views on #1 viral post" },
  { value: "638×",    label: "lift for 'just' opening word" },
  { value: "4.25×",   label: "score gap: leak vs. demo" },
];

export const tagColors: Record<Finding["tag"], string> = {
  narrative:    "bg-red-950 text-red-300 border-red-800",
  archetypes:   "bg-purple-950 text-purple-300 border-purple-800",
  copy:         "bg-pink-950 text-pink-300 border-pink-800",
  product:      "bg-yellow-950 text-yellow-300 border-yellow-800",
  distribution: "bg-green-950 text-green-300 border-green-800",
};
