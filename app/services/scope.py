"""Who can see what. Admins see the whole company. Managers see only what they created."""
from sqlalchemy import select

from app.models import ActivityLog, DecisionRecord, Department, Employee, Project, Team, User


def _is_admin(user: User) -> bool:
    return user.role == "admin"


def project_scope(user: User):
    if _is_admin(user):
        return Project.company_id == user.company_id
    return (Project.company_id == user.company_id) & (Project.owner_id == user.id)


def department_scope(user: User):
    if _is_admin(user):
        return Department.company_id == user.company_id
    return (Department.company_id == user.company_id) & (Department.owner_id == user.id)


def team_scope(user: User):
    if _is_admin(user):
        return Team.company_id == user.company_id
    return (Team.company_id == user.company_id) & (Team.owner_id == user.id)


def employee_scope(user: User):
    if _is_admin(user):
        return Employee.company_id == user.company_id
    return (Employee.company_id == user.company_id) & (Employee.owner_id == user.id)


def decision_scope(user: User):
    visible = select(Project.id).where(project_scope(user))
    return (DecisionRecord.company_id == user.company_id) & DecisionRecord.project_id.in_(visible)


def activity_scope(user: User):
    base = ActivityLog.company_id == user.company_id
    return base if _is_admin(user) else base & (ActivityLog.user_name == user.full_name)
