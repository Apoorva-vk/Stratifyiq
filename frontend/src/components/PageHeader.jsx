/** Page hero: bold condensed heading, vector artwork unique to each page, and an orange stats band.
 *  Replace the artwork with your own photo by putting an <img> in the "hero-art" slot. */

const WORDS = {
  dashboard: ["Health", "Budget", "Workload", "Risk"],
  projects: ["Plan", "Track", "Deliver"],
  team: ["Skills", "Workload", "Availability"],
  organisation: ["Company", "Departments", "Teams"],
  simulator: ["Simulate", "Predict", "Decide"],
  reports: ["PDF", "Excel", "Power BI"],
  insights: ["Briefing", "Suggestions", "Patterns"],
  activity: ["Changes", "People", "Time"],
};

const O = "#FF6A13", G = "#2E2E2E", L = "#8C8C8C";

function Art({ variant }) {
  const wrap = (children) => (
    <svg viewBox="0 0 400 260" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
      <rect width="400" height="260" fill="#111111" />
      {children}
    </svg>
  );
  switch (variant) {
    case "dashboard":
      return wrap(<>
        {[[30, 110], [84, 80], [138, 150], [192, 100], [246, 170], [300, 130]].map(([x, h], i) => (
          <rect key={i} x={x} y={260 - h} width="40" height={h} fill={i === 4 ? O : G} />
        ))}
        <line x1="352" y1="10" x2="352" y2="120" stroke={L} strokeWidth="3" />
        <line x1="268" y1="18" x2="380" y2="18" stroke={L} strokeWidth="3" />
        <line x1="352" y1="18" x2="268" y2="92" stroke={L} strokeWidth="1.5" />
      </>);
    case "projects":
      return wrap(<>
        {[...Array(9)].map((_, i) => <line key={`v${i}`} x1={i * 50} y1="0" x2={i * 50} y2="260" stroke="#222" />)}
        {[...Array(6)].map((_, i) => <line key={`h${i}`} x1="0" y1={i * 50} x2="400" y2={i * 50} stroke="#222" />)}
        <rect x="90" y="70" width="150" height="110" fill="none" stroke={O} strokeWidth="3" />
        <rect x="240" y="120" width="90" height="70" fill="none" stroke={L} strokeWidth="2" />
        <circle cx="330" cy="50" r="24" fill="none" stroke={O} strokeWidth="2" strokeDasharray="5 5" />
      </>);
    case "team":
      return wrap(<>
        {[[80, 90], [200, 60], [320, 110], [150, 190], [280, 200]].map(([x, y], i) => (
          <line key={i} x1="200" y1="130" x2={x} y2={y} stroke="#333" strokeWidth="2" />
        ))}
        <circle cx="200" cy="130" r="26" fill={O} />
        {[[80, 90], [200, 60], [320, 110], [150, 190], [280, 200]].map(([x, y], i) => (
          <circle key={`c${i}`} cx={x} cy={y} r="14" fill={G} stroke={L} strokeWidth="2" />
        ))}
      </>);
    case "organisation":
      return wrap(<>
        <rect x="150" y="30" width="100" height="44" fill={O} />
        {[60, 160, 260].map((x, i) => (
          <g key={i}>
            <line x1="200" y1="74" x2={x + 40} y2="110" stroke={L} strokeWidth="2" />
            <rect x={x} y="110" width="80" height="40" fill={G} stroke={L} strokeWidth="1.5" />
            <line x1={x + 40} y1="150" x2={x + 40} y2="186" stroke={L} strokeWidth="2" />
            <rect x={x} y="186" width="80" height="36" fill="none" stroke={O} strokeWidth="2" />
          </g>
        ))}
      </>);
    case "simulator":
      return wrap(<>
        {[40, 80, 120, 160, 200, 240, 280].map((x, i) => (
          <rect key={i} x={x} y={230 - i * 18} width="26" height={20 + i * 18} fill={i > 4 ? O : G} />
        ))}
        <polyline points="30,200 120,150 210,120 300,80 370,50" fill="none" stroke={O} strokeWidth="3" />
      </>);
    case "reports":
      return wrap(<>
        {[0, 1, 2].map((i) => (
          <g key={i} transform={`translate(${100 + i * 40} ${40 + i * 30})`}>
            <rect width="150" height="180" fill={i === 2 ? O : G} />
            {[0, 1, 2, 3, 4].map((j) => <rect key={j} x="18" y={34 + j * 26} width={110 - (j % 3) * 22} height="5" fill={i === 2 ? "#FFE3CC" : L} />)}
          </g>
        ))}
      </>);
    case "insights":
      return wrap(<>
        {[0, 1, 2].map((i) => (
          <path key={i} d={`M0 ${90 + i * 40} Q 50 ${40 + i * 40} 100 ${90 + i * 40} T 200 ${90 + i * 40} T 300 ${90 + i * 40} T 400 ${90 + i * 40}`}
            fill="none" stroke={i === 1 ? O : L} strokeWidth={i === 1 ? 3 : 1.5} opacity={i === 1 ? 1 : 0.6} />
        ))}
      </>);
    case "activity":
      return wrap(<>
        <polyline points="0,150 60,150 90,70 120,210 150,110 180,150 400,150" fill="none" stroke={O} strokeWidth="3" />
        {[0, 1, 2, 3].map((i) => <line key={i} x1="0" y1={40 + i * 60} x2="400" y2={40 + i * 60} stroke="#1f1f1f" />)}
      </>);
    default:
      return wrap(null);
  }
}

export default function PageHeader({ title, kicker, subtitle, variant = "default", actions }) {
  const parts = (title || "").split(" ");
  const last = parts.pop();
  const band = WORDS[variant] || [];
  return (
    <header className={`hero hero-${variant}`}>
      <div className="hero-main">
        {kicker && <p className="hero-kicker">{kicker}</p>}
        <h2 className="hero-title">
          {parts.length > 0 && <span>{parts.join(" ")} </span>}
          <span className="hero-accent">{last}</span>
        </h2>
        {subtitle && <p className="hero-sub">{subtitle}</p>}
        {actions && <div className="hero-actions">{actions}</div>}
      </div>
      <div className="hero-art"><Art variant={variant} /></div>
      {band.length > 0 && (
        <div className="hero-band">
          {band.map((w) => <span key={w}>{w}</span>)}
        </div>
      )}
    </header>
  );
}
