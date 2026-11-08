"""Excel and PDF company summaries built from the same calculations as the dashboard."""
import csv
from datetime import date, timedelta
from io import BytesIO, StringIO
from xml.sax.saxutils import escape

from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.services.scope import decision_scope, employee_scope, project_scope
from app.models import Employee, Project, User
from app.services.health import employee_health, project_health
from app.services.metrics import employee_utilization, project_snapshot
from app.services.notifications import build_alerts
from app.services.simulator import predict_from_snapshot


def company_data(db: Session, user: User):
    projects, team = [], []
    for p in db.scalars(select(Project).where(project_scope(user)).order_by(Project.id)).all():
        snap = project_snapshot(db, p)
        pred = predict_from_snapshot(snap)
        projects.append({
            "name": p.name, "budget": snap["budget"], "spent": snap["spent"],
            "progress": snap["progress"], "days_left": snap["days_left"],
            "risk": pred["risk_level"], "delay_pct": round(pred["delay_risk"] * 100, 1),
            "overrun_pct": round(pred["overrun_pct"], 1),
            "success_pct": round(pred["success_probability"], 1),
            "health": project_health(pred)["overall"],
        })
    for e in db.scalars(select(Employee).where(employee_scope(user)).order_by(Employee.id)).all():
        u = employee_utilization(db, e)
        team.append({"name": e.name, "title": e.title, "hours": e.capacity_hours,
                     "utilization_pct": u, "health": employee_health(u)})
    return projects, team, build_alerts(db, user)


def _bold_header(ws):
    for cell in ws[1]:
        cell.font = Font(bold=True)


def _widths(ws, widths):
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w


def make_excel(db: Session, user: User) -> bytes:
    projects, team, alerts = company_data(db, user)
    wb = Workbook()

    ws = wb.active
    ws.title = "Projects"
    ws.append(["Project", "Budget", "Spent", "Progress %", "Days left", "Risk",
               "Delay risk %", "Overrun %", "Success %", "Health"])
    for p in projects:
        ws.append([p["name"], p["budget"], p["spent"], p["progress"], p["days_left"], p["risk"],
                   p["delay_pct"], p["overrun_pct"], p["success_pct"], p["health"]])
    _bold_header(ws)
    _widths(ws, [28, 14, 14, 12, 11, 10, 14, 12, 12, 10])

    ws2 = wb.create_sheet("Team")
    ws2.append(["Name", "Title", "Hours per week", "Utilisation %", "Health"])
    for e in team:
        ws2.append([e["name"], e["title"], e["hours"], e["utilization_pct"], e["health"]])
    _bold_header(ws2)
    _widths(ws2, [24, 24, 16, 16, 10])

    ws3 = wb.create_sheet("Alerts")
    ws3.append(["Level", "Message"])
    for a in alerts:
        ws3.append([a["level"], a["message"]])
    _bold_header(ws3)
    _widths(ws3, [12, 80])

    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()


def _table(rows):
    t = Table(rows, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f3a5f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
    ]))
    return t


def make_pdf(db: Session, user: User) -> bytes:
    projects, team, alerts = company_data(db, user)
    styles = getSampleStyleSheet()
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)

    story = [
        Paragraph("StratifyIQ Company Summary", styles["Title"]),
        Paragraph(f"Generated {date.today().isoformat()}", styles["Normal"]),
        Spacer(1, 12),
        Paragraph("Projects", styles["Heading2"]),
        _table([["Project", "Budget", "Spent", "Progress", "Risk", "Health"]] + [
            [p["name"], f"{p['budget']:,.0f}", f"{p['spent']:,.0f}", f"{p['progress']:.0f}%", p["risk"], str(p["health"])]
            for p in projects
        ] if projects else [["No projects yet", "", "", "", "", ""]]),
        Spacer(1, 16),
        Paragraph("Team", styles["Heading2"]),
        _table([["Name", "Title", "Hours/week", "Utilisation", "Health"]] + [
            [e["name"], e["title"], f"{e['hours']:.0f}", f"{e['utilization_pct']:.0f}%", str(e["health"])]
            for e in team
        ] if team else [["No team members yet", "", "", "", ""]]),
        Spacer(1, 16),
        Paragraph("Alerts", styles["Heading2"]),
    ]
    if alerts:
        for a in alerts:
            story.append(Paragraph(f"{a['level'].upper()}: {escape(a['message'])}", styles["Normal"]))
    else:
        story.append(Paragraph("No alerts.", styles["Normal"]))

    doc.build(story)
    return buf.getvalue()


PROJECT_COLUMNS = ["name", "budget", "spent", "progress", "days_left", "risk",
                   "delay_pct", "overrun_pct", "success_pct", "health"]
TEAM_COLUMNS = ["name", "title", "hours", "utilization_pct", "health"]
ALERT_COLUMNS = ["level", "type", "message"]


def make_csv(rows: list[dict], columns: list[str]) -> bytes:
    """UTF-8 with a byte-order mark, so Excel and Power BI read accented names correctly."""
    buf = StringIO()
    writer = csv.DictWriter(buf, fieldnames=columns)
    writer.writeheader()
    for row in rows:
        writer.writerow({c: row.get(c, "") for c in columns})
    return buf.getvalue().encode("utf-8-sig")


def period_label(period: str, today: date) -> str:
    if period == "weekly":
        monday = today - timedelta(days=today.weekday())
        return f"Week of {monday:%d %b %Y}"
    return f"{today:%B %Y}"


def make_periodic_pdf(db: Session, user: User, period: str) -> bytes:
    """Weekly or monthly report: summary, projects, team, health story, decision accuracy and alerts."""
    from app.models import DecisionRecord
    from app.services.health_story import build_story
    from app.services.memory import accuracy

    projects, team, alerts = company_data(db, user)
    story = build_story(db, user)
    acc = accuracy(db.scalars(select(DecisionRecord).where(decision_scope(user))).all())
    styles = getSampleStyleSheet()
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)

    story_flow = [
        Paragraph(f"StratifyIQ {period.title()} Report", styles["Title"]),
        Paragraph(period_label(period, date.today()), styles["Normal"]),
        Spacer(1, 10),
        Paragraph(f"{len(projects)} projects, {len(team)} team members and {len(alerts)} alerts.", styles["Normal"]),
        Spacer(1, 10),
        Paragraph("Projects", styles["Heading2"]),
        _table([["Project", "Budget", "Spent", "Progress", "Risk", "Health"]] + [
            [p["name"], f"{p['budget']:,.0f}", f"{p['spent']:,.0f}", f"{p['progress']:.0f}%", p["risk"], str(p["health"])]
            for p in projects
        ] if projects else [["No projects yet", "", "", "", "", ""]]),
        Spacer(1, 14),
        Paragraph("Project health story", styles["Heading2"]),
    ]
    for line in story:
        story_flow.append(Paragraph(escape(line["text"]), styles["Normal"]))
    story_flow += [Spacer(1, 14), Paragraph("Decision accuracy", styles["Heading2"])]
    if acc["resolved"]:
        story_flow.append(Paragraph(
            f"Delay prediction accuracy {acc['delay_accuracy_pct']}% across {acc['resolved']} recorded outcomes. "
            f"Average overrun error {acc['overrun_error_pts']} points.", styles["Normal"]))
    else:
        story_flow.append(Paragraph("No decision outcomes recorded yet.", styles["Normal"]))
    story_flow += [Spacer(1, 14), Paragraph("Alerts", styles["Heading2"])]
    if alerts:
        for a in alerts:
            story_flow.append(Paragraph(f"{a['level'].upper()}: {escape(a['message'])}", styles["Normal"]))
    else:
        story_flow.append(Paragraph("No alerts.", styles["Normal"]))

    doc.build(story_flow)
    return buf.getvalue()
