import { useEffect, useState } from "react";
import { api } from "../api";

/** Plain-English weekly story of each project's health, built from recorded snapshots. */
export default function HealthStory() {
  const [items, setItems] = useState(null);
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");

  function load() {
    api("/health/story").then(setItems).catch((e) => setError(e.message));
  }
  useEffect(load, []);

  async function snapshot() {
    setError("");
    setMsg("");
    try {
      const r = await api("/health/snapshot", { method: "POST" });
      setMsg(`Recorded this week's health for ${r.recorded} project(s).`);
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div>
      <div className="row">
        <button onClick={snapshot}>Record this week's snapshot</button>
      </div>
      {msg && <p className="success">{msg}</p>}
      {error && <p className="error">{error}</p>}
      {!items ? (
        <p>Loading...</p>
      ) : items.length === 0 ? (
        <p className="muted">No projects yet.</p>
      ) : (
        items.map((i) => (
          <p key={i.project_id} className="story-line">{i.text}</p>
        ))
      )}
      <p className="muted small">Snapshots are kept, so the story grows richer each week the app is used.</p>
    </div>
  );
}
