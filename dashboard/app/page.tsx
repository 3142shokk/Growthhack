import { findings, stats } from "@/lib/findings";
import FindingCard from "@/components/FindingCard";
import Hero from "@/components/Hero";
import Nav from "@/components/Nav";

export default function Home() {
  return (
    <div className="min-h-screen" style={{ background: "var(--background)" }}>
      <Nav />
      <Hero />

      {/* Stats bar */}
      <section className="border-y" style={{ borderColor: "var(--border)" }}>
        <div className="max-w-7xl mx-auto px-6 py-6 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-6">
          {stats.map((s) => (
            <div key={s.label} className="text-center">
              <div className="text-2xl font-bold text-white">{s.value}</div>
              <div className="text-xs mt-1" style={{ color: "var(--muted)" }}>{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Findings */}
      <main className="max-w-7xl mx-auto px-6 py-16">
        <div className="mb-12">
          <p className="text-xs font-semibold tracking-widest uppercase mb-2" style={{ color: "var(--accent)" }}>
            Original Analysis
          </p>
          <h2 className="text-3xl font-bold text-white">8 Growth Findings</h2>
          <p className="mt-2 text-sm" style={{ color: "var(--muted)" }}>
            Every claim is sourced from the dataset. Charts are generated from scraped data, not illustrative.
          </p>
        </div>

        <div className="space-y-6">
          {findings.map((f) => (
            <FindingCard key={f.id} finding={f} />
          ))}
        </div>
      </main>

      <footer className="border-t mt-24" style={{ borderColor: "var(--border)" }}>
        <div className="max-w-7xl mx-auto px-6 py-8 flex items-center justify-between">
          <span className="text-xs" style={{ color: "var(--muted)" }}>
            HackNU 2026 · Growth Engineering Track
          </span>
          <span className="text-xs" style={{ color: "var(--muted)" }}>
            74,012 Reddit posts · 3,355 HN stories · 2,127 X tweets
          </span>
        </div>
      </footer>
    </div>
  );
}
