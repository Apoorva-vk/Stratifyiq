import { useEffect, useState } from "react";
import { api } from "../api";
import PageHeader from "../components/PageHeader";

/** Company profile, departments, teams and team membership. */
export default function Organisation() {
  const [company, setCompany] = useState(null);
  const [companyName, setCompanyName] = useState("");
  const [departments, setDepartments] = useState([]);
  const [teams, setTeams] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [newDept, setNewDept] = useState("");
  const [newTeam, setNewTeam] = useState({ name: "", department_id: "" });
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");

  function load() {
    Promise.all([api("/company"), api("/departments"), api("/teams"), api("/employees")])
      .then(([c, d, t, e]) => {
        setCompany(c);
        setCompanyName(c.name);
        setDepartments(d);
        setTeams(t);
        setEmployees(e);
      })
      .catch((e) => setError(e.message));
  }
  useEffect(load, []);

  async function run(action, success) {
    setError("");
    setMsg("");
    try {
      await action();
      setMsg(success);
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  const teamName = (id) => teams.find((t) => t.id === id)?.name || "No team";
  const deptName = (id) => departments.find((d) => d.id === id)?.name || "";

  if (!company) return error ? <p className="error">{error}</p> : <p>Loading...</p>;

  return (
    <div>
      <PageHeader variant="organisation" kicker="Structure" title="Organisation" subtitle="Company profile, departments and teams." />
      {msg && <p className="success">{msg}</p>}
      {error && <p className="error">{error}</p>}

      <div className="card">
        <h3>Company profile</h3>
        <form className="row" onSubmit={(e) => { e.preventDefault(); run(() => api("/company", { method: "PATCH", body: { name: companyName } }), "Company name saved."); }}>
          <label>Company name<input required minLength={2} value={companyName} onChange={(e) => setCompanyName(e.target.value)} /></label>
          <button type="submit">Save</button>
        </form>
        <p className="muted small">Only the Admin can change the company name.</p>
      </div>

      <div className="card">
        <h3>Departments</h3>
        <form className="row" onSubmit={(e) => { e.preventDefault(); run(() => api("/departments", { method: "POST", body: { name: newDept } }), `Department "${newDept}" added.`).then(() => setNewDept("")); }}>
          <label>New department<input required minLength={2} value={newDept} onChange={(e) => setNewDept(e.target.value)} /></label>
          <button type="submit">Add department</button>
        </form>
        <table>
          <thead><tr><th>Department</th><th>Teams</th><th></th></tr></thead>
          <tbody>
            {departments.map((d) => (
              <tr key={d.id}>
                <td>{d.name}</td>
                <td>{teams.filter((t) => t.department_id === d.id).map((t) => t.name).join(", ") || "—"}</td>
                <td>
                  <button className="danger" onClick={() => {
                    if (window.confirm(`Delete "${d.name}" and its teams? Members are kept.`)) {
                      run(() => api(`/departments/${d.id}`, { method: "DELETE" }), `"${d.name}" deleted.`);
                    }
                  }}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card">
        <h3>Teams</h3>
        <form className="row" onSubmit={(e) => { e.preventDefault(); run(() => api("/teams", { method: "POST", body: { name: newTeam.name, department_id: Number(newTeam.department_id) } }), `Team "${newTeam.name}" added.`).then(() => setNewTeam({ name: "", department_id: "" })); }}>
          <label>Team name<input required minLength={2} value={newTeam.name} onChange={(e) => setNewTeam({ ...newTeam, name: e.target.value })} /></label>
          <label>Department
            <select required value={newTeam.department_id} onChange={(e) => setNewTeam({ ...newTeam, department_id: e.target.value })}>
              <option value="">Choose...</option>
              {departments.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
            </select>
          </label>
          <button type="submit" disabled={departments.length === 0}>Add team</button>
        </form>
        <table>
          <thead><tr><th>Team</th><th>Department</th><th>Members</th><th></th></tr></thead>
          <tbody>
            {teams.map((t) => (
              <tr key={t.id}>
                <td>{t.name}</td>
                <td>{deptName(t.department_id)}</td>
                <td>{employees.filter((e) => e.team_id === t.id).length}</td>
                <td>
                  <button className="danger" onClick={() => {
                    if (window.confirm(`Delete team "${t.name}"? Members are kept and become unassigned.`)) {
                      run(() => api(`/teams/${t.id}`, { method: "DELETE" }), `"${t.name}" deleted.`);
                    }
                  }}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card">
        <h3>Team members</h3>
        <table>
          <thead><tr><th>Name</th><th>Title</th><th>Team</th></tr></thead>
          <tbody>
            {employees.map((e) => (
              <tr key={e.id}>
                <td>{e.name}</td>
                <td>{e.title}</td>
                <td>
                  <select value={e.team_id ?? ""} onChange={(ev) => run(
                    () => api(`/employees/${e.id}`, { method: "PATCH", body: { team_id: Number(ev.target.value) } }),
                    `${e.name} moved to ${teamName(Number(ev.target.value))}.`)}>
                    <option value="" disabled>{teamName(e.team_id)}</option>
                    {teams.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="muted small">Choosing a team here assigns the member. A member can't be left without a team once assigned.</p>
      </div>
    </div>
  );
}
