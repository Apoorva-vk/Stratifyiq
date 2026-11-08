import { useEffect, useState } from "react";
import { api } from "../api";
import TasksPanel from "../components/TasksPanel";
import MilestonesPanel from "../components/MilestonesPanel";
import JiraPanel from "../components/JiraPanel";
import TemplateCreator from "../components/TemplateCreator";
import BudgetForecast from "../components/BudgetForecast";
import ProjectEditor from "../components/ProjectEditor";
import PageHeader from "../components/PageHeader";

const EMPTY = { name: "", budget: "", start_date: "", deadline: "", scope_units: 100 };
const EMPTY_EXP = { description: "", amount: "", incurred_on: "" };

export default function Projects() {
  const [projects, setProjects] = useState([]);
  const [form, setForm] = useState(EMPTY);
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");
  const [selected, setSelected] = useState(null);
  const [budget, setBudget] = useState(null);
  const [expenses, setExpenses] = useState([]);
  const [progress, setProgress] = useState("");
  const [expForm, setExpForm] = useState(EMPTY_EXP);
  const [query, setQuery] = useState("");
  const [risks, setRisks] = useState({});
  const [riskFilter, setRiskFilter] = useState("ALL");
  const [tasksVersion, setTasksVersion] = useState(0);

  function loadProjects() {
    Promise.all([api("/projects"), api("/analytics/dashboard")])
      .then(([ps, d]) => {
        setProjects(ps);
        setRisks(Object.fromEntries(d.projects.map((p) => [p.project_id, p.risk_level])));
      })
      .catch((e) => setError(e.message));
  }
  useEffect(loadProjects, []);

  function loadDetail(id) {
    Promise.all([api(`/projects/${id}/budget`), api(`/projects/${id}/expenses`)])
      .then(([b, ex]) => {
        setBudget(b);
        setExpenses(ex);
      })
      .catch((e) => setError(e.message));
  }

  function manage(p) {
    setSelected(p);
    setProgress(p.progress);
    setMsg("");
    setError("");
    loadDetail(p.id);
  }

  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }));
  const setExp = (key) => (e) => setExpForm((f) => ({ ...f, [key]: e.target.value }));

  async function createProject(e) {
    e.preventDefault();
    setError("");
    setMsg("");
    try {
      await api("/projects", {
        method: "POST",
        body: { ...form, budget: Number(form.budget), scope_units: Number(form.scope_units) },
      });
      setMsg(`Project "${form.name}" created.`);
      setForm(EMPTY);
      loadProjects();
    } catch (err) {
      setError(err.message);
    }
  }

  async function useTaskProgress() {
    setError("");
    setMsg("");
    try {
      const res = await api(`/projects/${selected.id}/progress/from-tasks`, { method: "POST" });
      setProgress(res.progress);
      setMsg(`Progress set to ${res.progress}% from completed tasks.`);
      loadProjects();
    } catch (err) {
      setError(err.message);
    }
  }

  async function saveProgress() {
    setError("");
    setMsg("");
    try {
      await api(`/projects/${selected.id}/progress`, { method: "PATCH", body: { progress: Number(progress) } });
      setMsg("Progress saved.");
      loadProjects();
    } catch (err) {
      setError(err.message);
    }
  }

  async function addExpense(e) {
    e.preventDefault();
    setError("");
    setMsg("");
    try {
      await api(`/projects/${selected.id}/expenses`, {
        method: "POST",
        body: { description: expForm.description, amount: Number(expForm.amount), incurred_on: expForm.incurred_on },
      });
      setExpForm(EMPTY_EXP);
      setMsg("Expense recorded.");
      loadDetail(selected.id);
    } catch (err) {
      setError(err.message);
    }
  }

  async function deleteProject(p) {
    if (!window.confirm(`Delete "${p.name}" and all its tasks and expenses?`)) return;
    setError("");
    try {
      await api(`/projects/${p.id}`, { method: "DELETE" });
      setSelected(null);
      setMsg(`"${p.name}" deleted.`);
      loadProjects();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div>
      <PageHeader variant="projects" kicker="Portfolio" title="Projects" subtitle="Plan, track and manage every project in one place." />
      <TemplateCreator onCreated={loadProjects} />

      <form className="card form-grid" onSubmit={createProject}>
        <label>
          Name
          <input required value={form.name} onChange={set("name")} />
        </label>
        <label>
          Budget
          <input required type="number" min="1" value={form.budget} onChange={set("budget")} />
        </label>
        <label>
          Start date
          <input required type="date" value={form.start_date} onChange={set("start_date")} />
        </label>
        <label>
          Deadline
          <input required type="date" value={form.deadline} onChange={set("deadline")} />
        </label>
        <label>
          Scope units
          <input type="number" min="1" value={form.scope_units} onChange={set("scope_units")} />
        </label>
        <button type="submit">Add project</button>
      </form>

      {msg && <p className="success">{msg}</p>}
      {error && <p className="error">{error}</p>}

      <input className="search" placeholder="Search projects by name" value={query} onChange={(e) => setQuery(e.target.value)} />
      <select className="risk-filter" value={riskFilter} onChange={(e) => setRiskFilter(e.target.value)}>
        <option value="ALL">All risk levels</option>
        <option value="HIGH">High risk</option>
        <option value="MEDIUM">Medium risk</option>
        <option value="LOW">Low risk</option>
      </select>

      <table>
        <thead>
          <tr>
            <th>Project</th>
            <th>Budget</th>
            <th>Start</th>
            <th>Deadline</th>
            <th>Progress</th>
            <th>Risk</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {projects.filter((p) => p.name.toLowerCase().includes(query.toLowerCase()) && (riskFilter === "ALL" || risks[p.id] === riskFilter)).map((p) => (
            <tr key={p.id}>
              <td>{p.name}</td>
              <td>{Number(p.budget).toLocaleString()}</td>
              <td>{p.start_date}</td>
              <td>{p.deadline}</td>
              <td>{p.progress}%</td>
              <td>{risks[p.id] ? <span className={`badge ${risks[p.id]}`}>{risks[p.id]}</span> : "—"}</td>
              <td>
                <button onClick={() => manage(p)}>Manage</button>{" "}
                <button className="danger" onClick={() => deleteProject(p)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {selected && budget && (
        <div className="card detail">
          <h3>{selected.name}</h3>
          <ProjectEditor project={selected} onSaved={(updated) => { setSelected(updated); loadProjects(); loadDetail(updated.id); }} />
          <div className="grid">
            <div className="score">
              <span>Budget</span>
              <strong>{Number(budget.budget).toLocaleString()}</strong>
            </div>
            <div className="score">
              <span>Spent</span>
              <strong>{Number(budget.spent).toLocaleString()}</strong>
            </div>
            <div className="score">
              <span>Remaining</span>
              <strong>{Number(budget.remaining).toLocaleString()}</strong>
            </div>
            <div className="score">
              <span>Budget used</span>
              <strong>{budget.burn_ratio != null ? (budget.burn_ratio * 100).toFixed(1) + "%" : "—"}</strong>
            </div>
          </div>
          {budget.over_budget && <p className="error">This project is over budget.</p>}

          <div className="row" style={{ marginTop: 16 }}>
            <label>
              Progress %
              <input type="number" min="0" max="100" value={progress} onChange={(e) => setProgress(e.target.value)} />
            </label>
            <button onClick={saveProgress}>Save progress</button>
            <button onClick={useTaskProgress}>Use task completion</button>
          </div>

          <h4>Record an expense</h4>
          <form className="form-grid" onSubmit={addExpense}>
            <label>
              Description
              <input required value={expForm.description} onChange={setExp("description")} />
            </label>
            <label>
              Amount
              <input required type="number" min="0.01" step="0.01" value={expForm.amount} onChange={setExp("amount")} />
            </label>
            <label>
              Date
              <input required type="date" value={expForm.incurred_on} onChange={setExp("incurred_on")} />
            </label>
            <button type="submit">Add expense</button>
          </form>

          <BudgetForecast projectId={selected.id} />

          <JiraPanel projectId={selected.id} onChanged={() => setTasksVersion((v) => v + 1)} />

          <MilestonesPanel projectId={selected.id} />

          <TasksPanel key={tasksVersion} projectId={selected.id} />

          <h4>Expenses</h4>
          {expenses.length === 0 ? (
            <p className="muted">No expenses yet.</p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Description</th>
                  <th>Amount</th>
                </tr>
              </thead>
              <tbody>
                {expenses.map((x) => (
                  <tr key={x.id}>
                    <td>{x.incurred_on}</td>
                    <td>{x.description}</td>
                    <td>{Number(x.amount).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
}
