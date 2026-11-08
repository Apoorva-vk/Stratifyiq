import { useState } from "react";
import { api, downloadFile } from "../api";
import PageHeader from "../components/PageHeader";

const POWERBI_FILES = [
  ["Projects data", "/reports/powerbi/projects.csv", "stratifyiq-projects.csv"],
  ["Team data", "/reports/powerbi/team.csv", "stratifyiq-team.csv"],
  ["Alerts data", "/reports/powerbi/alerts.csv", "stratifyiq-alerts.csv"],
];

export default function Reports() {
  const [busy, setBusy] = useState("");
  const [period, setPeriod] = useState("weekly");
  const [error, setError] = useState("");
  const [msg, setMsg] = useState("");

  async function download(path, filename, key) {
    setError("");
    setMsg("");
    setBusy(key);
    try {
      await downloadFile(path, filename);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy("");
    }
  }

  async function emailReport() {
    setError("");
    setMsg("");
    setBusy("email");
    try {
      const res = await api("/reports/email", { method: "POST", body: { period } });
      setMsg(res.sent ? `${res.message} Sent to ${res.to}.` : res.message);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy("");
    }
  }

  return (
    <div>
      <PageHeader variant="reports" kicker="Documents" title="Reports" subtitle="Download or email the latest figures." />
      <p className="muted">Calculated from the live data, so each download reflects the current state.</p>
      {msg && <p className="success">{msg}</p>}
      {error && <p className="error">{error}</p>}
      <div className="report-cards">
        <div className="card report-card">
          <h3>Period report</h3>
          <p>A PDF covering projects, team, the health story, decision accuracy and alerts.</p>
          <select value={period} onChange={(e) => setPeriod(e.target.value)}>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
          </select>
          <button disabled={busy !== ""} onClick={() => download(
            `/reports/periodic.pdf?period=${period}`, `stratifyiq-${period}-report.pdf`, "period")}>
            {busy === "period" ? "Preparing..." : `Download ${period} PDF`}
          </button>
          <button disabled={busy !== ""} onClick={emailReport}>
            {busy === "email" ? "Sending..." : `Email ${period} report to me`}
          </button>
        </div>
        <div className="card report-card">
          <h3>Excel workbook</h3>
          <p>Three sheets: Projects, Team and Alerts. Use it for further analysis or sharing.</p>
          <button disabled={busy !== ""} onClick={() => download("/reports/summary.xlsx", "stratifyiq-summary.xlsx", "xlsx")}>
            {busy === "xlsx" ? "Preparing..." : "Download Excel"}
          </button>
        </div>
        <div className="card report-card">
          <h3>PDF summary</h3>
          <p>A printable summary for meetings and the viva demonstration.</p>
          <button disabled={busy !== ""} onClick={() => download("/reports/summary.pdf", "stratifyiq-summary.pdf", "pdf")}>
            {busy === "pdf" ? "Preparing..." : "Download PDF"}
          </button>
        </div>
        <div className="card report-card">
          <h3>Power BI data</h3>
          <p>CSV files for building Power BI dashboards. Import them into Power BI Desktop.</p>
          <div className="btn-stack">
            {POWERBI_FILES.map(([label, path, name], i) => (
              <button key={path} disabled={busy !== ""} onClick={() => download(path, name, `pbi${i}`)}>
                {busy === `pbi${i}` ? "Preparing..." : `Download ${label}`}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
