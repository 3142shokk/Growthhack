import { findings, tagColors } from "@/lib/findings";
import { notFound } from "next/navigation";
import Image from "next/image";
import Link from "next/link";
import Nav from "@/components/Nav";

export function generateStaticParams() {
  return findings.map((f) => ({ id: f.id }));
}

export default async function FindingPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const finding = findings.find((f) => f.id === id);
  if (!finding) notFound();

  const idx = findings.indexOf(finding);
  const prev = findings[idx - 1];
  const next = findings[idx + 1];

  return (
    <div className="min-h-screen" style={{ background: "var(--background)" }}>
      <Nav />

      <main className="max-w-6xl mx-auto px-6 py-16">
        {/* Back */}
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-sm mb-10 transition-colors hover:text-white"
          style={{ color: "var(--muted)" }}
        >
          <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          All findings
        </Link>

        {/* Header */}
        <div className="mb-12">
          <div className="flex flex-wrap items-center gap-3 mb-4">
            <span
              className="text-5xl font-bold tabular-nums"
              style={{ color: "#2a2a3a" }}
            >
              {String(finding.number).padStart(2, "0")}
            </span>
            <span className={`text-xs px-2.5 py-1 rounded-full border font-medium ${tagColors[finding.tag]}`}>
              {finding.tag}
            </span>
          </div>

          <h1 className="text-3xl sm:text-4xl font-bold text-white leading-tight">
            {finding.title}
          </h1>
          <p className="text-lg mt-3" style={{ color: "var(--muted)" }}>
            {finding.subtitle}
          </p>

          {/* Key stat */}
          <div
            className="inline-flex items-center gap-4 mt-6 px-6 py-4 rounded-xl border"
            style={{ borderColor: "var(--border)", background: "#0e0e18" }}
          >
            <div>
              <div className="text-3xl font-bold text-white">{finding.stat}</div>
              <div className="text-xs mt-0.5" style={{ color: "var(--muted)" }}>{finding.statLabel}</div>
            </div>
          </div>
        </div>

        {/* Body + charts */}
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-12">
          {/* Analysis — 2 cols */}
          <div className="lg:col-span-2 space-y-8">
            <div>
              <h2 className="text-xs font-semibold uppercase tracking-wider mb-4" style={{ color: "var(--muted)" }}>
                Finding
              </h2>
              <div className="space-y-4">
                {finding.body.split("\n\n").map((para, i) => (
                  <p key={i} className="text-sm leading-relaxed" style={{ color: "#c4c4d0" }}>
                    {para}
                  </p>
                ))}
              </div>
            </div>

            <div
              className="rounded-xl p-5 border-l-4"
              style={{ background: "#0e0e18", borderLeftColor: "var(--accent)", border: "1px solid var(--border)", borderLeft: "4px solid var(--accent)" }}
            >
              <div className="flex items-center gap-2 mb-3">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <path d="M7 1L8.5 5.5H13L9.25 8.25L10.75 12.75L7 10L3.25 12.75L4.75 8.25L1 5.5H5.5L7 1Z" fill="#6366f1" />
                </svg>
                <span className="text-xs font-semibold" style={{ color: "var(--accent)" }}>
                  For Higgsfield
                </span>
              </div>
              <p className="text-sm leading-relaxed" style={{ color: "#a0a0b8" }}>
                {finding.higgsfield}
              </p>
            </div>
          </div>

          {/* Charts — 3 cols */}
          <div className="lg:col-span-3 space-y-6">
            <h2 className="text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--muted)" }}>
              Supporting Charts ({finding.charts.length})
            </h2>
            {finding.charts.map((chart, i) => (
              <div key={i}>
                <div
                  className="rounded-xl overflow-hidden border"
                  style={{ borderColor: "var(--border)" }}
                >
                  <Image
                    src={`/charts/${chart.file}`}
                    alt={chart.caption}
                    width={900}
                    height={560}
                    className="w-full h-auto"
                    style={{ background: "#fff" }}
                  />
                </div>
                <p className="text-xs mt-2" style={{ color: "var(--muted)" }}>
                  {chart.caption}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Prev / next */}
        <div className="grid grid-cols-2 gap-4 mt-20 pt-8 border-t" style={{ borderColor: "var(--border)" }}>
          <div>
            {prev && (
              <Link
                href={`/finding/${prev.id}`}
                className="block p-4 rounded-xl border transition-colors hover:border-indigo-500/30 hover:bg-white/[0.02]"
                style={{ borderColor: "var(--border)" }}
              >
                <div className="text-xs mb-1" style={{ color: "var(--muted)" }}>← Previous</div>
                <div className="text-sm font-medium text-white">{prev.title}</div>
              </Link>
            )}
          </div>
          <div>
            {next && (
              <Link
                href={`/finding/${next.id}`}
                className="block p-4 rounded-xl border text-right transition-colors hover:border-indigo-500/30 hover:bg-white/[0.02]"
                style={{ borderColor: "var(--border)" }}
              >
                <div className="text-xs mb-1" style={{ color: "var(--muted)" }}>Next →</div>
                <div className="text-sm font-medium text-white">{next.title}</div>
              </Link>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
