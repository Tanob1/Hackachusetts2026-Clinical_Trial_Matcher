"""FastAPI application factory.

Clinical Trial Matcher — backend server.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.config import get_settings
from app.database import init_db, async_session
from app.routers import profile, trials, settings as settings_router, admin
from app.routers import sqlite_routes
from app.ctgov_sync import sync_trials

settings = get_settings()

# Configure logging — never log medical profile contents
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
# Suppress noisy libs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("apscheduler").setLevel(logging.INFO)
logger = logging.getLogger("name")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle: init DB + start scheduled sync."""
    logger.info("Starting Clinical Trial Matcher backend...")

    # Create tables (development — use Alembic in production)
    await init_db()

    # Start the ClinicalTrials.gov sync scheduler
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.cron import CronTrigger

    scheduler = AsyncIOScheduler()
    # Parse cron: "0 3 * * *" -> daily at 3 AM
    parts = settings.CTGOV_SYNC_CRON.split()
    if len(parts) == 5:
        trigger = CronTrigger(
            minute=parts[0], hour=parts[1], day=parts[2],
            month=parts[3], day_of_week=parts[4],
        )
        scheduler.add_job(
            scheduled_sync,
            trigger=trigger,
            id="ctgov_sync",
            replace_existing=True,
        )
        scheduler.start()
        logger.info(f"Sync scheduled: {settings.CTGOV_SYNC_CRON}")
        app.state.scheduler = scheduler

    yield

    # Shutdown
    if hasattr(app.state, "scheduler"):
        app.state.scheduler.shutdown(wait=False)
    logger.info("Backend shut down.")


async def scheduled_sync():
    """Run the ClinicalTrials.gov sync (called by scheduler)."""
    logger.info("Running scheduled ClinicalTrials.gov sync...")
    try:
        async with async_session() as db:
            count = await sync_trials(db, max_studies=5000)
        logger.info(f"Scheduled sync complete: {count} studies.")
    except Exception as e:
        logger.error(f"Scheduled sync failed: {e}")


app = FastAPI(
    title=settings.APP_NAME,
    description="Clinical trial matching backend. Pulls from ClinicalTrials.gov, stores user profiles securely, and runs a matching engine.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static web UI
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir, html=True), name="static")

# Web UI routes
@app.get("/web")
async def web_info():
    """Serve info page directing to Flask UI."""  
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "FastAPI server - visit /docs for API documentation"}

@app.get("/web/login")
async def web_login():
    """Serve the web login page."""
    login_path = os.path.join(static_dir, "login.html")
    if os.path.exists(login_path):
        return FileResponse(login_path)
    return {"error": "Login page not found"}
# Routers
# app.include_router(auth.router)  # TODO: Implement auth router
app.include_router(profile.router)
app.include_router(trials.router)
app.include_router(settings_router.router)
app.include_router(admin.router)
app.include_router(sqlite_routes.router)


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "docs": "/docs",
        "disclaimer": "This is an informational matching tool, not medical advice.",
    }





