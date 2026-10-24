"""Profile routes: get and update medical profile."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User, MedicalProfile
from app.schemas import MedicalProfileRequest, MedicalProfileResponse, MessageResponse
from app.deps import get_current_user

router = APIRouter(prefix="/profile", tags=["profile"])


async def _get_or_create_profile(user_id, db: AsyncSession) -> MedicalProfile:
    result = await db.execute(select(MedicalProfile).where(MedicalProfile.user_id == user_id))
    profile = result.scalar_one_or_none()
    if not profile:
        profile = MedicalProfile(user_id=user_id)
        db.add(profile)
        await db.flush()
    return profile


@router.get("", response_model=MedicalProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the current user's medical profile."""
    profile = await _get_or_create_profile(current_user.id, db)
    await db.commit()
    return MedicalProfileResponse(
        conditions=profile.conditions,
        medications=profile.medications,
        allergies=profile.allergies,
        medical_history=profile.medical_history,
        biomarkers=profile.biomarkers,
        smoking_status=profile.smoking_status.value if profile.smoking_status else None,
        alcohol_use=profile.alcohol_use.value if profile.alcohol_use else None,
        pregnancy_status=profile.pregnancy_status.value if profile.pregnancy_status else None,
        travel_radius_miles=profile.travel_radius_miles,
        updated_at=profile.updated_at,
    )


@router.put("", response_model=MedicalProfileResponse)
async def update_profile(
    req: MedicalProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update the current user's medical profile.

    ⚠️ This endpoint handles PHI. Data is stored in a separate schema.
    Profile contents are never logged.
    """
    profile = await _get_or_create_profile(current_user.id, db)

    # Update fields — do not log any of these values
    profile.conditions = req.conditions
    profile.medications = req.medications
    profile.allergies = req.allergies
    profile.medical_history = req.medical_history
    profile.biomarkers = req.biomarkers
    # Convert string enums to proper enum values
    from app.models import SmokingStatus, AlcoholUse, PregnancyStatus
    if req.smoking_status:
        try:
            profile.smoking_status = SmokingStatus(req.smoking_status)
        except ValueError:
            pass
    if req.alcohol_use:
        try:
            profile.alcohol_use = AlcoholUse(req.alcohol_use)
        except ValueError:
            pass
    if req.pregnancy_status:
        try:
            profile.pregnancy_status = PregnancyStatus(req.pregnancy_status)
        except ValueError:
            pass
    profile.travel_radius_miles = req.travel_radius_miles

    await db.commit()

    return MedicalProfileResponse(
        conditions=profile.conditions,
        medications=profile.medications,
        allergies=profile.allergies,
        medical_history=profile.medical_history,
        biomarkers=profile.biomarkers,
        smoking_status=profile.smoking_status.value if profile.smoking_status else None,
        alcohol_use=profile.alcohol_use.value if profile.alcohol_use else None,
        pregnancy_status=profile.pregnancy_status.value if profile.pregnancy_status else None,
        travel_radius_miles=profile.travel_radius_miles,
        updated_at=profile.updated_at,
    )
