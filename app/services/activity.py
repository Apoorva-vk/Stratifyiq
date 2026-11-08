"""Activity log: records successful changes (POST, PATCH, DELETE) to company data.
Only the write methods are recorded, so reading data never creates log entries."""
from app.db import SessionLocal
from app.models import ActivityLog, User

LOGGED_PREFIXES = ("/projects", "/employees", "/teams", "/departments", "/tasks", "/auth/invite", "/users")

_DESCRIPTIONS = {
    ("projects", None, "POST"): "Created a project",
    ("projects", None, "PATCH"): "Updated a project",
    ("projects", None, "DELETE"): "Deleted a project",
    ("projects", "tasks", "POST"): "Added a task",
    ("projects", "expenses", "POST"): "Recorded an expense",
    ("projects", "progress", "PATCH"): "Updated project progress",
    ("projects", "budget", "PATCH"): "Changed a project budget",
    ("tasks", None, "PATCH"): "Updated a task",
    ("employees", None, "POST"): "Added a team member",
    ("employees", None, "PATCH"): "Updated a team member",
    ("employees", None, "DELETE"): "Removed a team member",
    ("teams", None, "POST"): "Created a team",
    ("departments", None, "POST"): "Created a department",
    ("users", None, "PATCH"): "Changed a user's access",
}


def describe(method: str, path: str) -> str:
    parts = [p for p in path.strip("/").split("/") if p]
    if parts[:2] == ["auth", "invite"] and method == "POST":
        return "Invited a manager"
    head = parts[0] if parts else ""
    sub = parts[2] if len(parts) >= 3 else None
    return _DESCRIPTIONS.get((head, sub, method), f"{method} /{'/'.join(parts)}")


def record(user_id: int, method: str, path: str) -> None:
    db = SessionLocal()
    try:
        user = db.get(User, user_id)
        if user is None:
            return
        db.add(ActivityLog(company_id=user.company_id, user_name=user.full_name,
                           action=describe(method, path)))
        db.commit()
    finally:
        db.close()
