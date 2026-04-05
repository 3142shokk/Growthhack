import Nav from "@/components/Nav";
import AnalysisCard from "@/components/AnalysisCard";
import { analysisFindings } from "@/lib/analysis";

const GAPS = [
  { label: "X amplifiers (Claude)",      value: "8+",    note: "independent voices" },
  { label: "X amplifiers (Higgsfield)",   value: "1",     note: "EHuanglu" },
  { label: "r/ClaudeAI posts",           value: "60k",   note: "owned community" },
  { label: "r/HiggsfieldAI posts",       value: "2,094", note: "avg score 4.8; KLING content scores 2.5× higher" },
  { label: "YouTube engagement rate",    value: "5.12%", note: "Higgsfield — beats Claude" },
  { label: "HN presence",               value: "0",     note: "Higgsfield vs 107k Claude" },
];

export default function AnalysisPage() {
  return (
    <div className="min-h-screen" style={{ background: "var(--background)" }}>
      <Nav />

      {/* Hero */}
      <section className="max-w-7xl mx-auto px-6 pt-16 pb-10">
        <div
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-medium mb-6"
          style={{ borderColor: "rgba(224,123,57,0.3)", background: "rgba(224,123,57,0.06)", color: "#e07b39" }}
        >
          <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ background: "#e07b39" }} />
          Higgsfield vs Claude · Growth Gap Analysis
        </div>

        <h1 className="text-4xl sm:text-5xl font-bold text-white leading-tight tracking-tight">
          What Higgsfield Can<br />
          <span style={{ color: "#e07b39" }}>Take From Claude&apos;s Playbook</span>
        </h1>
        <p className="mt-4 text-base max-w-2xl leading-relaxed" style={{ color: "var(--muted)" }}>
          Six structural gaps identified from 197k data points. Each one is specific, measurable,
          and closable. Not strategic advice — concrete actions backed by the numbers.
        </p>
      </section>

      {/* Gap bar */}
      <section className="border-y" style={{ borderColor: "var(--border)" }}>
        <div className="max-w-7xl mx-auto px-6 py-0">
          <div className="grid grid-cols-2 lg:grid-cols-6">
            {GAPS.map((g, i) => (
              <div
                key={g.label}
                className="py-5 px-4 border-r last:border-r-0"
                style={{ borderColor: "var(--border)" }}
              >
                <div className="text-xs mb-1" style={{ color: "var(--muted)" }}>{g.label}</div>
                <div
                  className="text-xl font-bold"
                  style={{ color: i === 1 || i === 3 || i === 5 ? "#ef4444" : i === 4 ? "#22c55e" : "white" }}
                >
                  {g.value}
                </div>
                <div className="text-xs mt-0.5" style={{ color: "var(--muted)" }}>{g.note}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Analysis cards */}
      <main className="max-w-7xl mx-auto px-6 py-12">
        <div className="mb-10">
          <p className="text-xs font-semibold tracking-widest uppercase mb-2" style={{ color: "#e07b39" }}>
            Comparative Analysis
          </p>
          <h2 className="text-3xl font-bold text-white">6 Gaps, 6 Playbook Actions</h2>
          <p className="mt-2 text-sm" style={{ color: "var(--muted)" }}>
            Every finding is sourced from scraped data. Every action is specific enough to start this week.
          </p>
        </div>

        <div className="space-y-4">
          {analysisFindings.map((f) => (
            <AnalysisCard key={f.id} finding={f} />
          ))}
        </div>
      </main>

      {/* Bottom CTA */}
      <section
        className="border-t mt-8"
        style={{ borderColor: "var(--border)", background: "#0e0e18" }}
      >
        <div className="max-w-7xl mx-auto px-6 py-12 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
          <div>
            <h3 className="text-lg font-bold text-white">The gap is infrastructure, not content.</h3>
            <p className="text-sm mt-1 max-w-lg" style={{ color: "var(--muted)" }}>
              Higgsfield&apos;s YouTube engagement rate beats Claude&apos;s. The content works.
              What&apos;s missing is owned community, a distributed amplifier network,
              and one credible HN story.
            </p>
          </div>
          <div
            className="shrink-0 text-xs px-4 py-2 rounded-full border font-medium"
            style={{ borderColor: "rgba(224,123,57,0.4)", color: "#e07b39", background: "rgba(224,123,57,0.06)" }}
          >
            197k Claude · 3.6k Higgsfield
          </div>
        </div>
      </section>

      <footer className="border-t" style={{ borderColor: "var(--border)" }}>
        <div className="max-w-7xl mx-auto px-6 py-8 flex items-center justify-between">
          <span className="text-xs" style={{ color: "var(--muted)" }}>HackNU 2026 · Growth Engineering</span>
          <span className="text-xs" style={{ color: "var(--muted)" }}>Claude 197k items · Higgsfield 3.6k items</span>
        </div>
      </footer>
    </div>
  );
}
