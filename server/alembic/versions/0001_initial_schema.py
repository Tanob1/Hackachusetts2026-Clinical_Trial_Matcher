"""Initial schema: auth schema, medical schema, trials, saved_trials.

Revision ID: 0001_initial
Revises:
Create Date: 2026-10-24

Creates two separate schemas:
  auth   — user identity, refresh tokens
  medical — PHI (medical profiles), linked by internal UUID
  public — clinical trials, saved trials
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, Enum

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Enum types
trial_status_enum = sa.Enum(
    "recruiting", "active", "completed", "not_yet_recruiting",
    "terminated", "withdrawn", "unknown",
    name="trialstatus",
)
sex_enum = sa.Enum(
    "male", "female", "intersex", "prefer_not_to_answer",
    name="sexassignedatbirth",
)
smoking_enum = sa.Enum("never", "former", "current", name="smokingstatus")
alcohol_enum = sa.Enum("none", "occasional", "moderate", "heavy", name="alcoholuse")
pregnancy_enum = sa.Enum(
    "not_pregnant", "pregnant", "unsure", "not_applicable",
    name="pregnancystatus",
)


def upgrade() -> None:
    # Create schemas
    op.execute("CREATE SCHEMA IF NOT EXISTS auth")
    op.execute("CREATE SCHEMA IF NOT EXISTS medical")

    # ── auth.users ───────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(255), unique=True, nullable=True),
        sa.Column("phone", sa.String(20), unique=True, nullable=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("age", sa.Integer, nullable=True),
        sa.Column("sex_assigned_at_birth", sex_enum, nullable=True),
        sa.Column("location_text", sa.String(255), nullable=True),
        sa.Column("latitude", sa.Float, nullable=True),
        sa.Column("longitude", sa.Float, nullable=True),
        sa.Column("fcm_token", sa.String(255), nullable=True),
        sa.Column("notifications_enabled", sa.Boolean, server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="auth",
    )
    op.create_index("ix_auth_users_email", "users", ["email"], schema="auth")
    op.create_index("ix_auth_users_phone", "users", ["phone"], schema="auth")

    # ── auth.refresh_tokens ──────────────────────────────────────────────────
    op.create_table(
        "refresh_tokens",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token", sa.String(512), unique=True, nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked", sa.Boolean, server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="auth",
    )
    op.create_index("ix_auth_refresh_tokens_token", "refresh_tokens", ["token"], schema="auth")

    # ── medical.medical_profiles ──────────────────────────────────────────────
    op.create_table(
        "medical_profiles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("conditions", JSONB, server_default=sa.text("'[]'"), nullable=False),
        sa.Column("medications", JSONB, server_default=sa.text("'[]'"), nullable=False),
        sa.Column("allergies", JSONB, server_default=sa.text("'[]'"), nullable=False),
        sa.Column("medical_history", sa.Text, nullable=True),
        sa.Column("biomarkers", sa.Text, nullable=True),
        sa.Column("smoking_status", smoking_enum, nullable=True),
        sa.Column("alcohol_use", alcohol_enum, nullable=True),
        sa.Column("pregnancy_status", pregnancy_enum, nullable=True),
        sa.Column("travel_radius_miles", sa.Integer, server_default=sa.text("50"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="medical",
    )
    op.create_index("ix_medical_profiles_user_id", "medical_profiles", ["user_id"], schema="medical")

    # ── public.trials ─────────────────────────────────────────────────────────
    op.create_table(
        "trials",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("nct_id", sa.String(20), unique=True, nullable=False),
        sa.Column("title", sa.Text, nullable=False),
        sa.Column("brief_summary", sa.Text, nullable=True),
        sa.Column("detailed_description", sa.Text, nullable=True),
        sa.Column("phase", sa.String(50), nullable=True),
        sa.Column("conditions", JSONB, server_default=sa.text("'[]'"), nullable=False),
        sa.Column("keywords", JSONB, server_default=sa.text("'[]'"), nullable=False),
        sa.Column("sponsor", sa.String(500), nullable=True),
        sa.Column("locations", JSONB, server_default=sa.text("'[]'"), nullable=False),
        sa.Column("eligibility_inclusion", sa.Text, nullable=True),
        sa.Column("eligibility_exclusion", sa.Text, nullable=True),
        sa.Column("eligibility_sex", sa.String(50), nullable=True),
        sa.Column("eligibility_min_age", sa.String(50), nullable=True),
        sa.Column("eligibility_max_age", sa.String(50), nullable=True),
        sa.Column("enrollment_status", trial_status_enum, server_default=sa.text("'unknown'"), nullable=False),
        sa.Column("contact_name", sa.String(500), nullable=True),
        sa.Column("contact_phone", sa.String(100), nullable=True),
        sa.Column("contact_email", sa.String(255), nullable=True),
        sa.Column("url", sa.String(1000), nullable=True),
        sa.Column("last_updated", sa.DateTime(timezone=True), nullable=True),
        sa.Column("synced_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="public",
    )
    op.create_index("ix_public_trials_nct_id", "trials", ["nct_id"], schema="public")

    # ── public.saved_trials ──────────────────────────────────────────────────
    op.create_table(
        "saved_trials",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("auth.users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("trial_id", UUID(as_uuid=True), sa.ForeignKey("public.trials.id", ondelete="CASCADE"), nullable=False),
        sa.Column("interested", sa.Boolean, server_default=sa.text("false"), nullable=False),
        sa.Column("last_known_status", trial_status_enum, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        schema="public",
    )
    op.create_index("ix_public_saved_trials_user_id", "saved_trials", ["user_id"], schema="public")


def downgrade() -> None:
    op.drop_table("saved_trials", schema="public")
    op.drop_table("trials", schema="public")
    op.drop_table("medical_profiles", schema="medical")
    op.drop_table("refresh_tokens", schema="auth")
    op.drop_table("users", schema="auth")
    op.execute("DROP SCHEMA IF EXISTS medical CASCADE")
    op.execute("DROP SCHEMA IF EXISTS auth CASCADE")

    trial_status_enum.drop(op.get_bind(), checkfirst=False)
    sex_enum.drop(op.get_bind(), checkfirst=False)
    smoking_enum.drop(op.get_bind(), checkfirst=False)
    alcohol_enum.drop(op.get_bind(), checkfirst=False)
    pregnancy_enum.drop(op.get_bind(), checkfirst=False)
