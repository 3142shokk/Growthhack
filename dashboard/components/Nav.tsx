export default function Nav() {
  return (
    <nav
      className="sticky top-0 z-50 border-b backdrop-blur-md"
      style={{ borderColor: "var(--border)", background: "rgba(9,9,15,0.85)" }}
    >
      <div className="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-6 h-6 rounded-sm flex items-center justify-center" style={{ background: "var(--accent)" }}>
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M2 7L6 11L12 3" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
          <span className="text-sm font-semibold text-white">Claude Growth Analysis</span>
        </div>
        <div className="flex items-center gap-6">
          <span className="text-xs hidden sm:block" style={{ color: "var(--muted)" }}>HackNU 2026</span>
          <span
            className="text-xs px-2.5 py-1 rounded-full border font-medium"
            style={{ borderColor: "var(--border)", color: "var(--muted)" }}
          >
            Apr 2026
          </span>
        </div>
      </div>
    </nav>
  );
}
