def _clamp(x: float) -> float:
    return max(0.0, min(100.0, x))


def project_health(pred: dict) -> dict:
    financial = _clamp(100 - max(pred["overrun_pct"], 0) * 2)
    schedule = _clamp((1 - pred["delay_risk"]) * 100)
    workload = _clamp(100 - max(pred["resource_utilization_pct"] - 100, 0))
    return {
        "financial": round(financial, 1),
        "schedule": round(schedule, 1),
        "workload": round(workload, 1),
        "overall": round((financial + schedule + workload) / 3, 1),
    }


def employee_health(utilization_pct: float) -> float:
    """Healthy band is 40-100%. Overload and idle time both reduce the score."""
    if utilization_pct > 100:
        return round(_clamp(100 - (utilization_pct - 100)), 1)
    if utilization_pct < 40:
        return round(_clamp(100 - (40 - utilization_pct)), 1)
    return 100.0
