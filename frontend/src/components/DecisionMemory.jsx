import { useEffect, useState } from "react";
import { api } from "../api";

const LABELS = {
  hire_employee: "Hire", increase_budget: "Increase budget", reduce_budget: "Reduce budget",
  extend_deadline: "Extend deadline", reduce_scope: "Reduce scope", reallocate_resources: "Reallocate",
};

/** Saved decisions, the outcome once it is known, and how accurate the predictions have been. */
export default function DecisionMemory() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  function load() {
    api("/decisions").then(setData).catch((e) => setError(e.message));
  }
  useEffect(load, []);

  async function record(id, finishedLate) {
    setError("");
    try {
      await api(`/decisions/${id}/outcome`, { method: "POST", body: { finished_late: finishedLate } });
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  if (error) return <p className="error">{error}</p>;
  if (!data) return <p>Loading...</p>;
  const a = data.accuracy;

  return (
    <div>
      {a.resolved === 0 ? (
        <p className="muted">
          No outcomes recorded yet. Save a decision from the Simulator, and record how the project finished.
        </p>
      ) : (
        <div className="grid">
          <div className="score"><span>Outcomes recorded</span><strong>{a.resolved}</strong></div>
          <div className="score"><span>Delay prediction accuracy</span><strong>{a.delay_accuracy_pct}%</strong></div>
          <div className="score"><span>Average overrun error</span><strong>{a.overrun_error_pts} pts</strong></div>
        </div>
      )}

      {data.decisions.length === 0 ? (
        <p className="muted">No decisions saved yet.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Saved</th>
              <th>Project</th>
              <th>Decision</th>
              <th>Predicted delay</th>
              <th>Predicted overrun</th>
              <th>Outcome</th>
            </tr>
          </thead>
          <tbody>
            {data.decisions.map((d) => (
              <tr key={d.id}>
                <td>{d.created_at}</td>
                <td>{d.project}</td>
                <td>{LABELS[d.action]} ({Number(d.value).toString()})</td>
                <td>{d.predicted_delay_pct}%</td>
                <td>{d.predicted_overrun_pct}%</td>
                <td>
                  {d.outcome_late === null ? (
                    <>
                      <button onClick={() => record(d.id, false)}>Finished on time</button>{" "}
                      <button className="danger" onClick={() => record(d.id, true)}>Finished late</button>
                    </>
                  ) : (
                    <span>
                      {d.outcome_late ? "Late" : "On time"}, overrun {d.actual_overrun_pct}%
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
