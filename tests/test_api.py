import os
import tempfile
import uuid

os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mkdtemp()}/test.db"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

client = TestClient(app)


def _signup_admin():
    """Signs up, confirms the email (development fallback returns the token), then logs in."""
    email = f"admin-{uuid.uuid4().hex[:8]}@example.com"
    r = client.post("/auth/signup", json={
        "company_name": "Acme Ltd", "full_name": "Ada Admin", "email": email, "password": "Secret123!",
    })
    assert r.status_code == 201, r.text
    assert client.post("/auth/verify", json={"token": r.json()["verify_token"]}).status_code == 200
    login = client.post("/auth/login", json={"email": email, "password": "Secret123!"})
    assert login.status_code == 200, login.text
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_signup_creates_admin_and_me_works():
    h = _signup_admin()
    me = client.get("/auth/me", headers=h).json()
    assert me["role"] == "admin"


def test_full_decision_flow():
    h = _signup_admin()
    dept = client.post("/departments", json={"name": "Engineering"}, headers=h).json()
    team = client.post("/teams", json={"name": "Backend", "department_id": dept["id"]}, headers=h).json()
    emp = client.post("/employees", json={"name": "Asha", "title": "Dev", "team_id": team["id"],
                                          "skills": "Python", "capacity_hours": 40}, headers=h).json()
    proj = client.post("/projects", json={"name": "Portal", "budget": 500000, "start_date": "2026-09-01",
                                          "deadline": "2026-12-31", "scope_units": 100}, headers=h).json()
    pid = proj["id"]
    client.post(f"/projects/{pid}/tasks", json={"title": "API", "estimated_hours": 60,
                                                "assignee_id": emp["id"]}, headers=h)
    client.post(f"/projects/{pid}/expenses", json={"description": "Cloud", "amount": 20000,
                                                   "incurred_on": "2026-10-01"}, headers=h)
    client.patch(f"/projects/{pid}/progress", json={"progress": 30}, headers=h)

    assert client.get(f"/projects/{pid}/budget", headers=h).json()["spent"] == 20000
    assert client.get(f"/analytics/projects/{pid}/predict", headers=h).status_code == 200

    sim = client.post(f"/analytics/projects/{pid}/simulate",
                      json={"action": "hire_employee", "value": 1}, headers=h)
    assert sim.status_code == 200 and "delta" in sim.json()

    rec = client.get(f"/analytics/projects/{pid}/recommend", headers=h).json()
    assert len(rec["top_recommendations"]) == 3

    dash = client.get("/analytics/dashboard", headers=h)
    assert dash.status_code == 200
    assert "business_health" in dash.json()


def test_manager_cannot_invite_and_tenants_are_isolated():
    h1 = _signup_admin()
    h2 = _signup_admin()
    proj = client.post("/projects", json={"name": "Secret", "budget": 1000, "start_date": "2026-09-01",
                                          "deadline": "2026-12-31"}, headers=h1).json()
    # The other company must not see this project.
    assert client.get(f"/projects/{proj['id']}", headers=h2).status_code == 404

    email = f"mgr-{uuid.uuid4().hex[:8]}@example.com"
    inv = client.post("/auth/invite", json={"email": email, "role": "manager"}, headers=h1).json()
    acc = client.post("/auth/accept-invite", json={"token": inv["invite_token"],
                                                   "full_name": "Manny", "password": "Manager123"}).json()
    mh = {"Authorization": f"Bearer {acc['access_token']}"}
    assert client.post("/auth/invite", json={"email": "x@example.com", "role": "manager"},
                       headers=mh).status_code == 403


def test_assistant_answers_questions():
    h = _signup_admin()
    client.post("/projects", json={"name": "Assist Test", "budget": 100000, "start_date": "2026-09-01",
                                   "deadline": "2026-12-31", "scope_units": 50}, headers=h)
    for q in ["which project is most at risk", "what should I do", "budget overrun",
              "team workload", "project health", "hello"]:
        r = client.post("/assistant/ask", json={"question": q}, headers=h)
        assert r.status_code == 200, r.text
        assert r.json()["answer"]


def test_expenses_delete_project_and_employee():
    h = _signup_admin()
    proj = client.post("/projects", json={"name": "Delete Me", "budget": 1000, "start_date": "2026-09-01",
                                          "deadline": "2026-12-31"}, headers=h).json()
    pid = proj["id"]
    client.post(f"/projects/{pid}/expenses", json={"description": "Tools", "amount": 300,
                                                   "incurred_on": "2026-10-01"}, headers=h)
    assert client.get(f"/projects/{pid}/expenses", headers=h).json()[0]["amount"] == 300
    b = client.get(f"/projects/{pid}/budget", headers=h).json()
    assert b["spent"] == 300 and b["remaining"] == 700 and b["over_budget"] is False

    emp = client.post("/employees", json={"name": "Temp Person", "title": "Analyst"}, headers=h).json()
    assert client.delete(f"/employees/{emp['id']}", headers=h).status_code == 204
    assert client.delete(f"/projects/{pid}", headers=h).status_code == 204
    assert client.get(f"/projects/{pid}", headers=h).status_code == 404


def test_assistant_uses_rules_without_api_key():
    h = _signup_admin()
    r = client.post("/assistant/ask", json={"question": "project health"}, headers=h)
    assert r.status_code == 200
    assert r.json()["source"] == "rules"


def test_ollama_unreachable_falls_back_to_rules(monkeypatch):
    from app.config import settings
    from app.services.llm import ask_llm

    monkeypatch.setattr(settings, "AI_PROVIDER", "ollama")
    monkeypatch.setattr(settings, "OLLAMA_URL", "http://127.0.0.1:9")  # nothing listens here
    assert ask_llm("hello", {"projects": []}) is None
    h = _signup_admin()
    r = client.post("/assistant/ask", json={"question": "project health"}, headers=h)
    assert r.status_code == 200
    assert r.json()["source"] == "rules"


def test_notifications_and_reports():
    h = _signup_admin()
    client.post("/projects", json={"name": "Report Test", "budget": 1000, "start_date": "2026-09-01",
                                   "deadline": "2026-10-20"}, headers=h)
    n = client.get("/notifications", headers=h)
    assert n.status_code == 200 and isinstance(n.json(), list)
    x = client.get("/reports/summary.xlsx", headers=h)
    assert x.status_code == 200 and x.content[:2] == b"PK"
    p = client.get("/reports/summary.pdf", headers=h)
    assert p.status_code == 200 and p.content[:4] == b"%PDF"


def test_powerbi_csv_exports():
    h = _signup_admin()
    client.post("/projects", json={"name": "Café Upgrade", "budget": 5000, "start_date": "2026-09-01",
                                   "deadline": "2026-12-31"}, headers=h)
    for path, first_col in [("/reports/powerbi/projects.csv", "name"),
                            ("/reports/powerbi/team.csv", "name"),
                            ("/reports/powerbi/alerts.csv", "level")]:
        r = client.get(path, headers=h)
        assert r.status_code == 200, path
        assert r.headers["content-type"].startswith("text/csv")
        assert r.content.decode("utf-8-sig").splitlines()[0].startswith(first_col)
    body = client.get("/reports/powerbi/projects.csv", headers=h).content.decode("utf-8-sig")
    assert "Café Upgrade" in body


def test_invite_and_password_reset_flow():
    h = _signup_admin()
    email = f"new-{uuid.uuid4().hex[:8]}@example.com"
    inv = client.post("/auth/invite", json={"email": email, "role": "manager"}, headers=h).json()
    assert inv["email_sent"] is False and inv["invite_token"]  # no SMTP in tests
    acc = client.post("/auth/accept-invite", json={"token": inv["invite_token"],
                                                   "full_name": "New Manager", "password": "Manager123"})
    assert acc.status_code == 201

    fr = client.post("/auth/forgot-password", json={"email": email})
    assert fr.status_code == 202 and fr.json()["reset_token"]
    rt = fr.json()["reset_token"]
    assert client.post("/auth/reset-password", json={"token": rt, "password": "NewSecret99"}).status_code == 200
    assert client.post("/auth/login", json={"email": email, "password": "Manager123"}).status_code == 401
    assert client.post("/auth/login", json={"email": email, "password": "NewSecret99"}).status_code == 200
    assert client.post("/auth/reset-password", json={"token": rt, "password": "Another123"}).status_code == 400

    unknown = client.post("/auth/forgot-password", json={"email": "nobody-here@example.com"})
    assert unknown.status_code == 202 and "reset_token" not in unknown.json()


def test_budget_forecast():
    h = _signup_admin()
    proj = client.post("/projects", json={"name": "Forecast Test", "budget": 100000, "start_date": "2026-09-01",
                                          "deadline": "2026-12-31"}, headers=h).json()
    client.post(f"/projects/{proj['id']}/expenses", json={"description": "Spend", "amount": 10000,
                                                          "incurred_on": "2026-09-05"}, headers=h)
    r = client.get(f"/analytics/projects/{proj['id']}/forecast", headers=h)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] in ("ON_TRACK", "AT_RISK", "OVER_BUDGET")
    assert len(body["series"]) == 11
    assert body["spent"] == 10000 and body["budget"] == 100000
    assert body["projected_total_by_progress"] is None  # no progress recorded yet


def test_edit_project_and_employee_and_dashboard_team():
    h = _signup_admin()
    proj = client.post("/projects", json={"name": "Edit Me", "budget": 1000, "start_date": "2026-09-01",
                                          "deadline": "2026-12-31"}, headers=h).json()
    r = client.patch(f"/projects/{proj['id']}", json={"budget": 2500, "status": "on_hold"}, headers=h)
    assert r.status_code == 200 and r.json()["budget"] == 2500 and r.json()["status"] == "on_hold"
    bad = client.patch(f"/projects/{proj['id']}", json={"deadline": "2026-08-01"}, headers=h)
    assert bad.status_code == 422

    emp = client.post("/employees", json={"name": "Old Name", "title": "Analyst"}, headers=h).json()
    e = client.patch(f"/employees/{emp['id']}", json={"name": "New Name", "availability_pct": 50}, headers=h)
    assert e.status_code == 200 and e.json()["name"] == "New Name" and e.json()["availability_pct"] == 50
    assert e.json()["title"] == "Analyst"  # untouched fields stay the same

    dash = client.get("/analytics/dashboard", headers=h).json()
    assert "team" in dash and "budget" in dash["projects"][0] and "spent" in dash["projects"][0]


def test_activity_log_and_user_management():
    h = _signup_admin()
    client.post("/projects", json={"name": "Logged", "budget": 500, "start_date": "2026-09-01",
                                   "deadline": "2026-12-31"}, headers=h)
    acts = client.get("/activity", headers=h).json()
    assert any(a["action"] == "Created a project" for a in acts)

    me = client.get("/auth/me", headers=h).json()
    assert client.patch(f"/users/{me['id']}", json={"role": "manager"}, headers=h).status_code == 400
    assert client.patch(f"/users/{me['id']}", json={"is_active": False}, headers=h).status_code == 400

    email = f"team-{uuid.uuid4().hex[:8]}@example.com"
    inv = client.post("/auth/invite", json={"email": email, "role": "manager"}, headers=h).json()
    mgr = client.post("/auth/accept-invite", json={"token": inv["invite_token"],
                                                   "full_name": "Team Member", "password": "Member123"}).json()
    mh = {"Authorization": f"Bearer {mgr['access_token']}"}
    users = client.get("/users", headers=h).json()
    mgr_id = next(u["id"] for u in users if u["email"] == email)
    assert client.get("/users", headers=mh).status_code == 403  # managers cannot list users
    assert client.patch(f"/users/{mgr_id}", json={"is_active": False}, headers=h).status_code == 200
    assert client.get("/auth/me", headers=mh).status_code == 401  # deactivated users are locked out


def test_briefing_and_combined_scenario():
    h = _signup_admin()
    proj = client.post("/projects", json={"name": "Insight Test", "budget": 200000, "start_date": "2026-09-01",
                                          "deadline": "2026-10-20"}, headers=h).json()
    b = client.get("/briefing", headers=h)
    assert b.status_code == 200 and b.json()["text"] and b.json()["source"] == "rules"
    ok = client.post(f"/analytics/projects/{proj['id']}/scenario", headers=h, json={"actions": [
        {"action": "hire_employee", "value": 1}, {"action": "extend_deadline", "value": 14}]})
    assert ok.status_code == 200, ok.text
    assert "delta" in ok.json() and "scenario" in ok.json()
    too_many = client.post(f"/analytics/projects/{proj['id']}/scenario", headers=h, json={"actions": [
        {"action": "reallocate_resources", "value": 0}] * 5})
    assert too_many.status_code == 422


def test_achievements_points_and_badges():
    h = _signup_admin()
    emp = client.post("/employees", json={"name": "Badge Winner", "title": "Developer"}, headers=h).json()
    proj = client.post("/projects", json={"name": "Badge Project", "budget": 9000, "start_date": "2026-09-01",
                                          "deadline": "2026-12-31"}, headers=h).json()
    task = client.post(f"/projects/{proj['id']}/tasks", json={"title": "Ship it", "estimated_hours": 10,
                                                              "assignee_id": emp["id"]}, headers=h).json()
    client.patch(f"/tasks/{task['id']}", json={"done": True}, headers=h)
    board = client.get("/achievements", headers=h).json()
    row = next(r for r in board if r["employee_id"] == emp["id"])
    assert row["tasks_done"] == 1 and row["points"] == 15
    assert "First finish" in row["badges"]


def test_decision_memory_health_story():
    h = _signup_admin()
    proj = client.post("/projects", json={"name": "Memory Test", "budget": 100000, "start_date": "2026-09-01",
                                          "deadline": "2026-12-31"}, headers=h).json()
    d = client.post("/decisions", json={"project_id": proj["id"], "action": "extend_deadline", "value": 14}, headers=h)
    assert d.status_code == 201, d.text
    lst = client.get("/decisions", headers=h).json()
    assert len(lst["decisions"]) == 1 and lst["accuracy"]["resolved"] == 0
    assert client.post(f"/decisions/{d.json()['id']}/outcome", json={"finished_late": True}, headers=h).status_code == 200
    acc = client.get("/decisions", headers=h).json()["accuracy"]
    assert acc["resolved"] == 1 and acc["delay_accuracy_pct"] in (0.0, 100.0)
    assert client.post("/health/snapshot", headers=h).json()["recorded"] >= 1
    story = client.get("/health/story", headers=h).json()
    assert story and story[0]["text"]


def test_smart_reminders():
    from datetime import date, timedelta
    from app.db import SessionLocal
    from app.models import TaskMeta

    h = _signup_admin()
    proj = client.post("/projects", json={"name": "Reminder Test", "budget": 50000, "start_date": "2026-09-01",
                                          "deadline": "2026-12-31"}, headers=h).json()
    task = client.post(f"/projects/{proj['id']}/tasks", json={"title": "Long task", "estimated_hours": 16},
                       headers=h).json()
    assert client.get("/reminders", headers=h).json() == []

    db = SessionLocal()
    try:
        db.get(TaskMeta, task["id"]).started_at = date.today() - timedelta(days=28)
        db.commit()
    finally:
        db.close()
    assert any(r["task_id"] == task["id"] for r in client.get("/reminders", headers=h).json())
    assert any(a["type"] == "reminder" for a in client.get("/notifications", headers=h).json())


def test_organisation_departments_and_allocation():
    h = _signup_admin()
    assert client.patch("/company", json={"name": "Renamed Ltd"}, headers=h).json()["name"] == "Renamed Ltd"
    dept = client.post("/departments", json={"name": "Engineering"}, headers=h).json()
    team = client.post("/teams", json={"name": "Platform", "department_id": dept["id"]}, headers=h).json()
    emp = client.post("/employees", json={"name": "Assign Me", "title": "Developer"}, headers=h).json()
    moved = client.patch(f"/employees/{emp['id']}", json={"team_id": team["id"]}, headers=h)
    assert moved.status_code == 200 and moved.json()["team_id"] == team["id"]
    other = _signup_admin()
    their_dept = client.post("/departments", json={"name": "Theirs"}, headers=other).json()
    their_team = client.post("/teams", json={"name": "Theirs", "department_id": their_dept["id"]}, headers=other).json()
    assert client.patch(f"/employees/{emp['id']}", json={"team_id": their_team["id"]}, headers=h).status_code == 404
    assert client.delete(f"/teams/{team['id']}", headers=h).status_code == 204
    assert client.delete(f"/departments/{dept['id']}", headers=h).status_code == 204


def test_periodic_report_and_allocation_suggestion():
    h = _signup_admin()
    a = client.post("/employees", json={"name": "Overloaded Ana", "title": "Dev"}, headers=h).json()
    b = client.post("/employees", json={"name": "Free Ben", "title": "Dev"}, headers=h).json()
    proj = client.post("/projects", json={"name": "Balance Test", "budget": 90000, "start_date": "2026-09-01",
                                          "deadline": "2026-12-31"}, headers=h).json()
    for title in ("Big task one", "Big task two"):
        client.post(f"/projects/{proj['id']}/tasks", json={"title": title, "estimated_hours": 100,
                                                           "assignee_id": a["id"]}, headers=h)
    sug = client.get("/allocation", headers=h).json()
    match = [s for s in sug if s["from_id"] == a["id"] and s["to_id"] == b["id"]]
    assert match and match[0]["projected_to"] <= 100
    assert client.patch(f"/tasks/{match[0]['task_id']}", json={"assignee_id": b["id"]}, headers=h).status_code == 200

    r = client.get("/reports/periodic.pdf?period=weekly", headers=h)
    assert r.status_code == 200 and r.content[:4] == b"%PDF"
    m = client.get("/reports/periodic.pdf?period=monthly", headers=h)
    assert m.status_code == 200 and m.content[:4] == b"%PDF"
    assert client.get("/reports/periodic.pdf?period=yearly", headers=h).status_code == 422


def test_get_company_returns_profile():
    h = _signup_admin()
    r = client.get("/company", headers=h)
    assert r.status_code == 200 and r.json()["name"] == "Acme Ltd"



def test_signup_requires_email_confirmation():
    email = f"confirm-{uuid.uuid4().hex[:8]}@example.com"
    body = client.post("/auth/signup", json={"company_name": "Confirm Co", "full_name": "New Admin",
                                             "email": email, "password": "Secret123!"}).json()
    assert "access_token" not in body and body["verify_token"]
    blocked = client.post("/auth/login", json={"email": email, "password": "Secret123!"})
    assert blocked.status_code == 403 and "confirm" in blocked.json()["detail"].lower()
    assert client.post("/auth/verify", json={"token": body["verify_token"]}).status_code == 200
    assert client.post("/auth/login", json={"email": email, "password": "Secret123!"}).status_code == 200
    assert client.post("/auth/verify", json={"token": body["verify_token"]}).status_code == 400


def test_task_due_dates_and_overdue():
    h = _signup_admin()
    proj = client.post("/projects", json={"name": "Due Test", "budget": 5000, "start_date": "2026-09-01",
                                          "deadline": "2026-12-31"}, headers=h).json()
    task = client.post(f"/projects/{proj['id']}/tasks", json={"title": "Late task", "estimated_hours": 8},
                       headers=h).json()
    assert client.put(f"/tasks/{task['id']}/due-date", json={"due_date": "2026-01-01"}, headers=h).status_code == 200
    due = client.get(f"/projects/{proj['id']}/task-due-dates", headers=h).json()
    assert due[0]["overdue"] is True
    assert any(a["type"] == "task-deadline" for a in client.get("/notifications", headers=h).json())
    client.put(f"/tasks/{task['id']}/due-date", json={"due_date": None}, headers=h)
    assert client.get(f"/projects/{proj['id']}/task-due-dates", headers=h).json() == []


def test_milestones_with_dates():
    h = _signup_admin()
    proj = client.post("/projects", json={"name": "Milestone Test", "budget": 8000, "start_date": "2026-09-01",
                                          "deadline": "2026-12-31"}, headers=h).json()
    pid = proj["id"]
    m = client.post(f"/projects/{pid}/milestones", json={"name": "Phase 1", "due_date": "2026-01-15"}, headers=h)
    assert m.status_code == 201, m.text
    dup = client.post(f"/projects/{pid}/milestones", json={"name": "Phase 1", "due_date": "2026-02-01"}, headers=h)
    assert dup.status_code == 409
    client.post(f"/projects/{pid}/tasks", json={"title": "Design", "estimated_hours": 4, "milestone": "Phase 1"},
                headers=h)
    listed = client.get(f"/projects/{pid}/milestones", headers=h).json()
    assert listed[0]["total_tasks"] == 1 and listed[0]["overdue"] is True
    assert client.delete(f"/milestones/{m.json()['id']}", headers=h).status_code == 204
    assert client.get(f"/projects/{pid}/milestones", headers=h).json() == []


def test_email_report_without_smtp():
    h = _signup_admin()
    r = client.post("/reports/email", json={"period": "weekly"}, headers=h)
    assert r.status_code == 200
    body = r.json()
    assert body["sent"] is False and "not set up" in body["message"]
    assert client.post("/reports/email", json={"period": "yearly"}, headers=h).status_code == 422


def test_templates_suggestions_and_digest():
    h = _signup_admin()
    templates = client.get("/templates", headers=h).json()
    assert any(t["key"] == "software_release" for t in templates)
    made = client.post("/projects/from-template", headers=h, json={
        "template": "software_release", "name": "Template Launch", "budget": 120000,
        "start_date": "2026-09-01", "deadline": "2026-12-31"})
    assert made.status_code == 201, made.text
    pid = made.json()["id"]
    assert len(client.get(f"/projects/{pid}/milestones", headers=h).json()) == 4
    assert len(client.get(f"/projects/{pid}/tasks", headers=h).json()) >= 8

    client.post("/employees", json={"name": "Py Dev", "title": "Engineer", "skills": "python, fastapi"}, headers=h)
    client.post("/employees", json={"name": "Designer", "title": "UI", "skills": "figma, css"}, headers=h)
    ranked = client.post("/assignee-suggestions", json={"title": "Build fastapi endpoint", "hours": 8},
                         headers=h).json()
    assert ranked[0]["name"] == "Py Dev" and "fastapi" in ranked[0]["matched_skills"]

    digest = client.get("/digest/week", headers=h).json()
    assert "text" in digest and digest["changes"] >= 1
    assert client.post("/projects/from-template", headers=h, json={
        "template": "nope", "name": "Bad", "budget": 1, "start_date": "2026-09-01",
        "deadline": "2026-12-31"}).status_code == 422


def test_scheduled_report_runner_and_progress_from_tasks():
    from app import send_reports
    h = _signup_admin()
    results = send_reports.run("weekly")
    assert results and all(sent is False for _, sent in results)
    proj = client.post("/projects", json={"name": "Progress Test", "budget": 10000, "start_date": "2026-09-01",
                                          "deadline": "2026-12-31"}, headers=h).json()
    t1 = client.post(f"/projects/{proj['id']}/tasks", json={"title": "Half", "estimated_hours": 10}, headers=h).json()
    client.post(f"/projects/{proj['id']}/tasks", json={"title": "Rest", "estimated_hours": 10}, headers=h)
    client.patch(f"/tasks/{t1['id']}", json={"done": True}, headers=h)
    r = client.post(f"/projects/{proj['id']}/progress/from-tasks", headers=h)
    assert r.status_code == 200 and r.json()["progress"] == 50.0


def test_jira_import_and_sync(monkeypatch):
    from app.services import jira

    assert client.get("/integrations/jira", headers=_signup_admin()).json()["configured"] is False

    state = {"done": False}

    def fake_search(jql, max_results=50):
        return [
            {"key": "DEMO-1", "fields": {"summary": "Login page", "timeoriginalestimate": 28800,
                                         "status": {"statusCategory": {"key": "done" if state["done"] else "new"}}}},
            {"key": "DEMO-2", "fields": {"summary": "Export", "timeoriginalestimate": None,
                                         "status": {"statusCategory": {"key": "done"}}}},
        ]

    monkeypatch.setattr(jira, "search", fake_search)
    h = _signup_admin()
    proj = client.post("/projects", json={"name": "Jira Test", "budget": 9000, "start_date": "2026-09-01",
                                          "deadline": "2026-12-31"}, headers=h).json()
    pid = proj["id"]
    first = client.post(f"/projects/{pid}/jira/import", json={"jql": "project = DEMO"}, headers=h).json()
    assert first["imported"] == 2 and first["skipped"] == 0
    again = client.post(f"/projects/{pid}/jira/import", json={"jql": "project = DEMO"}, headers=h).json()
    assert again["imported"] == 0 and again["skipped"] == 2

    tasks = {t["title"]: t for t in client.get(f"/projects/{pid}/tasks", headers=h).json()}
    assert tasks["DEMO-1: Login page"]["estimated_hours"] == 8.0 and tasks["DEMO-1: Login page"]["done"] is False
    assert tasks["DEMO-2: Export"]["done"] is True

    state["done"] = True
    assert client.post(f"/projects/{pid}/jira/sync", headers=h).json()["updated"] == 2
    tasks = {t["title"]: t for t in client.get(f"/projects/{pid}/tasks", headers=h).json()}
    assert tasks["DEMO-1: Login page"]["done"] is True


def _invite_manager(h, name="Team Lead"):
    email = f"lead-{uuid.uuid4().hex[:8]}@example.com"
    inv = client.post("/auth/invite", json={"email": email, "role": "manager"}, headers=h).json()
    acc = client.post("/auth/accept-invite", json={"token": inv["invite_token"],
                                                   "full_name": name, "password": "Manager123"})
    assert acc.status_code == 201, acc.text
    return {"Authorization": f"Bearer {acc.json()['access_token']}"}


def test_manager_sees_only_own_work():
    h = _signup_admin()
    admin_proj = client.post("/projects", json={"name": "Admin Project", "budget": 5000, "start_date": "2026-09-01",
                                                "deadline": "2026-12-31"}, headers=h).json()
    client.post("/departments", json={"name": "Admin Dept"}, headers=h)
    mh = _invite_manager(h)
    assert client.get("/projects", headers=mh).json() == []
    own = client.post("/projects", json={"name": "Manager Project", "budget": 7000, "start_date": "2026-09-01",
                                         "deadline": "2026-12-31"}, headers=mh)
    assert own.status_code == 201, own.text
    own_id = own.json()["id"]
    assert [p["id"] for p in client.get("/projects", headers=mh).json()] == [own_id]
    assert client.get(f"/projects/{admin_proj['id']}", headers=mh).status_code == 404
    assert client.patch(f"/projects/{admin_proj['id']}", json={"name": "Changed"}, headers=mh).status_code == 404
    assert client.delete(f"/projects/{admin_proj['id']}", headers=mh).status_code == 404
    assert client.patch(f"/projects/{own_id}", json={"name": "Renamed"}, headers=mh).status_code == 200
    assert client.post(f"/projects/{own_id}/expenses", json={"description": "Tools", "amount": 100,
                                                             "incurred_on": "2026-10-01"}, headers=mh).status_code == 201
    assert client.get("/departments", headers=mh).json() == []
    dep = client.post("/departments", json={"name": "Lead Dept"}, headers=mh)
    assert dep.status_code == 201
    assert [d["id"] for d in client.get("/departments", headers=mh).json()] == [dep.json()["id"]]
    assert client.post("/reports/email", json={"period": "weekly"}, headers=mh).status_code == 200
    assert client.delete(f"/projects/{own_id}", headers=mh).status_code == 204
    assert client.get("/projects", headers=h).status_code == 200  # admin still sees everything
