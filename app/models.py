from datetime import date, datetime
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


def _now() -> datetime:
    return datetime.utcnow()


class Company(Base):
    __tablename__ = "companies"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(200))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20))  # admin | manager
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Invite(Base):
    __tablename__ = "invites"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    email: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="manager")
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    accepted: Mapped[bool] = mapped_column(Boolean, default=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime)


class Department(Base):
    __tablename__ = "departments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    owner_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(150))


class Team(Base):
    __tablename__ = "teams"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    owner_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.id"))
    name: Mapped[str] = mapped_column(String(150))


class Employee(Base):
    __tablename__ = "employees"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    owner_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    team_id: Mapped[Optional[int]] = mapped_column(ForeignKey("teams.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(150))
    title: Mapped[str] = mapped_column(String(150))
    skills: Mapped[str] = mapped_column(Text, default="")
    experience_years: Mapped[float] = mapped_column(Float, default=0)
    capacity_hours: Mapped[float] = mapped_column(Float, default=40)     # hours per week
    availability_pct: Mapped[float] = mapped_column(Float, default=100)
    hourly_cost: Mapped[float] = mapped_column(Float, default=0)


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    owner_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    budget: Mapped[float] = mapped_column(Float)
    start_date: Mapped[date] = mapped_column(Date)
    deadline: Mapped[date] = mapped_column(Date)
    scope_units: Mapped[float] = mapped_column(Float, default=100)
    progress: Mapped[float] = mapped_column(Float, default=0)            # 0-100
    status: Mapped[str] = mapped_column(String(20), default="active")


class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    estimated_hours: Mapped[float] = mapped_column(Float)
    assignee_id: Mapped[Optional[int]] = mapped_column(ForeignKey("employees.id"), nullable=True)
    milestone: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    done: Mapped[bool] = mapped_column(Boolean, default=False)


class Expense(Base):
    __tablename__ = "expenses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    description: Mapped[str] = mapped_column(String(200))
    amount: Mapped[float] = mapped_column(Float)
    incurred_on: Mapped[date] = mapped_column(Date)


class PasswordReset(Base):
    __tablename__ = "password_resets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    used: Mapped[bool] = mapped_column(Boolean, default=False)


class ActivityLog(Base):
    __tablename__ = "activity_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    user_name: Mapped[str] = mapped_column(String(200))
    action: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


class TaskMeta(Base):
    """When a task was created. Kept in its own table so existing databases need no migration."""
    __tablename__ = "task_meta"
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), primary_key=True)
    started_at: Mapped[date] = mapped_column(Date)


class DecisionRecord(Base):
    __tablename__ = "decisions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    saved_by: Mapped[str] = mapped_column(String(200))
    action: Mapped[str] = mapped_column(String(40))
    value: Mapped[float] = mapped_column(Float, default=0)
    scenario_delay: Mapped[float] = mapped_column(Float)
    scenario_overrun: Mapped[float] = mapped_column(Float)
    scenario_success: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    outcome_late: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    actual_overrun_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    recorded_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class HealthSnapshot(Base):
    __tablename__ = "health_snapshots"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    week_start: Mapped[date] = mapped_column(Date)
    overall: Mapped[float] = mapped_column(Float)
    financial: Mapped[float] = mapped_column(Float)
    schedule: Mapped[float] = mapped_column(Float)
    workload: Mapped[float] = mapped_column(Float)


class PendingVerification(Base):
    """Accounts that have not yet confirmed their email. Existing accounts have no row, so they are unaffected."""
    __tablename__ = "pending_verifications"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime)


class TaskDeadline(Base):
    __tablename__ = "task_deadlines"
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), primary_key=True)
    due_date: Mapped[date] = mapped_column(Date)


class MilestoneDate(Base):
    __tablename__ = "milestone_dates"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    name: Mapped[str] = mapped_column(String(200))
    due_date: Mapped[date] = mapped_column(Date)


class JiraLink(Base):
    """Links a task to a Jira issue key, so later syncs update the right task."""
    __tablename__ = "jira_links"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), unique=True)
    issue_key: Mapped[str] = mapped_column(String(50))
