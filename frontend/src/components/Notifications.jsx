import { useEffect, useState } from "react";
import { api } from "../api";

export default function Notifications() {
  const [open, setOpen] = useState(false);
  const [alerts, setAlerts] = useState([]);

  function load() {
    api("/notifications").then(setAlerts).catch(() => setAlerts([]));
  }
  useEffect(load, []);

  function toggle() {
    const next = !open;
    setOpen(next);
    if (next) load();
  }

  return (
    <div className="bell-wrap">
      <button className="bell" onClick={toggle}>
        Alerts {alerts.length > 0 && <span className="bell-count">{alerts.length}</span>}
      </button>
      {open && (
        <div className="alert-panel">
          <strong>Alerts</strong>
          {alerts.length === 0 && <p className="muted">Nothing needs attention right now.</p>}
          {alerts.map((a, i) => (
            <div key={i} className={`alert ${a.level}`}>
              <span className="alert-level">{a.level}</span> {a.message}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
