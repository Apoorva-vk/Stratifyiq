"""Ready-made project plans. Milestone dates fall at fixed fractions of the project's timeline."""
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models import MilestoneDate, Project, Task, TaskDeadline, TaskMeta

TEMPLATES = {
    "software_release": {
        "label": "Software release",
        "milestones": [
            {"name": "Requirements", "at": 0.15, "tasks": [("Gather requirements", 16), ("Write user stories", 8)]},
            {"name": "Build", "at": 0.55, "tasks": [("Design screens", 24), ("Build features", 80), ("Code review", 12)]},
            {"name": "Testing", "at": 0.8, "tasks": [("Write test cases", 16), ("Run regression tests", 12), ("Fix defects", 20)]},
            {"name": "Launch", "at": 1.0, "tasks": [("Deploy to production", 8), ("Write release notes", 4)]},
        ],
    },
    "client_onboarding": {
        "label": "Client onboarding",
        "milestones": [
            {"name": "Kickoff", "at": 0.1, "tasks": [("Kickoff meeting", 2), ("Confirm scope", 4)]},
            {"name": "Setup", "at": 0.5, "tasks": [("Configure accounts", 8), ("Import client data", 12)]},
            {"name": "Training", "at": 0.85, "tasks": [("Prepare training material", 10), ("Run user training", 6)]},
            {"name": "Handover", "at": 1.0, "tasks": [("Sign-off review", 3), ("Hand over documentation", 4)]},
        ],
    },
    "marketing_campaign": {
        "label": "Marketing campaign",
        "milestones": [
            {"name": "Planning", "at": 0.2, "tasks": [("Set campaign goals", 6), ("Audience research", 12)]},
            {"name": "Creative", "at": 0.5, "tasks": [("Write copy", 16), ("Design visuals", 20)]},
            {"name": "Launch", "at": 0.7, "tasks": [("Schedule posts", 4), ("Set up tracking", 6)]},
            {"name": "Review", "at": 1.0, "tasks": [("Measure results", 8), ("Write campaign report", 6)]},
        ],
    },
}


def create_from_template(db: Session, company_id: int, template: str, name: str, budget: float,
                         start: date, deadline: date, scope_units: float) -> Project:
    plan = TEMPLATES[template]
    total = (deadline - start).days
    project = Project(company_id=company_id, name=name, budget=budget, start_date=start,
                      deadline=deadline, scope_units=scope_units)
    db.add(project)
    db.flush()
    for m in plan["milestones"]:
        due = start + timedelta(days=round(total * m["at"]))
        db.add(MilestoneDate(project_id=project.id, name=m["name"], due_date=due))
        for title, hours in m["tasks"]:
            task = Task(project_id=project.id, title=title, estimated_hours=hours,
                        milestone=m["name"], done=False)
            db.add(task)
            db.flush()
            db.add(TaskMeta(task_id=task.id, started_at=date.today()))
            db.add(TaskDeadline(task_id=task.id, due_date=due))
    db.commit()
    db.refresh(project)
    return project
