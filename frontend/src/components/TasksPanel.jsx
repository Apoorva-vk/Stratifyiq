import { useEffect, useState } from "react";
import { api } from "../api";
import Confetti from "./Confetti";

const EMPTY = { title: "", estimated_hours: "", assignee_id: "", milestone: "", due_date: "" };

/** Tasks, milestones and due dates for one project, shown inside the project's Manage panel. */
export default function TasksPanel({ projectId }) {
  const [tasks, setTasks] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [dueDates, setDueDates] = useState({});
  const [form, setForm] = useState(EMPTY);
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");
  const [burst, setBurst] = useState(0);

  function load() {
    Promise.all([
      api(`/projects/${projectId}/tasks`),
      api("/employees"),
      api(`/projects/${projectId}/task-due-dates`),
    ])
      .then(([t, e, d]) => {
        setTasks(t);
        setEmployees(e);
        setDueDates(Object.fromEntries(d.map((x) => [x.task_id, x])));
      })
      .catch((e) => setError(e.message));
  }
  useEffect(load, [projectId]);

  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }));
  const nameOf = (id) => employees.find((e) => e.id === id)?.name || "Unassigned";

  async function addTask(e) {
    e.preventDefault();
    setError("");
    setMsg("");
    try {
      const task = await api(`/projects/${projectId}/tasks`, {
        method: "POST",
        body: {
          title: form.title,
          estimated_hours: Number(form.estimated_hours),
          assignee_id: form.assignee_id ? Number(form.assignee_id) : null,
          milestone: form.milestone || null,
        },
      });
      if (form.due_date) {
        await api(`/tasks/${task.id}/due-date`, { method: "PUT", body: { due_date: form.due_date } });
      }
      setForm(EMPTY);
      setMsg("Task added.");
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function toggleDone(t) {
    setError("");
    try {
      await api(`/tasks/${t.id}`, { method: "PATCH", body: { done: !t.done } });
      if (!t.done) setBurst((b) => b + 1);
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function reassign(t, value) {
    setError("");
    try {
      await api(`/tasks/${t.id}`, { method: "PATCH", body: { assignee_id: Number(value) } });
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function changeDue(t, value) {
    setError("");
    try {
      await api(`/tasks/${t.id}/due-date`, { method: "PUT", body: { due_date: value || null } });
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  const open = tasks.filter((t) => !t.done);
  const openHours = open.reduce((sum, t) => sum + Number(t.estimated_hours), 0);
  const overdueCount = Object.values(dueDates).filter((d) => d.overdue).length;

  const milestones = {};
  tasks.forEach((t) => {
    const key = t.milestone || "No milestone";
    milestones[key] = milestones[key] || { total: 0, done: 0 };
    milestones[key].total += 1;
    if (t.done) milestones[key].done += 1;
  });

  return (
    <div className="tasks">
      <Confetti trigger={burst} />
      <h4>Tasks and milestones</h4>
      <p className="muted">
        {tasks.length} tasks · {open.length} open · {openHours} hours of open work
        {overdueCount > 0 && <span className="overdue-text"> · {overdueCount} overdue</span>}
      </p>

      {Object.keys(milestones).length > 0 && (
        <div className="milestones">
          {Object.entries(milestones).map(([name, v]) => (
            <span key={name} className="chip">{name}: {v.done}/{v.total} done</span>
          ))}
        </div>
      )}

      <form className="form-grid" onSubmit={addTask}>
        <label>
          Task
          <input required value={form.title} onChange={set("title")} />
        </label>
        <label>
          Hours
          <input required type="number" min="0.5" step="0.5" value={form.estimated_hours} onChange={set("estimated_hours")} />
        </label>
        <label>
          Assign to
          <select value={form.assignee_id} onChange={set("assignee_id")}>
            <option value="">Unassigned</option>
            {employees.map((e) => <option key={e.id} value={e.id}>{e.name}</option>)}
          </select>
        </label>
        <label>
          Milestone
          <input value={form.milestone} onChange={set("milestone")} placeholder="e.g. Phase 1" />
        </label>
        <label>
          Due date
          <input type="date" value={form.due_date} onChange={set("due_date")} />
        </label>
        <button type="submit">Add task</button>
      </form>

      {msg && <p className="success">{msg}</p>}
      {error && <p className="error">{error}</p>}

      {tasks.length === 0 ? (
        <p className="muted">No tasks yet. Add one above.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Done</th>
              <th>Task</th>
              <th>Milestone</th>
              <th>Hours</th>
              <th>Due</th>
              <th>Assigned to</th>
            </tr>
          </thead>
          <tbody>
            {tasks.map((t) => {
              const due = dueDates[t.id];
              return (
                <tr key={t.id} className={`${t.done ? "done-row" : ""} ${due?.overdue ? "overdue-row" : ""}`}>
                  <td><input type="checkbox" checked={t.done} onChange={() => toggleDone(t)} /></td>
                  <td>{t.title}</td>
                  <td>{t.milestone || "—"}</td>
                  <td>{t.estimated_hours}</td>
                  <td>
                    <input type="date" value={due?.due_date || ""} onChange={(e) => changeDue(t, e.target.value)} />
                    {due?.overdue && <span className="badge CRITICAL">Overdue</span>}
                  </td>
                  <td>
                    <select value={t.assignee_id ?? ""} onChange={(e) => reassign(t, e.target.value)}>
                      <option value="" disabled>{nameOf(t.assignee_id)}</option>
                      {employees.map((e) => <option key={e.id} value={e.id}>{e.name}</option>)}
                    </select>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
}
