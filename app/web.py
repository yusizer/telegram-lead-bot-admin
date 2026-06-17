"""FastAPI admin panel: dashboard + lead management."""
from datetime import date
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import Date, cast, func, select
from starlette.middleware.sessions import SessionMiddleware

from .config import settings
from .database import SessionLocal, init_db
from .models import Lead

TEMPLATES_DIR = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

app = FastAPI(title="Lead Bot — Admin")
app.add_middleware(SessionMiddleware, secret_key=settings.session_secret)

VALID_STATUSES = {"new", "contacted", "closed"}


@app.on_event("startup")
async def _on_startup() -> None:
    """Make sure tables exist (also lets the admin run standalone)."""
    await init_db()


def is_admin(request: Request) -> bool:
    return request.session.get("admin") is True


# --- Auth -----------------------------------------------------------------

@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse(request, "login.html", {"error": None})


@app.post("/login")
async def login_submit(request: Request, password: str = Form(...)):
    if password == settings.admin_password:
        request.session["admin"] = True
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse(
        request, "login.html", {"error": "Неверный пароль"}
    )


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)


# --- Health (for Railway / uptime checks) ---------------------------------

@app.get("/health")
async def health():
    return {"status": "ok"}


# --- Dashboard ------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    if not is_admin(request):
        return RedirectResponse("/login", status_code=303)

    async with SessionLocal() as session:
        total = (await session.execute(select(func.count(Lead.id)))).scalar_one()
        today = date.today()
        today_count = (
            await session.execute(
                select(func.count(Lead.id)).where(
                    cast(Lead.created_at, Date) == today
                )
            )
        ).scalar_one()
        new = (
            await session.execute(
                select(func.count(Lead.id)).where(Lead.status == "new")
            )
        ).scalar_one()
        contacted = (
            await session.execute(
                select(func.count(Lead.id)).where(Lead.status == "contacted")
            )
        ).scalar_one()
        closed = (
            await session.execute(
                select(func.count(Lead.id)).where(Lead.status == "closed")
            )
        ).scalar_one()
        recent = (
            await session.execute(
                select(Lead).order_by(Lead.created_at.desc()).limit(10)
            )
        ).scalars().all()

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "stats": {
                "total": total,
                "today": today_count,
                "new": new,
                "contacted": contacted,
                "closed": closed,
            },
            "recent": recent,
        },
    )


# --- Leads ----------------------------------------------------------------

@app.get("/leads", response_class=HTMLResponse)
async def leads_list(request: Request, status: str | None = None):
    if not is_admin(request):
        return RedirectResponse("/login", status_code=303)

    query = select(Lead).order_by(Lead.created_at.desc())
    if status in VALID_STATUSES:
        query = query.where(Lead.status == status)
    async with SessionLocal() as session:
        rows = (await session.execute(query)).scalars().all()

    return templates.TemplateResponse(
        request,
        "leads.html",
        {"leads": rows, "current": status, "statuses": sorted(VALID_STATUSES)},
    )


@app.post("/leads/{lead_id}/status")
async def lead_update_status(
    request: Request, lead_id: int, status: str = Form(...)
):
    if not is_admin(request):
        return RedirectResponse("/login", status_code=303)
    if status not in VALID_STATUSES:
        return RedirectResponse("/leads", status_code=303)

    async with SessionLocal() as session:
        lead = await session.get(Lead, lead_id)
        if lead:
            lead.status = status
            await session.commit()

    return RedirectResponse("/leads", status_code=303)
