import { useEffect, useState } from "react";
import { api } from "../api";

/** Suggested task moves from overloaded people to people with spare capacity. */
export default function Allocation() {
  const [items, setItems] = useState(null);
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");

  function load() {
    api("/allocation").then(setItems).catch((e) => setError(e.message));
  }
  useEffect(load, []);

  async function apply(s) {
    setError("");
    setMsg("");
    try {
      await api(`/tasks/${s.task_id}`, { method: "PATCH", body: { assignee_id: s.to_id } });
      setMsg(`Moved '${s.task}' to ${s.to_name}.`);
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  if (error) return <p className="error">{error}</p>;
  if (!items) return <p>Loading...</p>;
  if (items.length === 0) {
    return <p className="muted">No one is overloaded with a safe move available. The team looks balanced.</p>;
  }
  return (
    <div>
      {msg && <p className="success">{msg}</p>}
      {items.map((s) => (
        <div key={`${s.task_id}-${s.to_id}`} className="suggestion">
          <p>{s.message}</p>
          <button onClick={() => apply(s)}>Apply this move</button>
        </div>
      ))}
      <p className="muted small">Suggestions are calculated from open tasks and capacity. Check them before applying.</p>
    </div>
  );
}
