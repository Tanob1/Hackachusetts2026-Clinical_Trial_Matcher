"""Matching engine.

Filters and ranks clinical trials against a user's medical profile.
This is NOT clinical-grade eligibility screening — it surfaces relevant studies.
Final eligibility is always determined by the trial team.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Trial, MedicalProfile, User, TrialStatus, MatchStrength


@dataclass
class MatchResult:
    """Scored match for a single trial."""
    trial: Trial
    score: float
    strength: str
    matched_conditions: list[str]
    nearest_distance_miles: float | None
    eligibility_summary: str
    # locations with computed distance attached
    locations_with_distance: list[dict] = field(default_factory=list)


# ── Geolocation ────────────────────────────────────────────────────────────────

def haversine_miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in miles between two lat/lng points."""
    R = 3958.7613  # Earth radius in miles
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


# ── Age parsing ─────────────────────────────────────────────────────────────────

def parse_age_years(age_str: str | None) -> float | None:
    """Parse '18 Years' or 'N/A' into a numeric age. Returns None if unbounded."""
    if not age_str or age_str.strip().upper() in ("N/A", "", "NONE"):
        return None
    m = re.search(r"(\d+)", age_str)
    if not m:
        return None
    val = int(m.group(1))
    if "month" in age_str.lower():
        return val / 12.0
    return float(val)


# ── Text utilities ────────────────────────────────────────────────────────────

def tokenize(text: str | None) -> set[str]:
    """Lowercase alphanumeric token set from free text."""
    if not text:
        return set()
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def extract_eligibility_keywords(inclusion: str | None, exclusion: str | None) -> set[str]:
    """Pull medication/comorbidity/treatment keywords from eligibility text."""
    tokens = tokenize(inclusion) | tokenize(exclusion)
    # Filter out very common stop words to reduce noise
    stop = {
        "the", "and", "or", "of", "to", "in", "for", "with", "without", "a",
        "an", "is", "are", "be", "must", "have", "has", "who", "which", "that",
        "this", "all", "any", "no", "not", "but", "if", "than", "more", "less",
        "at", "by", "on", "as", "it", "they", "their", "been", "will", "may",
        "should", "can", "from", "during", "after", "before", "other", "these",
        "such", "including", "exclusion", "inclusion", "criteria", "key",
    }
    return {t for t in tokens if len(t) > 2 and t not in stop}


# ── Plain-language eligibility summary ────────────────────────────────────────

def summarize_eligibility(trial: Trial) -> str:
    """Produce a short plain-language summary of key eligibility criteria."""
    parts: list[str] = []
    if trial.eligibility_sex and trial.eligibility_sex != "All":
        parts.append(f"Seeking {trial.eligibility_sex.lower()} participants")
    if trial.eligibility_min_age and trial.eligibility_min_age.strip().upper() not in ("N/A", ""):
        parts.append(f"Minimum age: {trial.eligibility_min_age}")
    if trial.eligibility_max_age and trial.eligibility_max_age.strip().upper() not in ("N/A", ""):
        parts.append(f"Maximum age: {trial.eligibility_max_age}")
    if trial.conditions:
        parts.append(f"Conditions: {', '.join(trial.conditions[:3])}")
    if not parts and trial.eligibility_inclusion:
        # Fallback: first 200 chars of inclusion criteria
        parts.append(trial.eligibility_inclusion[:200] + ("..." if len(trial.eligibility_inclusion) > 200 else ""))
    return " | ".join(parts) if parts else "See full criteria for details."


# ── Scoring ───────────────────────────────────────────────────────────────────

def score_trial(
    trial: Trial,
    user_conditions: list[str],
    user_meds: list[str],
    user_age: int | None,
    user_sex: str | None,
    user_pregnancy: str | None,
    user_smoking: str | None,
    user_lat: float | None,
    user_lng: float | None,
    travel_radius: int,
) -> MatchResult | None:
    """Score a single trial. Returns None if it fails hard filters."""

    # ── Hard filter: condition overlap ──
    trial_condition_tokens = set()
    for c in trial.conditions:
        trial_condition_tokens.update(tokenize(c))
    user_condition_tokens = set()
    for c in user_conditions:
        user_condition_tokens.update(tokenize(c))
    overlap = trial_condition_tokens & user_condition_tokens
    if not overlap:
        return None  # No condition match at all

    matched_conditions = [c for c in trial.conditions if tokenize(c) & overlap]

    # ── Hard filter: geographic distance ──
    nearest_dist: float | None = None
    locations_with_dist: list[dict] = []
    if user_lat is not None and user_lng is not None:
        for loc in trial.locations:
            loc_copy = dict(loc)
            if loc.get("lat") is not None and loc.get("lng") is not None:
                dist = haversine_miles(user_lat, user_lng, loc["lat"], loc["lng"])
                loc_copy["distance_miles"] = round(dist, 1)
                if nearest_dist is None or dist < nearest_dist:
                    nearest_dist = dist
            locations_with_dist.append(loc_copy)
        if nearest_dist is not None and nearest_dist > travel_radius:
            return None  # Too far
    else:
        locations_with_dist = list(trial.locations)

    # ── Soft filter: age ──
    min_age = parse_age_years(trial.eligibility_min_age)
    max_age = parse_age_years(trial.eligibility_max_age)
    if user_age is not None:
        if min_age is not None and user_age < min_age:
            return None
        if max_age is not None and user_age > max_age:
            return None

    # ── Soft filter: sex ──
    if trial.eligibility_sex and trial.eligibility_sex != "All":
        if user_sex:
            user_sex_lower = user_sex.lower()
            trial_sex_lower = trial.eligibility_sex.lower()
            if trial_sex_lower == "female" and "female" not in user_sex_lower:
                return None
            if trial_sex_lower == "male" and "male" not in user_sex_lower:
                return None

    # ── Scoring ────────────────────────────────────────────────────────────────
    score = 0.0

    # 1. Condition match weight (highest)
    num_conditions_matched = len(matched_conditions)
    score += num_conditions_matched * 40.0
    # Bonus if ALL trial conditions are matched
    if len(matched_conditions) == len(trial.conditions) and len(trial.conditions) > 0:
        score += 15.0

    # 2. Proximity score (closer = higher)
    if nearest_dist is not None:
        if nearest_dist <= 10:
            score += 30.0
        elif nearest_dist <= 25:
            score += 25.0
        elif nearest_dist <= 50:
            score += 20.0
        elif nearest_dist <= 100:
            score += 10.0
        elif nearest_dist <= 250:
            score += 5.0

    # 3. Eligibility keyword overlap
    elig_keywords = extract_eligibility_keywords(trial.eligibility_inclusion, trial.eligibility_exclusion)
    user_meds_tokens = set()
    for m in user_meds:
        user_meds_tokens.update(tokenize(m))
    med_overlap = elig_keywords & user_meds_tokens
    score += len(med_overlap) * 5.0

    # 4. Trial status bonus — recruiting trials rank higher
    if trial.enrollment_status == TrialStatus.recruiting:
        score += 10.0
    elif trial.enrollment_status == TrialStatus.not_yet_recruiting:
        score += 5.0

    # Determine strength label
    if score >= 60:
        strength = MatchStrength.high.value
    elif score >= 30:
        strength = MatchStrength.medium.value
    else:
        strength = MatchStrength.low.value

    return MatchResult(
        trial=trial,
        score=score,
        strength=strength,
        matched_conditions=matched_conditions,
        nearest_distance_miles=round(nearest_dist, 1) if nearest_dist is not None else None,
        eligibility_summary=summarize_eligibility(trial),
        locations_with_distance=locations_with_dist,
    )


# ── Main entry point ──────────────────────────────────────────────────────────

async def get_matches(
    db: AsyncSession,
    user: User,
    profile: MedicalProfile,
    limit: int = 50,
) -> list[MatchResult]:
    """Get ranked trial matches for a user."""
    # Fetch all recruiting + active trials (broad query, filter down)
    result = await db.execute(
        select(Trial).where(
            Trial.enrollment_status.in_([
                TrialStatus.recruiting,
                TrialStatus.active,
                TrialStatus.not_yet_recruiting,
            ])
        )
    )
    all_trials = result.scalars().all()

    results: list[MatchResult] = []
    for trial in all_trials:
        match = score_trial(
            trial=trial,
            user_conditions=profile.conditions,
            user_meds=profile.medications,
            user_age=user.age,
            user_sex=user.sex_assigned_at_birth.value if user.sex_assigned_at_birth else None,
            user_pregnancy=profile.pregnancy_status.value if profile.pregnancy_status else None,
            user_smoking=profile.smoking_status.value if profile.smoking_status else None,
            user_lat=user.latitude,
            user_lng=user.longitude,
            travel_radius=profile.travel_radius_miles,
        )
        if match is not None:
            results.append(match)

    # Sort by score descending
    results.sort(key=lambda r: r.score, reverse=True)

    return results[:limit]
