"""Weekly health snapshots and a plain-English story of how each project's health changed."""
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.services.scope import project_scope
from app.models import HealthSnapshot, Project, User
from app.services.health import project_health
from app.services.metrics import project_snapshot
from app.services.simulator import predict_from_snapshot

DRIVER_NAMES = {"financial": "budget", "schedule": "schedule", "workload": "workload"}


def current_week() -> date:
    today = date.today()
    return today - timedelta(days=today.weekday())


def record_snapshots(db: Session, user: User) -> dict:
    week = current_week()
    projects = db.scalars(select(Project).where(project_scope(user))).all()
    for p in projects:
        health = project_health(predict_from_snapshot(project_snapshot(db, p)))
        row = db.scalar(select(HealthSnapshot).where(
            HealthSnapshot.project_id == p.id, HealthSnapshot.week_start == week))
        if row is None:
            row = HealthSnapshot(company_id=user.company_id, project_id=p.id, week_start=week)
            db.add(row)
        row.overall, row.financial = health["overall"], health["financial"]
        row.schedule, row.workload = health["schedule"], health["workload"]
    db.commit()
    return {"recorded": len(projects), "week": week.isoformat()}


def build_story(db: Session, user: User) -> list[dict]:
    story = []
    projects = db.scalars(select(Project).where(project_scope(user)).order_by(Project.id)).all()
    for p in projects:
        snaps = db.scalars(
            select(HealthSnapshot).where(HealthSnapshot.project_id == p.id)
            .order_by(HealthSnapshot.week_start.desc()).limit(2)
        ).all()
        if not snaps:
            text = f"{p.name}: no health history yet. Record a snapshot to start tracking."
        elif len(snaps) == 1:
            text = (f"{p.name}: first snapshot recorded at {snaps[0].overall:.0f}/100. "
                    "Next week's snapshot will show what changed.")
        else:
            now, prev = snaps
            change = now.overall - prev.overall
            if abs(change) < 1:
                text = f"{p.name}: health held steady at {now.overall:.0f}/100 since {prev.week_start:%d %b}."
            else:
                direction = "improved" if change > 0 else "dropped"
                text = (f"{p.name}: health {direction} by {abs(change):.0f} points, "
                        f"from {prev.overall:.0f} to {now.overall:.0f}.")
            deltas = {k: getattr(now, k) - getattr(prev, k) for k in DRIVER_NAMES}
            biggest = max(deltas, key=lambda k: abs(deltas[k]))
            if abs(deltas[biggest]) >= 1:
                text += f" The biggest change was in {DRIVER_NAMES[biggest]} ({deltas[biggest]:+.0f} points)."
        story.append({"project_id": p.id, "name": p.name, "weeks_recorded": len(snaps), "text": text})
    return story
