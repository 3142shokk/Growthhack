"use client";

import { useState } from "react";
import Image from "next/image";
import { AnalysisFinding, analysisTagColors } from "@/lib/analysis";

export default function AnalysisCard({ finding: f }: { finding: AnalysisFinding }) {
  const [open, setOpen] = useState(false);
  const [activeChart, setActiveChart] = useState(0);

  return (
    <article
      className="rounded-xl border overflow-hidden transition-all duration-200"
      style={{ borderColor: "var(--border)", background: "#0e0e18" }}
    >
      <button
        className="w-full text-left p-6 flex items-start gap-5 hover:bg-white/[0.02] transition-colors"
        onClick={() => setOpen((v) => !v)}
      >
        <span
          className="text-4xl font-bold tabular-nums shrink-0 leading-none mt-0.5"
          style={{ color: "#2a2a3a" }}
        >
          {String(f.number).padStart(2, "0")}
        </span>

        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <span
              className={`text-xs px-2 py-0.5 rounded-full border font-medium ${analysisTagColors[f.tag]}`}
            >
              {f.tag}
            </span>
            <span className="text-xs" style={{ color: "var(--muted)" }}>
              {f.charts.length} chart{f.charts.length > 1 ? "s" : ""}
            </span>
          </div>
          <h3 className="text-base sm:text-lg font-semibold text-white leading-snug">
            {f.title}
          </h3>
          <p className="text-sm mt-1" style={{ color: "var(--muted)" }}>
            {f.subtitle}
          </p>
        </div>

        <div className="shrink-0 text-right hidden sm:block">
          <div className="text-xl font-bold text-white">{f.stat}</div>
          <div className="text-xs mt-0.5" style={{ color: "var(--muted)" }}>{f.statLabel}</div>
        </div>

        <div className="shrink-0 ml-2 mt-1">
          <svg
            className={`w-4 h-4 transition-transform duration-200 ${open ? "rotate-180" : ""}`}
            style={{ color: "var(--muted)" }}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>

      {open && (
        <div className="border-t" style={{ borderColor: "var(--border)" }}>
          <div className="p-6 grid grid-cols-1 lg:grid-cols-2 gap-8">

            <div className="space-y-6">
              <div>
                <h4 className="text-xs font-semibold uppercase tracking-wider mb-3" style={{ color: "var(--muted)" }}>
                  Analysis
                </h4>
                <div className="space-y-3">
                  {f.body.split("\n\n").map((para, i) => (
                    <p key={i} className="text-sm leading-relaxed" style={{ color: "#c4c4d0" }}>
                      {para}
                    </p>
                  ))}
                </div>
              </div>

              {/* Action callout — orange accent for Higgsfield */}
              <div
                className="rounded-lg p-4"
                style={{
                  background: "rgba(224,123,57,0.06)",
                  borderLeft: "4px solid #e07b39",
                  border: "1px solid rgba(224,123,57,0.2)",
                  borderLeftWidth: "4px",
                }}
              >
                <div className="flex items-center gap-2 mb-2">
                  <div
                    className="w-4 h-4 rounded-sm flex items-center justify-center"
                    style={{ background: "#e07b39" }}
                  >
                    <span className="text-white text-[8px] font-bold">H</span>
                  </div>
                  <span className="text-xs font-semibold" style={{ color: "#e07b39" }}>
                    Action for Higgsfield
                  </span>
                </div>
                <p className="text-sm leading-relaxed" style={{ color: "#c0a090" }}>
                  {f.action}
                </p>
              </div>
            </div>

            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wider mb-3" style={{ color: "var(--muted)" }}>
                Supporting Charts
              </h4>

              {f.charts.length > 1 && (
                <div className="flex gap-1 mb-3 flex-wrap">
                  {f.charts.map((c, i) => (
                    <button
                      key={i}
                      onClick={() => setActiveChart(i)}
                      className="text-xs px-3 py-1.5 rounded-md border transition-colors"
                      style={{
                        borderColor: activeChart === i ? "#e07b39" : "var(--border)",
                        background: activeChart === i ? "rgba(224,123,57,0.1)" : "transparent",
                        color: activeChart === i ? "#e07b39" : "var(--muted)",
                      }}
                    >
                      Chart {i + 1}
                    </button>
                  ))}
                </div>
              )}

              <div className="rounded-lg overflow-hidden border" style={{ borderColor: "var(--border)" }}>
                <Image
                  src={`/charts/${f.charts[activeChart].file}`}
                  alt={f.charts[activeChart].caption}
                  width={800}
                  height={500}
                  className="w-full h-auto"
                  style={{ background: "#fff" }}
                />
              </div>
              <p className="text-xs mt-2" style={{ color: "var(--muted)" }}>
                {f.charts[activeChart].caption}
              </p>
            </div>
          </div>
        </div>
      )}
    </article>
  );
}
