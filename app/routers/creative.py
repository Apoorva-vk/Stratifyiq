from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user, get_owned
from app.models import Project, User
from app.schemas import ScenarioIn
from app.services.achievements import leaderboard
from app.services.allocation import suggest
from app.services.briefing import build_briefing
from app.services.metrics import project_snapshot
from app.services.simulator import run_combined

router = APIRouter(tags=["insights"])


@router.get("/briefing")
def briefing(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return build_briefing(db, user)


@router.get("/achievements")
def achievements(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return leaderboard(db, user)


@router.get("/allocation")
def allocation(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return suggest(db, user)


@router.post("/analytics/projects/{project_id}/scenario")
def combined_scenario(project_id: int, body: ScenarioIn, user: User = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    proj = get_owned(db, Project, project_id, user)
    return run_combined(project_snapshot(db, proj), [a.model_dump() for a in body.actions])
