import { useEffect, useState } from "react";
import { api } from "../api";
import InviteManager from "../components/InviteManager";
import UserManager from "../components/UserManager";
import PageHeader from "../components/PageHeader";

const EMPTY = { name: "", title: "", skills: "", experience_years: 0, capacity_hours: 40, availability_pct: 100, hourly_cost: 0 };

function utilClass(u) {
  if (u > 100) return "OVER";
  if (u < 40) return "UNDER";
  return "OK";
}

export default function Team() {
  const [rows, setRows] = useState([]);
  const [form, setForm] = useState(EMPTY);
  const [editing, setEditing] = useState(null);
  const [query, setQuery] = useState("");
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");

  function load() {
    Promise.all([api("/employees"), api("/employees/workload")])
      .then(([emps, workload]) => {
        const util = Object.fromEntries(workload.map((w) => [w.employee_id, w.utilization_pct]));
        setRows(emps.map((e) => ({ ...e, util: util[e.id] ?? 0 })));
      })
      .catch((e) => setError(e.message));
  }
  useEffect(load, []);

  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }));
  const setEdit = (key) => (e) => setEditing((f) => ({ ...f, [key]: e.target.value }));

  const numbers = (f) => ({
    ...f,
    experience_years: Number(f.experience_years),
    capacity_hours: Number(f.capacity_hours),
    availability_pct: Number(f.availability_pct),
    hourly_cost: Number(f.hourly_cost),
  });

  async function add(e) {
    e.preventDefault();
    setError("");
    setMsg("");
    try {
      await api("/employees", { method: "POST", body: numbers(form) });
      setMsg(`${form.name} added to the team.`);
      setForm(EMPTY);
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function saveEdit(e) {
    e.preventDefault();
    setError("");
    setMsg("");
    const { id, util, ...fields } = editing;
    try {
      await api(`/employees/${id}`, { method: "PATCH", body: numbers(fields) });
      setMsg("Team member updated.");
      setEditing(null);
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function remove(emp) {
    if (!window.confirm(`Remove ${emp.name} from the team? Their tasks will be unassigned.`)) return;
    setError("");
    setMsg("");
    try {
      await api(`/employees/${emp.id}`, { method: "DELETE" });
      setMsg(`${emp.name} removed.`);
      if (editing?.id === emp.id) setEditing(null);
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  const shown = rows.filter((e) => (`${e.name} ${e.title} ${e.skills}`).toLowerCase().includes(query.toLowerCase()));

  return (
    <div>
      <PageHeader variant="team" kicker="People" title="Team" subtitle="Skills, workload and availability for everyone." />
      <InviteManager />
      <UserManager />

      <form className="card form-grid" onSubmit={add}>
        <label>
          Name
          <input required value={form.name} onChange={set("name")} />
        </label>
        <label>
          Job title
          <input required value={form.title} onChange={set("title")} />
        </label>
        <label>
          Skills (comma separated)
          <input value={form.skills} onChange={set("skills")} />
        </label>
        <label>
          Experience (years)
          <input type="number" min="0" value={form.experience_years} onChange={set("experience_years")} />
        </label>
        <label>
          Hours per week
          <input type="number" min="1" max="80" value={form.capacity_hours} onChange={set("capacity_hours")} />
        </label>
        <label>
          Availability %
          <input type="number" min="0" max="100" value={form.availability_pct} onChange={set("availability_pct")} />
        </label>
        <button type="submit">Add team member</button>
      </form>

      {editing && (
        <form className="card form-grid editor" onSubmit={saveEdit}>
          <h3 style={{ gridColumn: "1 / -1", margin: 0 }}>Edit {editing.name}</h3>
          <label>
            Name
            <input required value={editing.name} onChange={setEdit("name")} />
          </label>
          <label>
            Job title
            <input required value={editing.title} onChange={setEdit("title")} />
          </label>
          <label>
            Skills
            <input value={editing.skills} onChange={setEdit("skills")} />
          </label>
          <label>
            Hours per week
            <input type="number" min="1" max="80" value={editing.capacity_hours} onChange={setEdit("capacity_hours")} />
          </label>
          <label>
            Availability %
            <input type="number" min="0" max="100" value={editing.availability_pct} onChange={setEdit("availability_pct")} />
          </label>
          <div className="row">
            <button type="submit">Save</button>
            <button type="button" onClick={() => setEditing(null)}>Cancel</button>
          </div>
        </form>
      )}

      {msg && <p className="success">{msg}</p>}
      {error && <p className="error">{error}</p>}

      <input
        className="search"
        placeholder="Search by name, title or skill"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />

      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Title</th>
            <th>Skills</th>
            <th>Hours/week</th>
            <th>Workload</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {shown.map((e) => (
            <tr key={e.id}>
              <td>{e.name}</td>
              <td>{e.title}</td>
              <td>{e.skills}</td>
              <td>{e.capacity_hours}</td>
              <td>
                <div className="bar">
                  <span className={utilClass(e.util)} style={{ width: `${Math.min(e.util, 100)}%` }} />
                </div>
                <small>{e.util}%</small>{" "}
                <span className={`badge ${utilClass(e.util)}`}>{utilClass(e.util)}</span>
              </td>
              <td>
                <button onClick={() => setEditing({ ...e })}>Edit</button>{" "}
                <button className="danger" onClick={() => remove(e)}>Remove</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {shown.length === 0 && rows.length > 0 && <p className="muted">No team members match "{query}".</p>}
    </div>
  );
}
