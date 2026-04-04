"use client";

import { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { Finding, tagColors } from "@/lib/findings";

export default function FindingCard({ finding: f }: { finding: Finding }) {
  const [open, setOpen] = useState(false);
  const [activeChart, setActiveChart] = useState(0);

  return (
    <article
      className="finding-card rounded-xl border overflow-hidden transition-all duration-200"
      style={{ borderColor: "var(--border)", background: "#0e0e18" }}
    >
      {/* Header — always visible */}
      <button
        className="w-full text-left p-6 flex items-start gap-5 hover:bg-white/[0.02] transition-colors"
        onClick={() => setOpen((v) => !v)}
      >
        {/* Number */}
        <span
          className="finding-number text-4xl font-bold tabular-nums transition-colors shrink-0 leading-none mt-0.5"
          style={{ color: "#2a2a3a" }}
        >
          {String(f.number).padStart(2, "0")}
        </span>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <span
              className={`text-xs px-2 py-0.5 rounded-full border font-medium ${tagColors[f.tag]}`}
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

        {/* Stat + chevron */}
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

      {/* Expanded body */}
      {open && (
        <div className="border-t" style={{ borderColor: "var(--border)" }}>
          <div className="p-6 grid grid-cols-1 lg:grid-cols-2 gap-8">

            {/* Left: analysis text */}
            <div className="space-y-6">
              {/* Body */}
              <div>
                <h4 className="text-xs font-semibold uppercase tracking-wider mb-3" style={{ color: "var(--muted)" }}>
                  Finding
                </h4>
                <div className="space-y-3">
                  {f.body.split("\n\n").map((para, i) => (
                    <p key={i} className="text-sm leading-relaxed" style={{ color: "#c4c4d0" }}>
                      {para}
                    </p>
                  ))}
                </div>
              </div>

              {/* Higgsfield callout */}
              <div
                className="rounded-lg p-4 border-l-4"
                style={{ background: "#13131f", borderLeftColor: "var(--accent)" }}
              >
                <div className="flex items-center gap-2 mb-2">
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <path d="M7 1L8.5 5.5H13L9.25 8.25L10.75 12.75L7 10L3.25 12.75L4.75 8.25L1 5.5H5.5L7 1Z"
                      fill="#6366f1" />
                  </svg>
                  <span className="text-xs font-semibold" style={{ color: "var(--accent)" }}>
                    For Higgsfield
                  </span>
                </div>
                <p className="text-sm leading-relaxed" style={{ color: "#a0a0b8" }}>
                  {f.higgsfield}
                </p>
              </div>
            </div>

            {/* Right: charts */}
            <div>
              <h4 className="text-xs font-semibold uppercase tracking-wider mb-3" style={{ color: "var(--muted)" }}>
                Supporting Charts
              </h4>

              {/* Chart tabs */}
              {f.charts.length > 1 && (
                <div className="flex gap-1 mb-3 flex-wrap">
                  {f.charts.map((c, i) => (
                    <button
                      key={i}
                      onClick={() => setActiveChart(i)}
                      className="text-xs px-3 py-1.5 rounded-md border transition-colors"
                      style={{
                        borderColor: activeChart === i ? "var(--accent)" : "var(--border)",
                        background: activeChart === i ? "rgba(99,102,241,0.1)" : "transparent",
                        color: activeChart === i ? "#818cf8" : "var(--muted)",
                      }}
                    >
                      Chart {i + 1}
                    </button>
                  ))}
                </div>
              )}

              {/* Chart image */}
              <div
                className="rounded-lg overflow-hidden border"
                style={{ borderColor: "var(--border)" }}
              >
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

            <div className="mt-4 flex justify-end">
              <Link
                href={`/finding/${f.id}`}
                className="inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-md border transition-colors hover:border-indigo-500/50 hover:text-indigo-400"
                style={{ borderColor: "var(--border)", color: "var(--muted)" }}
                onClick={(e) => e.stopPropagation()}
              >
                View full finding
                <svg width="12" height="12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </Link>
            </div>
          </div>
        </div>
      )}
    </article>
  );
}
