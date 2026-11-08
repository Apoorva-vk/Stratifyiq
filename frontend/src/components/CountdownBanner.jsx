import { useEffect, useState } from "react";
import { api } from "../api";

/** Shows the nearest deadline among projects that are not yet complete. */
export default function CountdownBanner() {
  const [next, setNext] = useState(null);

  useEffect(() => {
    api("/projects")
      .then((projects) => {
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const open = projects
          .filter((p) => p.progress < 100)
          .map((p) => ({ name: p.name, days: Math.round((new Date(`${p.deadline}T00:00:00`) - today) / 86400000) }))
          .filter((p) => p.days >= 0)
          .sort((a, b) => a.days - b.days);
        setNext(open[0] || null);
      })
      .catch(() => setNext(null));
  }, []);

  if (!next) return null;
  const text = next.days === 0 ? "is due today" : `is due in ${next.days} day${next.days === 1 ? "" : "s"}`;
  return (
    <div className="countdown">
      <span className="countdown-days">{next.days}</span>
      <span>
        <strong>{next.name}</strong> {text}. Keep the momentum going.
      </span>
    </div>
  );
}
