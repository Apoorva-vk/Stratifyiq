"""Team achievements, calculated from real task and workload data.
Points: 10 for each completed task and 5 for each project someone has tasks in."""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.services.scope import employee_scope, project_scope
from app.models import Employee, Project, Task, User
from app.services.metrics import employee_utilization


def leaderboard(db: Session, user: User) -> list[dict]:
    done = dict(db.execute(
        select(Task.assignee_id, func.count(Task.id))
        .join(Project, Task.project_id == Project.id)
        .where(project_scope(user), Task.done.is_(True), Task.assignee_id.is_not(None))
        .group_by(Task.assignee_id)
    ).all())
    spread = dict(db.execute(
        select(Task.assignee_id, func.count(func.distinct(Task.project_id)))
        .join(Project, Task.project_id == Project.id)
        .where(project_scope(user), Task.assignee_id.is_not(None))
        .group_by(Task.assignee_id)
    ).all())

    rows = []
    for e in db.scalars(select(Employee).where(employee_scope(user))).all():
        finished = done.get(e.id, 0)
        projects = spread.get(e.id, 0)
        util = employee_utilization(db, e)
        badges = []
        if finished >= 1:
            badges.append("First finish")
        if finished >= 5:
            badges.append("Task machine")
        if projects >= 2:
            badges.append("Team player")
        if 40 <= util <= 100 and (finished or projects):
            badges.append("Balanced load")
        rows.append({
            "employee_id": e.id,
            "name": e.name,
            "title": e.title,
            "tasks_done": finished,
            "points": finished * 10 + projects * 5,
            "badges": badges,
        })
    rows.sort(key=lambda r: (-r["points"], r["name"]))
    return rows
