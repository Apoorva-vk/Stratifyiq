from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user, get_owned, require_role
from app.models import MilestoneDate, Project, Task, TaskDeadline, User
from app.schemas import MilestoneIn, TaskDueIn

router = APIRouter(tags=["deadlines"])


@router.put("/tasks/{task_id}/due-date")
def set_due_date(task_id: int, body: TaskDueIn, user: User = Depends(require_role("admin", "manager")),
                 db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(404, "Task not found")
    get_owned(db, Project, task.project_id, user)
    row = db.get(TaskDeadline, task.id)
    if body.due_date is None:
        if row is not None:
            db.delete(row)
    elif row is not None:
        row.due_date = body.due_date
    else:
        db.add(TaskDeadline(task_id=task.id, due_date=body.due_date))
    db.commit()
    return {"task_id": task.id, "due_date": body.due_date.isoformat() if body.due_date else None}


@router.get("/projects/{project_id}/task-due-dates")
def task_due_dates(project_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    get_owned(db, Project, project_id, user)
    rows = db.execute(
        select(TaskDeadline, Task.done)
        .join(Task, TaskDeadline.task_id == Task.id)
        .where(Task.project_id == project_id)
    ).all()
    today = date.today()
    return [{"task_id": d.task_id, "due_date": d.due_date.isoformat(),
             "overdue": (not done) and d.due_date < today} for d, done in rows]


@router.post("/projects/{project_id}/milestones", status_code=201)
def add_milestone(project_id: int, body: MilestoneIn, user: User = Depends(require_role("admin", "manager")),
                  db: Session = Depends(get_db)):
    get_owned(db, Project, project_id, user)
    if db.scalar(select(MilestoneDate).where(MilestoneDate.project_id == project_id,
                                             MilestoneDate.name == body.name)):
        raise HTTPException(409, "A milestone with this name already exists in this project")
    m = MilestoneDate(project_id=project_id, name=body.name, due_date=body.due_date)
    db.add(m)
    db.commit()
    db.refresh(m)
    return {"id": m.id, "name": m.name, "due_date": m.due_date.isoformat()}


@router.get("/projects/{project_id}/milestones")
def list_milestones(project_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    get_owned(db, Project, project_id, user)
    milestones = db.scalars(select(MilestoneDate).where(MilestoneDate.project_id == project_id)
                            .order_by(MilestoneDate.due_date)).all()
    tasks = db.scalars(select(Task).where(Task.project_id == project_id)).all()
    today = date.today()
    out = []
    for m in milestones:
        group = [t for t in tasks if t.milestone == m.name]
        done = sum(1 for t in group if t.done)
        complete = bool(group) and done == len(group)
        out.append({
            "id": m.id,
            "name": m.name,
            "due_date": m.due_date.isoformat(),
            "total_tasks": len(group),
            "done_tasks": done,
            "complete": complete,
            "overdue": (not complete) and m.due_date < today,
        })
    return out


@router.delete("/milestones/{milestone_id}", status_code=204)
def delete_milestone(milestone_id: int, user: User = Depends(require_role("admin", "manager")),
                     db: Session = Depends(get_db)):
    m = db.get(MilestoneDate, milestone_id)
    if m is None:
        raise HTTPException(404, "Milestone not found")
    get_owned(db, Project, m.project_id, user)
    db.delete(m)
    db.commit()
    from fastapi import Response
    return Response(status_code=204)
