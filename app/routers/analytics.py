"""Prediction, Decision Simulator, Recommendation and Business Health endpoints.
Read-only: nothing here changes project data."""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.services.scope import employee_scope, project_scope
from app.db import get_db
from app.deps import get_current_user, get_owned
from app.models import Employee, Project, User
from app.schemas import SimulateIn
from app.services.forecast import forecast
from app.services.health import employee_health, project_health
from app.services.metrics import employee_utilization, project_snapshot
from app.services.ml import risk_level
from app.services.recommender import recommend
from app.services.simulator import predict_from_snapshot, run_scenario

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _avg(values):
    vals = [v for v in values if v is not None]
    return round(sum(vals) / len(vals), 1) if vals else None


@router.get("/projects/{project_id}/predict")
def predict_project(project_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    proj = get_owned(db, Project, project_id, user)
    snap = project_snapshot(db, proj)
    pred = predict_from_snapshot(snap)
    return {"snapshot": snap, "prediction": pred, "health": project_health(pred)}


@router.post("/projects/{project_id}/simulate")
def simulate_decision(project_id: int, body: SimulateIn, user: User = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    proj = get_owned(db, Project, project_id, user)
    snap = project_snapshot(db, proj)
    return run_scenario(snap, body.action, body.value)


@router.get("/projects/{project_id}/recommend")
def recommend_project(project_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    proj = get_owned(db, Project, project_id, user)
    return recommend(project_snapshot(db, proj))


@router.get("/dashboard")
def executive_dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    projects = db.scalars(select(Project).where(project_scope(user))).all()
    per_project = []
    for p in projects:
        snap = project_snapshot(db, p)
        pred = predict_from_snapshot(snap)
        per_project.append({
            "project_id": p.id,
            "name": p.name,
            "budget": snap["budget"],
            "spent": snap["spent"],
            "prediction": pred,
            "risk_level": risk_level(pred["delay_risk"]),
            "health": project_health(pred),
        })

    employees = db.scalars(select(Employee).where(employee_scope(user))).all()
    team = [{"name": e.name, "utilization_pct": employee_utilization(db, e)} for e in employees]
    emp_scores = [employee_health(t["utilization_pct"]) for t in team]

    proj_health = [p["health"] for p in per_project]
    project_avg = _avg([h["overall"] for h in proj_health])
    employee_avg = _avg(emp_scores)
    business_health = {
        "overall_health": _avg([project_avg, employee_avg]),
        "project_health": project_avg,
        "financial_health": _avg([h["financial"] for h in proj_health]),
        "risk_health": _avg([h["schedule"] for h in proj_health]),
        "employee_health": employee_avg,
    }
    return {
        "business_health": business_health,
        "total_projects": len(projects),
        "total_employees": len(employees),
        "high_risk_projects": [p for p in per_project if p["risk_level"] == "HIGH"],
        "projects": per_project,
        "team": team,
    }


@router.get("/projects/{project_id}/forecast")
def forecast_project(project_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    proj = get_owned(db, Project, project_id, user)
    snap = project_snapshot(db, proj)
    return forecast(proj.start_date, proj.deadline, snap["budget"], snap["spent"], snap["progress"])
