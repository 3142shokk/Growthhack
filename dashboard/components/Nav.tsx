import Link from "next/link";

const NAV_LINKS = [
  { href: "/",         label: "01 · Claude Insights",      color: "#818cf8", border: "rgba(99,102,241,0.35)",  bg: "rgba(99,102,241,0.06)"  },
  { href: "/compare",  label: "02 · Claude vs Higgsfield",  color: "#e07b39", border: "rgba(224,123,57,0.35)", bg: "rgba(224,123,57,0.06)"  },
  { href: "/pipeline", label: "03 · Automation Pipeline",   color: "#22c55e", border: "rgba(34,197,94,0.3)",   bg: "rgba(34,197,94,0.05)"   },
  { href: "/playbook", label: "04 · Counter-Playbook",      color: "#f59e0b", border: "rgba(245,158,11,0.35)", bg: "rgba(245,158,11,0.05)"  },
];

export default function Nav() {
  return (
    <nav
      className="sticky top-0 z-50 border-b backdrop-blur-md"
      style={{ borderColor: "var(--border)", background: "rgba(9,9,15,0.85)" }}
    >
      <div className="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link href="/" className="flex items-center gap-2 mr-3">
            <div className="w-6 h-6 rounded-sm flex items-center justify-center" style={{ background: "var(--accent)" }}>
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M2 7L6 11L12 3" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </div>
            <span className="text-sm font-semibold text-white hidden md:block">GrowthHack</span>
          </Link>
          {NAV_LINKS.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className="text-xs px-3 py-1.5 rounded-md border transition-colors hidden sm:block"
              style={{ borderColor: l.border, color: l.color, background: l.bg }}
            >
              {l.label}
            </Link>
          ))}
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
