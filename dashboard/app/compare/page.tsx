import Nav from "@/components/Nav";
import CompareGrid from "@/components/CompareGrid";
import AnalysisCard from "@/components/AnalysisCard";
import { comparisonCharts, categoryLabels, categoryColors } from "@/lib/comparisons";
import { analysisFindings, analysisTagColors } from "@/lib/analysis";

const STATS = [
  { label: "Claude Reddit posts", cl: "84,088", hf: "2,094",   delta: "40×" },
  { label: "X avg views / post",  cl: "352k",  hf: "172k",    delta: "2×" },
  { label: "YouTube avg views",   cl: "75k",   hf: "33k",     delta: "2.3×" },
  { label: "Top X post (views)",  cl: "33.6M", hf: "5.2M",    delta: "6.5×" },
  { label: "Top Reddit score",    cl: "6,167", hf: "276",     delta: "22×" },
  { label: "HN stories",          cl: "107k",  hf: "—",       delta: "∞" },
];

export default function ComparePage() {
  const categories = [...new Set(comparisonCharts.map((c) => c.category))];

  return (
    <div className="min-h-screen" style={{ background: "var(--background)" }}>
      <Nav />

      {/* Hero */}
      <section className="max-w-7xl mx-auto px-6 pt-16 pb-10">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-7 h-7 rounded-sm flex items-center justify-center" style={{ background: "#e07b39" }}>
            <span className="text-white text-xs font-bold">C</span>
          </div>
          <span className="text-xl font-bold" style={{ color: "#e07b39" }}>Claude</span>
          <span className="text-2xl font-light" style={{ color: "var(--muted)" }}>vs</span>
          <div className="w-7 h-7 rounded-sm flex items-center justify-center" style={{ background: "#6366f1" }}>
            <span className="text-white text-xs font-bold">H</span>
          </div>
          <span className="text-xl font-bold" style={{ color: "#6366f1" }}>Higgsfield</span>
        </div>

        <h1 className="text-4xl font-bold text-white leading-tight">
          Head-to-Head Growth Analysis
        </h1>
        <p className="mt-3 text-base max-w-2xl" style={{ color: "var(--muted)" }}>
          15 comparison charts across community scale, engagement, content archetypes,
          amplifier networks, and platform mix. Data from full scraped datasets for both brands.
        </p>
      </section>

      {/* Key numbers bar */}
      <section className="border-y" style={{ borderColor: "var(--border)" }}>
        <div className="max-w-7xl mx-auto px-6 py-0">
          <div className="grid grid-cols-3 lg:grid-cols-6">
            {STATS.map((s, i) => (
              <div
                key={s.label}
                className="py-5 px-4 border-r last:border-r-0"
                style={{ borderColor: "var(--border)" }}
              >
                <div className="text-xs mb-2" style={{ color: "var(--muted)" }}>{s.label}</div>
                <div className="flex items-end gap-2">
                  <span className="text-base font-bold" style={{ color: "#e07b39" }}>{s.cl}</span>
                  <span className="text-xs pb-0.5" style={{ color: "var(--muted)" }}>vs</span>
                  <span className="text-base font-bold" style={{ color: "#6366f1" }}>{s.hf}</span>
                </div>
                <div className="text-xs mt-1 font-semibold" style={{ color: s.delta === "∞" ? "#ef4444" : "#22c55e" }}>
                  {s.delta} gap
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Category filter + grid */}
      <main className="max-w-7xl mx-auto px-6 py-12">
        <CompareGrid charts={comparisonCharts} categories={categories} />
      </main>

      {/* ── STRUCTURAL GAPS ── */}
      <section className="border-t" style={{ borderColor: "var(--border)" }}>
        <div className="max-w-7xl mx-auto px-6 py-16">
          <div className="mb-10">
            <p className="text-xs font-semibold tracking-widest uppercase mb-2" style={{ color: "#e07b39" }}>
              Gap Analysis
            </p>
            <h2 className="text-3xl font-bold text-white">6 Structural Gaps</h2>
            <p className="mt-2 text-sm max-w-2xl" style={{ color: "var(--muted)" }}>
              What the data reveals about Higgsfield's growth infrastructure — fragility, community, efficiency, brand, and distribution.
              Each finding includes a concrete action to close the gap.
            </p>
          </div>
          <div className="space-y-5">
            {analysisFindings.map((f) => (
              <AnalysisCard key={f.id} finding={f} />
            ))}
          </div>
        </div>
      </section>

      <footer className="border-t mt-4" style={{ borderColor: "var(--border)" }}>
        <div className="max-w-7xl mx-auto px-6 py-8 flex items-center justify-between">
          <span className="text-xs" style={{ color: "var(--muted)" }}>HackNU 2026 · Growth Engineering</span>
          <span className="text-xs" style={{ color: "var(--muted)" }}>197k Claude items · 3.6k Higgsfield items</span>
        </div>
      </footer>
    </div>
  );
}
