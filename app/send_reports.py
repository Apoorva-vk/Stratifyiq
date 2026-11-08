"""Emails the weekly or monthly report to every active Admin, for scheduled runs.

Run manually:   python -m app.send_reports --period weekly
Or from Windows Task Scheduler using send-weekly-report.bat (see docs/SCHEDULED_REPORTS.md).
"""
import argparse

from sqlalchemy import select

from app.db import Base, SessionLocal, engine
from app.models import User
from app.services.email import send_email_with_attachment
from app.services.reports import make_periodic_pdf


def run(period: str) -> list[tuple[str, bool]]:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    results = []
    try:
        admins = db.scalars(select(User).where(User.role == "admin", User.is_active.is_(True))).all()
        for admin in admins:
            pdf = make_periodic_pdf(db, admin, period)
            sent = send_email_with_attachment(
                admin.email,
                f"StratifyIQ {period} report",
                f"Hello {admin.full_name},\n\nYour {period} StratifyIQ report is attached.\n",
                pdf,
                f"stratifyiq-{period}-report.pdf",
            )
            results.append((admin.email, sent))
    finally:
        db.close()
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Email the StratifyIQ report to every Admin.")
    parser.add_argument("--period", choices=["weekly", "monthly"], default="weekly")
    args = parser.parse_args()
    for email, sent in run(args.period):
        print(f"{email}: {'sent' if sent else 'not sent (email not set up or failed)'}")
