import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models import DecisionRecord, Department, Employee, Project, Team, User

_bearer = HTTPBearer(auto_error=True)


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(creds.credentials, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.get(User, int(payload["sub"]))
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user


def require_role(*roles: str):
    """Dependency factory: allow only users whose stored role is in `roles`."""

    def _checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail=f"Requires role: {' or '.join(roles)}")
        return user

    return _checker


def get_owned(db: Session, model, obj_id: int, user: User):
    """Fetch a row and enforce access. Same company always; managers only reach what they created."""
    obj = db.get(model, obj_id)
    if obj is None or obj.company_id != user.company_id:
        raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
    if user.role != "admin":
        if model in (Project, Department, Team, Employee) and obj.owner_id != user.id:
            raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
        if model is DecisionRecord:
            proj = db.get(Project, obj.project_id)
            if proj is None or proj.owner_id != user.id:
                raise HTTPException(status_code=404, detail="DecisionRecord not found")
    return obj
