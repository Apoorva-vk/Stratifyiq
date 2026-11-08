"""StratifyIQ Assistant (rule-based for now).

It reads the same predictions and recommendations as the dashboard and answers
common questions in plain language. The keyword routing can later be replaced by
a language model without changing the API.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.services.scope import employee_scope, project_scope
from app.config import settings
from app.models import Employee, Project, User
from app.services.llm import ask_llm
from app.services.health import project_health
from app.services.metrics import employee_utilization, project_snapshot
from app.services.recommender import recommend
from app.services.simulator import predict_from_snapshot


def _has(text: str, words: list[str]) -> bool:
    return any(w in text for w in words)


def _rule_answer(question: str, db: Session, user: User) -> dict:
    q = question.lower()
    projects = db.scalars(select(Project).where(project_scope(user))).all()
    if not projects:
        return {"answer": "You have no projects yet. Add one on the Projects page and I can analyse it.", "data": None}

    analysed = []
    for p in projects:
        snap = project_snapshot(db, p)
        analysed.append({"id": p.id, "name": p.name, "snap": snap, "pred": predict_from_snapshot(snap)})

    if _has(q, ["recommend", "should", "what to do", "improve", "fix", "best"]):
        target = max(analysed, key=lambda a: a["pred"]["delay_risk"])
        rec = recommend(target["snap"])
        top = rec["top_recommendations"][0]
        drivers = ", ".join(rec["primary_risk_drivers"])
        return {
            "answer": f"For {target['name']}, the best option is: {top['summary']} Main risk drivers: {drivers}.",
            "data": {"project_id": target["id"], "recommendation": top},
        }

    if _has(q, ["budget", "overrun", "cost", "spend", "money"]):
        worst = max(analysed, key=lambda a: a["pred"]["overrun_pct"])
        over = worst["pred"]["overrun_pct"]
        text = (f"{worst['name']} has the highest predicted budget overrun at {over:.1f}%."
                if over > 0 else "No project is currently predicted to overrun its budget.")
        return {"answer": text, "data": {"project_id": worst["id"], "overrun_pct": over}}

    if _has(q, ["employee", "staff", "team", "workload", "overload", "utili"]):
        employees = db.scalars(select(Employee).where(employee_scope(user))).all()
        util = {e.name: employee_utilization(db, e) for e in employees}
        overloaded = [n for n, u in util.items() if u > 100]
        idle = [n for n, u in util.items() if u < 40]
        parts = [
            f"Overloaded (over 100%): {', '.join(overloaded)}." if overloaded else "Nobody is overloaded.",
            f"Under-used (below 40%): {', '.join(idle)}." if idle else "Nobody is under-used.",
        ]
        return {"answer": " ".join(parts), "data": util}

    if _has(q, ["health", "score"]):
        scores = [(a["name"], project_health(a["pred"])["overall"]) for a in analysed]
        avg = sum(s for _, s in scores) / len(scores)
        lowest = min(scores, key=lambda x: x[1])
        return {
            "answer": f"Average project health is {avg:.1f}/100. Lowest is {lowest[0]} at {lowest[1]}.",
            "data": dict(scores),
        }

    if _has(q, ["risk", "delay", "late", "deadline", "danger", "critical"]):
        high = [a for a in analysed if a["pred"]["risk_level"] == "HIGH"]
        worst = max(analysed, key=lambda a: a["pred"]["delay_risk"])
        pct = worst["pred"]["delay_risk"] * 100
        if high:
            names = ", ".join(a["name"] for a in high)
            text = f"{len(high)} project(s) are HIGH risk: {names}. The most at risk is {worst['name']} at {pct:.1f}% delay risk."
        else:
            text = f"No project is HIGH risk. The most at risk is {worst['name']} at {pct:.1f}% delay risk."
        return {"answer": text, "data": {"project_id": worst["id"]}}

    high_count = sum(1 for a in analysed if a["pred"]["risk_level"] == "HIGH")
    return {
        "answer": (f"You have {len(analysed)} projects, {high_count} rated HIGH risk. "
                   "Ask me about risk, budget, team workload, health or recommendations."),
        "data": None,
    }


def _llm_answer(question: str, db: Session, user: User) -> str | None:
    if settings.AI_PROVIDER == "none":
        return None
    projects = db.scalars(select(Project).where(project_scope(user))).all()
    if not projects:
        return None
    project_rows = []
    for p in projects:
        snap = project_snapshot(db, p)
        pred = predict_from_snapshot(snap)
        project_rows.append({
            "name": p.name,
            "budget": snap["budget"],
            "spent": snap["spent"],
            "progress_pct": snap["progress"],
            "days_left": snap["days_left"],
            "delay_risk_pct_estimate": round(pred["delay_risk"] * 100, 1),
            "risk_level": pred["risk_level"],
            "overrun_pct_estimate": pred["overrun_pct"],
            "success_probability_estimate": pred["success_probability"],
            "overall_health": project_health(pred)["overall"],
        })
    employees = db.scalars(select(Employee).where(employee_scope(user))).all()
    team = [{"name": e.name, "title": e.title, "utilization_pct": employee_utilization(db, e)} for e in employees]
    return ask_llm(question, {"projects": project_rows, "team": team})


def answer(question: str, db: Session, user: User) -> dict:
    """AI answer when a key is configured; otherwise the rule-based answer."""
    text = _llm_answer(question, db, user)
    if text:
        return {"answer": text, "data": None, "source": "ai"}
    result = _rule_answer(question, db, user)
    result["source"] = "rules"
    return result
