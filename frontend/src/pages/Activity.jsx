import { useEffect, useState } from "react";
import { api } from "../api";
import PageHeader from "../components/PageHeader";

export default function Activity() {
  const [items, setItems] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api("/activity").then(setItems).catch((e) => setError(e.message));
  }, []);

  if (error) return <p className="error">{error}</p>;
  if (!items) return <p>Loading...</p>;

  return (
    <div>
      <PageHeader variant="activity" kicker="Audit" title="Activity" subtitle="Recent changes made by your team." />
      <p className="muted">Changes made by your team, newest first. Reading data is not recorded.</p>
      {items.length === 0 ? (
        <p className="muted">No activity yet. Make a change, such as adding a project, and it will appear here.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>When</th>
              <th>Who</th>
              <th>What</th>
            </tr>
          </thead>
          <tbody>
            {items.map((i) => (
              <tr key={i.id}>
                <td>{new Date(i.created_at.replace(" ", "T") + "Z").toLocaleString()}</td>
                <td>{i.user}</td>
                <td>{i.action}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
