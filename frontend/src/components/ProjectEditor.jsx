import { useEffect, useState } from "react";
import { api } from "../api";

/** Edit a project's details. Progress and expenses have their own controls on the page. */
export default function ProjectEditor({ project, onSaved }) {
  const [form, setForm] = useState(null);
  const [open, setOpen] = useState(false);
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    setOpen(false);
    setMsg("");
    setError("");
    setForm({
      name: project.name,
      budget: project.budget,
      deadline: project.deadline,
      scope_units: project.scope_units,
      status: project.status,
    });
  }, [project.id]);

  if (!form) return null;
  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }));

  async function save(e) {
    e.preventDefault();
    setError("");
    setMsg("");
    try {
      const updated = await api(`/projects/${project.id}`, {
        method: "PATCH",
        body: { ...form, budget: Number(form.budget), scope_units: Number(form.scope_units) },
      });
      setMsg("Project updated.");
      setOpen(false);
      onSaved(updated);
    } catch (err) {
      setError(err.message);
    }
  }

  if (!open) {
    return (
      <div className="editor-bar">
        <button onClick={() => setOpen(true)}>Edit details</button>
        {msg && <span className="success">{msg}</span>}
      </div>
    );
  }

  return (
    <form className="card form-grid editor" onSubmit={save}>
      <label>
        Name
        <input required value={form.name} onChange={set("name")} />
      </label>
      <label>
        Budget
        <input required type="number" min="1" value={form.budget} onChange={set("budget")} />
      </label>
      <label>
        Deadline
        <input required type="date" value={form.deadline} onChange={set("deadline")} />
      </label>
      <label>
        Scope units
        <input type="number" min="1" value={form.scope_units} onChange={set("scope_units")} />
      </label>
      <label>
        Status
        <select value={form.status} onChange={set("status")}>
          <option value="active">Active</option>
          <option value="on_hold">On hold</option>
          <option value="completed">Completed</option>
        </select>
      </label>
      <div className="row">
        <button type="submit">Save</button>
        <button type="button" onClick={() => setOpen(false)}>Cancel</button>
      </div>
      {error && <p className="error">{error}</p>}
    </form>
  );
}
