export default function Hero() {
  return (
    <section className="max-w-7xl mx-auto px-6 pt-20 pb-16">
      <div className="max-w-3xl">
        <div
          className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-medium mb-6"
          style={{ borderColor: "#2a2a4a", background: "#13131f", color: "#818cf8" }}
        >
          <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse" />
          Growth Engineering Research · Higgsfield
        </div>

        <h1 className="text-5xl sm:text-6xl font-bold text-white leading-tight tracking-tight">
          Reverse-Engineering<br />
          <span style={{ color: "var(--accent)" }}>Claude&apos;s Virality</span>
        </h1>

        <p className="mt-6 text-lg leading-relaxed" style={{ color: "var(--muted)" }}>
          Original analysis from 74,012 Reddit posts, 3,355 HN stories, and 2,127 X tweets.
          8 data-backed findings on how Claude content goes viral — and what Higgsfield can steal.
        </p>

        <div className="mt-8 flex flex-wrap gap-3">
          {["Community dilution", "Cascade architecture", "Platform mismatch", "Amplifier network", "Copy patterns", "Competitive framing"].map((tag) => (
            <span
              key={tag}
              className="text-xs px-3 py-1.5 rounded-full border"
              style={{ borderColor: "var(--border)", color: "var(--muted)" }}
            >
              {tag}
            </span>
          ))}
        </div>
      </div>
    </section>
  );
}
