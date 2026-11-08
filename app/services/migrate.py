"""Adds the owner_id column to tables created before ownership existed. Safe to run every start."""
from sqlalchemy import inspect, text

from app.db import engine

TABLES = ["projects", "departments", "teams", "employees"]


def ensure_owner_columns() -> None:
    insp = inspect(engine)
    existing = set(insp.get_table_names())
    for table in TABLES:
        if table not in existing:
            continue
        columns = {c["name"] for c in insp.get_columns(table)}
        if "owner_id" not in columns:
            with engine.begin() as conn:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN owner_id INTEGER"))
