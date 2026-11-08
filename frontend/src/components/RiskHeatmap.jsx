import { useEffect, useState } from "react";
import { api } from "../api";

const COLUMNS = [
  { label: "Delay risk %", get: (p) => p.prediction.delay_risk * 100, level: (v) => (v >= 65 ? "bad" : v >= 35 ? "warn" : "good") },
  { label: "Overrun %", get: (p) => p.prediction.overrun_pct, level: (v) => (v > 10 ? "bad" : v > 0 ? "warn" : "good") },
  { label: "Workload %", get: (p) => p.prediction.resource_utilization_pct, level: (v) => (v > 100 ? "bad" : v > 85 ? "warn" : "good") },
  { label: "Success %", get: (p) => p.prediction.success_probability, level: (v) => (v < 60 ? "bad" : v < 80 ? "warn" : "good") },
  { label: "Health", get: (p) => p.health.overall, level: (v) => (v < 50 ? "bad" : v < 75 ? "warn" : "good") },
];

/** Each project against five measures. Green is fine, amber needs watching, red needs action. */
export default function RiskHeatmap() {
  const [projects, setProjects] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api("/analytics/dashboard").then((d) => setProjects(d.projects)).catch((e) => setError(e.message));
  }, []);

  if (error) return <p className="error">{error}</p>;
  if (!projects) return <p>Loading...</p>;
  if (projects.length === 0) return <p className="muted">No projects yet.</p>;

  return (
    <div>
      <table className="heatmap">
        <thead>
          <tr>
            <th>Project</th>
            {COLUMNS.map((c) => (
              <th key={c.label}>{c.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {projects.map((p) => (
            <tr key={p.project_id}>
              <td>{p.name}</td>
              {COLUMNS.map((c) => {
                const v = c.get(p);
                return (
                  <td key={c.label} className={`hm hm-${c.level(v)}`}>
                    {v.toFixed(1)}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
      <p className="muted small">Thresholds are rules of thumb. The figures are model estimates, not guarantees.</p>
    </div>
  );
}
