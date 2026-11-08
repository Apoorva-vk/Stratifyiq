import { useEffect, useState } from "react";
import { api } from "../api";

/** A short plain-English summary of the last seven days. */
export default function WeekDigest() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api("/digest/week").then(setData).catch((e) => setError(e.message));
  }, []);

  if (error) return <p className="error">{error}</p>;
  if (!data) return <p>Loading...</p>;
  return (
    <div>
      <p className="briefing-text">{data.text}</p>
      <div className="grid">
        <div className="score"><span>Changes this week</span><strong>{data.changes}</strong></div>
        <div className="score"><span>Decisions saved</span><strong>{data.decisions_saved}</strong></div>
        <div className="score"><span>Active people</span><strong>{Object.keys(data.by_person).length}</strong></div>
      </div>
    </div>
  );
}
