from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.services.scope import activity_scope
from app.db import get_db
from app.deps import get_current_user
from app.models import ActivityLog, User

router = APIRouter(tags=["activity"])


@router.get("/activity")
def list_activity(limit: int = 100, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.scalars(
        select(ActivityLog)
        .where(activity_scope(user))
        .order_by(ActivityLog.id.desc())
        .limit(min(max(limit, 1), 500))
    ).all()
    return [{"id": r.id, "user": r.user_name, "action": r.action,
             "created_at": r.created_at.strftime("%Y-%m-%d %H:%M:%S")} for r in rows]
