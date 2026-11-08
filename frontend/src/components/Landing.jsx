import { useState } from "react";

const POINTS = [
  { title: "Predict", text: "Estimate delay, overrun and success before they happen." },
  { title: "Simulate", text: "Test a hiring, budget or deadline choice without changing the plan." },
  { title: "Recommend", text: "See the best next action, with the reasons behind it." },
];

const FEATURES = [
  { title: "Scenario Simulator", text: "Model every path before you commit, and compare outcomes side by side." },
  { title: "Portfolio View", text: "Every project, risk and dependency in one clear picture." },
  { title: "Detailed Reporting", text: "Weekly digests and live dashboards that keep stakeholders aligned." },
  { title: "Decision Memory", text: "A record of what was decided, why, and what happened next." },
];

const PLATFORM = [
  { title: "Scenario Simulation", text: "Weigh budget, timeline and risk trade-offs before a single resource moves.", art: "a" },
  { title: "Live Reports & Forecasts", text: "Health rings, burn analysis and forecasts delivered to the people who need them.", art: "b" },
  { title: "Team Intelligence", text: "Suggestions and workload signals that keep your people as healthy as your plans.", art: "c" },
];

const RESOURCES = [
  { title: "Dashboard", text: "Company health, budgets and workload on one screen." },
  { title: "Reports", text: "PDF, Excel and Power BI files built from the same figures." },
  { title: "Security", text: "Admins see everything. Managers see the work they created." },
];

const Icon = ({ d }) => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d={d} />
  </svg>
);
const ICONS = {
  Predict: "M3 17l6-6 4 4 8-8M14 7h7v7",
  Simulate: "M4 6h16M4 12h10M4 18h7M18 14l3 3-3 3",
  Recommend: "M12 3l2.5 5.5L20 11l-5.5 2.5L12 19l-2.5-5.5L4 11l5.5-2.5z",
  "Scenario Simulator": "M4 4h16v12H4zM8 20h8",
  "Portfolio View": "M12 3l9 5-9 5-9-5 9-5zM3 13l9 5 9-5",
  "Detailed Reporting": "M7 3h7l5 5v13H7zM14 3v5h5M10 13h6M10 17h6",
  "Decision Memory": "M4 4h12l4 4v12H4zM8 12h8M8 16h5",
};

function scrollTo(id) {
  const el = document.getElementById(id);
  if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
}

export default function Landing({ onEnter }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const [cube, setCube] = useState({ x: -18, y: 28 });

  function onHeroMove(e) {
    const r = e.currentTarget.getBoundingClientRect();
    const x = (e.clientX - r.left) / r.width - 0.5;
    const y = (e.clientY - r.top) / r.height - 0.5;
    setCube({ x: -18 - y * 24, y: 28 + x * 50 });
  }

  function go(id) {
    setMenuOpen(false);
    scrollTo(id);
  }

  return (
    <div className="lp lp2">
      <header className="lp2-nav">
        <div className="lp2-wrap lp2-nav-inner">
          <button className="lp2-brand" onClick={() => go("top")} aria-label="StratifyIQ home">
            <svg width="30" height="30" viewBox="0 0 40 40" aria-hidden="true">
              <polygon points="20,2 36,11 36,29 20,38 4,29 4,11" fill="#E8701A" />
              <path d="M26 12.5 H14 V19.5 H26 V27.5 H14" fill="none" stroke="#FFF6EC" strokeWidth="3.4" />
            </svg>
            <span>StratifyIQ</span>
          </button>
          <nav className={`lp2-links ${menuOpen ? "open" : ""}`} aria-label="Main">
            <button onClick={() => go("features")}>Solutions</button>
            <button onClick={() => go("platform")}>Platform</button>
            <button onClick={() => go("resources")}>Resources</button>
            <button onClick={() => go("contact")}>Contact</button>
          </nav>
          <div className="lp2-nav-actions">
            <button className="lp2-ghost" onClick={onEnter}>Sign in</button>
            <button className="lp2-burger" aria-expanded={menuOpen} aria-label="Open menu" onClick={() => setMenuOpen(!menuOpen)}>
              {menuOpen ? "Close" : "Menu"}
            </button>
          </div>
        </div>
      </header>

      <section className="lp2-hero" id="top" onMouseMove={onHeroMove}>
        <div className="lp2-wrap lp2-hero-grid">
          <div className="lp2-hero-copy">
            <p className="lp2-eyebrow">Decision intelligence platform</p>
            <h1 className="lp2-title">
              <span className="lp2-accent">Decision</span> intelligence for every project
            </h1>
            <p className="lp2-lead">
              Plan projects, test decisions before you make them, and see the likely outcome first.
            </p>
            <div className="lp2-actions">
              <button className="lp2-btn" onClick={onEnter}>Open Dashboard</button>
              <button className="lp2-ghost" onClick={() => go("platform")}>Explore the platform</button>
            </div>
          </div>
          <div className="lp2-cube-stage" aria-hidden="true">
            <div className="lp2-cube" style={{ transform: `rotateX(${cube.x}deg) rotateY(${cube.y}deg)` }}>
              <div className="lp2-face f1"><span>S</span></div>
              <div className="lp2-face f2" />
              <div className="lp2-face f3" />
              <div className="lp2-face f4" />
              <div className="lp2-face f5" />
              <div className="lp2-face f6" />
            </div>
          </div>
        </div>
        <div className="lp2-wrap">
          <ul className="lp2-points">
            {POINTS.map((p) => (
              <li key={p.title}>
                <span className="lp2-point-icon"><Icon d={ICONS[p.title]} /></span>
                <div>
                  <strong>{p.title}</strong>
                  <span>{p.text}</span>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </section>

      <section className="lp2-section" id="features">
        <div className="lp2-wrap">
          <p className="lp2-kicker">Solutions</p>
          <h2 className="lp2-h2">Everything you need to decide well</h2>
          <div className="lp2-grid4">
            {FEATURES.map((f) => (
              <article key={f.title} className="lp2-card">
                <span className="lp2-card-icon"><Icon d={ICONS[f.title]} /></span>
                <h3>{f.title}</h3>
                <p>{f.text}</p>
                <button className="lp2-link" onClick={onEnter}>Open</button>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="lp2-section lp2-alt" id="platform">
        <div className="lp2-wrap">
          <p className="lp2-kicker">The platform</p>
          <h2 className="lp2-h2">Built around how managers actually work</h2>
          <div className="lp2-grid3">
            {PLATFORM.map((p) => (
              <article key={p.title} className="lp2-tile">
                <div className={`lp2-tile-art lp2-art-${p.art}`} aria-hidden="true" />
                <div className="lp2-tile-body">
                  <h3>{p.title}</h3>
                  <p>{p.text}</p>
                  <button className="lp2-btn small" onClick={onEnter}>Explore</button>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="lp2-section" id="resources">
        <div className="lp2-wrap">
          <p className="lp2-kicker">Resources</p>
          <h2 className="lp2-h2">Explore the parts of the system</h2>
          <div className="lp2-grid3 lp2-slim">
            {RESOURCES.map((r) => (
              <article key={r.title} className="lp2-card">
                <h3>{r.title}</h3>
                <p>{r.text}</p>
                <button className="lp2-link" onClick={onEnter}>Sign in to view</button>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="lp2-cta" id="cta">
        <div className="lp2-wrap lp2-cta-inner">
          <div>
            <h2>Make the call with confidence</h2>
            <p>Bring strategy, execution and memory into one platform.</p>
          </div>
          <button className="lp2-btn" onClick={onEnter}>Get started</button>
        </div>
      </section>

      <footer className="lp2-footer" id="contact">
        <div className="lp2-wrap lp2-foot-grid">
          <div>
            <strong className="lp2-foot-brand">StratifyIQ</strong>
            <p>Decision intelligence for projects, budgets and teams.</p>
          </div>
          <div className="lp2-foot-col">
            <span>Explore</span>
            <button onClick={() => go("features")}>Solutions</button>
            <button onClick={() => go("platform")}>Platform</button>
            <button onClick={() => go("resources")}>Resources</button>
          </div>
          <div className="lp2-foot-col">
            <span>Account</span>
            <button onClick={onEnter}>Sign in</button>
            <button onClick={onEnter}>Create account</button>
          </div>
          <div className="lp2-foot-col">
            <span>Contact</span>
            <a href="mailto:hello@stratifyiq.example">hello@stratifyiq.example</a>
          </div>
        </div>
        <div className="lp2-wrap lp2-copy">© {new Date().getFullYear()} StratifyIQ. All rights reserved.</div>
      </footer>
    </div>
  );
}
