import { useEffect, useState } from "react";
import { api } from "../api";

/** Import Jira issues into a project as tasks, and keep their done status in step with Jira. */
export default function JiraPanel({ projectId, onChanged }) {
  const [status, setStatus] = useState(null);
  const [jql, setJql] = useState("project = DEMO ORDER BY created DESC");
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState("");

  useEffect(() => {
    api("/integrations/jira").then(setStatus).catch(() => setStatus({ configured: false }));
  }, []);

  async function run(key, action) {
    setBusy(key);
    setError("");
    setMsg("");
    try {
      const res = await action();
      setMsg(res.message);
      if (onChanged) onChanged();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy("");
    }
  }

  async function test() {
    await run("test", async () => {
      const r = await api("/integrations/jira/test", { method: "POST" });
      return { message: `Connected to Jira as ${r.connected_as}.` };
    });
  }

  async function importIssues() {
    await run("import", async () => {
      const r = await api(`/projects/${projectId}/jira/import`, { method: "POST", body: { jql } });
      return { message: `Imported ${r.imported} issue(s); ${r.skipped} already linked.` };
    });
  }

  async function sync() {
    await run("sync", async () => {
      const r = await api(`/projects/${projectId}/jira/sync`, { method: "POST" });
      return { message: `Updated ${r.updated} task(s) from Jira.` };
    });
  }

  if (!status) return null;

  return (
    <div className="card jira-card">
      <h4>Jira</h4>
      {!status.configured ? (
        <p className="muted small">
          Jira is not connected. Add JIRA_BASE_URL, JIRA_EMAIL and JIRA_API_TOKEN to the backend window, then restart it.
          See docs/JIRA_SETUP.md.
        </p>
      ) : (
        <>
          <p className="muted small">Connected to {status.base_url}. Imported issues are read-only: nothing is changed in Jira.</p>
          <div className="row">
            <button onClick={test} disabled={busy !== ""}>{busy === "test" ? "Testing..." : "Test connection"}</button>
          </div>
          <div className="row">
            <label>
              JQL (which issues to import)
              <input value={jql} onChange={(e) => setJql(e.target.value)} style={{ minWidth: 360 }} />
            </label>
            <button onClick={importIssues} disabled={busy !== ""}>{busy === "import" ? "Importing..." : "Import issues"}</button>
            <button onClick={sync} disabled={busy !== ""}>{busy === "sync" ? "Syncing..." : "Sync status"}</button>
          </div>
        </>
      )}
      {msg && <p className="success">{msg}</p>}
      {error && <p className="error">{error}</p>}
    </div>
  );
}
