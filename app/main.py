import jwt
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401  (registers tables)
from app.db import Base, engine
from app.config import settings
from app.routers import activity, analytics, assistant, auth, core, creative, deadlines, integrations, memory, reports, smart, users, workspace
from app.services.activity import LOGGED_PREFIXES, record

Base.metadata.create_all(bind=engine)
from app.services.migrate import ensure_owner_columns
ensure_owner_columns()  # MVP: create tables on start. Use Alembic later.

app = FastAPI(title="StratifyIQ API", version="1.0.0",
              description="AI-powered enterprise decision intelligence platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(core.router)
app.include_router(analytics.router)
app.include_router(assistant.router)
app.include_router(reports.router)
app.include_router(activity.router)
app.include_router(users.router)
app.include_router(creative.router)
app.include_router(memory.router)
app.include_router(workspace.router)
app.include_router(deadlines.router)
app.include_router(smart.router)
app.include_router(integrations.router)


WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


@app.middleware("http")
async def audit_changes(request: Request, call_next):
    """Records every successful change to company data in the activity log."""
    response = await call_next(request)
    path = request.url.path
    if request.method in WRITE_METHODS and response.status_code < 300 and path.startswith(LOGGED_PREFIXES):
        token = request.headers.get("authorization", "").removeprefix("Bearer ").strip()
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            record(int(payload["sub"]), request.method, path)
        except Exception:
            pass  # unauthenticated or unknown requests are simply not logged
    return response


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok"}
