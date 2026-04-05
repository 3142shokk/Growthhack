import Nav from "@/components/Nav";

/* ─── data ─────────────────────────────────────────────────────── */

// The 3 core Claude mechanisms we are replicating
const MECHANISMS = [
  {
    number: "M1",
    name: "Threat > Launch",
    claude: "Distillation attack disclosure: 33.6M views. Best product launch: 5M. 6.7× gap.",
    insight: "Claude's viral ceiling isn't product announcements — it's existential stakes. The industrial-scale attack disclosure worked because it made the AI conversation feel real and urgent to people who don't follow AI.",
    higgsfield: "The Hollywood AI displacement conversation (WGA, SAG-AFTRA, studio policy) is live, urgent, and mainstream. A Higgsfield post with something credible to say inside it gets carried by an audience far larger than Higgsfield's current followers.",
    data: "Finding 1: threat-over-launch · 33.6M vs 5M views · weekly engagement timeline",
    color: "#ef4444",
  },
  {
    number: "M2",
    name: "Insider Leak Archetype",
    claude: "230 Insider Leak posts, avg 102. 1,208 Capability Demo posts, avg 24. 4.25× gap.",
    insight: "The community produces 20× more demos but Insider Leaks get 4× higher per-post engagement. Scarcity is load-bearing: everyone posts demos, almost nobody has genuine access or timing advantage.",
    higgsfield: "Higgsfield's subreddit is 39% Showcase posts (avg 4.6 score) and has near-zero Insider/Controversy content. Every Showcase post produced is competing in the lowest-ROI archetype. One genuine insider post — a real filmmaker, a real production outcome, an honest failure — is worth 20 demos.",
    data: "Finding 2: archetype-trap · Reddit n=74k · r/HiggsfieldAI flair analysis n=2,094",
    color: "#a855f7",
  },
  {
    number: "M3",
    name: "Copy Formula",
    claude: "'just' opener: 638× viral lift. 'claude' opener: 1.26×. Title sweet spot: 70–130 chars.",
    insight: "The performing opening words are story hooks, not product claims. 'Sonnet [just] [did specific thing] in [context]' — recency + personal + outcome + time frame. Claude's own name as an opener barely beats baseline.",
    higgsfield: "Every Higgsfield post title should pass this test: does it start with a story hook or a product claim? 'Higgsfield releases cinematic AI' → 1.26× lift. 'Just tried to recreate a Spielberg tracking shot with AI for $0' → potentially 638×.",
    data: "Finding 3: copy-formula · Reddit title analysis n=74k · lift chart 6c",
    color: "#f59e0b",
  },
];

// Audience segments to target
const SEGMENTS = [
  {
    id: "S1",
    name: "Working Film/VFX Professionals",
    size: "~50k–200k on Reddit",
    description: "DoPs, VFX supervisors, editors, indie directors. They have professional credibility and an audience that trusts them on technical decisions. When they post about Higgsfield, it's a product endorsement from a credible voice — not a paid review.",
    channels: ["r/VFX (150k members)", "r/Filmmakers (1.5M members)", "r/HiggsfieldAI (owned)", "HN (Show HN + technical threads)"],
    contentType: "F1 Insider Reveal, F2 Production Breakdown, F4 Constraint/Workaround",
    recruitStrategy: "Early access offer + direct DM with a specific project brief. Not 'would you like to try Higgsfield?' — 'we're making a trailer for [your genre]. We'll fund one shot completely. Here's the brief.'",
    why: "This is the Karpathy/rubenhassid segment — Claude's researcher amplifiers who post technical content to audiences that trust them. These 6 posts averaged 1.8M views each. Film professionals are the equivalent for Higgsfield.",
    color: "#a855f7",
  },
  {
    id: "S2",
    name: "Creator / AI Hobbyist Community",
    size: "~2,094 posts in r/HiggsfieldAI",
    description: "Early adopters, AI enthusiasts, people who post weekly Higgsfield content already. They are volume — not individually influential, but they generate the subreddit floor that makes the community look alive.",
    channels: ["r/HiggsfieldAI (owned — primary)", "r/generativeAI (shared)", "r/aivideo (shared)"],
    contentType: "F3 Competitor Comparison, F4 Constraint/Workaround, weekly challenges",
    recruitStrategy: "Give the top 10 r/HiggsfieldAI contributors moderator status and early feature access. They're already posting. Make them invested in the community's health.",
    why: "BholaCoder (112 posts), memerwala_londa (74 posts, avg 9.8) — these are the community. They're currently posting KLING content because there's no content strategy keeping them on Higgsfield. A flair audit + community role makes them advocates.",
    color: "#6366f1",
  },
  {
    id: "S3",
    name: "Technical / Developer Audience",
    size: "0 HN presence for Higgsfield vs 107k for Claude",
    description: "ML engineers, AI researchers, developer-adjacent builders. This is Claude's primary HN audience — people who share things in engineering Slack channels and write newsletters. They don't watch YouTube demos but they will read a technical writeup about how character consistency works without per-person fine-tuning.",
    channels: ["HN (Show HN)", "r/MachineLearning", "r/MediaSynthesis"],
    contentType: "F2 Production Breakdown (HN format), technical architecture posts",
    recruitStrategy: "DM adocomplete and meetpateltech (Claude's top HN submitters, 947 and 368 avg pts). They cover AI broadly — Higgsfield is a natural submission. One-sentence pitch: 'built a method for consistent actor identity without fine-tuning — might interest HN.'",
    why: "HN front page → tech press within 24h. This is the distribution cascade Claude uses. Zero Higgsfield HN presence means zero developer credibility infrastructure. One front-page story creates years of searchable history.",
    color: "#22c55e",
  },
  {
    id: "S4",
    name: "Industry Press & Policy Layer",
    size: "Trade outlets: Variety, THR, The Verge, WIRED",
    description: "Journalists covering Hollywood AI policy, AI video tools, entertainment tech. They monitor HN and follow the discourse. They need a credible voice inside the Hollywood AI story that isn't OpenAI or Google.",
    channels: ["HN (credibility primer)", "X (news cycle surfing)", "LinkedIn (professional signal)"],
    contentType: "F5 Industry Stance, narrative surfing posts (see Section 5)",
    recruitStrategy: "Be quotable before you need press. Post a clear policy position, a real cost-data point, a real filmmaker outcome. Journalists need sources with something concrete to say. Become that source.",
    why: "Claude's DoW statement got 18.5M views — #2 viral moment overall — because it was a credible position inside an ongoing news story. Higgsfield needs 1 similar moment inside the Hollywood AI policy story.",
    color: "#e07b39",
  },
];

// Channel tactics
const CHANNELS = [
  {
    platform: "r/HiggsfieldAI",
    type: "owned",
    priority: "PRIMARY",
    current: "2,094 posts · avg score 4.8 · KLING 153 posts (avg 6.6) outscoring Higgsfield video model 46 posts (avg 2.6)",
    tactics: [
      "Establish posting guidelines: Higgsfield-first content. Competitor comparison posts allowed only with Higgsfield as the primary subject.",
      "Create 'HF Insider' flair for team/early-access posts — Announcements already avg 13.2 (highest in subreddit). Feed this archetype.",
      "Weekly Challenge thread every Monday (pinned). Gives casual users a reason to post on-topic content on a schedule.",
      "Tutorial/Workflow posts → target 6.0 avg (current Tips avg). Specific title formula: 'just figured out how to [specific outcome]'.",
      "Track weekly: avg score, % competitor-flaired posts (target <3%), % Showcase vs Insider+Tutorial.",
    ],
    postingFreq: "3–5× per week (owned subreddit: highest priority)",
    color: "#6366f1",
  },
  {
    platform: "YouTube",
    type: "owned",
    priority: "HIGH",
    current: "5.12% engagement rate vs Claude's 3.02% — content quality is there, discoverability is missing",
    tactics: [
      "10 SEO-optimized tutorials in 60 days. Title formula: '[specific filmmaker problem] — AI solution (step-by-step)'. Target: 'AI filmmaking workflow', 'consistent AI characters', 'AI green screen replacement'.",
      "Each tutorial ends with a specific limitation and workaround — this is the most engaging content type (Workaround avg beats Built_with_ avg).",
      "Thumbnail formula from Claude YouTube data: face + text overlay with specific claim. No abstract AI imagery.",
      "Upload Tue/Thu — optimal for algorithm pickup based on engagement timing data.",
      "Cross-promote to r/HiggsfieldAI same day: personal-story Reddit post about making the video.",
    ],
    postingFreq: "2× per week (Tue + Thu)",
    color: "#ef4444",
  },
  {
    platform: "Hacker News",
    type: "earned",
    priority: "HIGH",
    current: "0 Higgsfield posts vs Claude's 107k — entire developer credibility gap",
    tactics: [
      "First submission: 'Show HN: How we maintain consistent actor faces across AI video shots without per-person fine-tuning' — technical, specific, invites discussion.",
      "Second submission (Month 2): open-source evaluation framework for AI video quality — give engineers something to use.",
      "Submission timing: Tue 9–11am EST (peak HN traffic window). Don't submit Fridays or weekends.",
      "Direct DM to adocomplete (10 stories, 947 avg pts) and meetpateltech (27 stories, 368 avg pts) the day before with a 1-sentence pitch. These are enthusiasts, not gatekeepers.",
      "HN post must have: technical architecture, real numbers, honest tradeoffs, open question at the end.",
    ],
    postingFreq: "1× per month (quality over volume — selectivity = higher avg pts)",
    color: "#f59e0b",
  },
  {
    platform: "X / Twitter",
    type: "earned",
    priority: "MEDIUM",
    current: "EHuanglu dependency: 69.4% of community views. Higgsfield official account untested at scale.",
    tactics: [
      "Official X account: post at Tue–Thu 14:00–19:00 UTC (Claude peak engagement window from timeline data).",
      "Format mix: 70% video clips with specific outcome text overlay, 30% text threads with data/findings.",
      "Title formula applies here too: open with 'just' or 'when' — not brand name.",
      "Amplifier strategy: identify 5 film/VFX creators with 100k–500k followers. Give early access, exclusive content previews. Goal: reduce EHuanglu dependency from 69.4% to <30% within 6 months.",
      "When Hollywood AI news spikes (WGA, SAG, studio policy): have pre-drafted Higgsfield position ready to deploy within 4h.",
    ],
    postingFreq: "1× per day (official account) + amplifier network posts",
    color: "#818cf8",
  },
  {
    platform: "Reddit (Shared Subs)",
    type: "borrowed",
    priority: "LOW",
    current: "r/generativeAI, r/aivideo, r/filmmakers — Higgsfield competes with Runway and Sora for the same feed",
    tactics: [
      "Cross-post ONLY after content has hit r/HiggsfieldAI and performed (score ≥10). Never as first destination.",
      "Title format for shared subs must be more generic — remove Higgsfield brand from opener. Lead with the outcome or the problem.",
      "r/filmmakers is the highest-ROI shared sub: 1.5M members, film professionals, responds to F1/F5 formats.",
      "r/aivideo posts should be Competitor Comparison format — this is where the Higgsfield vs Kling battle is happening organically.",
      "Track shared vs owned ratio weekly. If shared sub posts score higher than owned, investigate why — content may be too brand-focused for owned community.",
    ],
    postingFreq: "2–3× per week (selected top-performing r/HiggsfieldAI posts only)",
    color: "#22c55e",
  },
];

// Content formats
const FORMATS = [
  {
    number: "F1",
    name: "Filmmaker Insider Reveal",
    archetype: "Insider Leak / Reveal",
    avgScore: "102",
    claudeData: "n=230 posts · avg 102 · scarcest high-ROI archetype (only 0.3% of all Reddit posts)",
    why: "4.25× better than Capability Demo (avg 24). Rare because it requires genuine access. Most brands never produce this. The post that performs isn't about Higgsfield — it's about a filmmaker's real experience using it on a real project with honest failures included.",
    template: `Opening (story hook, 'just' or 'i'm'):
"I'm a VFX supervisor at [studio]. We used Higgsfield on [real project type]. Here's what actually happened:"

Body (4 honest data points):
— What worked: [specific capability + time saved/cost saved]
— What broke: [specific failure with context]
— Cost vs. traditional production: [real $ numbers]
— Would I use it again: [verdict with condition]

Close (invite engagement):
"Happy to answer specific questions about [use case]. Anyone else tried this for [adjacent problem]?"`,
    titleFormula: "70–130 chars · open with 'I'm a [credential]' or 'just used Higgsfield on [real context]' · state the honest outcome in the title",
    exampleTitle: "I'm a VFX supervisor. We used AI video for the first time on a paid shoot. Here's the honest breakdown — what it saved and what it broke.",
    targeting: "S1 (Film/VFX Professionals) — recruit them, give them early access, let them post authentically",
    platforms: ["r/HiggsfieldAI", "r/VFX", "r/Filmmakers"],
    color: "#a855f7",
  },
  {
    number: "F2",
    name: "Production Breakdown (HN Format)",
    archetype: "Model Release / Technical",
    avgScore: "242 (HN)",
    claudeData: "HN: Model Release avg 242 pts · n=1,187 · best HN archetype in dataset",
    why: "Technical depth is what HN rewards. This is not a demo — it's an architecture writeup. Claude's highest-scoring HN content explains HOW something works, invites critique, and treats the reader as an engineer. The HN audience shares this in engineering Slack channels and developer Discord servers.",
    template: `HN Title: "Show HN: [specific technical problem we solved]"

Opening: Why this problem is hard
Technical approach: [actual method, no marketing language]
Results: [specific measurable outcomes]
Tradeoffs: [what you lose, what breaks at scale]
Open question: [genuine unresolved problem — invites expert comments]

Reddit version of the same post:
"just figured out how to [specific outcome]"
[same content, shorter, story format]`,
    titleFormula: "HN: 'Show HN: How we [solved specific technical problem]' · Reddit: 'just figured out [specific capability]' — different platform, same content, different opener",
    exampleTitle: "Show HN: How we maintain consistent actor identity across AI video shots without per-person fine-tuning",
    targeting: "S3 (Technical/Developer Audience) — reaches engineers who influence enterprise adoption",
    platforms: ["HN (Show HN)", "r/MachineLearning", "r/HiggsfieldAI"],
    color: "#06b6d4",
  },
  {
    number: "F3",
    name: "Competitor Comparison",
    archetype: "Controversy / Data-Driven",
    avgScore: "+56% lift",
    claudeData: "Reddit competitor-mention posts avg 28 vs 18 for solo-brand posts (56% lift). 'kling' already in Higgsfield wordcloud — community is doing this organically.",
    why: "The community in r/HiggsfieldAI is already posting KLING content (153 posts, avg 6.6). Higgsfield scores 2.6 with its own model flair in its own subreddit. A structured, data-backed Higgsfield vs Kling comparison would surface in both communities simultaneously and take ownership of the comparison the community is already making.",
    template: `"Tested Higgsfield vs [Kling/Runway/Sora] on [specific use case]: [verdict in title]

Test setup:
— Same prompt, both tools, [N] runs
— Evaluation criteria: [specific metrics]
— Hardware/tier: [context for reproducibility]

Results:
— [Specific outcome 1 with numbers]
— [Specific outcome 2 with numbers]
— Where Higgsfield wins: [honest]
— Where it loses: [honest]

Conclusion: [verdict with use-case specificity]"`,
    titleFormula: "Include competitor name. Include specific test methodology. State the verdict in the title — readers must know what the result is before clicking.",
    exampleTitle: "Higgsfield vs Kling on cinematic action sequences: I ran 50 prompts. Full breakdown with scores.",
    targeting: "S2 (Creator/AI Hobbyist) + S1 (Film/VFX Pros) — both communities follow the Kling vs Higgsfield debate",
    platforms: ["r/HiggsfieldAI", "r/aivideo", "r/generativeAI"],
    color: "#f59e0b",
  },
  {
    number: "F4",
    name: "Constraint / Workaround",
    archetype: "Workaround",
    avgScore: "16.8",
    claudeData: "Workaround flair avg 16.8 beats Built_with_Claude flair (15.7). 'limit' is one of top words in Claude top-500 post wordcloud. Community engages more with what AI can't do than with what it can — because they've personally hit the same wall.",
    why: "The honest limitation post performs better than the showcase because it's useful. The reader has already hit the same wall and is searching for a solution. Claude's community generates workaround content organically — it's the second most discoverable content type. Higgsfield has almost none.",
    template: `"Higgsfield [specific limitation] — here's the workaround

Problem: [what breaks, why it breaks, what you were trying to do]

Workaround: [specific technique with exact steps]
Step 1: [concrete action]
Step 2: [concrete action]
Step 3: [concrete action]

Result: [before/after — specific, not vague]

Trade-off: [what you lose with this method]

[Optional: link to example output]"`,
    titleFormula: "Name the constraint explicitly in the title. Promise the solution. Be honest about the trade-off. Users searching for this problem will find it via search.",
    exampleTitle: "Higgsfield struggles with long-take tracking shots — here's how I get consistent motion with 3-second clips + transition technique.",
    targeting: "S2 (Creator Community) — high-value search traffic, long-tail discovery from people hitting the same problem",
    platforms: ["r/HiggsfieldAI", "r/aivideo"],
    color: "#22c55e",
  },
  {
    number: "F5",
    name: "Industry Stance",
    archetype: "Controversy / Stance",
    avgScore: "102",
    claudeData: "Controversy/Stance archetype avg 102 — ties with Insider Reveal for highest in dataset. Dario's DoW statement: 18.5M views. Pete Hegseth response: 17.6M. Position-taking at scale beats product announcements by 3.5×.",
    why: "The entertainment industry is in a live fight about AI. WGA and SAG-AFTRA have active AI policies. Trade press is covering it weekly. Claude rode the policy conversation to 17.6M views by having something specific to say. Higgsfield is the only AI video company that could say something credible from a filmmaking perspective — not from an AI company perspective.",
    template: `"[Clear, specific position on AI + filmmaking]

Context: I've used Higgsfield on [real project context]
What I actually found: [specific data point or observation]

The claim I'm pushing back on: [specific industry claim]

Why I think it's more nuanced:
— [Specific point 1]
— [Specific point 2]
— [Evidence from real experience]

The question that actually matters isn't [common framing].
It's [better framing]."`,
    titleFormula: "State the position directly in the title. Don't soften it. 'I think [controversial claim]' → works. 'Some perspectives on AI...' → doesn't. Emotional trigger BREAKING has 2.7× lift — use urgency framing when the moment is live.",
    exampleTitle: "AI video isn't replacing cinematographers. It's replacing the $500/day rental equipment decisions. Here's why that's a completely different problem.",
    targeting: "S4 (Industry Press/Policy Layer) + S1 (Film Professionals) — enter conversations that are already happening at scale",
    platforms: ["r/Filmmakers", "r/movies", "HN", "X (during news spikes)"],
    color: "#ef4444",
  },
  {
    number: "F6",
    name: "Narrative Surfing Post",
    archetype: "Third-Party Validation / Controversy",
    avgScore: "9.3× boost (DeepSeek lesson)",
    claudeData: "DeepSeek mentions gave Claude tweets 9.3× view boost (2.8M vs 0.3M baseline) during the Jan–Feb 2026 news cycle. The mechanism: content gets surfaced to everyone following the larger story.",
    why: "The Hollywood AI story is live and mainstream. When WGA or SAG-AFTRA announces a new AI policy, trade press runs it. Mainstream press sometimes picks it up. The audience for that story is orders of magnitude larger than Higgsfield's current follower base. A post with something credible to say inside that conversation gets surfaced to all of them — for hours, until the news cycle moves on.",
    template: `[Triggered by a specific news event — pre-drafted, deployed within 2–4h]

"[React to specific event] — here's what this means from an actual filmmaker's perspective:

[1–2 sentence honest reaction with specificity]

What I can tell you from using AI video tools:
— [Specific data point from Higgsfield experience]
— [Honest limitation that's relevant to the policy debate]
— [What the policy gets right / wrong based on actual use]

The conversation should be about [reframe that positions Higgsfield credibly]."`,
    titleFormula: "Reference the news event directly. Lead with the filmmaker/creator perspective. Have this drafted BEFORE the news breaks — preparation window is 2–4h, not 24h.",
    exampleTitle: "SAG-AFTRA just updated their AI video policy. I've been using AI video tools for 6 months. Here's what the policy gets right and what it misses.",
    targeting: "All segments + new audience carried by the news cycle",
    platforms: ["X (primary, within 2h of news)", "r/Filmmakers", "r/movies", "HN if technical angle"],
    color: "#818cf8",
  },
];

// Amplifier recruitment
const AMPLIFIER_PLAN = {
  problem: "69.4% of Higgsfield X views come from EHuanglu — one person. If they pivot to Sora or take a break, Higgsfield's X monthly views likely halve. Claude has 8+ independent amplifier voices. Each serves a different function.",
  claudeModel: [
    { role: "Depth engine", account: "AnthropicAI", function: "580M total views · 923 tweets · drives official narrative" },
    { role: "Technical credibility", account: "karpathy / rubenhassid", function: "6–8 posts each · avg 1.8M+ · reaches developer and researcher audiences" },
    { role: "Cross-industry signal", account: "SenSanders / andrewchen", function: "Non-AI audiences · makes Claude feel culturally significant, not just tech-relevant" },
    { role: "Rapid surface", account: "ns123abc", function: "17 tweets · avg 2.4M · finds and surfaces breaking Anthropic stories fast" },
  ],
  higgsfieldTarget: [
    { role: "Technical filmmaker", criteria: "DoP or VFX supervisor, 50k–200k followers, posts technical creative content", how: "Early access + 'let us fund one shot for your next project'", timeline: "Week 5–6" },
    { role: "Indie director / creator", criteria: "YouTube filmmaker, 100k–500k subscribers, regularly reviews AI tools", how: "Exclusive feature preview 2 weeks before public launch", timeline: "Week 5–6" },
    { role: "AI video enthusiast", criteria: "Already in r/HiggsfieldAI, 20k–100k followers, posts weekly", how: "Moderator role + direct line to team for bug reports", timeline: "Week 1–2" },
    { role: "Industry insider", criteria: "Film school educator, trade journalist, film festival person", how: "Data from our corpus: real cost/workflow comparisons they can cite", timeline: "Week 7–8" },
    { role: "Cross-industry voice", criteria: "Non-film creator who uses video for business (course creator, event videographer)", how: "Free credits + use-case brief for their specific workflow", timeline: "Week 7–8" },
  ],
};

// Narrative moments to monitor
const NARRATIVE_TRIGGERS = [
  {
    trigger: "WGA / SAG-AFTRA AI policy update",
    probability: "High — active negotiations, regular updates",
    sources: "Variety, THR, Deadline Hollywood · r/movies · r/Screenwriting",
    predratedAngles: [
      "What AI video policy should actually require from AI companies (from a Higgsfield-user perspective)",
      "The real cost comparison: AI video vs. traditional production for indie vs. studio",
      "What fair attribution looks like for AI-assisted filmmaking (with Higgsfield's approach as example)",
    ],
    deployWindow: "2–4 hours after publication",
    expectedBoost: "3–10× based on DeepSeek mechanism (9.3× at peak news cycle)",
    color: "#ef4444",
  },
  {
    trigger: "Major AI video competitor launches or fails publicly",
    probability: "Medium-high — Sora, Runway, Pika releasing updates regularly",
    sources: "TechCrunch, The Verge, r/AIVideo · X trending",
    predratedAngles: [
      "Direct comparison: specific capability tested side-by-side with real outputs",
      "What the new model gets right that Higgsfield doesn't (honest — earns credibility)",
      "The capability that Higgsfield specifically beats on (with specific evidence)",
    ],
    deployWindow: "Within 4 hours — this is the competitor comparison archetype on a live news hook",
    expectedBoost: "56% score lift from competitor mention + news cycle amplification",
    color: "#f59e0b",
  },
  {
    trigger: "Major Hollywood studio announces AI policy or AI-made production",
    probability: "Medium — Netflix, Disney, A24 all have in-progress AI policies",
    sources: "THR, Variety, Wall Street Journal · LinkedIn (industry professionals)",
    predratedAngles: [
      "A filmmaker's view on what this means for independent production (not studio budgets)",
      "The specific workflow this enables that wasn't possible before",
      "What responsible disclosure looks like for AI-assisted content (Higgsfield's position)",
    ],
    deployWindow: "Same day — LinkedIn + X simultaneously, Reddit next day",
    expectedBoost: "High reach from industry audiences + potential press pickup (HN credibility primer needed first)",
    color: "#a855f7",
  },
];

// Execution calendar
const TIMING = [
  {
    week: "Week 1–2",
    phase: "Foundation",
    focus: "Fix the infrastructure before adding volume",
    color: "#6366f1",
    actions: [
      "Audit r/HiggsfieldAI flair policy — remove KLING/SORA/WAN competitor flairs or rename to 'AI Video Comparison' (current competitor flair avg 6.6 > Higgsfield video model avg 2.6 — competitors are winning in our own space)",
      "Post 10 foundation pieces to r/HiggsfieldAI: 4× Filmmaker Story (F1), 3× Constraint/Workaround (F4), 2× Production Breakdown (F2), 1× Competitor Comparison (F3)",
      "Apply title formula to every post: 70–130 chars, story hook opener ('just', 'when', 'i'm'). Benchmark: beat the 4.8 subreddit avg",
      "Identify top 10 r/HiggsfieldAI contributors by post count (BholaCoder 112, memerwala_londa 74, la_dehram 48) — offer moderator status to top 3",
      "Draft 3 pre-written narrative surfing posts (F6) for the 3 most likely news triggers. Store in drafts — don't publish yet",
    ],
  },
  {
    week: "Week 3–4",
    phase: "Content Volume",
    focus: "Establish posting rhythm, start YouTube, first HN attempt",
    color: "#a855f7",
    actions: [
      "Post 3× per week to r/HiggsfieldAI. Format mix: 2× F4 Constraint/Workaround (highest search traffic) + 1× F3 Competitor Comparison. Track score vs 4.8 baseline",
      "Launch first YouTube tutorial: 'AI filmmaking workflow for indie directors' — SEO title, specific outcome, workaround section included. Post on Tuesday",
      "Submit first Show HN: 'Show HN: How we maintain consistent actor identity across AI video shots without per-person fine-tuning'. DM adocomplete day before with 1-sentence pitch",
      "Start amplifier outreach — identify 5 film/VFX professionals, research their content, note their specific use cases. Don't reach out yet",
      "Cross-post top-performing r/HiggsfieldAI posts (score ≥10) to r/aivideo and r/generativeAI with modified titles",
    ],
  },
  {
    week: "Week 5–6",
    phase: "Amplification",
    focus: "Activate amplifiers, second YouTube video, narrative moment prep",
    color: "#f59e0b",
    actions: [
      "DM adocomplete and meetpateltech with second HN story pitch. Lead with outcome: 'we built an open-source quality eval framework for AI video — here's the repo and findings'",
      "Outreach to 3 film/VFX professionals (S1 segment): early access + specific project brief. Not 'try our tool' — 'we'll fund one shot for your next project using Higgsfield'",
      "Second YouTube tutorial: 'How to maintain character consistency in AI video — step-by-step'. Upload Thursday",
      "Post F5 Industry Stance piece if any Hollywood AI news event has occurred in the last 2 weeks — ride the narrative window",
      "Monitor: r/HiggsfieldAI avg score trending. If it's moved above 4.8, the archetype shift is working. If not, audit what's being posted",
    ],
  },
  {
    week: "Week 7–8",
    phase: "First Measurement",
    focus: "Measure what worked, kill what didn't, plan sprint 2",
    color: "#e07b39",
    actions: [
      "Pull metrics: r/HiggsfieldAI avg score (target >7), competitor content % (target <5%), YouTube avg views (target >20k), HN pts earned (target >100)",
      "Classify top 5 posts by score — what archetype were they? Format mix for next 8 weeks follows the winners, not the plan",
      "Kill any format averaging <8 score in r/HiggsfieldAI. No exceptions — the data tells you what the community actually values",
      "Amplifier check: have any of the 3 outreach contacts posted about Higgsfield? If not, send a follow-up with a fresh angle + exclusive asset",
      "HN check: if first submission didn't front-page, analyze what it got vs what front-paged that week. Adjust second submission accordingly",
    ],
  },
];

// Metrics
const METRICS = [
  {
    name: "r/HiggsfieldAI Avg Score",
    formula: "Mean score of all r/HiggsfieldAI posts in rolling 30-day window",
    now: "4.8",
    week8: "≥8",
    target: ">15",
    signal: "Below 4.8 sustained = archetype mix is wrong. Check Showcase % (currently 39%, avg 4.6) vs Announcement+Tutorial+Insider (13.2 avg). Announcement content is your highest-ROI category — produce more of it.",
    color: "#6366f1",
  },
  {
    name: "Competitor Content Ratio",
    formula: "KLING + SORA + competitor-flaired posts ÷ total r/HiggsfieldAI posts",
    now: "~8%",
    week8: "<4%",
    target: "<2%",
    signal: ">10% competitor content = the subreddit is being used as a neutral AI video forum, not a Higgsfield community. Enforce flair policy. Competitors scoring higher in our own subreddit (KLING 6.6 vs HF video model 2.6) is a community capture problem.",
    color: "#ef4444",
  },
  {
    name: "Archetype Distribution",
    formula: "% of posts classified as Insider Reveal + Controversy/Stance in trailing 30 days",
    now: "~0%",
    week8: ">10%",
    target: ">20%",
    signal: "<10% high-ROI archetypes 3 weeks running: the content team is defaulting to Showcase. Run an Insider Reveal workshop — brief a specific filmmaker on the format with a concrete ask.",
    color: "#a855f7",
  },
  {
    name: "HN Points Earned",
    formula: "Total HN points from Higgsfield-originated or Higgsfield-seeded submissions",
    now: "0",
    week8: ">50",
    target: "500+",
    signal: "0 HN points after 4 weeks = content is not technical enough for the platform. A Show HN needs an architecture, not a demo. 0 front-page stories after 2 submissions = the submission network hasn't been activated. DM adocomplete directly.",
    color: "#f59e0b",
  },
  {
    name: "YouTube Avg Views",
    formula: "Average views per video published in trailing 30 days",
    now: "33k",
    week8: ">40k",
    target: ">75k",
    signal: "If engagement rate stays >5% (it's already 5.12%) but views don't grow after Week 4: SEO problem, not content problem. Audit titles against YouTube search volume. If engagement rate drops below 4%: content quality regressing — return to specific outcome format.",
    color: "#22c55e",
  },
  {
    name: "Independent Amplifier Count",
    formula: "# of X accounts with >50k followers who posted positively about Higgsfield in trailing 30 days",
    now: "1",
    week8: "3",
    target: "≥5",
    signal: "1 amplifier = EHuanglu dependency unchanged. Reaching 2 means the outreach worked. Target 5 means reaching the Claude research-amplifier tier. Each independent voice is an insurance policy — if one pivots, the floor doesn't collapse.",
    color: "#e07b39",
  },
];

/* ─── components ─────────────────────────────────────────────────── */

function DataTag({ text }: { text: string }) {
  return (
    <span className="inline-block text-[9px] font-mono px-1.5 py-0.5 rounded border"
      style={{ borderColor: "#2a2a4a", background: "#0e0e18", color: "#5a5a7a" }}>
      ↗ {text}
    </span>
  );
}

function SectionLabel({ n, title, sub }: { n: string; title: string; sub?: string }) {
  return (
    <div className="mb-6">
      <div className="flex items-center gap-3 mb-1">
        <span className="font-mono text-[10px] font-bold px-2 py-1 rounded"
          style={{ background: "rgba(99,102,241,0.15)", color: "#818cf8" }}>
          {n}
        </span>
        <h2 className="text-2xl font-bold text-white">{title}</h2>
      </div>
      {sub && <p className="text-sm ml-14" style={{ color: "var(--muted)" }}>{sub}</p>}
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════ */
export default function PlaybookPage() {
  return (
    <div className="min-h-screen" style={{ background: "var(--background)" }}>
      <Nav />

      {/* HERO */}
      <section className="max-w-7xl mx-auto px-6 pt-16 pb-12">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-medium mb-6"
          style={{ borderColor: "rgba(224,123,57,0.4)", background: "rgba(224,123,57,0.06)", color: "#e07b39" }}>
          Part 4 · Counter-Playbook
        </div>
        <h1 className="text-4xl sm:text-5xl font-bold text-white leading-tight tracking-tight">
          The Higgsfield<br />
          <span style={{ color: "#e07b39" }}>Growth Counter-Playbook</span>
        </h1>
        <p className="mt-4 text-base max-w-2xl leading-relaxed" style={{ color: "var(--muted)" }}>
          3 mechanisms from Claude's viral playbook applied to Higgsfield. Channels, formats, audience targeting,
          narrative moments, amplifier recruitment, 8-week calendar, and 6 tracked metrics.
          Every recommendation connects back to something we actually found in the data.
        </p>
        <div className="mt-6 flex flex-wrap gap-2">
          {["84k Claude Reddit posts","107k HN stories","r/HiggsfieldAI n=2,094","5.12% YouTube engagement","Archetype corpus n=74k","Title lift n=74k posts"].map((tag) => (
            <span key={tag} className="font-mono text-[10px] px-2.5 py-1 rounded border"
              style={{ borderColor: "var(--border)", color: "var(--muted)" }}>
              {tag}
            </span>
          ))}
        </div>
      </section>

      {/* ── SECTION 1: THE CORE THESIS ── */}
      <section className="border-t" style={{ borderColor: "var(--border)" }}>
        <div className="max-w-7xl mx-auto px-6 py-12">
          <SectionLabel n="01" title="3 Mechanisms to Replicate"
            sub="Claude's viral growth runs on identifiable, repeatable mechanics. These are the three we can directly apply to Higgsfield." />
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
            {MECHANISMS.map((m) => (
              <div key={m.number} className="rounded-xl border p-6"
                style={{ borderColor: m.color + "30", background: m.color + "06" }}>
                <div className="flex items-center gap-3 mb-4">
                  <span className="font-mono text-xs font-bold px-2 py-1 rounded"
                    style={{ background: m.color + "20", color: m.color }}>{m.number}</span>
                  <span className="text-sm font-bold text-white">{m.name}</span>
                </div>
                <div className="space-y-3">
                  <div>
                    <div className="text-[10px] font-semibold uppercase tracking-wider mb-1" style={{ color: "var(--muted)" }}>Claude data</div>
                    <p className="text-xs font-mono leading-relaxed" style={{ color: m.color + "cc" }}>{m.claude}</p>
                  </div>
                  <div>
                    <div className="text-[10px] font-semibold uppercase tracking-wider mb-1" style={{ color: "var(--muted)" }}>Why it works</div>
                    <p className="text-sm leading-relaxed" style={{ color: "#c4c4d0" }}>{m.insight}</p>
                  </div>
                  <div className="rounded-lg p-3 border-l-2" style={{ borderColor: m.color, background: m.color + "0a" }}>
                    <div className="text-[10px] font-semibold uppercase tracking-wider mb-1" style={{ color: m.color }}>For Higgsfield</div>
                    <p className="text-xs leading-relaxed" style={{ color: "#a0a0c0" }}>{m.higgsfield}</p>
                  </div>
                  <DataTag text={m.data} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── SECTION 2: AUDIENCE TARGETING ── */}
      <section className="border-t" style={{ borderColor: "var(--border)" }}>
        <div className="max-w-7xl mx-auto px-6 py-12">
          <SectionLabel n="02" title="Audience Targeting"
            sub="4 segments with different channels, content types, and recruitment strategies. Claude's amplifier stack has 8+ independent voices serving different functions — Higgsfield has 1." />
          <div className="space-y-4">
            {SEGMENTS.map((s) => (
              <div key={s.id} className="rounded-xl border p-6 grid grid-cols-1 lg:grid-cols-5 gap-5"
                style={{ borderColor: s.color + "30", background: s.color + "06" }}>
                <div>
                  <div className="font-mono text-xs font-bold mb-1" style={{ color: s.color }}>{s.id}</div>
                  <div className="text-sm font-bold text-white mb-1">{s.name}</div>
                  <div className="font-mono text-[10px]" style={{ color: "var(--muted)" }}>{s.size}</div>
                </div>
                <div>
                  <div className="text-[10px] font-semibold uppercase tracking-wider mb-1" style={{ color: "var(--muted)" }}>Who they are</div>
                  <p className="text-xs leading-relaxed" style={{ color: "#c4c4d0" }}>{s.description}</p>
                </div>
                <div>
                  <div className="text-[10px] font-semibold uppercase tracking-wider mb-1" style={{ color: "var(--muted)" }}>Channels</div>
                  <ul className="space-y-0.5">
                    {s.channels.map((c) => (
                      <li key={c} className="text-xs font-mono" style={{ color: s.color + "cc" }}>· {c}</li>
                    ))}
                  </ul>
                  <div className="mt-2 text-[10px] font-semibold uppercase tracking-wider mb-0.5" style={{ color: "var(--muted)" }}>Content type</div>
                  <p className="text-xs font-mono" style={{ color: "#6a6a8a" }}>{s.contentType}</p>
                </div>
                <div>
                  <div className="text-[10px] font-semibold uppercase tracking-wider mb-1" style={{ color: "var(--muted)" }}>Recruit strategy</div>
                  <p className="text-xs leading-relaxed" style={{ color: "#c4c4d0" }}>{s.recruitStrategy}</p>
                </div>
                <div>
                  <div className="text-[10px] font-semibold uppercase tracking-wider mb-1" style={{ color: "var(--muted)" }}>Why this segment</div>
                  <p className="text-xs leading-relaxed" style={{ color: "#7a7a9a" }}>{s.why}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── SECTION 3: CHANNEL STRATEGY ── */}
      <section className="border-t" style={{ borderColor: "var(--border)" }}>
        <div className="max-w-7xl mx-auto px-6 py-12">
          <SectionLabel n="03" title="Channel Strategy"
            sub="5 channels ranked by ROI, with specific tactics per channel. Owned channels first. Earned last." />
          <div className="space-y-4">
            {CHANNELS.map((ch) => (
              <div key={ch.platform} className="rounded-xl border overflow-hidden"
                style={{ borderColor: "var(--border)", background: "#0e0e18" }}>
                <div className="px-6 py-4 border-b flex items-center justify-between"
                  style={{ borderColor: "var(--border)", background: ch.color + "08" }}>
                  <div className="flex items-center gap-4">
                    <span className="font-mono text-sm font-bold" style={{ color: ch.color }}>{ch.platform}</span>
                    <span className="text-xs px-2 py-0.5 rounded border font-mono uppercase tracking-wider"
                      style={{
                        borderColor: ch.type === "owned" ? "#22c55e40" : ch.type === "earned" ? "#f59e0b40" : "#6b728040",
                        color: ch.type === "owned" ? "#22c55e" : ch.type === "earned" ? "#f59e0b" : "#6b7280",
                      }}>
                      {ch.type}
                    </span>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="font-mono text-[10px] font-bold px-2 py-0.5 rounded"
                      style={{ background: ch.color + "20", color: ch.color }}>{ch.priority}</span>
                    <span className="text-[10px] font-mono" style={{ color: "var(--muted)" }}>freq: {ch.postingFreq}</span>
                  </div>
                </div>
                <div className="p-6 grid grid-cols-1 lg:grid-cols-3 gap-5">
                  <div>
                    <div className="text-[10px] font-semibold uppercase tracking-wider mb-2" style={{ color: "var(--muted)" }}>Current state</div>
                    <p className="text-xs leading-relaxed font-mono" style={{ color: ch.color + "aa" }}>{ch.current}</p>
                  </div>
                  <div className="lg:col-span-2">
                    <div className="text-[10px] font-semibold uppercase tracking-wider mb-2" style={{ color: "var(--muted)" }}>Specific tactics</div>
                    <ul className="space-y-1.5">
                      {ch.tactics.map((t, i) => (
                        <li key={i} className="flex items-start gap-2 text-xs leading-relaxed" style={{ color: "#9a9ab8" }}>
                          <span style={{ color: ch.color, marginTop: 2 }}>›</span> {t}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── SECTION 4: CONTENT FORMATS ── */}
      <section className="border-t" style={{ borderColor: "var(--border)" }}>
        <div className="max-w-7xl mx-auto px-6 py-12">
          <SectionLabel n="04" title="Content Format Playbook"
            sub="6 formats derived from Claude's archetype data. Each has a ready-to-use template, a title formula, and targeting specification. Avg score = from Reddit archetype analysis (n=74k posts)." />
          <p className="text-xs font-mono mb-8 -mt-4" style={{ color: "#4a4a6a" }}>
            opening word 'just' = 638× lift · 'claude/higgsfield' as opener = 1.26× · title sweet spot 70–130 chars · copy formula from 74k Reddit posts
          </p>
          <div className="space-y-6">
            {FORMATS.map((f) => (
              <div key={f.number} className="rounded-xl border overflow-hidden"
                style={{ borderColor: "var(--border)", background: "#0e0e18" }}>
                <div className="px-6 py-4 border-b flex items-center justify-between"
                  style={{ borderColor: "var(--border)", background: f.color + "08" }}>
                  <div className="flex items-center gap-4">
                    <span className="font-mono text-sm font-bold" style={{ color: f.color }}>{f.number}</span>
                    <div>
                      <div className="text-sm font-bold text-white">{f.name}</div>
                      <div className="text-[10px] font-mono mt-0.5" style={{ color: "var(--muted)" }}>
                        archetype: {f.archetype} · targeting: {f.targeting}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-white">{f.avgScore}</div>
                    <div className="text-xs" style={{ color: "var(--muted)" }}>avg score / boost</div>
                  </div>
                </div>
                <div className="px-6 py-3 border-b" style={{ borderColor: "var(--border)", background: "rgba(255,255,255,0.015)" }}>
                  <div className="text-[9px] font-mono" style={{ color: "#5a5a7a" }}>DATA: {f.claudeData}</div>
                </div>
                <div className="p-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
                  <div className="space-y-3">
                    <div>
                      <div className="text-[10px] font-semibold uppercase tracking-wider mb-1" style={{ color: "var(--muted)" }}>Why it works</div>
                      <p className="text-sm leading-relaxed" style={{ color: "#c4c4d0" }}>{f.why}</p>
                    </div>
                    <div>
                      <div className="text-[10px] font-semibold uppercase tracking-wider mb-1" style={{ color: "var(--muted)" }}>Post to</div>
                      <div className="flex flex-wrap gap-1">
                        {f.platforms.map((p) => (
                          <span key={p} className="text-xs px-2 py-0.5 rounded border font-mono"
                            style={{ borderColor: f.color + "40", color: f.color, background: f.color + "0a" }}>
                            {p}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                  <div>
                    <div className="text-[10px] font-semibold uppercase tracking-wider mb-2" style={{ color: "var(--muted)" }}>Post template</div>
                    <pre className="text-xs leading-relaxed p-3 rounded border whitespace-pre-wrap"
                      style={{ borderColor: f.color + "30", background: f.color + "06", color: "#9a9ab8", fontFamily: "monospace" }}>
                      {f.template}
                    </pre>
                  </div>
                  <div className="space-y-4">
                    <div>
                      <div className="text-[10px] font-semibold uppercase tracking-wider mb-1" style={{ color: "var(--muted)" }}>Title formula</div>
                      <p className="text-xs leading-relaxed" style={{ color: "#7a7a9a" }}>{f.titleFormula}</p>
                    </div>
                    <div className="rounded p-3 border-l-2" style={{ borderColor: f.color, background: "rgba(255,255,255,0.02)" }}>
                      <div className="text-[9px] uppercase tracking-wider mb-1" style={{ color: "var(--muted)" }}>Example title</div>
                      <p className="text-xs italic" style={{ color: "#c4c4d0" }}>{f.exampleTitle}</p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── SECTION 5: AMPLIFIER RECRUITMENT ── */}
      <section className="border-t" style={{ borderColor: "var(--border)" }}>
        <div className="max-w-7xl mx-auto px-6 py-12">
          <SectionLabel n="05" title="Amplifier Recruitment"
            sub="Claude has 8+ independent amplifier voices, each serving a different distribution function. Higgsfield has 1. This is a structural risk and a strategic opportunity." />

          {/* The problem */}
          <div className="rounded-xl border p-5 mb-6" style={{ borderColor: "#ef444440", background: "rgba(239,68,68,0.06)" }}>
            <p className="text-sm" style={{ color: "#c4c4d0" }}>{AMPLIFIER_PLAN.problem}</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Claude model */}
            <div>
              <div className="text-xs font-semibold uppercase tracking-widest mb-3" style={{ color: "var(--muted)" }}>
                Claude's amplifier model (what we are copying)
              </div>
              <div className="space-y-2">
                {AMPLIFIER_PLAN.claudeModel.map((a) => (
                  <div key={a.account} className="rounded-lg border p-3 grid grid-cols-3 gap-3"
                    style={{ borderColor: "var(--border)", background: "#0e0e18" }}>
                    <div className="text-xs font-mono font-bold" style={{ color: "#6366f1" }}>{a.role}</div>
                    <div className="text-xs font-mono" style={{ color: "#818cf8" }}>{a.account}</div>
                    <div className="text-[10px]" style={{ color: "var(--muted)" }}>{a.function}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Higgsfield target */}
            <div>
              <div className="text-xs font-semibold uppercase tracking-widest mb-3" style={{ color: "#e07b39" }}>
                Higgsfield target amplifier stack (build in 8 weeks)
              </div>
              <div className="space-y-2">
                {AMPLIFIER_PLAN.higgsfieldTarget.map((a) => (
                  <div key={a.role} className="rounded-lg border p-3"
                    style={{ borderColor: "#e07b3930", background: "rgba(224,123,57,0.04)" }}>
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-xs font-bold" style={{ color: "#e07b39" }}>{a.role}</span>
                      <span className="font-mono text-[9px] px-1.5 py-0.5 rounded" style={{ background: "rgba(224,123,57,0.15)", color: "#e07b39" }}>
                        {a.timeline}
                      </span>
                    </div>
                    <div className="text-[10px] mb-1" style={{ color: "var(--muted)" }}>Criteria: {a.criteria}</div>
                    <div className="text-[10px]" style={{ color: "#9a9ab8" }}>How: {a.how}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── SECTION 6: NARRATIVE MOMENTS ── */}
      <section className="border-t" style={{ borderColor: "var(--border)" }}>
        <div className="max-w-7xl mx-auto px-6 py-12">
          <SectionLabel n="06" title="Narrative Moment Calendar"
            sub="Claude's #1 viral moment was a threat disclosure (33.6M views). DeepSeek gave Claude a 9.3× X view boost by being in the right conversation at the right time. The Hollywood AI story is Higgsfield's equivalent — it's live, mainstream, and Higgsfield is the only credible participant." />

          <div className="space-y-4">
            {NARRATIVE_TRIGGERS.map((n) => (
              <div key={n.trigger} className="rounded-xl border overflow-hidden"
                style={{ borderColor: n.color + "35" }}>
                <div className="px-5 py-3 flex items-center gap-3" style={{ background: n.color + "10" }}>
                  <span className="w-2 h-2 rounded-full" style={{ background: n.color }} />
                  <span className="text-sm font-bold text-white">{n.trigger}</span>
                  <span className="ml-auto font-mono text-[10px]" style={{ color: n.color }}>{n.probability}</span>
                </div>
                <div className="p-5 grid grid-cols-1 lg:grid-cols-4 gap-5">
                  <div>
                    <div className="text-[10px] font-semibold uppercase tracking-wider mb-1" style={{ color: "var(--muted)" }}>Monitor these sources</div>
                    <p className="text-xs font-mono leading-relaxed" style={{ color: n.color + "cc" }}>{n.sources}</p>
                    <div className="mt-3 text-[10px] font-semibold uppercase tracking-wider mb-1" style={{ color: "var(--muted)" }}>Deploy window</div>
                    <p className="text-xs font-mono" style={{ color: "#9a9ab8" }}>{n.deployWindow}</p>
                    <div className="mt-2 text-[10px] font-semibold uppercase tracking-wider mb-1" style={{ color: "var(--muted)" }}>Expected boost</div>
                    <p className="text-xs font-mono" style={{ color: n.color }}>{n.expectedBoost}</p>
                  </div>
                  <div className="lg:col-span-3">
                    <div className="text-[10px] font-semibold uppercase tracking-wider mb-2" style={{ color: "var(--muted)" }}>Pre-drafted angles (write now, publish when triggered)</div>
                    <div className="space-y-2">
                      {n.predratedAngles.map((a, i) => (
                        <div key={i} className="flex items-start gap-2 text-xs p-2 rounded border"
                          style={{ borderColor: n.color + "20", background: n.color + "06", color: "#9a9ab8" }}>
                          <span className="font-mono text-[10px] shrink-0 mt-px" style={{ color: n.color }}>angle {i + 1}</span>
                          <span>{a}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── SECTION 7: 8-WEEK CALENDAR ── */}
      <section className="border-t" style={{ borderColor: "var(--border)" }}>
        <div className="max-w-7xl mx-auto px-6 py-12">
          <SectionLabel n="07" title="8-Week Execution Calendar"
            sub="Foundation first. Volume second. Amplification third. Measure at Week 8 — kill what didn't work, double down on what did." />
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {TIMING.map((t) => (
              <div key={t.week} className="rounded-xl border p-5"
                style={{ borderColor: t.color + "30", background: t.color + "05" }}>
                <div className="flex items-center gap-2 mb-2">
                  <span className="font-mono text-[10px] font-bold px-2 py-0.5 rounded"
                    style={{ background: t.color + "20", color: t.color }}>{t.week}</span>
                </div>
                <div className="text-sm font-bold text-white mb-0.5">{t.phase}</div>
                <div className="text-[10px] mb-3 italic" style={{ color: "var(--muted)" }}>{t.focus}</div>
                <ul className="space-y-2">
                  {t.actions.map((a, i) => (
                    <li key={i} className="flex items-start gap-1.5 text-[11px] leading-relaxed" style={{ color: "#7a7a9a" }}>
                      <span style={{ color: t.color, marginTop: 2 }}>·</span>
                      {a}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── SECTION 8: METRICS ── */}
      <section className="border-t" style={{ borderColor: "var(--border)" }}>
        <div className="max-w-7xl mx-auto px-6 py-12">
          <SectionLabel n="08" title="Metrics That Matter"
            sub="6 metrics directly derived from the data. Each has a Week 8 milestone and an alert that tells you what to do — not just what happened." />
          <div className="space-y-3">
            {METRICS.map((m) => (
              <div key={m.name} className="rounded-xl border p-5 grid grid-cols-1 lg:grid-cols-6 gap-4 items-start"
                style={{ borderColor: "var(--border)", background: "#0e0e18" }}>
                <div className="lg:col-span-2">
                  <div className="text-xs font-semibold uppercase tracking-wider mb-1" style={{ color: m.color }}>{m.name}</div>
                  <div className="font-mono text-[10px] leading-relaxed" style={{ color: "var(--muted)" }}>{m.formula}</div>
                </div>
                <div className="text-center">
                  <div className="text-[10px] uppercase tracking-wider mb-1" style={{ color: "var(--muted)" }}>Now</div>
                  <div className="text-xl font-bold" style={{ color: "#ef4444" }}>{m.now}</div>
                </div>
                <div className="text-center">
                  <div className="text-[10px] uppercase tracking-wider mb-1" style={{ color: "var(--muted)" }}>Week 8</div>
                  <div className="text-xl font-bold" style={{ color: "#f59e0b" }}>{m.week8}</div>
                </div>
                <div className="text-center">
                  <div className="text-[10px] uppercase tracking-wider mb-1" style={{ color: "var(--muted)" }}>Target</div>
                  <div className="text-xl font-bold" style={{ color: "#22c55e" }}>{m.target}</div>
                </div>
                <div>
                  <div className="text-[10px] font-semibold uppercase tracking-wider mb-1" style={{ color: "var(--muted)" }}>Alert / action</div>
                  <p className="text-xs leading-relaxed" style={{ color: "#7a7a9a" }}>{m.signal}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* DATA TRAIL */}
      <section className="border-t" style={{ borderColor: "var(--border)", background: "#0a0a12" }}>
        <div className="max-w-7xl mx-auto px-6 py-10">
          <div className="text-xs font-semibold uppercase tracking-widest mb-4" style={{ color: "var(--muted)" }}>
            Data Trail — Every recommendation traced to its source
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 font-mono text-[10px]">
            {[
              ["Insider Reveal avg 102", "Reddit corpus, archetype classifier, n=230 posts"],
              ["Capability Demo avg 24", "Reddit corpus, archetype classifier, n=1,208 posts"],
              ["Threat disclosure 33.6M vs launch 5M (6.7×)", "Top 20 viral moments table, Anthropic accounts + r/ClaudeAI"],
              ["Competitor mention +56%", "Reddit corpus, 2,098 competitor posts vs 71,914 solo"],
              ["Opening word 'just' 638×", "Reddit title analysis, top-10% viral vs baseline (n=74k)"],
              ["Title sweet spot 70–130 chars", "Reddit score vs title length, n=74k posts"],
              ["Workaround flair avg 16.8", "Reddit flair engagement, n=1,937 workaround posts"],
              ["HN Model Release avg 242 pts", "HN corpus, archetype breakdown, n=1,187 posts"],
              ["HN adocomplete 947 avg pts (10 stories)", "HN top submitters chart, selectivity vs volume analysis"],
              ["YouTube engagement 5.12% vs Claude 3.02%", "YouTube scrape, Higgsfield channel (likes+comments÷views)"],
              ["r/HiggsfieldAI 2,094 posts · avg 4.8 · KLING 153 posts avg 6.6", "r/HiggsfieldAI scrape (n=2,094). Flair breakdown analysis."],
              ["EHuanglu: 69.4% of Higgsfield X views", "X amplifier scrape, official vs community split (cmp_07)"],
              ["DeepSeek 9.3× X view boost", "X competitor timeline, Jan–Feb 2026 (Anthropic account scrape)"],
              ["Announcement flair avg 13.2 (highest in r/HiggsfieldAI)", "r/HiggsfieldAI flair analysis, n=33 announcement posts"],
              ["Claude Reddit 11.5× growth in 12 months", "r/ClaudeAI monthly post volume chart, cmp_02"],
            ].map(([claim, source]) => (
              <div key={claim} className="flex gap-2 items-start">
                <span style={{ color: "#4a4a6a", marginTop: 1 }}>→</span>
                <div>
                  <div style={{ color: "#8a8ab0" }}>{claim}</div>
                  <div style={{ color: "#4a4a6a" }}>{source}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <footer className="border-t" style={{ borderColor: "var(--border)" }}>
        <div className="max-w-7xl mx-auto px-6 py-8 flex items-center justify-between">
          <span className="text-xs" style={{ color: "var(--muted)" }}>HackNU 2026 · Part 4 · Counter-Playbook for Higgsfield</span>
          <span className="text-xs" style={{ color: "var(--muted)" }}>8 sections · 6 metrics · 15 data citations · every claim sourced</span>
        </div>
      </footer>
    </div>
  );
}
