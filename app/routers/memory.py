from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.services.scope import decision_scope
from app.db import get_db
from app.deps import get_current_user, get_owned, require_role
from app.models import DecisionRecord, Project, User
from app.schemas import DecisionIn, OutcomeIn
from app.services.health_story import build_story, record_snapshots
from app.services.memory import accuracy, serialize
from app.services.metrics import project_snapshot
from app.services.reminders import build_reminders
from app.services.simulator import run_scenario

router = APIRouter(tags=["memory"])


@router.post("/decisions", status_code=201)
def save_decision(body: DecisionIn, user: User = Depends(require_role("admin", "manager")), db: Session = Depends(get_db)):
    proj = get_owned(db, Project, body.project_id, user)
    result = run_scenario(project_snapshot(db, proj), body.action, body.value)
    rec = DecisionRecord(
        company_id=user.company_id, project_id=proj.id, saved_by=user.full_name,
        action=body.action, value=body.value,
        scenario_delay=result["scenario"]["delay_risk"],
        scenario_overrun=result["scenario"]["overrun_pct"],
        scenario_success=result["scenario"]["success_probability"],
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return serialize(rec, proj.name)


@router.get("/decisions")
def list_decisions(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.execute(
        select(DecisionRecord, Project.name)
        .join(Project, DecisionRecord.project_id == Project.id)
        .where(decision_scope(user))
        .order_by(DecisionRecord.id.desc())
    ).all()
    return {
        "decisions": [serialize(r, name) for r, name in rows],
        "accuracy": accuracy([r for r, _ in rows]),
    }


@router.post("/decisions/{decision_id}/outcome")
def record_outcome(decision_id: int, body: OutcomeIn, user: User = Depends(require_role("admin", "manager")),
                   db: Session = Depends(get_db)):
    rec = get_owned(db, DecisionRecord, decision_id, user)
    proj = db.get(Project, rec.project_id)
    snap = project_snapshot(db, proj)
    rec.outcome_late = body.finished_late
    rec.actual_overrun_pct = round((snap["spent"] / snap["budget"] - 1) * 100, 1) if snap["budget"] else 0.0
    rec.recorded_at = datetime.utcnow()
    db.commit()
    return serialize(rec, proj.name)


@router.post("/health/snapshot")
def health_snapshot(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return record_snapshots(db, user)


@router.get("/health/story")
def health_story(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return build_story(db, user)


@router.get("/reminders")
def reminders(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return build_reminders(db, user)
