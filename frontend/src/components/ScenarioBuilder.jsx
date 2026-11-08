import { useEffect, useState } from "react";
import { api } from "../api";

const ACTIONS = [
  { value: "hire_employee", label: "Hire employees (count)" },
  { value: "increase_budget", label: "Increase budget (amount)" },
  { value: "reduce_budget", label: "Reduce budget (amount)" },
  { value: "extend_deadline", label: "Extend deadline (days)" },
  { value: "reduce_scope", label: "Reduce scope (percent)" },
  { value: "reallocate_resources", label: "Reallocate resources" },
];
const DEFAULTS = { hire_employee: 1, increase_budget: 50000, reduce_budget: 50000, extend_deadline: 14, reduce_scope: 10, reallocate_resources: 0 };
const pct = (x) => (x * 100).toFixed(1) + "%";

/** Test up to four decisions together and see the combined effect. Nothing is saved. */
export default function ScenarioBuilder({ projectId }) {
  const [steps, setSteps] = useState([
    { action: "hire_employee", value: 1 },
    { action: "extend_deadline", value: 14 },
  ]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    setResult(null);
    setError("");
  }, [projectId]);

  function changeAction(i, action) {
    setSteps((s) => s.map((x, j) => (j === i ? { action, value: DEFAULTS[action] } : x)));
  }
  function changeValue(i, value) {
    setSteps((s) => s.map((x, j) => (j === i ? { ...x, value: Number(value) } : x)));
  }
  function addStep() {
    if (steps.length < 4) setSteps([...steps, { action: "reallocate_resources", value: 0 }]);
  }
  function removeStep(i) {
    setSteps(steps.filter((_, j) => j !== i));
  }

  async function run() {
    setError("");
    setResult(null);
    try {
      setResult(await api(`/analytics/projects/${projectId}/scenario`, { method: "POST", body: { actions: steps } }));
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="card scenario">
      <h3>Combined what-if</h3>
      <p className="muted small">Stack up to four decisions and see their combined effect. Nothing is saved.</p>

      {steps.map((s, i) => (
        <div key={i} className="row step">
          <select value={s.action} onChange={(e) => changeAction(i, e.target.value)}>
            {ACTIONS.map((a) => (
              <option key={a.value} value={a.value}>
                {a.label}
              </option>
            ))}
          </select>
          <input type="number" value={s.value} onChange={(e) => changeValue(i, e.target.value)} />
          <button className="danger" onClick={() => removeStep(i)}>Remove</button>
        </div>
      ))}

      <div className="row">
        <button onClick={addStep} disabled={steps.length >= 4}>Add decision</button>
        <button onClick={run} disabled={steps.length === 0 || !projectId}>Run combined scenario</button>
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
    </div>
  );
}
