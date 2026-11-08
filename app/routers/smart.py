import re
from collections import Counter
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.services.scope import activity_scope, decision_scope, employee_scope
from app.db import get_db
from app.deps import get_current_user, require_role
from app.models import ActivityLog, DecisionRecord, Employee, Project, Task, User
from app.schemas import AssigneeIn, TemplateProjectIn
from app.services.metrics import employee_utilization
from app.services.templates import TEMPLATES, create_from_template

router = APIRouter(tags=["smart"])


@router.get("/templates")
def list_templates(user: User = Depends(get_current_user)):
    return [{"key": k, "label": v["label"],
             "milestones": [m["name"] for m in v["milestones"]],
             "tasks": sum(len(m["tasks"]) for m in v["milestones"])} for k, v in TEMPLATES.items()]


@router.post("/projects/from-template", status_code=201)
def project_from_template(body: TemplateProjectIn, user: User = Depends(require_role("admin", "manager")),
                          db: Session = Depends(get_db)):
    if body.deadline <= body.start_date:
        raise HTTPException(422, "Deadline must be after start date")
    project = create_from_template(db, user.company_id, body.template, body.name, body.budget,
                                   body.start_date, body.deadline, body.scope_units)
    project.owner_id = user.id
    db.commit()
    return {"id": project.id, "name": project.name, "template": body.template}


def _words(text: str) -> set[str]:
    return {w for w in re.split(r"[^a-z0-9]+", text.lower()) if len(w) >= 3}


def _matches(word: str, skill: str) -> bool:
    if word == skill:
        return True
    return len(skill) >= 4 and len(word) >= 4 and (skill in word or word in skill)


@router.post("/assignee-suggestions")
def assignee_suggestions(body: AssigneeIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Ranks the team for a task: skill matches first, then spare capacity. Nothing is changed."""
    words = _words(body.title)
    rows = []
    for e in db.scalars(select(Employee).where(employee_scope(user))).all():
        skills = [s.strip().lower() for s in (e.skills or "").split(",") if s.strip()]
        matched = sorted({s for s in skills if any(_matches(w, s) for w in words)})
        util = employee_utilization(db, e)
        score = len(matched) * 10 + max(0.0, 100 - util) / 10 - (20 if util > 100 else 0)
        reason = (f"Skills match: {', '.join(matched)}" if matched else "No skill match") + \
                 f"; currently at {util:.0f}% workload"
        rows.append({"employee_id": e.id, "name": e.name, "title": e.title, "utilization_pct": util,
                     "matched_skills": matched, "score": round(score, 1), "reason": reason})
    rows.sort(key=lambda r: -r["score"])
    return rows[:3]


@router.get("/digest/week")
def week_digest(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    since = datetime.utcnow() - timedelta(days=7)
    acts = db.scalars(select(ActivityLog).where(activity_scope(user),
                                                ActivityLog.created_at >= since)).all()
    decisions = db.scalars(select(DecisionRecord).where(decision_scope(user),
                                                        DecisionRecord.created_at >= since)).all()
    by_person = Counter(a.user_name for a in acts)
    by_action = Counter(a.action for a in acts)
    lines = [f"{len(acts)} change(s) were made in the last 7 days."]
    if by_person:
        name, n = by_person.most_common(1)[0]
        lines.append(f"{name} made the most changes ({n}).")
    if by_action:
        action, n = by_action.most_common(1)[0]
        lines.append(f"The most common change was: {action.lower()} ({n} times).")
    lines.append(f"{len(decisions)} decision(s) were saved for comparison.")
    return {"text": " ".join(lines), "changes": len(acts), "by_person": dict(by_person),
            "by_action": dict(by_action), "decisions_saved": len(decisions)}


@router.post("/projects/{project_id}/progress/from-tasks")
def progress_from_tasks(project_id: int, user: User = Depends(require_role("admin", "manager")),
                        db: Session = Depends(get_db)):
    """Sets progress to the share of estimated hours completed. Projects without tasks are left unchanged."""
    from app.deps import get_owned
    proj = get_owned(db, Project, project_id, user)
    tasks = db.scalars(select(Task).where(Task.project_id == project_id)).all()
    total = sum(t.estimated_hours for t in tasks)
    if total <= 0:
        raise HTTPException(422, "This project has no tasks yet, so progress cannot be calculated from them")
    done = sum(t.estimated_hours for t in tasks if t.done)
    proj.progress = round(done / total * 100, 1)
    db.commit()
    return {"progress": proj.progress}
