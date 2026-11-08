"""Decision Simulator: applies a what-if decision to a project snapshot and
compares predicted outcomes before and after. Nothing is written to the database."""
from app.services.metrics import derive_features
from app.services.ml import predict

HIRE_MONTHLY_COST = 60000.0  # assumed fully loaded cost per hire per month


def predict_from_snapshot(snapshot: dict, reallocated: bool = False) -> dict:
    return predict(derive_features(snapshot, reallocated))


def simulate(snapshot: dict, action: str, value: float = 0.0):
    """Return (modified snapshot, reallocated flag, immediate cost impact)."""
    s = dict(snapshot)
    reallocated = False
    cost = 0.0

    if action == "hire_employee":
        n = max(int(value or 1), 1)
        cost = n * HIRE_MONTHLY_COST * max(s["days_left"], 30) / 30
        s["team_size"] += n
        s["extra_cost"] += cost
    elif action == "increase_budget":
        s["budget"] += value
        cost = value
    elif action == "reduce_budget":
        s["budget"] = max(s["budget"] - value, 1.0)
    elif action == "extend_deadline":
        s["days_left"] += int(value)
    elif action == "reduce_scope":
        factor = 1 - value / 100
        s["open_hours"] *= factor
        s["scope_units"] *= factor
    elif action == "reallocate_resources":
        reallocated = True
    else:
        raise ValueError(f"Unknown action: {action}")
    return s, reallocated, cost


def _summary(action: str, delta: dict) -> str:
    d_delay = delta["delay_risk"] * 100
    d_over = delta["overrun_pct"]
    return (
        f"{action.replace('_', ' ').capitalize()}: delay risk "
        f"{'falls' if d_delay < 0 else 'rises'} by {abs(d_delay):.1f} points; "
        f"budget overrun {'drops' if d_over < 0 else 'rises'} by {abs(d_over):.1f} points."
    )


def run_scenario(snapshot: dict, action: str, value: float = 0.0) -> dict:
    baseline = predict_from_snapshot(snapshot)
    modified, reallocated, cost = simulate(snapshot, action, value)
    scenario = predict_from_snapshot(modified, reallocated)
    numeric = ["delay_risk", "success_probability", "overrun_pct", "resource_utilization_pct"]
    delta = {k: round(scenario[k] - baseline[k], 3) for k in numeric}
    return {
        "action": action,
        "value": value,
        "cost_impact": round(cost, 2),
        "baseline": baseline,
        "scenario": scenario,
        "delta": delta,
        "summary": _summary(action, delta),
    }


def run_combined(snapshot: dict, actions: list[dict]) -> dict:
    """Applies several decisions in order and predicts the combined outcome."""
    current = dict(snapshot)
    reallocated = False
    cost = 0.0
    for step in actions:
        current, realloc, step_cost = simulate(current, step["action"], step.get("value", 0.0))
        reallocated = reallocated or realloc
        cost += step_cost
    baseline = predict_from_snapshot(snapshot)
    scenario = predict_from_snapshot(current, reallocated)
    numeric = ["delay_risk", "success_probability", "overrun_pct", "resource_utilization_pct"]
    delta = {k: round(scenario[k] - baseline[k], 3) for k in numeric}
    return {
        "actions": actions,
        "cost_impact": round(cost, 2),
        "baseline": baseline,
        "scenario": scenario,
        "delta": delta,
        "summary": _summary("Combined scenario", delta),
    }
