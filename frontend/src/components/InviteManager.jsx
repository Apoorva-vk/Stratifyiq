import { useEffect, useState } from "react";
import { api } from "../api";

/** Shown only to Admins: invite a Manager by email. */
export default function InviteManager() {
  const [role, setRole] = useState(null);
  const [email, setEmail] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api("/auth/me").then((u) => setRole(u.role)).catch(() => setRole(null));
  }, []);

  if (role !== "admin") return null;

  async function send(e) {
    e.preventDefault();
    setError("");
    setResult(null);
    try {
      setResult(await api("/auth/invite", { method: "POST", body: { email, role: "manager" } }));
      setEmail("");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="card invite-card">
      <h3>Invite a manager</h3>
      <form className="row" onSubmit={send}>
        <label>
          Email
          <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
        </label>
        <button type="submit">Send invitation</button>
      </form>
      {result && <p className={result.email_sent ? "success" : "muted"}>{result.message}</p>}
      {result?.invite_link && (
        <div className="invite-link">
          <p className="muted small">Share this link with the manager (valid for 7 days):</p>
          <div className="invite-link-row">
            <code className="linkbox">{result.invite_link}</code>
            <button type="button" onClick={() => navigator.clipboard?.writeText(result.invite_link)}>Copy link</button>
          </div>
        </div>
      )}
      {error && <p className="error">{error}</p>}
    </div>
  );
}
