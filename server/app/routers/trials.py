"""Trial routes: matches, trial detail, save/unsave, saved list."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.database import get_db
from app.models import User, Trial, MedicalProfile, SavedTrial, TrialStatus
from app.schemas import (
    TrialSummary, TrialDetail, SavedTrialResponse, SaveTrialRequest,
    MessageResponse,
)
from app.deps import get_current_user
from app.matching import get_matches

router = APIRouter(tags=["trials"])


def trial_to_summary(trial: Trial, match_result=None) -> dict:
    """Convert Trial ORM to summary dict (optionally with match fields)."""
    data = {
        "id": trial.id,
        "nct_id": trial.nct_id,
        "title": trial.title,
        "phase": trial.phase,
        "conditions": trial.conditions,
        "sponsor": trial.sponsor,
        "locations": match_result.locations_with_distance if match_result else trial.locations,
        "eligibility_inclusion": trial.eligibility_inclusion,
        "eligibility_exclusion": trial.eligibility_exclusion,
        "enrollment_status": trial.enrollment_status.value if trial.enrollment_status else "unknown",
        "last_updated": trial.last_updated,
        "match_score": match_result.score if match_result else None,
        "match_strength": match_result.strength if match_result else None,
        "matched_conditions": match_result.matched_conditions if match_result else None,
        "nearest_distance_miles": match_result.nearest_distance_miles if match_result else None,
        "eligibility_summary": match_result.eligibility_summary if match_result else None,
    }
    return data


@router.get("/matches", response_model=list[TrialSummary])
async def get_user_matches(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get ranked clinical trials matching the user's profile.

    This is an informational matching tool â€” not a clinical recommendation.
    Final eligibility is always determined by the trial team.
    """
    # Get user's medical profile
    result = await db.execute(select(MedicalProfile).where(MedicalProfile.user_id == current_user.id))
    profile = result.scalar_one_or_none()
    if not profile or not profile.conditions:
        return []

    matches = await get_matches(db, current_user, profile, limit=limit)

    return [trial_to_summary(m.trial, m) for m in matches]


@router.get("/trials/{trial_id}", response_model=TrialDetail)
async def get_trial_detail(
    trial_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get full trial detail."""
    result = await db.execute(select(Trial).where(Trial.id == trial_id))
    trial = result.scalar_one_or_none()
    if not trial:
        raise HTTPException(status_code=404, detail="Trial not found")

    # Check if saved
    saved_result = await db.execute(
        select(SavedTrial).where(SavedTrial.user_id == current_user.id, SavedTrial.trial_id == trial_id)
    )
    saved = saved_result.scalar_one_or_none()

    return TrialDetail(
        id=trial.id,
        nct_id=trial.nct_id,
        title=trial.title,
        brief_summary=trial.brief_summary,
        detailed_description=trial.detailed_description,
        phase=trial.phase,
        conditions=trial.conditions,
        keywords=trial.keywords,
        sponsor=trial.sponsor,
        locations=trial.locations,
        eligibility_inclusion=trial.eligibility_inclusion,
        eligibility_exclusion=trial.eligibility_exclusion,
        eligibility_sex=trial.eligibility_sex,
        eligibility_min_age=trial.eligibility_min_age,
        eligibility_max_age=trial.eligibility_max_age,
        enrollment_status=trial.enrollment_status.value if trial.enrollment_status else "unknown",
        contact_name=trial.contact_name,
        contact_phone=trial.contact_phone,
        contact_email=trial.contact_email,
        url=trial.url,
        last_updated=trial.last_updated,
        is_saved=saved is not None,
        is_interested=saved.interested if saved else False,
    )


@router.post("/trials/{trial_id}/save", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def save_trial(
    trial_id: uuid.UUID,
    req: SaveTrialRequest = SaveTrialRequest(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Bookmark a trial (or mark 'interested')."""
    # Verify trial exists
    result = await db.execute(select(Trial).where(Trial.id == trial_id))
    trial = result.scalar_one_or_none()
    if not trial:
        raise HTTPException(status_code=404, detail="Trial not found")

    # Check if already saved
    existing = await db.execute(
        select(SavedTrial).where(SavedTrial.user_id == current_user.id, SavedTrial.trial_id == trial_id)
    )
    existing_save = existing.scalar_one_or_none()

    if existing_save:
        existing_save.interested = req.interested
        await db.commit()
        return MessageResponse(message="Updated")

    db.add(SavedTrial(
        user_id=current_user.id,
        trial_id=trial_id,
        interested=req.interested,
        last_known_status=trial.enrollment_status,
    ))
    await db.commit()
    return MessageResponse(message="Saved")


@router.delete("/trials/{trial_id}/save", response_model=MessageResponse)
async def unsave_trial(
    trial_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a bookmark."""
    await db.execute(
        delete(SavedTrial).where(
            SavedTrial.user_id == current_user.id,
            SavedTrial.trial_id == trial_id,
        )
    )
    await db.commit()
    return MessageResponse(message="Removed")


@router.get("/saved", response_model=list[SavedTrialResponse])
async def get_saved_trials(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List saved trials with status-change detection."""
    result = await db.execute(
        select(SavedTrial, Trial)
        .join(Trial, SavedTrial.trial_id == Trial.id)
        .where(SavedTrial.user_id == current_user.id)
        .order_by(SavedTrial.created_at.desc())
    )
    rows = result.all()

    saved_list = []
    for saved, trial in rows:
        status_changed = (
            saved.last_known_status is not None
            and trial.enrollment_status is not None
            and saved.last_known_status != trial.enrollment_status
        )

        # Update the last known status
        if status_changed:
            saved.last_known_status = trial.enrollment_status

        summary = trial_to_summary(trial)
        saved_list.append(SavedTrialResponse(
            id=saved.id,
            trial=summary,
            interested=saved.interested,
            last_known_status=saved.last_known_status.value if saved.last_known_status else None,
            status_changed=status_changed,
            created_at=saved.created_at,
        ))
    await db.commit()
    return saved_list


