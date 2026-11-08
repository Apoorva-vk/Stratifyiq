from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_owned, require_role
from app.models import User
from app.schemas import UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


def _public(u: User) -> dict:
    return {"id": u.id, "full_name": u.full_name, "email": u.email, "role": u.role, "is_active": u.is_active}


@router.get("")
def list_users(admin: User = Depends(require_role("admin")), db: Session = Depends(get_db)):
    rows = db.scalars(select(User).where(User.company_id == admin.company_id).order_by(User.id)).all()
    return [_public(u) for u in rows]


@router.patch("/{user_id}")
def update_user(user_id: int, body: UserUpdate, admin: User = Depends(require_role("admin")),
                db: Session = Depends(get_db)):
    target = get_owned(db, User, user_id, admin)
    changes = body.model_dump(exclude_unset=True)
    if target.id == admin.id and (changes.get("is_active") is False or changes.get("role") == "manager"):
        raise HTTPException(400, "You cannot deactivate or demote your own account")
    for key, value in changes.items():
        if value is not None:
            setattr(target, key, value)
    db.commit()
    db.refresh(target)
    return _public(target)
