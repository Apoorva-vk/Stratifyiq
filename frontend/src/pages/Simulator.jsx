import { useEffect, useState } from "react";
import { api } from "../api";
import ScenarioBuilder from "../components/ScenarioBuilder";
import PageHeader from "../components/PageHeader";

const ACTIONS = [
  { value: "hire_employee", label: "Hire employees (count)", def: 1 },
  { value: "increase_budget", label: "Increase budget (amount)", def: 50000 },
  { value: "reduce_budget", label: "Reduce budget (amount)", def: 50000 },
  { value: "extend_deadline", label: "Extend deadline (days)", def: 14 },
  { value: "reduce_scope", label: "Reduce scope (percent)", def: 10 },
  { value: "reallocate_resources", label: "Reallocate resources", def: 0 },
];

export default function Simulator({ projectId, setProjectId }) {
  const [projects, setProjects] = useState([]);
  const [action, setAction] = useState("hire_employee");
  const [value, setValue] = useState(1);
  const [result, setResult] = useState(null);
  const [recs, setRecs] = useState(null);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState("");

  useEffect(() => {
    api("/projects")
      .then((ps) => {
        setProjects(ps);
        if (!projectId && ps.length) setProjectId(ps[0].id);
      })
      .catch((e) => setError(e.message));
  }, []);

  useEffect(() => {
    setResult(null);
    setRecs(null);
  }, [projectId]);

  function pickAction(a) {
    setAction(a);
    setValue(ACTIONS.find((x) => x.value === a).def);
  }

  async function runSimulation() {
    setError("");
    try {
      setResult(
        await api(`/analytics/projects/${projectId}/simulate`, {
          method: "POST",
          body: { action, value: Number(value) },
        })
      );
    } catch (e) {
      setError(e.message);
    }
  }

  async function loadRecommendations() {
    setError("");
    try {
      setRecs(await api(`/analytics/projects/${projectId}/recommend`));
    } catch (e) {
      setError(e.message);
    }
  }

  async function saveDecision() {
    setError("");
    setSaved("");
    try {
      await api("/decisions", { method: "POST", body: { project_id: projectId, action, value: Number(value) } });
      setSaved("Saved to decision memory. Record the outcome in Insights when the project finishes.");
    } catch (err) {
      setError(err.message);
    }
  }

  const pct = (x) => (x * 100).toFixed(1) + "%";

  return (
    <div>
      <PageHeader variant="simulator" kicker="Decisions" title="Decision Simulator" subtitle="Test a choice before you make it." />
      <div className="row">
        <label>
          Project
          <select value={projectId ?? ""} onChange={(e) => setProjectId(Number(e.target.value))}>
            {projects.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          Decision
          <select value={action} onChange={(e) => pickAction(e.target.value)}>
            {ACTIONS.map((a) => (
              <option key={a.value} value={a.value}>
                {a.label}
              </option>
            ))}
          </select>
        </label>
        <label>
          Value
          <input type="number" value={value} onChange={(e) => setValue(e.target.value)} />
        </label>
        <button onClick={runSimulation} disabled={!projectId}>
          Run simulation
        </button>
        <button onClick={loadRecommendations} disabled={!projectId}>
          Get recommendations
        </button>
      </div>

      {error && <p className="error">{error}</p>}

      {result && (
        <div className="card">
          <p>
            <strong>{result.summary}</strong>
          </p>
          <p>Cost impact: {result.cost_impact.toLocaleString()}</p>
          <table>
            <thead>
              <tr>
                <th></th>
                <th>Before</th>
                <th>After</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Delay risk</td>
                <td>{pct(result.baseline.delay_risk)}</td>
                <td>{pct(result.scenario.delay_risk)}</td>
              </tr>
              <tr>
                <td>Success probability</td>
                <td>{result.baseline.success_probability.toFixed(1)}</td>
                <td>{result.scenario.success_probability.toFixed(1)}</td>
              </tr>
              <tr>
                <td>Overrun %</td>
                <td>{result.baseline.overrun_pct.toFixed(1)}</td>
                <td>{result.scenario.overrun_pct.toFixed(1)}</td>
              </tr>
              <tr>
                <td>Resource utilization %</td>
                <td>{result.baseline.resource_utilization_pct}</td>
                <td>{result.scenario.resource_utilization_pct}</td>
              </tr>
            </tbody>
          </table>
        </div>
      )}

      {result && (
        <div className="row">
          <button onClick={saveDecision}>Save to decision memory</button>
        </div>
      )}
      {saved && <p className="success">{saved}</p>}

      {recs && (
        <div className="card">
          <h3>Top recommendations</h3>
          <p>Primary risk drivers: {recs.primary_risk_drivers.join(", ")}</p>
          <ol>
            {recs.top_recommendations.map((r, i) => (
              <li key={i}>
                {r.summary} <em>(cost {r.cost_impact.toLocaleString()})</em>
              </li>
            ))}
          </ol>
        </div>
      )}
      <ScenarioBuilder projectId={projectId} />
    </div>
  );
}
