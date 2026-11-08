import { useEffect, useState } from "react";
import { api } from "../api";

const MEDALS = ["1st", "2nd", "3rd"];

/** Team leaderboard with points and badges, calculated from real task data. */
export default function Achievements() {
  const [rows, setRows] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api("/achievements").then(setRows).catch((e) => setError(e.message));
  }, []);

  if (error) return <p className="error">{error}</p>;
  if (!rows) return <p>Loading...</p>;
  if (rows.length === 0) return <p className="muted">Add team members and tasks to start earning points.</p>;

  return (
    <div className="leaderboard">
      {rows.map((r, i) => (
        <div key={r.employee_id} className={`leader ${i === 0 ? "gold" : ""}`}>
          <div className="rank">{MEDALS[i] || `${i + 1}th`}</div>
          <div className="leader-main">
            <strong>{r.name}</strong>
            <small>{r.title}</small>
            <div className="badges">
              {r.badges.length === 0 ? (
                <span className="muted small">No badges yet</span>
              ) : (
                r.badges.map((b) => (
                  <span key={b} className="badge-chip">{b}</span>
                ))
              )}
            </div>
          </div>
          <div className="points">
            <strong>{r.points}</strong>
            <small>points</small>
          </div>
        </div>
      ))}
      <p className="muted small">Points: 10 per completed task, 5 per project you work on.</p>
    </div>
  );
}
