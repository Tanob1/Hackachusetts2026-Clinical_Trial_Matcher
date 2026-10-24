"""Admin routes: manual sync trigger, health check."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db, async_session
from app.models import User
from app.schemas import MessageResponse
from app.deps import get_current_user
from app.ctgov_sync import sync_trials

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/sync", response_model=MessageResponse)
async def trigger_sync(current_user: User = Depends(get_current_user)):
    """Manually trigger a ClinicalTrials.gov sync (admin endpoint).

    This is a fire-and-forget trigger — the sync runs in the background.
    """
    async with async_session() as db:
        count = await sync_trials(db, max_studies=500)
    return MessageResponse(message=f"Sync complete: {count} studies synced")


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "trial-matcher-backend"}
