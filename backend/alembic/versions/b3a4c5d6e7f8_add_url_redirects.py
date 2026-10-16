"""Add url_redirects table for canonical slug and alias lifecycle.

Revision ID: b3a4c5d6e7f8
Revises: a6b7c8d9e0f1
Create Date: 2026-10-14 14:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = 'b3a4c5d6e7f8'
down_revision = 'a6b7c8d9e0f1'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'url_redirects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('old_path', sa.String(length=500), nullable=False),
        sa.Column('target_path', sa.String(length=500), nullable=True),
        sa.Column('status_code', sa.Integer(), nullable=False, server_default='301'),
        sa.Column('entity_type', sa.String(length=50), nullable=True),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_url_redirects_id'), 'url_redirects', ['id'], unique=False)
    op.create_index(op.f('ix_url_redirects_old_path'), 'url_redirects', ['old_path'], unique=True)


def downgrade():
    op.drop_index(op.f('ix_url_redirects_old_path'), table_name='url_redirects')
    op.drop_index(op.f('ix_url_redirects_id'), table_name='url_redirects')
    op.drop_table('url_redirects')
