import { useEffect, useState } from "react";
import { api } from "../api";

export default function Reminders() {
  const [items, setItems] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api("/reminders").then(setItems).catch((e) => setError(e.message));
  }, []);

  if (error) return <p className="error">{error}</p>;
  if (!items) return <p>Loading...</p>;
  if (items.length === 0) {
    return <p className="muted">Nothing is overdue against its estimate. Tasks added from now on are tracked.</p>;
  }
  return (
    <div>
      {items.map((r) => (
        <div key={r.task_id} className="reminder">{r.message}</div>
      ))}
    </div>
  );
}
