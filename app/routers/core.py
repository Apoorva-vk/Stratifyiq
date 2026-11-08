"""Company workspace, employees, projects, tasks and budget endpoints.
Reads require any authenticated user; writes require Admin or Manager.
All queries are scoped to the caller's company."""
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.services.scope import department_scope, employee_scope, project_scope, team_scope
from app.db import get_db
from app.deps import get_current_user, get_owned, require_role
from app.models import Company, Department, Employee, Expense, Project, Task, TaskMeta, Team, User
from app.schemas import (
    BudgetIn, DepartmentIn, EmployeeIn, EmployeeUpdate, ExpenseIn, ProgressIn, ProjectIn, ProjectUpdate,
    TaskIn, TaskUpdate, TeamIn,
)
from app.services.metrics import employee_utilization

router = APIRouter(tags=["workspace"])
WRITER = ("admin", "manager")


def _to_dict(obj) -> dict:
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


def _task_owned(db: Session, task_id: int, user: User) -> Task:
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(404, "Task not found")
    get_owned(db, Project, task.project_id, user)  # tenant check goes through the project
    return task


# ---------- Company workspace ----------

@router.get("/company")
def get_company(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    company = db.get(Company, user.company_id)  # a company is its own tenant
    return _to_dict(company)


@router.post("/departments", status_code=201)
def create_department(body: DepartmentIn, user: User = Depends(require_role(*WRITER)), db: Session = Depends(get_db)):
    dept = Department(company_id=user.company_id, owner_id=user.id, name=body.name)
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return _to_dict(dept)


@router.get("/departments")
def list_departments(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(Department).where(department_scope(user))).all()
    return [_to_dict(r) for r in rows]


@router.post("/teams", status_code=201)
def create_team(body: TeamIn, user: User = Depends(require_role(*WRITER)), db: Session = Depends(get_db)):
    get_owned(db, Department, body.department_id, user)
    team = Team(company_id=user.company_id, owner_id=user.id, department_id=body.department_id, name=body.name)
    db.add(team)
    db.commit()
    db.refresh(team)
    return _to_dict(team)


@router.get("/teams")
def list_teams(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(Team).where(team_scope(user))).all()
    return [_to_dict(r) for r in rows]


# ---------- Employees ----------

@router.post("/employees", status_code=201)
def create_employee(body: EmployeeIn, user: User = Depends(require_role(*WRITER)), db: Session = Depends(get_db)):
    if body.team_id is not None:
        get_owned(db, Team, body.team_id, user)
    emp = Employee(company_id=user.company_id, owner_id=user.id, **body.model_dump())
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return _to_dict(emp)


@router.get("/employees")
def list_employees(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(Employee).where(employee_scope(user))).all()
    return [_to_dict(r) for r in rows]


@router.get("/employees/workload")
def employees_workload(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(Employee).where(employee_scope(user))).all()
    return [
        {"employee_id": e.id, "name": e.name, "utilization_pct": employee_utilization(db, e)}
        for e in rows
    ]


# ---------- Projects ----------

@router.post("/projects", status_code=201)
def create_project(body: ProjectIn, user: User = Depends(require_role(*WRITER)), db: Session = Depends(get_db)):
    if body.deadline <= body.start_date:
        raise HTTPException(422, "Deadline must be after start date")
    proj = Project(company_id=user.company_id, owner_id=user.id, **body.model_dump())
    db.add(proj)
    db.commit()
    db.refresh(proj)
    return _to_dict(proj)


@router.get("/projects")
def list_projects(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(Project).where(project_scope(user))).all()
    return [_to_dict(r) for r in rows]


@router.get("/projects/{project_id}")
def get_project(project_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    proj = get_owned(db, Project, project_id, user)
    return _to_dict(proj)


@router.patch("/projects/{project_id}/budget")
def allocate_budget(project_id: int, body: BudgetIn, user: User = Depends(require_role(*WRITER)),
                    db: Session = Depends(get_db)):
    proj = get_owned(db, Project, project_id, user)
    proj.budget = body.budget
    db.commit()
    return _to_dict(proj)


@router.patch("/projects/{project_id}/progress")
def update_progress(project_id: int, body: ProgressIn, user: User = Depends(require_role(*WRITER)),
                    db: Session = Depends(get_db)):
    proj = get_owned(db, Project, project_id, user)
    proj.progress = body.progress
    db.commit()
    return _to_dict(proj)


# ---------- Tasks and milestones ----------

@router.post("/projects/{project_id}/tasks", status_code=201)
def create_task(project_id: int, body: TaskIn, user: User = Depends(require_role(*WRITER)),
                db: Session = Depends(get_db)):
    get_owned(db, Project, project_id, user)
    if body.assignee_id is not None:
        get_owned(db, Employee, body.assignee_id, user)
    task = Task(project_id=project_id, **body.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    db.add(TaskMeta(task_id=task.id, started_at=date.today()))
    db.commit()
    return _to_dict(task)


@router.get("/projects/{project_id}/tasks")
def list_tasks(project_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    get_owned(db, Project, project_id, user)
    rows = db.scalars(select(Task).where(Task.project_id == project_id)).all()
    return [_to_dict(r) for r in rows]


@router.patch("/tasks/{task_id}")
def update_task(task_id: int, body: TaskUpdate, user: User = Depends(require_role(*WRITER)),
                db: Session = Depends(get_db)):
    task = _task_owned(db, task_id, user)
    if body.done is not None:
        task.done = body.done
    if body.assignee_id is not None:
        get_owned(db, Employee, body.assignee_id, user)
        task.assignee_id = body.assignee_id
    db.commit()
    return _to_dict(task)


# ---------- Budget tracking ----------

@router.post("/projects/{project_id}/expenses", status_code=201)
def add_expense(project_id: int, body: ExpenseIn, user: User = Depends(require_role(*WRITER)),
                db: Session = Depends(get_db)):
    get_owned(db, Project, project_id, user)
    exp = Expense(project_id=project_id, **body.model_dump())
    db.add(exp)
    db.commit()
    db.refresh(exp)
    return _to_dict(exp)


@router.get("/projects/{project_id}/budget")
def budget_summary(project_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    proj = get_owned(db, Project, project_id, user)
    spent = float(db.scalar(
        select(func.coalesce(func.sum(Expense.amount), 0.0)).where(Expense.project_id == project_id)
    ))
    return {
        "project_id": project_id,
        "budget": proj.budget,
        "spent": round(spent, 2),
        "remaining": round(proj.budget - spent, 2),
        "burn_ratio": round(spent / proj.budget, 3) if proj.budget else None,
        "over_budget": spent > proj.budget,
    }


@router.get("/projects/{project_id}/expenses")
def list_expenses(project_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    get_owned(db, Project, project_id, user)
    rows = db.scalars(
        select(Expense).where(Expense.project_id == project_id).order_by(Expense.incurred_on.desc())
    ).all()
    return [_to_dict(r) for r in rows]


@router.delete("/projects/{project_id}", status_code=204)
def delete_project(project_id: int, user: User = Depends(require_role(*WRITER)), db: Session = Depends(get_db)):
    proj = get_owned(db, Project, project_id, user)
    db.query(Expense).filter(Expense.project_id == proj.id).delete()
    db.query(Task).filter(Task.project_id == proj.id).delete()
    db.delete(proj)
    db.commit()
    return Response(status_code=204)


@router.delete("/employees/{employee_id}", status_code=204)
def delete_employee(employee_id: int, user: User = Depends(require_role(*WRITER)), db: Session = Depends(get_db)):
    emp = get_owned(db, Employee, employee_id, user)
    db.query(Task).filter(Task.assignee_id == emp.id).update({Task.assignee_id: None})
    db.delete(emp)
    db.commit()
    return Response(status_code=204)


def _changes(model) -> dict:
    """Only the fields the client actually sent, ignoring explicit nulls."""
    return {k: v for k, v in model.model_dump(exclude_unset=True).items() if v is not None}


@router.patch("/projects/{project_id}")
def update_project(project_id: int, body: ProjectUpdate, user: User = Depends(require_role(*WRITER)),
                   db: Session = Depends(get_db)):
    proj = get_owned(db, Project, project_id, user)
    changes = _changes(body)
    new_deadline = changes.get("deadline", proj.deadline)
    if new_deadline <= proj.start_date:
        raise HTTPException(422, "Deadline must be after start date")
    for key, value in changes.items():
        setattr(proj, key, value)
    db.commit()
    db.refresh(proj)
    return _to_dict(proj)


@router.patch("/employees/{employee_id}")
def update_employee(employee_id: int, body: EmployeeUpdate, user: User = Depends(require_role(*WRITER)),
                    db: Session = Depends(get_db)):
    emp = get_owned(db, Employee, employee_id, user)
    changes = _changes(body)
    if changes.get("team_id") is not None:
        get_owned(db, Team, changes["team_id"], user)  # the team must belong to this company
    for key, value in changes.items():
        setattr(emp, key, value)
    db.commit()
    db.refresh(emp)
    return _to_dict(emp)
