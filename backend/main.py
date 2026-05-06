"""
AutoJustice AI NEXUS - FastAPI Application Entry Point
AI-Driven Digital Forensics & Automated Threat Triage Platform
"""
import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse

sys.path.insert(0, str(Path(__file__).parent))

from database import engine, Base, SessionLocal
from routers import reports, dashboard
from routers.auth import router as auth_router, ensure_default_admin
from routers.cases import router as cases_router
from routers.digilocker import router as digilocker_router
from middleware.rate_limiter import RateLimiterMiddleware
from config import settings

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ─── Application Lifespan ─────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 60)
    logger.info(f"  {settings.app_name} v{settings.app_version}")
    logger.info("  Initializing database schema...")
    Base.metadata.create_all(bind=engine)

    # Create default admin account if no officers exist
    db = SessionLocal()
    try:
        ensure_default_admin(db)
    finally:
        db.close()

    logger.info("  Database ready.")
    logger.info(f"  Station: {settings.station_name}")
    logger.info(f"  Rate limiting: {'enabled' if settings.rate_limit_enabled else 'disabled'}")
    logger.info("=" * 60)
    yield
    logger.info("AutoJustice AI NEXUS shutting down.")


# ─── FastAPI App ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="AutoJustice AI NEXUS",
    description=(
        "AI-Driven Digital Forensics & Automated Threat Triage Platform for Law Enforcement. "
        "Powered by Google Gemini + Tesseract OCR. "
        "Section 65B | BNS 2023 | DPDP Act 2023 Compliant."
    ),
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# ─── Middleware ───────────────────────────────────────────────────────────────
app.add_middleware(RateLimiterMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # Restrict to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Static Files & Templates ─────────────────────────────────────────────────
BACKEND_DIR = Path(__file__).parent
STATIC_DIR = BACKEND_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)
(STATIC_DIR / "css").mkdir(exist_ok=True)
(STATIC_DIR / "js").mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(BACKEND_DIR / "templates"))

# ─── API Routers ──────────────────────────────────────────────────────────────
app.include_router(auth_router,       prefix="/api/auth",       tags=["Authentication"])
app.include_router(reports.router,    prefix="/api/reports",    tags=["Reports"])
app.include_router(dashboard.router,  prefix="/api/dashboard",  tags=["Dashboard"])
app.include_router(cases_router,      prefix="/api/cases",      tags=["Case Management"])
app.include_router(digilocker_router, prefix="/api/digilocker", tags=["DigiLocker Identity"])


# ─── Frontend Routes ──────────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
async def citizen_portal(request: Request):
    """Citizen evidence submission portal."""
    return templates.TemplateResponse(
        request=request,
        name="citizen_portal.html",
        context={"station_name": settings.station_name},
    )


@app.get("/dashboard", include_in_schema=False)
async def police_dashboard(request: Request):
    """Police command dashboard."""
    return templates.TemplateResponse(
        request=request,
        name="police_dashboard.html",
        context={"station_name": settings.station_name},
    )


@app.get("/track", include_in_schema=False)
@app.get("/track/{case_number}", include_in_schema=False)
async def track_case(request: Request, case_number: str = ""):
    """Citizen case tracking page."""
    return templates.TemplateResponse(
        request=request,
        name="case_tracking.html",
        context={"case_number": case_number, "station_name": settings.station_name},
    )


@app.get("/login", include_in_schema=False)
async def login_page(request: Request):
    """Officer login page."""
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"station_name": settings.station_name},
    )


# ─── Health Check ─────────────────────────────────────────────────────────────
@app.get("/api/health", tags=["System"])
async def health_check():
    return {
        "status": "operational",
        "system": settings.app_name,
        "version": settings.app_version,
        "station": settings.station_name,
    }


# ─── Global Error Handler ─────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error. Please contact system administrator."},
    )
