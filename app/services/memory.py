"""Decision memory: compares what the model predicted for a saved decision with what happened."""
from app.models import DecisionRecord


def serialize(r: DecisionRecord, project_name: str) -> dict:
    return {
        "id": r.id,
        "project_id": r.project_id,
        "project": project_name,
        "saved_by": r.saved_by,
        "action": r.action,
        "value": r.value,
        "created_at": r.created_at.strftime("%Y-%m-%d %H:%M"),
        "predicted_delay_pct": round(r.scenario_delay * 100, 1),
        "predicted_overrun_pct": round(r.scenario_overrun, 1),
        "predicted_success_pct": round(r.scenario_success, 1),
        "outcome_late": r.outcome_late,
        "actual_overrun_pct": r.actual_overrun_pct,
    }


def accuracy(records: list[DecisionRecord]) -> dict:
    """Delay accuracy: did a 50%+ predicted delay risk match a late finish?
    Overrun error: average gap between predicted and actual overrun, in points."""
    resolved = [r for r in records if r.outcome_late is not None]
    if not resolved:
        return {"resolved": 0, "delay_accuracy_pct": None, "overrun_error_pts": None}
    correct = sum(1 for r in resolved if (r.scenario_delay >= 0.5) == r.outcome_late)
    gaps = [abs(r.scenario_overrun - r.actual_overrun_pct) for r in resolved]
    return {
        "resolved": len(resolved),
        "delay_accuracy_pct": round(correct / len(resolved) * 100, 1),
        "overrun_error_pts": round(sum(gaps) / len(gaps), 1),
    }
