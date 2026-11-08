import { useEffect, useState } from "react";
import { api } from "../api";
import HealthRing from "../components/HealthRing";
import BarList from "../components/BarList";
import MoodFace from "../components/MoodFace";
import CountdownBanner from "../components/CountdownBanner";
import PageHeader from "../components/PageHeader";

const money = (n) => Number(n).toLocaleString();

export default function Dashboard({ onSimulate }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api("/analytics/dashboard").then(setData).catch((e) => setError(e.message));
  }, []);

  if (error) return <p className="error">{error}</p>;
  if (!data) return <p>Loading...</p>;

  const h = data.business_health;

  const budgetRows = data.projects.map((p) => ({
    label: p.name,
    value: p.spent,
    max: p.budget,
    detail: `${money(p.spent)} of ${money(p.budget)}`,
    cls: p.spent > p.budget ? "OVER" : p.spent > 0.9 * p.budget ? "UNDER" : "OK",
  }));

  const teamRows = data.team.map((t) => ({
    label: t.name,
    value: Math.min(t.utilization_pct, 100),
    max: 100,
    detail: `${t.utilization_pct}%`,
    cls: t.utilization_pct > 100 ? "OVER" : t.utilization_pct < 40 ? "UNDER" : "OK",
  }));

  return (
    <div>
      <PageHeader variant="dashboard" kicker="Overview" title="Executive Dashboard" subtitle="Company health, budgets and workload at a glance." />
      <p className="muted">
        {data.total_projects} projects · {data.total_employees} team members · {data.high_risk_projects.length} high risk
      </p>

      <CountdownBanner />

      <div className="rings">
        <HealthRing value={h.overall_health} label="Overall health" />
        <HealthRing value={h.project_health} label="Project health" />
        <HealthRing value={h.financial_health} label="Financial health" />
        <HealthRing value={h.risk_health} label="Risk health" />
        <HealthRing value={h.employee_health} label="Employee health" />
      </div>

      <div className="charts">
        <div className="card">
          <h3>Budget used by project</h3>
          <BarList rows={budgetRows} emptyText="No projects yet." />
          <p className="muted small">Amber means over 90% used, red means over budget.</p>
        </div>
        <div className="card">
          <h3>Team workload</h3>
          <BarList rows={teamRows} emptyText="No team members yet." />
          <p className="muted small">Green is healthy, amber is under 40%, red is over 100%.</p>
        </div>
      </div>

      <h3>Projects</h3>
      <table>
        <thead>
          <tr>
            <th>Project</th>
            <th>Risk</th>
            <th>Delay risk</th>
            <th>Overrun %</th>
            <th>Success %</th>
            <th>Mood</th>
            <th>Health</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {data.projects.map((p) => (
            <tr key={p.project_id}>
              <td>{p.name}</td>
              <td>
                <span className={`badge ${p.risk_level}`}>{p.risk_level}</span>
              </td>
              <td>{(p.prediction.delay_risk * 100).toFixed(1)}%</td>
              <td>{p.prediction.overrun_pct.toFixed(1)}</td>
              <td>{p.prediction.success_probability.toFixed(1)}</td>
              <td><MoodFace health={p.health.overall} /></td>
              <td>{p.health.overall}</td>
              <td>
                <button onClick={() => onSimulate(p.project_id)}>Simulate</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
