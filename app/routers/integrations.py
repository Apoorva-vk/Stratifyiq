from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.deps import get_current_user, get_owned, require_role
from app.models import JiraLink, Project, Task, TaskMeta, User
from app.schemas import JiraIn
from app.services import jira

router = APIRouter(tags=["integrations"])


@router.get("/integrations/jira")
def jira_status(user: User = Depends(get_current_user)):
    return {"configured": jira.configured(), "base_url": settings.JIRA_BASE_URL or None}


@router.post("/integrations/jira/test")
def jira_test(user: User = Depends(require_role("admin", "manager"))):
    try:
        return {"ok": True, "connected_as": jira.test_connection()}
    except jira.JiraError as e:
        raise HTTPException(400, str(e))
    except Exception:
        raise HTTPException(502, "Could not reach Jira. Check JIRA_BASE_URL and your internet connection.")


@router.post("/projects/{project_id}/jira/import")
def jira_import(project_id: int, body: JiraIn, user: User = Depends(require_role("admin", "manager")),
                db: Session = Depends(get_db)):
    get_owned(db, Project, project_id, user)
    try:
        issues = jira.search(body.jql)
    except jira.JiraError as e:
        raise HTTPException(400, str(e))
    except Exception:
        raise HTTPException(502, "Could not reach Jira. Check JIRA_BASE_URL and your internet connection.")

    imported, skipped = [], 0
    for issue in issues:
        mapped = jira.to_task(issue)
        if db.scalar(select(JiraLink).where(JiraLink.project_id == project_id, JiraLink.issue_key == mapped["key"])):
            skipped += 1
            continue
        task = Task(project_id=project_id, title=mapped["title"], estimated_hours=mapped["hours"], done=mapped["done"])
        db.add(task)
        db.flush()
        db.add(TaskMeta(task_id=task.id, started_at=date.today()))
        db.add(JiraLink(project_id=project_id, task_id=task.id, issue_key=mapped["key"]))
        imported.append(mapped["key"])
    db.commit()
    return {"imported": len(imported), "skipped": skipped, "imported_keys": imported}


@router.post("/projects/{project_id}/jira/sync")
def jira_sync(project_id: int, user: User = Depends(require_role("admin", "manager")), db: Session = Depends(get_db)):
    get_owned(db, Project, project_id, user)
    links = db.scalars(select(JiraLink).where(JiraLink.project_id == project_id)).all()
    if not links:
        raise HTTPException(422, "No Jira issues are linked to this project yet. Import some first.")
    keys = [l.issue_key for l in links][:100]
    try:
        issues = jira.search(f"key in ({','.join(keys)})", max_results=100)
    except jira.JiraError as e:
        raise HTTPException(400, str(e))
    except Exception:
        raise HTTPException(502, "Could not reach Jira. Check JIRA_BASE_URL and your internet connection.")

    by_key = {jira.to_task(i)["key"]: jira.to_task(i) for i in issues}
    updated = 0
    for link in links:
        mapped = by_key.get(link.issue_key)
        task = db.get(Task, link.task_id)
        if mapped is None or task is None:
            continue
        task.done = mapped["done"]
        task.title = mapped["title"]
        updated += 1
    db.commit()
    return {"updated": updated}
