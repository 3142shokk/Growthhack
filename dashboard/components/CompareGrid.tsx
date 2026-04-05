"use client";

import { useState } from "react";
import Image from "next/image";
import { ComparisonChart, categoryLabels, categoryColors } from "@/lib/comparisons";

export default function CompareGrid({
  charts,
  categories,
}: {
  charts: ComparisonChart[];
  categories: ComparisonChart["category"][];
}) {
  const [active, setActive] = useState<ComparisonChart["category"] | "all">("all");
  const [expanded, setExpanded] = useState<string | null>(null);

  const visible = active === "all" ? charts : charts.filter((c) => c.category === active);

  return (
    <div>
      {/* Filter tabs */}
      <div className="flex flex-wrap gap-2 mb-8">
        <button
          onClick={() => setActive("all")}
          className="text-xs px-4 py-2 rounded-full border font-medium transition-colors"
          style={{
            borderColor: active === "all" ? "var(--accent)" : "var(--border)",
            background: active === "all" ? "rgba(99,102,241,0.12)" : "transparent",
            color: active === "all" ? "#818cf8" : "var(--muted)",
          }}
        >
          All ({charts.length})
        </button>
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setActive(cat)}
            className="text-xs px-4 py-2 rounded-full border font-medium transition-colors"
            style={{
              borderColor: active === cat ? "var(--accent)" : "var(--border)",
              background: active === cat ? "rgba(99,102,241,0.12)" : "transparent",
              color: active === cat ? "#818cf8" : "var(--muted)",
            }}
          >
            {categoryLabels[cat]} ({charts.filter((c) => c.category === cat).length})
          </button>
        ))}
      </div>

      {/* Chart grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {visible.map((chart) => (
          <div
            key={chart.file}
            className="rounded-xl border overflow-hidden transition-all duration-200"
            style={{ borderColor: "var(--border)", background: "#0e0e18" }}
          >
            {/* Chart image */}
            <button
              className="w-full cursor-zoom-in"
              onClick={() => setExpanded(expanded === chart.file ? null : chart.file)}
            >
              <Image
                src={`/charts/${chart.file}`}
                alt={chart.title}
                width={900}
                height={560}
                className="w-full h-auto"
                style={{ background: "#fff" }}
              />
            </button>

            {/* Info */}
            <div className="p-5">
              <div className="flex items-start justify-between gap-3 mb-2">
                <div>
                  <span className={`text-xs px-2 py-0.5 rounded-full border font-medium mr-2 ${categoryColors[chart.category]}`}>
                    {categoryLabels[chart.category]}
                  </span>
                  <h3 className="inline text-sm font-semibold text-white">{chart.title}</h3>
                </div>
              </div>
              <p className="text-xs mb-3" style={{ color: "var(--muted)" }}>{chart.subtitle}</p>

              {/* Insight */}
              <div
                className="rounded-lg p-3 border-l-4"
                style={{ background: "#13131f", borderLeftColor: "#6366f1" }}
              >
                <p className="text-xs leading-relaxed" style={{ color: "#a0a0c8" }}>
                  {chart.insight}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Lightbox */}
      {expanded && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          style={{ background: "rgba(0,0,0,0.92)" }}
          onClick={() => setExpanded(null)}
        >
          <div className="max-w-5xl w-full" onClick={(e) => e.stopPropagation()}>
            <Image
              src={`/charts/${expanded}`}
              alt="Chart"
              width={1200}
              height={750}
              className="w-full h-auto rounded-xl"
              style={{ background: "#fff" }}
            />
            <button
              className="mt-3 text-xs px-4 py-2 rounded-full border mx-auto block"
              style={{ borderColor: "var(--border)", color: "var(--muted)" }}
              onClick={() => setExpanded(null)}
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
