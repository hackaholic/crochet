"""Add magic_link_tokens table for V1 email magic link authentication.

Revision ID: e9a1f7c3d280
Revises: f5399f52930d
Create Date: 2026-10-01

Removes phone OTP as an auth method (V1 contract). Table otp_verifications is
preserved for historical records. magic_link_tokens is the new single-use
hashed token store for passwordless email sign-in.
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "e9a1f7c3d280"
down_revision = "f5399f52930d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "magic_link_tokens",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("email", sa.String(255), nullable=False, index=True),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True, index=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("is_used", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("used_at", sa.DateTime(), nullable=True),
    )
    op.create_index(
        "ix_magic_link_tokens_email_unused",
        "magic_link_tokens",
        ["email", "is_used"],
    )


def downgrade() -> None:
    op.drop_index("ix_magic_link_tokens_email_unused", table_name="magic_link_tokens")
    op.drop_table("magic_link_tokens")
