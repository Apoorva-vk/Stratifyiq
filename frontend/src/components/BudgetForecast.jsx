import { useEffect, useState } from "react";
import { api } from "../api";

const W = 620;
const H = 240;
const P = 36;
const STATUS = {
  ON_TRACK: ["On track", "#17663a", "#d7f5e3"],
  AT_RISK: ["At risk", "#7a5600", "#fdf0c8"],
  OVER_BUDGET: ["Over budget", "#8a1d1d", "#fbd5d5"],
};
const money = (n) => (n == null ? "—" : Number(n).toLocaleString());

/** Budget forecast for one project: burn rate, projected total and a planned-versus-projected chart. */
export default function BudgetForecast({ projectId }) {
  const [f, setF] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    setF(null);
    setError("");
    api(`/analytics/projects/${projectId}/forecast`).then(setF).catch((e) => setError(e.message));
  }, [projectId]);

  if (error) return <p className="error">{error}</p>;
  if (!f) return null;

  const [label, color, bg] = STATUS[f.status];
  const maxY = Math.max(f.budget, f.projected_spend_at_current_burn, ...f.series.map((s) => s.projected)) * 1.1;
  const x = (d) => P + (d / f.total_days) * (W - 2 * P);
  const y = (v) => H - P - (v / maxY) * (H - 2 * P);
  const line = (key) => f.series.map((s) => `${x(s.day)},${y(s[key])}`).join(" ");
  const todayX = x(f.elapsed_days);

  return (
    <div className="forecast">
      <h4>
        Budget forecast{" "}
        <span className="chip" style={{ background: bg, color }}>{label}</span>
      </h4>

      <div className="grid">
        <div className="score"><span>Spent so far</span><strong>{money(f.spent)}</strong></div>
        <div className="score"><span>Daily burn</span><strong>{money(f.daily_burn)}</strong></div>
        <div className="score"><span>Projected at current burn</span><strong>{money(f.projected_spend_at_current_burn)}</strong></div>
        <div className="score"><span>Projected overrun</span><strong>{f.projected_overrun_pct}%</strong></div>
        <div className="score"><span>Total implied by progress</span><strong>{money(f.projected_total_by_progress)}</strong></div>
        <div className="score"><span>Days left</span><strong>{f.days_left}</strong></div>
      </div>

      <svg viewBox={`0 0 ${W} ${H}`} className="forecast-chart" role="img" aria-label="Planned versus projected spend">
        <line x1={P} y1={H - P} x2={W - P} y2={H - P} stroke="#c5ccd8" />
        <line x1={P} y1={P} x2={P} y2={H - P} stroke="#c5ccd8" />
        <line x1={todayX} y1={P} x2={todayX} y2={H - P} stroke="#1f3a5f" strokeDasharray="4 4" />
        <text x={todayX + 4} y={P + 10} fontSize="11" fill="#1f3a5f">today</text>
        <line x1={P} y1={y(f.budget)} x2={W - P} y2={y(f.budget)} stroke="#d64545" strokeDasharray="6 4" />
        <text x={W - P - 4} y={y(f.budget) - 6} fontSize="11" fill="#d64545" textAnchor="end">budget {money(f.budget)}</text>
        <polyline points={line("planned")} fill="none" stroke="#8a94a6" strokeWidth="2" />
        <polyline points={line("projected")} fill="none" stroke="#1f3a5f" strokeWidth="3" />
        <text x={P} y={H - 10} fontSize="11" fill="#5b6578">day 0</text>
        <text x={W - P} y={H - 10} fontSize="11" fill="#5b6578" textAnchor="end">deadline</text>
      </svg>
      <p className="muted small">
        Grey line: planned spend if the budget were used evenly. Blue line: spend at the current burn rate.
      </p>
    </div>
  );
}
