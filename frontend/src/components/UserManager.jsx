import { useEffect, useState } from "react";
import { api } from "../api";

/** Admin-only: change roles and activate or deactivate team accounts. */
export default function UserManager() {
  const [me, setMe] = useState(null);
  const [users, setUsers] = useState([]);
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");

  function load() {
    api("/users").then(setUsers).catch((e) => setError(e.message));
  }
  useEffect(() => {
    api("/auth/me").then(setMe).catch(() => setMe(null));
  }, []);
  useEffect(() => {
    if (me?.role === "admin") load();
  }, [me]);

  if (me?.role !== "admin") return null;

  async function update(u, changes) {
    setError("");
    setMsg("");
    try {
      await api(`/users/${u.id}`, { method: "PATCH", body: changes });
      setMsg(`${u.full_name} updated.`);
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="card" style={{ marginBottom: 20 }}>
      <h3>Users and access</h3>
      {msg && <p className="success">{msg}</p>}
      {error && <p className="error">{error}</p>}
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Role</th>
            <th>Status</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {users.map((u) => {
            const isMe = u.id === me.id;
            return (
              <tr key={u.id}>
                <td>{u.full_name}{isMe && " (you)"}</td>
                <td>{u.email}</td>
                <td>
                  <select value={u.role} disabled={isMe} onChange={(e) => update(u, { role: e.target.value })}>
                    <option value="admin">Admin</option>
                    <option value="manager">Manager</option>
                  </select>
                </td>
                <td>
                  <span className={`badge ${u.is_active ? "OK" : "OVER"}`}>{u.is_active ? "Active" : "Deactivated"}</span>
                </td>
                <td>
                  <button
                    className={u.is_active ? "danger" : ""}
                    disabled={isMe}
                    onClick={() => update(u, { is_active: !u.is_active })}
                  >
                    {u.is_active ? "Deactivate" : "Activate"}
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
