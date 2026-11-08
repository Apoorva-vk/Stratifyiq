import { useEffect, useState } from "react";
import { api } from "../api";

/** Every project as a bar from its start to its deadline, with progress and a line for today. */
export default function Timeline() {
  const [projects, setProjects] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api("/projects").then(setProjects).catch((e) => setError(e.message));
  }, []);

  if (error) return <p className="error">{error}</p>;
  if (projects.length === 0) return <p className="muted">No projects yet.</p>;

  const toMs = (s) => new Date(`${s}T00:00:00`).getTime();
  const now = Date.now();
  const min = Math.min(...projects.map((p) => toMs(p.start_date)), now);
  const max = Math.max(...projects.map((p) => toMs(p.deadline)), now);
  const span = max - min || 1;
  const pos = (ms) => ((ms - min) / span) * 100;

  return (
    <div className="timeline">
      {projects.map((p) => {
        const left = pos(toMs(p.start_date));
        const width = pos(toMs(p.deadline)) - left;
        return (
          <div key={p.id} className="trow">
            <div className="tlabel">
              <strong>{p.name}</strong>
              <small>
                {p.start_date} to {p.deadline}
              </small>
            </div>
            <div className="track">
              <div className="span" style={{ left: `${left}%`, width: `${Math.max(width, 1)}%` }}>
                <div className="fill" style={{ width: `${p.progress}%` }} />
              </div>
              <div className="today" style={{ left: `${pos(now)}%` }} />
            </div>
          </div>
        );
      })}
      <p className="muted small">Pale bar: project duration. Dark fill: progress. Red line: today.</p>
    </div>
  );
}
