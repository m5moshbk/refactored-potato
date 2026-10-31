"""Create initial Voice Nexus tables.

Revision ID: 0001_initial
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=True),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "voice_profiles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("fingerprint", sa.String(), nullable=False),
        sa.Column("model_version", sa.String(), nullable=True, server_default="v1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_voice_profiles_user_id", "voice_profiles", ["user_id"])

    op.create_table(
        "audio_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("file_name", sa.String(), nullable=False),
        sa.Column("transcript", sa.Text(), nullable=True),
        sa.Column("language", sa.String(), nullable=True, server_default="ar"),
        sa.Column("confidence", sa.Float(), nullable=True, server_default="0"),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_audio_records_user_id", "audio_records", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_audio_records_user_id", table_name="audio_records")
    op.drop_table("audio_records")
    op.drop_index("ix_voice_profiles_user_id", table_name="voice_profiles")
    op.drop_table("voice_profiles")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
