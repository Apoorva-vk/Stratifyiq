import { useState } from "react";
import { api } from "../api";

/** Describe a task and see who on the team is the best fit, by skills and spare capacity. */
export default function AssigneeSuggester() {
  const [title, setTitle] = useState("");
  const [results, setResults] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function suggest(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      setResults(await api("/assignee-suggestions", { method: "POST", body: { title, hours: 0 } }));
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <form className="row" onSubmit={suggest}>
        <label>
          Describe the task
          <input required minLength={2} value={title} onChange={(e) => setTitle(e.target.value)}
                 placeholder="e.g. Build a FastAPI endpoint for invoices" style={{ minWidth: 360 }} />
        </label>
        <button type="submit" disabled={busy}>{busy ? "Thinking..." : "Suggest people"}</button>
      </form>
      {error && <p className="error">{error}</p>}
      {results && results.length === 0 && <p className="muted">Add team members with skills to get suggestions.</p>}
      {results && results.map((r) => (
        <div key={r.employee_id} className="suggestion">
          <p><strong>{r.name}</strong> ({r.title}): {r.reason}</p>
        </div>
      ))}
    </div>
  );
}
