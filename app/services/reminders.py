"""Smart reminders: open tasks that have been open for more working days than their estimate.
Assumes an 8-hour working day, so a 16-hour estimate is 2 working days."""
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.services.scope import project_scope
from app.models import Project, Task, TaskMeta, User

HOURS_PER_DAY = 8


def workdays_between(start: date, end: date) -> int:
    count, d = 0, start
    while d < end:
        if d.weekday() < 5:
            count += 1
        d += timedelta(days=1)
    return count


def build_reminders(db: Session, user: User) -> list[dict]:
    today = date.today()
    rows = db.execute(
        select(Task, TaskMeta.started_at, Project.name)
        .join(TaskMeta, TaskMeta.task_id == Task.id)
        .join(Project, Task.project_id == Project.id)
        .where(project_scope(user), Task.done.is_(False))
    ).all()
    out = []
    for task, started, project_name in rows:
        open_days = workdays_between(started, today)
        estimate_days = task.estimated_hours / HOURS_PER_DAY
        if open_days > estimate_days:
            out.append({
                "task_id": task.id,
                "task": task.title,
                "project": project_name,
                "open_workdays": open_days,
                "estimated_hours": task.estimated_hours,
                "message": (f"'{task.title}' in {project_name} has been open for {open_days} working days, "
                            f"but was estimated at {task.estimated_hours:g} hours "
                            f"(about {estimate_days:g} working days)."),
            })
    out.sort(key=lambda r: -r["open_workdays"])
    return out
