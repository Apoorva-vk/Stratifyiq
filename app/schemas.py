from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field


class SignupIn(BaseModel):
    company_name: str = Field(min_length=2, max_length=200)
    full_name: str = Field(min_length=2, max_length=200)
    email: EmailStr
    password: str = Field(min_length=8)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class InviteIn(BaseModel):
    email: EmailStr
    role: Literal["manager"] = "manager"  # only managers are invited; admins are created at signup


class AcceptInviteIn(BaseModel):
    token: str
    full_name: str = Field(min_length=2, max_length=200)
    password: str = Field(min_length=8)


class ForgotPasswordIn(BaseModel):
    email: EmailStr


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    company_id: int


class DepartmentIn(BaseModel):
    name: str = Field(min_length=2, max_length=150)


class TeamIn(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    department_id: int


class EmployeeIn(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    title: str = Field(min_length=2, max_length=150)
    team_id: Optional[int] = None
    skills: str = ""
    experience_years: float = Field(0, ge=0)
    capacity_hours: float = Field(40, gt=0, le=80)
    availability_pct: float = Field(100, ge=0, le=100)
    hourly_cost: float = Field(0, ge=0)


class ProjectIn(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    budget: float = Field(gt=0)
    start_date: date
    deadline: date
    scope_units: float = Field(100, gt=0)


class BudgetIn(BaseModel):
    budget: float = Field(gt=0)


class ProgressIn(BaseModel):
    progress: float = Field(ge=0, le=100)


class TaskIn(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    estimated_hours: float = Field(gt=0)
    assignee_id: Optional[int] = None
    milestone: Optional[str] = None


class TaskUpdate(BaseModel):
    done: Optional[bool] = None
    assignee_id: Optional[int] = None


class ExpenseIn(BaseModel):
    description: str = Field(min_length=2, max_length=200)
    amount: float = Field(gt=0)
    incurred_on: date


class SimulateIn(BaseModel):
    action: Literal[
        "hire_employee",
        "increase_budget",
        "reduce_budget",
        "extend_deadline",
        "reduce_scope",
        "reallocate_resources",
    ]
    value: float = 0


class ResetPasswordIn(BaseModel):
    token: str
    password: str = Field(min_length=8)


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    budget: Optional[float] = Field(None, gt=0)
    deadline: Optional[date] = None
    scope_units: Optional[float] = Field(None, gt=0)
    status: Optional[Literal["active", "on_hold", "completed"]] = None


class EmployeeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    title: Optional[str] = Field(None, min_length=2, max_length=150)
    skills: Optional[str] = None
    experience_years: Optional[float] = Field(None, ge=0)
    capacity_hours: Optional[float] = Field(None, gt=0, le=80)
    availability_pct: Optional[float] = Field(None, ge=0, le=100)
    hourly_cost: Optional[float] = Field(None, ge=0)
    team_id: Optional[int] = None


class UserUpdate(BaseModel):
    role: Optional[Literal["admin", "manager"]] = None
    is_active: Optional[bool] = None


class ScenarioIn(BaseModel):
    actions: list[SimulateIn] = Field(min_length=1, max_length=4)


class DecisionIn(BaseModel):
    project_id: int
    action: Literal[
        "hire_employee", "increase_budget", "reduce_budget", "extend_deadline", "reduce_scope", "reallocate_resources",
    ]
    value: float = 0


class OutcomeIn(BaseModel):
    finished_late: bool


class CompanyUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=200)


class VerifyIn(BaseModel):
    token: str


class TaskDueIn(BaseModel):
    due_date: Optional[date] = None


class MilestoneIn(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    due_date: date


class ReportEmailIn(BaseModel):
    period: Literal["weekly", "monthly"] = "weekly"


class TemplateProjectIn(BaseModel):
    template: Literal["software_release", "client_onboarding", "marketing_campaign"]
    name: str = Field(min_length=2, max_length=200)
    budget: float = Field(gt=0)
    start_date: date
    deadline: date
    scope_units: float = Field(100, gt=0)


class AssigneeIn(BaseModel):
    title: str = Field(min_length=2, max_length=300)
    hours: float = Field(0, ge=0)


class JiraIn(BaseModel):
    jql: str = Field(min_length=2, max_length=500)
