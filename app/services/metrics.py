from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Employee, Expense, Project, Task

WEEKLY_HOURS = 35  # standard working hours per person per week used for load calculations


def project_snapshot(db: Session, project: Project) -> dict:
    """Raw, unit-based state of a project. Everything the models and simulator need."""
    tasks = db.scalars(select(Task).where(Task.project_id == project.id)).all()
    open_hours = sum(t.estimated_hours for t in tasks if not t.done)
    team_size = len({t.assignee_id for t in tasks if t.assignee_id}) or 1
    spent = db.scalar(
        select(func.coalesce(func.sum(Expense.amount), 0.0)).where(Expense.project_id == project.id)
    )
    days_left = max((project.deadline - date.today()).days, 0)
    return {
        "budget": float(project.budget),
        "spent": float(spent),
        "extra_cost": 0.0,            # cost added by simulated decisions only
        "progress": float(project.progress),
        "days_left": days_left,
        "team_size": team_size,
        "open_hours": float(open_hours),
        "scope_units": float(project.scope_units),
    }


def derive_features(s: dict, reallocated: bool = False) -> dict:
    """Turn a raw snapshot into the model's input features."""
    weeks_left = max(s["days_left"], 1) / 7
    capacity = s["team_size"] * WEEKLY_HOURS * weeks_left
    load = s["open_hours"] / capacity if capacity else 0.0
    # Reallocation assumption: moving work off overloaded people removes half the excess load.
    if reallocated and load > 1:
        load = 1 + (load - 1) * 0.5
    budget_used = (s["spent"] + s["extra_cost"]) / s["budget"] if s["budget"] else 1.0
    return {
        "budget_used_ratio": budget_used,
        "progress": s["progress"],
        "load_ratio": load,
        "days_left": s["days_left"],
        "team_size": s["team_size"],
        "scope_units": s["scope_units"],
    }


def employee_utilization(db: Session, emp: Employee) -> float:
    """Open assigned hours vs. 4-week availability, as a percentage."""
    open_hours = db.scalar(
        select(func.coalesce(func.sum(Task.estimated_hours), 0.0)).where(
            Task.assignee_id == emp.id, Task.done.is_(False)
        )
    )
    capacity = emp.capacity_hours * (emp.availability_pct / 100) * 4
    return round(float(open_hours) / capacity * 100, 1) if capacity else 0.0
