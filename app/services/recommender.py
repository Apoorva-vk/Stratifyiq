"""Recommendation engine: scores candidate decisions and ranks them.

Lower objective is better. The objective combines delay risk (weighted heavily),
budget overrun, low success probability, the cost of the decision as a share of
budget, and a penalty for scope cuts (quality cost). The baseline is 'do nothing'.
"""
from app.services.simulator import predict_from_snapshot, run_scenario

CANDIDATES = [
    ("hire_employee", 1),
    ("extend_deadline", 14),
    ("extend_deadline", 30),
    ("reduce_scope", 10),
    ("reduce_scope", 20),
    ("reallocate_resources", 0),
    ("increase_budget", "10_percent"),
]


def _objective(scenario: dict, cost_ratio: float, scope_cut_pct: float) -> float:
    return round(
        50 * scenario["delay_risk"]
        + 0.3 * max(scenario["overrun_pct"], 0)
        + 0.2 * (100 - scenario["success_probability"])
        + 100 * cost_ratio
        + 0.3 * scope_cut_pct,
        2,
    )


def _drivers(snapshot: dict, baseline: dict) -> list[str]:
    drivers = []
    if baseline["resource_utilization_pct"] > 100:
        drivers.append("Workload exceeds team capacity")
    budget_used = (snapshot["spent"] + snapshot["extra_cost"]) / snapshot["budget"]
    if budget_used > snapshot["progress"] / 100:
        drivers.append("Spending is ahead of progress")
    if snapshot["days_left"] < 30:
        drivers.append("Deadline is close")
    return drivers or ["No major risk driver detected"]


def recommend(snapshot: dict) -> dict:
    baseline_pred = predict_from_snapshot(snapshot)
    results = []
    for action, value in CANDIDATES:
        if value == "10_percent":
            value = round(snapshot["budget"] * 0.10, 2)
        res = run_scenario(snapshot, action, value)
        cost_ratio = res["cost_impact"] / snapshot["budget"] if snapshot["budget"] else 0.0
        scope_cut = value if action == "reduce_scope" else 0.0
        res["objective"] = _objective(res["scenario"], cost_ratio, scope_cut)
        results.append(res)

    results.sort(key=lambda r: r["objective"])
    return {
        "baseline": baseline_pred,
        "baseline_objective": _objective(baseline_pred, 0.0, 0.0),
        "primary_risk_drivers": _drivers(snapshot, baseline_pred),
        "top_recommendations": results[:3],
    }
