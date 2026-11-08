"""Load demo data: one company, an Admin, a Manager, teams, employees and three projects.
Run with: python -m app.seed"""
from datetime import date, timedelta

from sqlalchemy import select

from app.db import Base, SessionLocal, engine
from app.models import Company, Department, Employee, Expense, Project, Task, Team, User
from app.security import hash_password


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.scalar(select(User).where(User.email == "admin@demo.com")):
            print("Demo data already present.")
            return

        today = date.today()
        company = Company(name="Demo Corp")
        db.add(company)
        db.flush()
        db.add_all([
            User(company_id=company.id, email="admin@demo.com", full_name="Demo Admin",
                 password_hash=hash_password("Admin@123"), role="admin"),
            User(company_id=company.id, email="manager@demo.com", full_name="Demo Manager",
                 password_hash=hash_password("Manager@123"), role="manager"),
        ])

        eng = Department(company_id=company.id, name="Engineering")
        db.add(eng)
        db.flush()
        backend = Team(company_id=company.id, department_id=eng.id, name="Backend")
        frontend = Team(company_id=company.id, department_id=eng.id, name="Frontend")
        db.add_all([backend, frontend])
        db.flush()

        emps = [
            Employee(company_id=company.id, team_id=backend.id, name="Asha Rao", title="Backend Developer",
                     skills="Python,FastAPI,PostgreSQL", experience_years=3, capacity_hours=40,
                     availability_pct=100, hourly_cost=800),
            Employee(company_id=company.id, team_id=backend.id, name="Rahul Menon", title="Data Engineer",
                     skills="Python,Pandas,SQL", experience_years=4, capacity_hours=40,
                     availability_pct=90, hourly_cost=900),
            Employee(company_id=company.id, team_id=frontend.id, name="Priya Nair", title="Frontend Developer",
                     skills="React,CSS", experience_years=2, capacity_hours=40,
                     availability_pct=100, hourly_cost=700),
            Employee(company_id=company.id, team_id=frontend.id, name="Karthik S", title="UI Designer",
                     skills="Figma,CSS", experience_years=5, capacity_hours=30,
                     availability_pct=80, hourly_cost=750),
        ]
        db.add_all(emps)
        db.flush()

        # (name, budget, start offset, deadline offset, scope, progress,
        #  tasks [(title, hours, employee index, done)], expenses [(desc, amount, day offset)])
        spec = [
            ("Mobile Banking Revamp", 1_200_000, -60, 45, 120, 55,
             [("API gateway", 80, 0, True), ("Auth flow", 40, 0, False),
              ("Dashboard UI", 120, 2, False), ("Load testing", 60, 1, False)],
             [("Cloud hosting", 150_000, -40), ("Licences", 60_000, -20)]),
            ("Customer Portal", 800_000, -30, 20, 80, 30,
             [("Portal pages", 200, 2, False), ("Payment integration", 150, 0, False),
              ("Notifications", 90, 1, False), ("QA", 100, 3, False)],
             [("Design tools", 40_000, -25)]),
            ("Data Warehouse Migration", 1_500_000, -90, 120, 200, 40,
             [("Schema design", 60, 1, True), ("ETL pipelines", 260, 1, False),
              ("Reporting views", 120, 0, False)],
             [("Cloud compute", 320_000, -30), ("Consultants", 180_000, -10)]),
        ]

        for name, budget, s_off, d_off, scope, progress, tasks, expenses in spec:
            proj = Project(company_id=company.id, name=name, budget=budget,
                           start_date=today + timedelta(days=s_off),
                           deadline=today + timedelta(days=d_off),
                           scope_units=scope, progress=progress)
            db.add(proj)
            db.flush()
            for title, hours, idx, done in tasks:
                db.add(Task(project_id=proj.id, title=title, estimated_hours=hours,
                            assignee_id=emps[idx].id, done=done))
            for desc, amount, off in expenses:
                db.add(Expense(project_id=proj.id, description=desc, amount=amount,
                               incurred_on=today + timedelta(days=off)))

        db.commit()
        print("Seeded demo company. Login: admin@demo.com / Admin@123")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
