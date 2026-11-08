import { useEffect, useState } from "react";
import { api } from "../api";

const EMPTY = { template: "software_release", name: "", budget: "", start_date: "", deadline: "" };

/** Creates a project from a ready-made plan, with milestones and dated tasks. */
export default function TemplateCreator({ onCreated }) {
  const [templates, setTemplates] = useState([]);
  const [form, setForm] = useState(EMPTY);
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    api("/templates").then(setTemplates).catch((e) => setError(e.message));
  }, []);

  const current = templates.find((t) => t.key === form.template);

  async function create(e) {
    e.preventDefault();
    setError("");
    setMsg("");
    try {
      const res = await api("/projects/from-template", {
        method: "POST",
        body: { ...form, budget: Number(form.budget), scope_units: 100 },
      });
      setMsg(`Created "${res.name}" from the ${current?.label} template.`);
      setForm(EMPTY);
      onCreated();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="card template-card">
      <h3>New project from a template</h3>
      <p className="muted small">
        {current ? `${current.label}: ${current.milestones.join(" → ")} (${current.tasks} tasks)` : "Loading templates..."}
      </p>
      <form className="form-grid" onSubmit={create}>
        <label>
          Template
          <select value={form.template} onChange={(e) => setForm({ ...form, template: e.target.value })}>
            {templates.map((t) => <option key={t.key} value={t.key}>{t.label}</option>)}
          </select>
        </label>
        <label>
          Project name
          <input required minLength={2} value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
        </label>
        <label>
          Budget
          <input required type="number" min="1" value={form.budget} onChange={(e) => setForm({ ...form, budget: e.target.value })} />
        </label>
        <label>
          Start date
          <input required type="date" value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })} />
        </label>
        <label>
          Deadline
          <input required type="date" value={form.deadline} onChange={(e) => setForm({ ...form, deadline: e.target.value })} />
        </label>
        <button type="submit">Create from template</button>
      </form>
      {msg && <p className="success">{msg}</p>}
      {error && <p className="error">{error}</p>}
    </div>
  );
}
