import { useEffect, useState } from "react";
import { api } from "../api";

/** Milestones with due dates. A milestone is complete when every task labelled with its name is done. */
export default function MilestonesPanel({ projectId }) {
  const [items, setItems] = useState([]);
  const [form, setForm] = useState({ name: "", due_date: "" });
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");

  function load() {
    api(`/projects/${projectId}/milestones`).then(setItems).catch((e) => setError(e.message));
  }
  useEffect(load, [projectId]);

  async function add(e) {
    e.preventDefault();
    setError("");
    setMsg("");
    try {
      await api(`/projects/${projectId}/milestones`, { method: "POST", body: form });
      setMsg(`Milestone "${form.name}" added.`);
      setForm({ name: "", due_date: "" });
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function remove(m) {
    if (!window.confirm(`Delete milestone "${m.name}"? Its tasks are kept.`)) return;
    setError("");
    try {
      await api(`/milestones/${m.id}`, { method: "DELETE" });
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="milestones-panel">
      <h4>Milestones</h4>
      <form className="form-grid" onSubmit={add}>
        <label>
          Milestone name
          <input required minLength={2} value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="e.g. Phase 1" />
        </label>
        <label>
          Due date
          <input required type="date" value={form.due_date} onChange={(e) => setForm({ ...form, due_date: e.target.value })} />
        </label>
        <button type="submit">Add milestone</button>
      </form>
      {msg && <p className="success">{msg}</p>}
      {error && <p className="error">{error}</p>}
      {items.length === 0 ? (
        <p className="muted">No milestones yet. Tasks can be grouped under a milestone by typing its name.</p>
      ) : (
        <table>
          <thead>
            <tr><th>Milestone</th><th>Due</th><th>Progress</th><th>Status</th><th></th></tr>
          </thead>
          <tbody>
            {items.map((m) => (
              <tr key={m.id}>
                <td>{m.name}</td>
                <td>{m.due_date}</td>
                <td>{m.done_tasks}/{m.total_tasks} tasks</td>
                <td>
                  {m.complete ? <span className="badge OK">Complete</span>
                    : m.overdue ? <span className="badge CRITICAL">Overdue</span>
                    : <span className="badge UNDER">In progress</span>}
                </td>
                <td><button className="danger" onClick={() => remove(m)}>Delete</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
