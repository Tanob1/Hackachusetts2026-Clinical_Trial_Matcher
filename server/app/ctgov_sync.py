"""ClinicalTrials.gov v2 API sync job.

Pulls studies, normalizes them, and stores them in the database.
Designed to run on a schedule (daily) via APScheduler.
"""
from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import Trial, TrialStatus

logger = logging.getLogger(__name__)
settings = get_settings()


# ── Age parsing helpers ────────────────────────────────────────────────────────

def parse_min_age(age_str: str | None) -> str | None:
    """Normalize '18 Years' -> '18 Years' (pass through)."""
    if not age_str or age_str.upper() == "N/A":
        return None
    return age_str


def parse_max_age(age_str: str | None) -> str | None:
    if not age_str or age_str.upper() == "N/A":
        return None
    return age_str


# ── Status mapping ────────────────────────────────────────────────────────────

def map_status(raw_status: str | None) -> TrialStatus:
    """Map ClinicalTrials.gov status to our TrialStatus enum."""
    if not raw_status:
        return TrialStatus.unknown
    s = raw_status.upper().strip()
    mapping = {
        "RECRUITING": TrialStatus.recruiting,
        "ACTIVE_NOT_RECRUITING": TrialStatus.active,
        "COMPLETED": TrialStatus.completed,
        "NOT_YET_RECRUITING": TrialStatus.not_yet_recruiting,
        "TERMINATED": TrialStatus.terminated,
        "WITHDRAWN": TrialStatus.withdrawn,
    }
    return mapping.get(s, TrialStatus.unknown)


# ── Study normalization ──────────────────────────────────────────────────────

def normalize_study(study: dict[str, Any]) -> dict | None:
    """Convert a raw ClinicalTrials.gov v2 study record to our normalized dict."""
    try:
        protocol = study.get("protocolSection", {})
        status_module = protocol.get("statusModule", {})
        description_module = protocol.get("descriptionModule", {})
        conditions_module = protocol.get("conditionsModule", {})
        sponsor_module = protocol.get("sponsorCollaboratorsModule", {})
        design_module = protocol.get("designModule", {})
        locations_module = protocol.get("locationsModule", {})
        eligibility_module = protocol.get("eligibilityModule", {})
        contacts_module = protocol.get("contactsLocationsModule", {})

        nct_id = study.get("nctId") or protocol.get("identificationModule", {}).get("nctId")
        if not nct_id:
            return None

        identification = protocol.get("identificationModule", {})
        title = identification.get("officialTitle") or identification.get("briefTitle", "")

        # Phase
        phases = design_module.get("phases", [])
        phase = ", ".join(phases) if phases else None

        # Conditions
        conditions = conditions_module.get("conditions", [])
        keywords = conditions_module.get("keywords", [])

        # Sponsor
        sponsor = sponsor_module.get("leadSponsor", {}).get("name")

        # Summary / description
        brief_summary = description_module.get("briefSummary")
        detailed_description = description_module.get("detailedDescription")

        # Locations
        raw_locations = locations_module.get("locations", [])
        locations = []
        for loc in raw_locations:
            locations.append({
                "city": loc.get("city"),
                "state": loc.get("state"),
                "country": loc.get("country"),
                "facility": loc.get("facility", ""),
                "lat": None,   # ClinicalTrials.gov v2 doesn't always provide lat/lng
                "lng": None,   # We geocode separately if needed
                "status": loc.get("status"),
            })

        # Eligibility
        eligibility_inclusion = eligibility_module.get("eligibilityCriteria", "")
        # Split inclusion / exclusion — ClinicalTrials.gov puts them in one text block
        inclusion_text = eligibility_inclusion
        exclusion_text = None
        if eligibility_inclusion and "Exclusion Criteria" in eligibility_inclusion:
            parts = eligibility_inclusion.split("Exclusion Criteria", 1)
            inclusion_text = parts[0].replace("Inclusion Criteria", "").strip("- :\n")
            exclusion_text = parts[1].strip("- :\n") if len(parts) > 1 else None

        # Sex
        eligibility_sex = eligibility_module.get("sex")
        min_age = eligibility_module.get("minimumAge")
        max_age = eligibility_module.get("maximumAge")

        # Contacts
        contact_name = None
        contact_phone = None
        contact_email = None
        central_contact = contacts_module.get("centralContact")
        if central_contact:
            contact_name = central_contact.get("name")
            contact_phone = central_contact.get("phone")
            contact_email = central_contact.get("email")

        # Status
        enrollment_status = map_status(status_module.get("overallStatus"))

        # Last update
        last_updated_str = status_module.get("lastUpdateSubmitDate")
        last_updated = None
        if last_updated_str:
            for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"):
                try:
                    last_updated = datetime.strptime(last_updated_str, fmt).replace(tzinfo=timezone.utc)
                    break
                except ValueError:
                    continue

        return {
            "nct_id": nct_id,
            "title": title.strip() if title else nct_id,
            "brief_summary": brief_summary,
            "detailed_description": detailed_description,
            "phase": phase,
            "conditions": conditions,
            "keywords": keywords,
            "sponsor": sponsor,
            "locations": locations,
            "eligibility_inclusion": inclusion_text,
            "eligibility_exclusion": exclusion_text,
            "eligibility_sex": eligibility_sex,
            "eligibility_min_age": parse_min_age(min_age),
            "eligibility_max_age": parse_max_age(max_age),
            "enrollment_status": enrollment_status,
            "contact_name": contact_name,
            "contact_phone": contact_phone,
            "contact_email": contact_email,
            "url": f"https://clinicaltrials.gov/study/{nct_id}",
            "last_updated": last_updated,
        }
    except Exception as e:
        logger.error(f"Failed to normalize study {study.get('nctId', 'unknown')}: {e}")
        return None


# ── Geocoding (optional, lightweight) ─────────────────────────────────────────

async def geocode_location(city: str | None, state: str | None) -> tuple[float | None, float | None]:
    """Best-effort geocoding using Nominatim (OpenStreetMap). Returns (lat, lng)."""
    if not city and not state:
        return None, None
    query_parts = [p for p in [city, state] if p]
    query = ", ".join(query_parts)
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": query, "format": "json", "limit": 1},
                headers={"User-Agent": "trial-matcher-sync/1.0"},
                timeout=10,
            )
            if resp.status_code == 200 and resp.json():
                data = resp.json()[0]
                return float(data["lat"]), float(data["lng"])
    except Exception as e:
        logger.debug(f"Geocoding failed for {query}: {e}")
    return None, None


# ── User location geocoding ────────────────────────────────────────────────────

async def geocode_user_location(location_text: str) -> tuple[float | None, float | None]:
    """Geocode a user's location text (city/state or ZIP)."""
    return await geocode_location(None, location_text)


# ── Main sync ─────────────────────────────────────────────────────────────────

async def sync_trials(
    db: AsyncSession,
    batch_size: int | None = None,
    max_studies: int = 5000,
) -> int:
    """Pull studies from ClinicalTrials.gov and upsert into the database.

    Returns count of studies synced.
    """
    batch_size = batch_size or settings.CTGOV_SYNC_BATCH_SIZE
    total_synced = 0
    page_token = None

    async with httpx.AsyncClient(timeout=60) as client:
        while total_synced < max_studies:
            params: dict[str, Any] = {
                "pageSize": str(batch_size),
                "format": "json",
                # Only sync studies that are in a relevant status
                "filter.overallStatus": "RECRUITING,ACTIVE_NOT_RECRUITING,NOT_YET_RECRUITING,COMPLETED",
            }
            if page_token:
                params["pageToken"] = page_token

            try:
                resp = await client.get(
                    f"{settings.CTGOV_API_BASE}/studies",
                    params=params,
                )
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                logger.error(f"Failed to fetch from ClinicalTrials.gov: {e}")
                break

            studies = data.get("studies", [])
            if not studies:
                break

            for study in studies:
                normalized = normalize_study(study)
                if not normalized:
                    continue

                # Check if trial already exists
                existing = await db.execute(
                    select(Trial).where(Trial.nct_id == normalized["nct_id"])
                )
                existing_trial = existing.scalar_one_or_none()

                if existing_trial:
                    # Update existing trial
                    for key, value in normalized.items():
                        setattr(existing_trial, key, value)
                    existing_trial.synced_at = datetime.now(timezone.utc)
                else:
                    # Create new trial
                    trial = Trial(**normalized)
                    db.add(trial)

                total_synced += 1

            await db.commit()
            logger.info(f"Synced {total_synced} studies so far...")

            page_token = data.get("nextPageToken")
            if not page_token:
                break

    logger.info(f"Sync complete: {total_synced} studies synced.")
    return total_synced
