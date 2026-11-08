"""Morning briefing: a short plain-language summary of the company's position.
Written from the rules by default. If an AI provider is configured, the same facts
are passed to the model for more natural wording."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.services.scope import employee_scope, project_scope
from app.models import Employee, Project, User
from app.services.llm import ask_llm
from app.services.metrics import employee_utilization, project_snapshot
from app.services.simulator import predict_from_snapshot


def build_briefing(db: Session, user: User) -> dict:
    projects = db.scalars(select(Project).where(project_scope(user))).all()
    team = db.scalars(select(Employee).where(employee_scope(user))).all()

    rows = []
    for p in projects:
        snap = project_snapshot(db, p)
        pred = predict_from_snapshot(snap)
        rows.append({"name": p.name, "snap": snap, "pred": pred})

    high = [r["name"] for r in rows if r["pred"]["risk_level"] == "HIGH"]
    over = [r["name"] for r in rows if r["snap"]["budget"] and r["snap"]["spent"] > r["snap"]["budget"]]
    due_soon = [r for r in rows if r["snap"]["progress"] < 100 and r["snap"]["days_left"] <= 14]
    overloaded = [e.name for e in team if employee_utilization(db, e) > 100]
    total_budget = sum(r["snap"]["budget"] for r in rows)
    total_spent = sum(r["snap"]["spent"] for r in rows)

    facts = {
        "projects": len(rows),
        "total_budget": round(total_budget, 2),
        "total_spent": round(total_spent, 2),
        "high_risk_projects": high,
        "over_budget_projects": over,
        "due_within_14_days": [{"name": r["name"], "days_left": r["snap"]["days_left"],
                                "progress_pct": round(r["snap"]["progress"])} for r in due_soon],
        "overloaded_team_members": overloaded,
        "team_size": len(team),
    }

    lines = [f"You have {len(rows)} projects with {total_spent:,.0f} spent of a {total_budget:,.0f} total budget."]
    if high:
        lines.append(f"{len(high)} project(s) are rated high risk: {', '.join(high)}.")
    else:
        lines.append("No project is currently rated high risk.")
    if over:
        lines.append(f"Over budget: {', '.join(over)}.")
    if due_soon:
        names = ", ".join(f"{r['name']} ({r['snap']['days_left']} days left)" for r in due_soon)
        lines.append(f"Deadlines within two weeks: {names}.")
    if overloaded:
        lines.append(f"Overloaded team members: {', '.join(overloaded)}.")
    if not (high or over or due_soon or overloaded):
        lines.append("Nothing needs urgent attention today.")
    rules_text = " ".join(lines)

    ai_text = ask_llm(
        "Write a short morning briefing (3 to 4 sentences) for a manager, based only on these facts. "
        "Lead with the most urgent point.",
        facts,
    )
    return {
        "text": ai_text or rules_text,
        "source": "ai" if ai_text else "rules",
        "facts": facts,
    }
