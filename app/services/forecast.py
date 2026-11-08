"""Budget forecast for one project.

Two simple, explainable projections:
- Burn rate: spending per day so far, carried forward to the deadline.
- Progress: the total implied by spend so far and percentage complete.
The series compares a straight-line planned budget with spending at the current burn rate.
"""
from datetime import date


def forecast(start: date, deadline: date, budget: float, spent: float, progress: float,
             today: date | None = None) -> dict:
    today = today or date.today()
    total_days = max((deadline - start).days, 1)
    elapsed = min(max((today - start).days, 1), total_days)
    days_left = max((deadline - today).days, 0)

    daily_burn = spent / elapsed
    projected_by_burn = spent + daily_burn * days_left
    projected_by_progress = spent / (progress / 100) if progress > 0 else None
    overrun_pct = (projected_by_burn - budget) / budget * 100 if budget else 0.0

    if projected_by_burn > budget:
        status = "OVER_BUDGET"
    elif projected_by_burn > 0.9 * budget:
        status = "AT_RISK"
    else:
        status = "ON_TRACK"

    series = []
    for i in range(11):
        day = round(total_days * i / 10)
        series.append({
            "day": day,
            "planned": round(budget * i / 10, 2),
            "projected": round(daily_burn * day, 2),
        })

    return {
        "budget": budget,
        "spent": spent,
        "elapsed_days": elapsed,
        "days_left": days_left,
        "total_days": total_days,
        "daily_burn": round(daily_burn, 2),
        "projected_spend_at_current_burn": round(projected_by_burn, 2),
        "projected_overrun_pct": round(overrun_pct, 1),
        "projected_total_by_progress": None if projected_by_progress is None else round(projected_by_progress, 2),
        "status": status,
        "series": series,
    }
