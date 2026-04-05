import Nav from "@/components/Nav";

/* ─── colour tokens ─────────────────────────────────────────── */
const C = {
  ingest:    { border: "#00b4d8", bg: "rgba(0,180,216,0.07)",   text: "#00b4d8" },
  process:   { border: "#a855f7", bg: "rgba(168,85,247,0.07)",  text: "#a855f7" },
  router:    { border: "#f59e0b", bg: "rgba(245,158,11,0.07)",  text: "#f59e0b" },
  realtime:  { border: "#ef4444", bg: "rgba(239,68,68,0.07)",   text: "#ef4444" },
  scheduled: { border: "#22c55e", bg: "rgba(34,197,94,0.07)",   text: "#22c55e" },
  measure:   { border: "#6366f1", bg: "rgba(99,102,241,0.07)",  text: "#818cf8" },
};

/* ─── node component ─────────────────────────────────────────── */
function Node({
  title, status = "running", freq, vol, lines, color, wide = false,
}: {
  title: string; status?: string; freq?: string; vol?: string;
  lines: string[]; color: typeof C.ingest; wide?: boolean;
}) {
  const statusColor = status === "running" ? "#22c55e" : status === "triggered" ? "#f59e0b" : "#6b7280";
  return (
    <div
      className={`rounded-lg border font-mono flex flex-col gap-2 ${wide ? "w-full" : "flex-1 min-w-0"}`}
      style={{ borderColor: color.border + "60", background: color.bg, padding: "14px 16px" }}
    >
      {/* header row */}
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <span className="w-1.5 h-1.5 rounded-full shrink-0" style={{ background: statusColor }} />
          <span className="text-[11px] font-bold uppercase tracking-widest truncate" style={{ color: color.text }}>
            {title}
          </span>
        </div>
        <span className="text-[9px] uppercase tracking-wider shrink-0" style={{ color: statusColor }}>
          {status}
        </span>
      </div>
      {/* stats row */}
      {(freq || vol) && (
        <div className="flex gap-3 border-t pt-2" style={{ borderColor: color.border + "25" }}>
          {freq && (
            <span className="text-[9px]" style={{ color: "#4a4a6a" }}>
              <span style={{ color: "#6a6a8a" }}>freq</span> {freq}
            </span>
          )}
          {vol && (
            <span className="text-[9px]" style={{ color: "#4a4a6a" }}>
              <span style={{ color: "#6a6a8a" }}>vol</span> {vol}
            </span>
          )}
        </div>
      )}
      {/* detail lines */}
      <div className="space-y-0.5">
        {lines.map((l, i) => (
          <div key={i} className="text-[10px] leading-relaxed" style={{ color: "#5a5a7a" }}>
            {l}
          </div>
        ))}
      </div>
    </div>
  );
}

/* ─── simple vertical arrow ──────────────────────────────────── */
function VArrow({ label, color = "#2a2a4a" }: { label?: string; color?: string }) {
  return (
    <div className="flex flex-col items-center py-1 shrink-0">
      <div style={{ width: 1, height: 16, background: color }} />
      {label && (
        <span
          className="font-mono text-[9px] uppercase tracking-wider px-2 py-0.5 rounded my-1"
          style={{ background: "#0a0a14", border: `1px solid ${color}`, color: "#4a4a6a" }}
        >
          {label}
        </span>
      )}
      <div style={{ width: 1, height: 16, background: color }} />
      <div style={{
        width: 0, height: 0,
        borderLeft: "4px solid transparent", borderRight: "4px solid transparent",
        borderTop: `7px solid ${color}`,
      }} />
    </div>
  );
}

/* ─── layer label ────────────────────────────────────────────── */
function LayerLabel({ n, title, color }: { n: string; title: string; color: string }) {
  return (
    <div className="flex items-center gap-3 mb-3">
      <span className="font-mono text-[10px] font-bold px-2 py-0.5 rounded" style={{ background: color + "22", color }}>
        {n}
      </span>
      <span className="font-mono text-[11px] uppercase tracking-widest" style={{ color: "#3a3a5a" }}>
        {title}
      </span>
      <div className="flex-1 h-px" style={{ background: color + "20" }} />
    </div>
  );
}

/* ─── split into two tracks ──────────────────────────────────── */
function TrackSplit() {
  return (
    <div className="relative flex items-start justify-center overflow-visible" style={{ height: 56 }}>
      <svg viewBox="0 0 600 56" className="w-full h-full" preserveAspectRatio="none">
        <line x1="300" y1="0" x2="300" y2="14" stroke="#2a2a4a" strokeWidth="1" />
        <line x1="120" y1="14" x2="480" y2="14" stroke="#2a2a4a" strokeWidth="1" />
        <line x1="120" y1="14" x2="120" y2="56" stroke="#ef4444" strokeWidth="1" strokeDasharray="3 2" />
        <line x1="480" y1="14" x2="480" y2="56" stroke="#22c55e" strokeWidth="1" strokeDasharray="3 2" />
        <text x="120" y="10" textAnchor="middle" fill="#ef4444" fontSize="7" fontFamily="monospace">SPIKE RESPONSE</text>
        <text x="480" y="10" textAnchor="middle" fill="#22c55e" fontSize="7" fontFamily="monospace">SCHEDULED INTEL</text>
      </svg>
    </div>
  );
}

/* ─── merge from two tracks ──────────────────────────────────── */
function TrackMerge() {
  return (
    <div className="relative flex items-start justify-center overflow-visible" style={{ height: 48 }}>
      <svg viewBox="0 0 600 48" className="w-full h-full" preserveAspectRatio="none">
        <line x1="120" y1="0" x2="120" y2="34" stroke="#ef4444" strokeWidth="1" strokeDasharray="3 2" />
        <line x1="480" y1="0" x2="480" y2="34" stroke="#22c55e" strokeWidth="1" strokeDasharray="3 2" />
        <line x1="120" y1="34" x2="480" y2="34" stroke="#2a2a4a" strokeWidth="1" />
        <line x1="300" y1="34" x2="300" y2="48" stroke="#2a2a4a" strokeWidth="1" />
        <polygon points="296,44 304,44 300,48" fill="#2a2a4a" />
      </svg>
    </div>
  );
}

/* ─── routing rule row ───────────────────────────────────────── */
function Rule({ condition, output, platforms }: { condition: string; output: string; platforms: string[] }) {
  return (
    <div className="flex items-start gap-3 py-1.5 border-b last:border-b-0 font-mono" style={{ borderColor: "#1a1a2e" }}>
      <span className="text-[9px] shrink-0 mt-px" style={{ color: "#4a4a6a" }}>IF</span>
      <span className="text-[10px] flex-1" style={{ color: "#8a8ab0" }}>{condition}</span>
      <span className="text-[9px] shrink-0 mt-px" style={{ color: "#4a4a6a" }}>→</span>
      <span className="text-[10px] shrink-0" style={{ color: "#c4c4d0" }}>{output}</span>
      <div className="flex gap-1 shrink-0">
        {platforms.map((p) => (
          <span key={p} className="text-[8px] px-1 py-px rounded font-bold" style={{ background: "#1a1a2e", color: "#6366f1" }}>
            {p}
          </span>
        ))}
      </div>
    </div>
  );
}

/* ─── post schema ────────────────────────────────────────────── */
const SCHEMA = `class Post(BaseModel):
    id:          str
    platform:    Literal["reddit","hn","x","youtube","gtrends"]
    text:        str
    score:       int          # upvotes / points / views (k)
    author:      str
    created_at:  datetime
    url:         str
    comments_n:  int
    # enriched fields (added by processing layer)
    archetype:   str | None   # classifier output
    spike_flag:  bool         # 2σ above 4-week rolling avg
    cascade_dir: str | None   # "top_down" | "bottom_up"
    narrative:   str | None   # trending news cycle tag`;

/* ─── routing matrix ─────────────────────────────────────────── */
const MATRIX = [
  { arch: "Capability Demo",   reddit: { v: "24",   t: "avoid" }, hn: { v: "70",  t: "good"  }, x: { v: "408k", t: "good"  }, yt: { v: "5.1%", t: "best"  } },
  { arch: "Insider Reveal",    reddit: { v: "102",  t: "best"  }, hn: { v: "81",  t: "good"  }, x: { v: "153k", t: "ok"    }, yt: { v: "—",    t: "none"  } },
  { arch: "Controversy",       reddit: { v: "102",  t: "best"  }, hn: { v: "89",  t: "good"  }, x: { v: "1.8M", t: "best"  }, yt: { v: "—",    t: "none"  } },
  { arch: "Third-Party Valid.",reddit: { v: "51",   t: "ok"    }, hn: { v: "24",  t: "ok"    }, x: { v: "533k", t: "best"  }, yt: { v: "—",    t: "none"  } },
  { arch: "Model Release",     reddit: { v: "39",   t: "ok"    }, hn: { v: "242", t: "best"  }, x: { v: "370k", t: "ok"    }, yt: { v: "—",    t: "none"  } },
  { arch: "Personal Story",    reddit: { v: "16",   t: "avoid" }, hn: { v: "23",  t: "avoid" }, x: { v: "395k", t: "best"  }, yt: { v: "—",    t: "none"  } },
  { arch: "Humor / Meme",      reddit: { v: "68",   t: "good"  }, hn: { v: "—",   t: "none"  }, x: { v: "839k", t: "best"  }, yt: { v: "—",    t: "none"  } },
];

type Tier = "best" | "good" | "ok" | "avoid" | "none";
const TIER: Record<Tier, { bg: string; text: string }> = {
  best:  { bg: "rgba(34,197,94,0.14)",  text: "#22c55e" },
  good:  { bg: "rgba(99,102,241,0.14)", text: "#818cf8" },
  ok:    { bg: "rgba(234,179,8,0.12)",  text: "#eab308" },
  avoid: { bg: "rgba(239,68,68,0.12)",  text: "#ef4444" },
  none:  { bg: "transparent",           text: "#3a3a5a" },
};

/* ═══════════════════════════════════════════════════════════════ */
export default function PipelinePage() {
  return (
    <div
      className="min-h-screen"
      style={{
        background: "#07070f",
        backgroundImage: "radial-gradient(circle, rgba(99,102,241,0.12) 1px, transparent 1px)",
        backgroundSize: "28px 28px",
      }}
    >
      <Nav />

      {/* ── HERO ── */}
      <section className="max-w-6xl mx-auto px-6 pt-16 pb-10">
        <div className="flex items-center gap-3 mb-5">
          <div
            className="font-mono text-[10px] uppercase tracking-widest px-3 py-1.5 rounded-full border flex items-center gap-2"
            style={{ borderColor: "#22c55e40", background: "rgba(34,197,94,0.05)", color: "#22c55e" }}
          >
            <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
            system online · stage 3
          </div>
          <span className="font-mono text-[10px]" style={{ color: "#3a3a5a" }}>
            automated intelligence pipeline · v1.0
          </span>
        </div>

        <h1 className="text-4xl sm:text-5xl font-bold text-white leading-tight tracking-tight">
          Automated Growth<br />
          <span style={{ color: "#f59e0b" }}>Intelligence Pipeline</span>
        </h1>
        <p className="mt-4 text-sm max-w-2xl leading-relaxed font-mono" style={{ color: "#5a5a7a" }}>
          5 ingestion sources → unified schema → signal processing → platform routing →
          dual-track execution → flywheel measurement. Recurring · self-correcting · data-backed.
        </p>

        <div className="mt-6 flex flex-wrap gap-6">
          {[
            { label: "sources", value: "5" },
            { label: "posts/hr", value: "~2,400" },
            { label: "archetypes", value: "9" },
            { label: "platforms routed", value: "4" },
            { label: "exec tracks", value: "2" },
            { label: "kpi signals", value: "4" },
          ].map((s) => (
            <div key={s.label} className="font-mono">
              <div className="text-xl font-bold text-white">{s.value}</div>
              <div className="text-[10px] uppercase tracking-wider" style={{ color: "#3a3a5a" }}>{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── MAIN ARCHITECTURE DIAGRAM ── */}
      <section className="max-w-6xl mx-auto px-6 pb-16">

        {/* LAYER 0: SOURCES */}
        <LayerLabel n="L0" title="Data Sources" color={C.ingest.text} />
        <div className="flex gap-3">
          {[
            { title: "REDDIT_SCRAPER",   freq: "60min",  vol: "200 posts/run",  lines: ["target: r/ClaudeAI · r/HiggsfieldAI", "library: PRAW · auth: read-only", "fields: title · score · comments · flair · author"] },
            { title: "HN_WATCHER",       freq: "real-time", vol: "top-30 stories", lines: ["endpoint: Algolia HN API · /search_by_date", "trigger: any story matching keyword list", "fields: objectID · title · points · num_comments"] },
            { title: "X_SCRAPER",        freq: "60min",  vol: "50 tweets/run",  lines: ["method: GraphQL keyword search", "targets: claude · anthropic · higgsfield", "fields: id · text · view_count · like_count"] },
            { title: "YOUTUBE_API",      freq: "daily",  vol: "trending+channel", lines: ["API: YouTube Data v3 · search + videos", "queries: 'claude AI' · 'higgsfield AI'", "fields: videoId · viewCount · likeCount · title"] },
            { title: "GTRENDS_POLLER",   freq: "weekly", vol: "comparison index", lines: ["library: pytrends · geo: US+GB+IN", "keywords: claude vs chatgpt vs higgsfield", "fields: date · interest · relative_index"] },
          ].map((src) => (
            <Node key={src.title} {...src} color={C.ingest} />
          ))}
        </div>

        <VArrow label="POST[ ] → normalize → Post schema" color={C.ingest.border} />

        {/* LAYER 1: COLLECTOR */}
        <LayerLabel n="L1" title="Unified Collector" color={C.ingest.text} />
        <Node
          title="UNIFIED_COLLECTOR"
          freq="continuous"
          vol="~2,400 posts/hr"
          lines={[
            "input:  raw platform objects from all 5 scrapers",
            "output: Post[] — pydantic-validated · deduplicated by (platform, id)",
            "store:  SQLite · posts.db · indexed on (platform, created_at, score)",
            "dedup:  upsert on primary key · update score + comments on re-scrape",
          ]}
          color={C.ingest}
          wide
        />

        <VArrow label="Post{id, platform, text, score, timestamp}" color={C.process.border} />

        {/* LAYER 2: PROCESSING */}
        <LayerLabel n="L2" title="Signal Processing" color={C.process.text} />
        <div className="flex gap-3">
          {[
            { title: "SPIKE_DETECTOR",      freq: "hourly",  vol: "per-platform",   lines: ["algorithm: z-score vs 4-week rolling avg", "threshold: 2σ above baseline", "output: spike_flag=True + delta_pct"] },
            { title: "ARCHETYPE_CLASSIFIER",freq: "on-ingest", vol: "every post",   lines: ["method: regex ruleset → 9 classes", "classes: Insider·Controversy·Demo·Story…", "fallback: 'other' if no rule matches"] },
            { title: "CASCADE_DETECTOR",    freq: "hourly",  vol: "cross-platform", lines: ["logic: compare first-post timestamp by platform", "if X_first → top_down · if Reddit_first → bottom_up", "window: ±48h around same story/topic cluster"] },
            { title: "NARRATIVE_MONITOR",   freq: "hourly",  vol: "HN + X trending", lines: ["scan: HN front page · X trending topics", "match: keyword overlap with current Claude content", "flag: narrative='deepseek' | 'regulation' | etc."] },
          ].map((proc) => (
            <Node key={proc.title} {...proc} color={C.process} />
          ))}
        </div>

        <VArrow label="Signal{archetype, spike, cascade_dir, narrative}" color={C.router.border} />

        {/* LAYER 3: ROUTER */}
        <LayerLabel n="L3" title="Routing Engine" color={C.router.text} />
        <div
          className="rounded-lg border font-mono p-5 mb-0"
          style={{ borderColor: C.router.border + "60", background: C.router.bg }}
        >
          <div className="flex items-center justify-between mb-4">
            <span className="text-[11px] font-bold uppercase tracking-widest" style={{ color: C.router.text }}>
              ● PLATFORM × ARCHETYPE ROUTER
            </span>
            <span className="text-[9px] uppercase tracking-wider" style={{ color: "#4a4a6a" }}>
              decision engine · 9 archetypes × 4 platforms
            </span>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-x-8">
            <div>
              <Rule condition="archetype = capability_demo"  output="→ HN first, then YouTube"     platforms={["HN","YT"]} />
              <Rule condition="archetype = insider_reveal"   output="→ cascade trigger: all"        platforms={["X","HN","R"]} />
              <Rule condition="archetype = controversy"      output="→ X + Reddit simultaneous"     platforms={["X","R"]} />
              <Rule condition="archetype = model_release"    output="→ HN priority (242 avg pts)"   platforms={["HN","X"]} />
            </div>
            <div>
              <Rule condition="archetype = personal_story"   output="→ X first (395k avg views)"   platforms={["X"]} />
              <Rule condition="archetype = third_party"      output="→ X priority (533k avg views)" platforms={["X","HN"]} />
              <Rule condition="spike_flag = True"            output="→ real-time track + amplifier alert" platforms={["A"]} />
              <Rule condition="narrative != None"            output="→ insert into live news cycle (surfing)" platforms={["X"]} />
            </div>
          </div>
          <div className="mt-3 pt-3 border-t text-[9px]" style={{ borderColor: "#1a1a2e", color: "#4a4a6a" }}>
            ELSE → scheduled_track · add to weekly content calendar · assign copy formula (opening_word + length_target)
          </div>
        </div>

        {/* SPLIT */}
        <TrackSplit />

        {/* LAYER 4: TWO TRACKS SIDE BY SIDE */}
        <LayerLabel n="L4" title="Execution Tracks" color="#6b7280" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">

          {/* TRACK A: REAL-TIME */}
          <div
            className="rounded-lg border p-4 flex flex-col gap-3"
            style={{ borderColor: C.realtime.border + "50", background: C.realtime.bg }}
          >
            <div className="font-mono text-[10px] font-bold uppercase tracking-widest flex items-center gap-2" style={{ color: C.realtime.text }}>
              <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ background: C.realtime.text }} />
              Track A · Spike Response
            </div>
            {[
              { step: "T+0min",  label: "BRIEF_GEN",        detail: "generate content brief: platform, archetype, copy formula (70–130 chars, 'just/when/i'm' opener)" },
              { step: "T+15min", label: "AMPLIFIER_ALERT",  detail: "Slack/DM to active creators · EHuanglu + 4 film creators · include brief + asset" },
              { step: "T+30min", label: "OFFICIAL_POST",    detail: "X post via official account · optimal time: Tue–Thu 14:00–19:00 UTC" },
              { step: "T+90min", label: "HN_SUBMIT",        detail: "DM adocomplete / meetpateltech · 1-sentence pitch + link" },
              { step: "T+4hr",   label: "REDDIT_SEED",      detail: "post personal-story version to r/HiggsfieldAI first · then r/aivideo day+1" },
              { step: "T+8hr",   label: "X_WAVE_2",         detail: "thread replies · quote-tweets from community · engagement monitoring" },
            ].map((s) => (
              <div key={s.step} className="flex gap-3 font-mono">
                <span className="text-[9px] shrink-0 w-14 text-right pt-px" style={{ color: C.realtime.text }}>{s.step}</span>
                <div>
                  <div className="text-[10px] font-bold" style={{ color: "#c4c4d0" }}>{s.label}</div>
                  <div className="text-[9px] leading-relaxed" style={{ color: "#5a5a7a" }}>{s.detail}</div>
                </div>
              </div>
            ))}
          </div>

          {/* TRACK B: SCHEDULED */}
          <div
            className="rounded-lg border p-4 flex flex-col gap-3"
            style={{ borderColor: C.scheduled.border + "50", background: C.scheduled.bg }}
          >
            <div className="font-mono text-[10px] font-bold uppercase tracking-widest flex items-center gap-2" style={{ color: C.scheduled.text }}>
              <span className="w-1.5 h-1.5 rounded-full" style={{ background: C.scheduled.text }} />
              Track B · Scheduled Intelligence
            </div>
            {[
              { step: "Sun",  label: "WEEKLY_DIGEST",      detail: "aggregate last 7 days: top archetypes, score distribution, competitor mentions, trend deltas" },
              { step: "Mon",  label: "CONTENT_CALENDAR",   detail: "generate 5 content briefs for the week · platform assignments · opening word suggestions" },
              { step: "Mon",  label: "ARCHETYPE_AUDIT",    detail: "check % Insider Reveal + Controversy in last 30 days · alert if below 20% target" },
              { step: "Tue",  label: "COMMUNITY_SEED",     detail: "3 posts to r/HiggsfieldAI · templates: weekly challenge, filmmaker spotlight, prompt showcase" },
              { step: "Thu",  label: "HN_OPPORTUNITY",     detail: "scan for Claude HN stories without Higgsfield counterpart · identify submission gap" },
              { step: "Fri",  label: "FLYWHEEL_REPORT",    detail: "owned ratio, amplifier index, archetype mix, X floor · delta vs prior week · Slack post" },
            ].map((s) => (
              <div key={s.step + s.label} className="flex gap-3 font-mono">
                <span className="text-[9px] shrink-0 w-14 text-right pt-px" style={{ color: C.scheduled.text }}>{s.step}</span>
                <div>
                  <div className="text-[10px] font-bold" style={{ color: "#c4c4d0" }}>{s.label}</div>
                  <div className="text-[9px] leading-relaxed" style={{ color: "#5a5a7a" }}>{s.detail}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* MERGE */}
        <TrackMerge />

        {/* LAYER 5: MEASUREMENT */}
        <LayerLabel n="L5" title="Flywheel Measurement" color={C.measure.text} />
        <div className="flex gap-3">
          {[
            { title: "OWNED_RATIO",      freq: "weekly",  vol: "per platform",   lines: ["metric: r/HiggsfieldAI ÷ total Reddit posts", "current: ~3% · target: >50%", "alert: if ratio drops week-over-week"] },
            { title: "AMPLIFIER_INDEX",  freq: "weekly",  vol: "X accounts",     lines: ["metric: # independent voices with >100k followers", "current: 1 · target: ≥5", "decay: weight recent posts higher than old"] },
            { title: "ARCHETYPE_MIX",    freq: "weekly",  vol: "30d window",     lines: ["metric: % Insider + Controversy of total posts", "current: ~0% · target: >20%", "source: archetype_classifier output"] },
            { title: "VIEW_FLOOR",       freq: "monthly", vol: "trailing 3mo",   lines: ["metric: lowest monthly X view total (trailing 3)", "current: ~5M · target: >20M", "floor not peak — measures structural reach"] },
          ].map((m) => (
            <Node key={m.title} {...m} status="idle" color={C.measure} />
          ))}
        </div>

        {/* Feedback annotation */}
        <div
          className="mt-4 flex items-center gap-3 rounded-lg px-4 py-3 font-mono border"
          style={{ background: "rgba(99,102,241,0.04)", borderColor: "#6366f130" }}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <path d="M1 4v6h6M23 20v-6h-6" stroke="#6366f1" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M20.49 9A9 9 0 005.64 5.64L1 10M23 14l-4.64 4.36A9 9 0 013.51 15" stroke="#6366f1" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          <span className="text-[10px]" style={{ color: "#818cf8" }}>
            <strong>feedback loop</strong> — L5 metrics update L2 baselines weekly. rising owned_ratio lowers spike_threshold for r/HiggsfieldAI. rising view_floor raises cascade priority score. the pipeline self-calibrates.
          </span>
        </div>
      </section>

      {/* ── DATA SCHEMA ── */}
      <section className="border-t" style={{ borderColor: "#1a1a2e" }}>
        <div className="max-w-6xl mx-auto px-6 py-12">
          <LayerLabel n="ref" title="Unified Post Schema" color="#6366f1" />
          <div
            className="rounded-lg border p-5 overflow-x-auto"
            style={{ background: "#05050d", borderColor: "#1a1a2e" }}
          >
            <pre className="font-mono text-[11px] leading-relaxed" style={{ color: "#6a8a6a" }}>
              {SCHEMA}
            </pre>
          </div>
        </div>
      </section>

      {/* ── AUTOMATED vs HUMAN ── */}
      <section className="border-t" style={{ borderColor: "#1a1a2e" }}>
        <div className="max-w-6xl mx-auto px-6 py-12">
          <LayerLabel n="ref" title="Automated vs. Human-Reviewed Tasks" color="#a855f7" />
          <p className="font-mono text-[10px] mb-5" style={{ color: "#4a4a6a" }}>
            every task in the pipeline has a clear owner — machine or human. ambiguity here causes missed spikes.
          </p>
          <div className="overflow-x-auto rounded-lg border" style={{ borderColor: "#1a1a2e" }}>
            <table className="w-full border-collapse font-mono">
              <thead>
                <tr style={{ background: "#0a0a14" }}>
                  {["Task", "Owner", "Trigger", "SLA", "Fallback"].map((h) => (
                    <th key={h} className="text-left text-[10px] uppercase tracking-wider py-3 px-4 border-b" style={{ color: "#4a4a6a", borderColor: "#1a1a2e" }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {[
                  { task: "Scrape + ingest",          owner: "auto",  trigger: "cron schedule",            sla: "<2 min lag",   fallback: "retry queue, alert if >3 fails" },
                  { task: "Spike detection",           owner: "auto",  trigger: "new post batch",           sla: "<5 min",       fallback: "daily digest if real-time down" },
                  { task: "Archetype classification",  owner: "auto",  trigger: "on ingest",                sla: "< 1 min",      fallback: "'other' label, manual review queue" },
                  { task: "Content brief generation",  owner: "auto",  trigger: "spike_flag = True",        sla: "T+0 min",      fallback: "template brief if LLM unavailable" },
                  { task: "Amplifier notification",    owner: "auto",  trigger: "brief ready + spike",      sla: "T+15 min",     fallback: "Slack DM, not email" },
                  { task: "Official post decision",    owner: "human", trigger: "brief reviewed",           sla: "T+30 min",     fallback: "skip if no human available" },
                  { task: "HN submission",             owner: "human", trigger: "weekly scan + spike",      sla: "same day",     fallback: "queue for next opportunity" },
                  { task: "Community seeding (Reddit)",owner: "human", trigger: "Mon/Tue schedule",         sla: "3×/week",      fallback: "auto-post template if missed" },
                  { task: "Flywheel report",           owner: "auto",  trigger: "Friday EOW",               sla: "Fri 17:00 UTC", fallback: "Slack post with raw numbers" },
                  { task: "Narrative monitoring",      owner: "auto",  trigger: "continuous (HN+X scan)",   sla: "<30 min detect", fallback: "flag to human, daily summary" },
                ].map((row, ri) => (
                  <tr key={ri} className="border-b" style={{ borderColor: "#1a1a2e", background: ri % 2 === 0 ? "transparent" : "rgba(255,255,255,0.008)" }}>
                    <td className="py-2.5 px-4 text-[11px] text-white">{row.task}</td>
                    <td className="py-2.5 px-4">
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded" style={{
                        background: row.owner === "auto" ? "rgba(34,197,94,0.12)" : "rgba(245,158,11,0.12)",
                        color: row.owner === "auto" ? "#22c55e" : "#f59e0b",
                      }}>
                        {row.owner === "auto" ? "⚡ auto" : "👤 human"}
                      </span>
                    </td>
                    <td className="py-2.5 px-4 text-[10px]" style={{ color: "#6a6a8a" }}>{row.trigger}</td>
                    <td className="py-2.5 px-4 text-[10px]" style={{ color: "#6a6a8a" }}>{row.sla}</td>
                    <td className="py-2.5 px-4 text-[10px]" style={{ color: "#4a4a6a" }}>{row.fallback}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* ── TOOL STACK ── */}
      <section className="border-t" style={{ borderColor: "#1a1a2e" }}>
        <div className="max-w-6xl mx-auto px-6 py-12">
          <LayerLabel n="ref" title="Tool Stack & Justification" color="#00b4d8" />
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {[
              {
                layer: "Ingestion",
                tools: [
                  { name: "PRAW 7.x", role: "Reddit scraper", why: "Official API wrapper, handles auth + rate limits, 100 req/min free tier" },
                  { name: "Algolia HN API", role: "HN watcher", why: "Real-time search index for HN, no auth needed, full-text + date filtering" },
                  { name: "tweepy / snscrape", role: "X scraper", why: "tweepy for API v2 (limited), snscrape for no-auth fallback on public posts" },
                  { name: "youtube-data-api v3", role: "YouTube", why: "Official, 10k quota/day free, covers search + video stats in one call" },
                  { name: "pytrends", role: "Google Trends", why: "Unofficial but stable, weekly poll is within rate limits, no auth needed" },
                ],
                color: "#00b4d8",
              },
              {
                layer: "Storage & Scheduling",
                tools: [
                  { name: "SQLite → PostgreSQL", role: "Post store", why: "Start with SQLite (zero ops); migrate to Postgres at ~500k posts or when concurrent writes needed" },
                  { name: "APScheduler", role: "Cron orchestrator", why: "Pure Python, no Celery/Redis dependency, supports cron + interval + one-off jobs in-process" },
                  { name: "pydantic v2", role: "Schema validation", why: "Runtime validation + serialisation for Post model; catches malformed platform responses early" },
                ],
                color: "#a855f7",
              },
              {
                layer: "Processing & Classification",
                tools: [
                  { name: "regex ruleset", role: "Archetype classifier", why: "95% accurate on 9 classes with 50-rule set; instant, no GPU, deterministic — easy to audit" },
                  { name: "scipy / numpy", role: "Spike detector (z-score)", why: "Rolling z-score over 4-week window; 2σ threshold calibrated to our 74k-post dataset" },
                  { name: "claude-haiku-4-5 API", role: "Brief generation", why: "Fast + cheap ($0.25/M tokens); generates 70–130 char briefs with archetype context in <3s" },
                ],
                color: "#f59e0b",
              },
              {
                layer: "Alerting & Delivery",
                tools: [
                  { name: "Slack Webhook", role: "Amplifier alerts + reports", why: "Zero setup, free, immediate delivery, supports rich message blocks for structured briefs" },
                  { name: "SQLite FTS5", role: "Narrative keyword scan", why: "Full-text search on post.text without external index; HN + X monitoring at 1M rows stays sub-50ms" },
                  { name: "GitHub Actions", role: "CI + scheduled runs", why: "Free for public repos, cron triggers (min 5min), no server needed for scheduled scrapes" },
                ],
                color: "#22c55e",
              },
            ].map((section) => (
              <div key={section.layer} className="rounded-lg border p-4" style={{ borderColor: section.color + "30", background: section.color + "06" }}>
                <div className="font-mono text-[10px] font-bold uppercase tracking-widest mb-3" style={{ color: section.color }}>
                  {section.layer}
                </div>
                <div className="space-y-2">
                  {section.tools.map((t) => (
                    <div key={t.name} className="flex gap-2">
                      <span className="font-mono text-[10px] font-bold shrink-0 w-36" style={{ color: "#c4c4d0" }}>{t.name}</span>
                      <div>
                        <span className="font-mono text-[9px]" style={{ color: "#6a6a8a" }}>[{t.role}] </span>
                        <span className="font-mono text-[9px]" style={{ color: "#4a4a6a" }}>{t.why}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── COST & SCALE ── */}
      <section className="border-t" style={{ borderColor: "#1a1a2e" }}>
        <div className="max-w-6xl mx-auto px-6 py-12">
          <LayerLabel n="ref" title="Cost Estimates — Current & 10× Scale" color="#f59e0b" />
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <div className="font-mono text-[10px] font-bold uppercase tracking-widest mb-3" style={{ color: "#22c55e" }}>
                Current (2,400 posts/hr · 1 brand pair)
              </div>
              <div className="space-y-2 font-mono">
                {[
                  { item: "Compute (VPS / GitHub Actions)", cost: "~$0 – $5/mo", note: "GitHub Actions free tier covers scheduled scrapes; VPS ~$5/mo if self-hosted" },
                  { item: "Reddit PRAW", cost: "$0", note: "Free read-only API, 100 req/min" },
                  { item: "YouTube Data API v3", cost: "$0", note: "10k units/day free = ~200 video lookups/day, sufficient for monitoring" },
                  { item: "Claude Haiku brief gen", cost: "~$0.10/mo", note: "~400 briefs/mo × 200 tokens × $0.25/M = $0.02; rounding to $0.10 with overhead" },
                  { item: "Slack Webhooks", cost: "$0", note: "Free indefinitely" },
                  { item: "Storage (SQLite)", cost: "$0", note: "~2GB for 1M posts; fits on any VPS" },
                ].map((r) => (
                  <div key={r.item} className="flex gap-3 items-start py-1.5 border-b" style={{ borderColor: "#1a1a2e" }}>
                    <span className="text-[10px] flex-1" style={{ color: "#8a8ab0" }}>{r.item}</span>
                    <span className="text-[10px] font-bold shrink-0 w-24 text-right" style={{ color: "#22c55e" }}>{r.cost}</span>
                    <span className="text-[9px] flex-1" style={{ color: "#4a4a6a" }}>{r.note}</span>
                  </div>
                ))}
                <div className="flex justify-between pt-2 border-t font-bold" style={{ borderColor: "#22c55e40" }}>
                  <span className="text-[11px]" style={{ color: "#22c55e" }}>Total / month</span>
                  <span className="text-[11px]" style={{ color: "#22c55e" }}>~$5–10</span>
                </div>
              </div>
            </div>
            <div>
              <div className="font-mono text-[10px] font-bold uppercase tracking-widest mb-3" style={{ color: "#f59e0b" }}>
                10× Scale (10 brand pairs · full real-time · PostgreSQL)
              </div>
              <div className="space-y-2 font-mono">
                {[
                  { item: "Compute (dedicated server)", cost: "$40–80/mo", note: "2 vCPU / 4GB RAM handles 10 brands; add worker per 5 additional brands" },
                  { item: "PostgreSQL (managed, e.g. Supabase)", cost: "$25/mo", note: "Up to 8GB, connection pooling, read replicas; SQLite won't scale past 5M rows" },
                  { item: "YouTube Data API", cost: "$0–50/mo", note: "May need paid quota at 10 brands; $50/month buys 50 extra 1M units" },
                  { item: "Claude Haiku brief gen", cost: "~$1/mo", note: "10× volume = ~4,000 briefs; still under $1/mo at Haiku pricing" },
                  { item: "X API (Basic tier)", cost: "$100/mo", note: "Required if volume exceeds free tier; Basic = 10k reads/month" },
                  { item: "Storage (Postgres + backups)", cost: "~$10/mo", note: "Automated daily backups, 30-day retention" },
                ].map((r) => (
                  <div key={r.item} className="flex gap-3 items-start py-1.5 border-b" style={{ borderColor: "#1a1a2e" }}>
                    <span className="text-[10px] flex-1" style={{ color: "#8a8ab0" }}>{r.item}</span>
                    <span className="text-[10px] font-bold shrink-0 w-24 text-right" style={{ color: "#f59e0b" }}>{r.cost}</span>
                    <span className="text-[9px] flex-1" style={{ color: "#4a4a6a" }}>{r.note}</span>
                  </div>
                ))}
                <div className="flex justify-between pt-2 border-t font-bold" style={{ borderColor: "#f59e0b40" }}>
                  <span className="text-[11px]" style={{ color: "#f59e0b" }}>Total / month</span>
                  <span className="text-[11px]" style={{ color: "#f59e0b" }}>~$175–260</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── ALERT DESIGN ── */}
      <section className="border-t" style={{ borderColor: "#1a1a2e" }}>
        <div className="max-w-6xl mx-auto px-6 py-12">
          <LayerLabel n="ref" title="Alert Design — Something Is Happening Right Now" color="#ef4444" />
          <p className="font-mono text-[10px] mb-6" style={{ color: "#4a4a6a" }}>
            three alert tiers with distinct channels, urgency levels, and required human actions.
          </p>
          <div className="space-y-4">
            {[
              {
                tier: "TIER 1 · Spike Alert",
                color: "#ef4444",
                trigger: "Any post reaches 2σ above 4-week rolling avg within 2 hours of publication",
                channel: "Slack #spike-alerts — immediate ping to content team + amplifiers",
                payload: [
                  "post title, platform, current score, baseline, delta%",
                  "archetype classification + recommended platform routing",
                  "pre-generated content brief (70–130 char, opening word, format)",
                  "amplifier DM template ready to send",
                ],
                sla: "Human must decide within 30 min: post or skip. No decision = auto-skip.",
                example: `SPIKE DETECTED · reddit · r/ClaudeAI\n"just had sonnet rewrite my entire test suite in 40 minutes"\nscore: 847 (+1,240% vs baseline 63) · 2h 14m old\narchetype: personal_story → route: X first\nbrief: "Just watched [specific task] get done in [time] — [surprising outcome]"\nAmplifier DMs: ready to send · approve? [YES / SKIP]`,
              },
              {
                tier: "TIER 2 · Narrative Signal",
                color: "#f59e0b",
                trigger: "HN front page OR X trending topic overlaps with Higgsfield keyword set",
                channel: "Slack #narrative-monitor — daily digest at 09:00 UTC + immediate alert if confidence > 80%",
                payload: [
                  "narrative label (e.g. 'Hollywood AI policy', 'AI video deepfakes')",
                  "matching keywords found in top 10 HN/X posts",
                  "estimated time window: how long this story has been trending",
                  "2–3 pre-drafted Higgsfield response angles (from prepared library)",
                ],
                sla: "Response window: 4–6 hours. After that, the news cycle has usually moved on.",
                example: `NARRATIVE SIGNAL · HN + X · confidence 91%\nlabel: "Hollywood AI displacement"\nmatching: 'WGA', 'AI video', 'SAG-AFTRA', 'Sora replace'\ntrending since: 3h ago · estimated window: 18–36h\nangles available: filmmaker-perspective · cost-data · disclosure-policy\naction: pick one angle, draft post, schedule for next 4h`,
              },
              {
                tier: "TIER 3 · Flywheel Warning",
                color: "#a855f7",
                trigger: "Any L5 metric declines week-over-week OR misses target by >20%",
                channel: "Slack #weekly-flywheel — Friday report, no ping unless decline",
                payload: [
                  "metric name, current value, prior week, target, delta",
                  "root cause guess: which archetype or platform drove the change",
                  "one recommended corrective action with data reference",
                ],
                sla: "Review in Monday planning meeting. No urgent action needed.",
                example: `⚠ FLYWHEEL WARNING · week ending Apr 11\nARCHETYPE_MIX: 4% (↓ from 9%) — target >20%\nroot cause: 0 Insider/Controversy posts this week (7 Demo posts)\naction: schedule 2 Insider posts next week using templates F1 + F2\nOWNED_RATIO: 8% (stable) · AMPLIFIER_INDEX: 1 (stable) · VIEW_FLOOR: 5.2M (↑ 3%)`,
              },
            ].map((alert) => (
              <div key={alert.tier} className="rounded-lg border overflow-hidden" style={{ borderColor: alert.color + "40" }}>
                <div className="flex items-center gap-3 px-5 py-3" style={{ background: alert.color + "12" }}>
                  <span className="w-2 h-2 rounded-full animate-pulse" style={{ background: alert.color }} />
                  <span className="font-mono text-[11px] font-bold uppercase tracking-widest" style={{ color: alert.color }}>{alert.tier}</span>
                </div>
                <div className="p-5 grid grid-cols-1 lg:grid-cols-2 gap-5">
                  <div className="space-y-3">
                    <div>
                      <div className="font-mono text-[9px] uppercase tracking-wider mb-1" style={{ color: "#4a4a6a" }}>trigger</div>
                      <div className="font-mono text-[10px]" style={{ color: "#8a8ab0" }}>{alert.trigger}</div>
                    </div>
                    <div>
                      <div className="font-mono text-[9px] uppercase tracking-wider mb-1" style={{ color: "#4a4a6a" }}>channel</div>
                      <div className="font-mono text-[10px]" style={{ color: "#8a8ab0" }}>{alert.channel}</div>
                    </div>
                    <div>
                      <div className="font-mono text-[9px] uppercase tracking-wider mb-1" style={{ color: "#4a4a6a" }}>payload includes</div>
                      <ul className="space-y-0.5">
                        {alert.payload.map((p, i) => (
                          <li key={i} className="font-mono text-[9px] flex gap-2" style={{ color: "#5a5a7a" }}>
                            <span style={{ color: alert.color }}>›</span> {p}
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <div className="font-mono text-[9px] uppercase tracking-wider mb-1" style={{ color: "#4a4a6a" }}>human SLA</div>
                      <div className="font-mono text-[10px]" style={{ color: alert.color + "cc" }}>{alert.sla}</div>
                    </div>
                  </div>
                  <div>
                    <div className="font-mono text-[9px] uppercase tracking-wider mb-2" style={{ color: "#4a4a6a" }}>example alert payload</div>
                    <pre
                      className="rounded p-3 text-[9px] leading-relaxed overflow-x-auto whitespace-pre-wrap"
                      style={{ background: "#05050d", border: `1px solid ${alert.color}25`, color: "#6a6a8a" }}
                    >
                      {alert.example}
                    </pre>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── ROUTING MATRIX ── */}
      <section className="border-t" style={{ borderColor: "#1a1a2e" }}>
        <div className="max-w-6xl mx-auto px-6 py-12">
          <LayerLabel n="ref" title="Platform × Archetype Routing Matrix" color="#f59e0b" />
          <p className="font-mono text-[10px] mb-5" style={{ color: "#4a4a6a" }}>
            routing decisions backed by 74k Reddit posts · 107k HN stories · 2,127 X tweets.
            values: Reddit=avg_score · HN=avg_pts · X=avg_views · YT=engagement_rate
          </p>
          <div className="overflow-x-auto rounded-lg border" style={{ borderColor: "#1a1a2e" }}>
            <table className="w-full border-collapse font-mono">
              <thead>
                <tr style={{ background: "#0a0a14" }}>
                  <th className="text-left text-[10px] uppercase tracking-wider py-3 px-4 border-b" style={{ color: "#4a4a6a", borderColor: "#1a1a2e", width: "26%" }}>
                    archetype
                  </th>
                  {["Reddit", "HN", "X", "YouTube"].map((p) => (
                    <th key={p} className="text-center text-[10px] uppercase tracking-wider py-3 px-4 border-b" style={{ color: "#4a4a6a", borderColor: "#1a1a2e" }}>
                      {p}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {MATRIX.map((row, ri) => (
                  <tr key={row.arch} className="border-b" style={{ borderColor: "#1a1a2e", background: ri % 2 === 0 ? "transparent" : "rgba(255,255,255,0.008)" }}>
                    <td className="py-2.5 px-4 text-[11px] text-white">{row.arch}</td>
                    {[row.reddit, row.hn, row.x, row.yt].map((cell, ci) => {
                      const t = cell.t as Tier;
                      return (
                        <td key={ci} className="py-2.5 px-4 text-center">
                          <span
                            className="inline-block text-[10px] font-bold px-2 py-0.5 rounded font-mono"
                            style={{ background: TIER[t].bg, color: TIER[t].text }}
                          >
                            {t === "none" ? "—" : cell.v}
                          </span>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="flex flex-wrap gap-4 mt-3">
            {([["best","#22c55e","rgba(34,197,94,0.14)"],["good","#818cf8","rgba(99,102,241,0.14)"],["ok","#eab308","rgba(234,179,8,0.12)"],["avoid","#ef4444","rgba(239,68,68,0.12)"]] as const).map(([l,c,bg]) => (
              <div key={l} className="flex items-center gap-1.5 font-mono">
                <span className="w-3 h-3 rounded-sm" style={{ background: bg, border: `1px solid ${c}40` }} />
                <span className="text-[9px] uppercase tracking-wider" style={{ color: c }}>{l}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      <footer className="border-t" style={{ borderColor: "#1a1a2e", background: "#05050d" }}>
        <div className="max-w-6xl mx-auto px-6 py-6 flex items-center justify-between font-mono">
          <span className="text-[10px]" style={{ color: "#3a3a5a" }}>HackNU 2026 · Stage 3 · Automated Intelligence Pipeline</span>
          <span className="text-[10px]" style={{ color: "#3a3a5a" }}>L0 → L1 → L2 → L3 → L4a|L4b → L5 → ↺</span>
        </div>
      </footer>
    </div>
  );
}
