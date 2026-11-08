from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user, get_owned, require_role
from app.models import Company, Department, Employee, Team, User
from app.schemas import CompanyUpdate

router = APIRouter(tags=["workspace"])
WRITER = ("admin", "manager")


def _to_dict(obj) -> dict:
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


def _unassign_team(db: Session, team_id: int) -> None:
    db.query(Employee).filter(Employee.team_id == team_id).update({Employee.team_id: None})


@router.patch("/company")
def rename_company(body: CompanyUpdate, admin: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    company = db.get(Company, admin.company_id)  # a company is its own tenant, so no company_id check
    company.name = body.name
    db.commit()
    db.refresh(company)
    return _to_dict(company)


@router.delete("/teams/{team_id}", status_code=204)
def delete_team(team_id: int, user: User = Depends(require_role(*WRITER)), db: Session = Depends(get_db)):
    team = get_owned(db, Team, team_id, user)
    _unassign_team(db, team.id)  # members are kept, just moved to "no team"
    db.delete(team)
    db.commit()
    return Response(status_code=204)


@router.delete("/departments/{department_id}", status_code=204)
def delete_department(department_id: int, user: User = Depends(require_role(*WRITER)),
                      db: Session = Depends(get_db)):
    dept = get_owned(db, Department, department_id, user)
    for team in db.query(Team).filter(Team.department_id == dept.id).all():
        _unassign_team(db, team.id)
        db.delete(team)
    db.delete(dept)
    db.commit()
    return Response(status_code=204)
