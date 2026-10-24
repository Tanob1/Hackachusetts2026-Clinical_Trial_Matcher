"""Settings routes: profile, notifications, data export, delete account."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.database import get_db
from app.models import User, MedicalProfile, SavedTrial, RefreshToken
from app.schemas import (
    UserResponse, DataExportResponse, UpdateFCMTokenRequest,
    NotificationPreferenceRequest, MessageResponse,
)
from app.deps import get_current_user

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/export", response_model=DataExportResponse)
async def export_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export all user data (HIPAA-compliant data portability)."""
    # Medical profile
    profile_result = await db.execute(
        select(MedicalProfile).where(MedicalProfile.user_id == current_user.id)
    )
    profile = profile_result.scalar_one_or_none()

    # Saved trials
    saved_result = await db.execute(
        select(SavedTrial).where(SavedTrial.user_id == current_user.id)
    )
    saved = saved_result.scalars().all()

    return DataExportResponse(
        user={
            "id": str(current_user.id),
            "email": current_user.email,
            "phone": current_user.phone,
            "age": current_user.age,
            "sex_assigned_at_birth": current_user.sex_assigned_at_birth.value if current_user.sex_assigned_at_birth else None,
            "location_text": current_user.location_text,
        },
        medical_profile={
            "conditions": profile.conditions if profile else [],
            "medications": profile.medications if profile else [],
            "allergies": profile.allergies if profile else [],
            "medical_history": profile.medical_history if profile else None,
            "biomarkers": profile.biomarkers if profile else None,
            "smoking_status": profile.smoking_status.value if profile and profile.smoking_status else None,
            "alcohol_use": profile.alcohol_use.value if profile and profile.alcohol_use else None,
            "pregnancy_status": profile.pregnancy_status.value if profile and profile.pregnancy_status else None,
            "travel_radius_miles": profile.travel_radius_miles if profile else 50,
        } if profile else None,
        saved_trials=[
            {
                "id": str(s.id),
                "trial_id": str(s.trial_id),
                "interested": s.interested,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in saved
        ],
    )


@router.put("/fcm-token", response_model=MessageResponse)
async def update_fcm_token(
    req: UpdateFCMTokenRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Register or update the Firebase Cloud Messaging token."""
    current_user.fcm_token = req.fcm_token
    await db.commit()
    return MessageResponse(message="FCM token updated")


@router.put("/notifications", response_model=MessageResponse)
async def set_notification_preference(
    req: NotificationPreferenceRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Enable or disable push notifications."""
    current_user.notifications_enabled = req.notifications_enabled
    await db.commit()
    return MessageResponse(message="Notification preference updated")


@router.delete("/account", response_model=MessageResponse)
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Permanently delete the user's account and all associated data.

    This removes:
    - Medical profile (PHI)
    - Saved trials
    - Refresh tokens
    - The user record itself

    This action is irreversible.
    """
    # Delete medical profile
    await db.execute(
        delete(MedicalProfile).where(MedicalProfile.user_id == current_user.id)
    )
    # Delete saved trials
    await db.execute(
        delete(SavedTrial).where(SavedTrial.user_id == current_user.id)
    )
    # Delete refresh tokens
    await db.execute(
        delete(RefreshToken).where(RefreshToken.user_id == current_user.id)
    )
    # Delete user
    await db.delete(current_user)
    await db.commit()
    return MessageResponse(message="Account deleted")
