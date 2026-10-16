"""Add width, height, and content_type columns to product_images table.

Revision ID: c4d5e6f7a8b9
Revises: b3a4c5d6e7f8
Create Date: 2026-10-14 16:20:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = 'c4d5e6f7a8b9'
down_revision = 'b3a4c5d6e7f8'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('product_images', sa.Column('width', sa.Integer(), nullable=True))
    op.add_column('product_images', sa.Column('height', sa.Integer(), nullable=True))
    op.add_column('product_images', sa.Column('content_type', sa.String(length=50), nullable=True))


def downgrade():
    op.drop_column('product_images', 'content_type')
    op.drop_column('product_images', 'height')
    op.drop_column('product_images', 'width')
