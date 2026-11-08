"""Resource allocation suggestions: move one open task from an overloaded person to someone
with spare capacity, when the move lowers the overload and keeps the receiver under 100%."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.services.scope import employee_scope, project_scope
from app.models import Employee, Project, Task, User
from app.services.metrics import employee_utilization


def _capacity(e: Employee) -> float:
    return e.capacity_hours * (e.availability_pct / 100) * 4  # same 4-week basis as utilisation


def suggest(db: Session, user: User, limit: int = 5) -> list[dict]:
    employees = db.scalars(select(Employee).where(employee_scope(user))).all()
    if len(employees) < 2:
        return []
    util = {e.id: employee_utilization(db, e) for e in employees}
    by_id = {e.id: e for e in employees}
    tasks = db.execute(
        select(Task, Project.name)
        .join(Project, Task.project_id == Project.id)
        .where(project_scope(user), Task.done.is_(False), Task.assignee_id.is_not(None))
    ).all()
    open_hours = {e.id: 0.0 for e in employees}
    for t, _ in tasks:
        open_hours[t.assignee_id] += t.estimated_hours

    overloaded = sorted([e for e in employees if util[e.id] > 100], key=lambda e: -util[e.id])
    suggestions = []
    for source in overloaded:
        movable = sorted([(t, n) for t, n in tasks if t.assignee_id == source.id],
                         key=lambda x: -x[0].estimated_hours)
        for task, project_name in movable:
            for target in sorted(employees, key=lambda e: util[e.id]):
                if target.id == source.id or util[target.id] >= 85:
                    continue
                new_source = (open_hours[source.id] - task.estimated_hours) / _capacity(source) * 100
                new_target = (open_hours[target.id] + task.estimated_hours) / _capacity(target) * 100
                if new_target <= 100 and new_source < util[source.id]:
                    suggestions.append({
                        "task_id": task.id,
                        "task": task.title,
                        "project": project_name,
                        "hours": task.estimated_hours,
                        "from_id": source.id,
                        "from_name": source.name,
                        "from_util": util[source.id],
                        "to_id": target.id,
                        "to_name": target.name,
                        "to_util": util[target.id],
                        "projected_from": round(new_source, 1),
                        "projected_to": round(new_target, 1),
                        "message": (f"Move '{task.title}' ({task.estimated_hours:g} h, {project_name}) "
                                    f"from {source.name} ({util[source.id]:.0f}%) to {target.name} "
                                    f"({util[target.id]:.0f}%). Projected: {source.name} "
                                    f"{new_source:.0f}%, {target.name} {new_target:.0f}%."),
                    })
                    break
            if len(suggestions) >= limit:
                return suggestions
            break  # one suggestion per overloaded person keeps the list focused
    return suggestions
