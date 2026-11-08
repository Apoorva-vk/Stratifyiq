"""Alerts computed from live data: budget, deadline, high risk and team overload.
Computed on request, so there is no alert table to keep in sync."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.services.scope import employee_scope, project_scope
from app.models import Employee, Project, User
from app.services.metrics import employee_utilization, project_snapshot
from app.services.simulator import predict_from_snapshot

ORDER = {"critical": 0, "warning": 1}


def build_alerts(db: Session, user: User) -> list[dict]:
    alerts = []
    projects = db.scalars(select(Project).where(project_scope(user))).all()
    for p in projects:
        snap = project_snapshot(db, p)
        pred = predict_from_snapshot(snap)
        used = snap["spent"] / snap["budget"] if snap["budget"] else 0.0
        if used > 1:
            alerts.append({"level": "critical", "type": "budget",
                           "message": f"{p.name} has spent {used * 100:.0f}% of its budget"})
        elif used >= 0.9:
            alerts.append({"level": "warning", "type": "budget",
                           "message": f"{p.name} has used {used * 100:.0f}% of its budget"})
        if snap["progress"] < 100 and snap["days_left"] == 0:
            alerts.append({"level": "critical", "type": "deadline",
                           "message": f"{p.name} is past its deadline at {snap['progress']:.0f}% complete"})
        elif snap["progress"] < 100 and snap["days_left"] <= 14:
            alerts.append({"level": "warning", "type": "deadline",
                           "message": f"{p.name} is due in {snap['days_left']} days at {snap['progress']:.0f}% complete"})
        if pred["risk_level"] == "HIGH":
            alerts.append({"level": "critical", "type": "risk",
                           "message": f"{p.name} is rated HIGH delay risk ({pred['delay_risk'] * 100:.0f}%)"})

    employees = db.scalars(select(Employee).where(employee_scope(user))).all()
    for e in employees:
        u = employee_utilization(db, e)
        if u > 100:
            alerts.append({"level": "warning", "type": "workload",
                           "message": f"{e.name} is overloaded ({u:.0f}% of capacity)"})

    from app.services.reminders import build_reminders  # local import avoids a circular import
    for r in build_reminders(db, user):
        alerts.append({"level": "warning", "type": "reminder", "message": r["message"]})

    from datetime import date as _date
    from app.models import Task, TaskDeadline
    overdue = db.execute(
        select(Task, TaskDeadline.due_date, Project.name)
        .join(TaskDeadline, TaskDeadline.task_id == Task.id)
        .join(Project, Task.project_id == Project.id)
        .where(project_scope(user), Task.done.is_(False),
               TaskDeadline.due_date < _date.today())
    ).all()
    for task, due, project_name in overdue:
        alerts.append({"level": "critical", "type": "task-deadline",
                       "message": f"'{task.title}' in {project_name} was due {due:%d %b} and is not done"})

    alerts.sort(key=lambda a: ORDER[a["level"]])
    return alerts
