from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user
from app.models import User
from app.schemas import ReportEmailIn
from app.services.email import send_email_with_attachment
from app.services.notifications import build_alerts
from app.services.reports import (
    ALERT_COLUMNS, PROJECT_COLUMNS, TEAM_COLUMNS, company_data, make_csv, make_excel, make_pdf, make_periodic_pdf,
)

router = APIRouter(tags=["reports"])

XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
CSV = "text/csv; charset=utf-8"


@router.get("/notifications")
def notifications(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return build_alerts(db, user)


@router.get("/reports/summary.xlsx")
def summary_excel(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return Response(content=make_excel(db, user), media_type=XLSX,
                    headers={"Content-Disposition": "attachment; filename=stratifyiq-summary.xlsx"})


@router.get("/reports/summary.pdf")
def summary_pdf(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return Response(content=make_pdf(db, user), media_type="application/pdf",
                    headers={"Content-Disposition": "attachment; filename=stratifyiq-summary.pdf"})


@router.get("/reports/periodic.pdf")
def periodic_pdf(period: str = "weekly", user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if period not in ("weekly", "monthly"):
        raise HTTPException(422, "period must be weekly or monthly")
    return Response(content=make_periodic_pdf(db, user, period), media_type="application/pdf",
                    headers={"Content-Disposition": f"attachment; filename=stratifyiq-{period}-report.pdf"})


@router.post("/reports/email")
def email_report(body: ReportEmailIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Emails the period report as a PDF attachment to the signed-in user."""
    pdf = make_periodic_pdf(db, user, body.period)
    sent = send_email_with_attachment(
        user.email,
        f"StratifyIQ {body.period} report",
        f"Hello {user.full_name},\n\nYour {body.period} StratifyIQ report is attached.\n",
        pdf,
        f"stratifyiq-{body.period}-report.pdf",
    )
    message = ("Report emailed to you." if sent else
               "Email is not set up, so the report was not sent. Download it from this page instead.")
    return {"sent": sent, "to": user.email, "message": message}


def _csv_response(content: bytes, filename: str) -> Response:
    return Response(content=content, media_type=CSV,
                    headers={"Content-Disposition": f"attachment; filename={filename}"})


@router.get("/reports/powerbi/projects.csv")
def powerbi_projects(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    projects, _, _ = company_data(db, user)
    return _csv_response(make_csv(projects, PROJECT_COLUMNS), "stratifyiq-projects.csv")


@router.get("/reports/powerbi/team.csv")
def powerbi_team(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _, team, _ = company_data(db, user)
    return _csv_response(make_csv(team, TEAM_COLUMNS), "stratifyiq-team.csv")


@router.get("/reports/powerbi/alerts.csv")
def powerbi_alerts(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _, _, alerts = company_data(db, user)
    return _csv_response(make_csv(alerts, ALERT_COLUMNS), "stratifyiq-alerts.csv")
