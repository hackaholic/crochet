"""add_search_events

Revision ID: a1b2c3d4e5f6
Revises: e1b2c3d4e5f6
Create Date: 2026-10-07 09:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'e1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'search_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('query', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('search_events', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_search_events_id'), ['id'], unique=False)
        batch_op.create_index(batch_op.f('ix_search_events_query'), ['query'], unique=False)
        batch_op.create_index(batch_op.f('ix_search_events_created_at'), ['created_at'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('search_events', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_search_events_created_at'))
        batch_op.drop_index(batch_op.f('ix_search_events_query'))
        batch_op.drop_index(batch_op.f('ix_search_events_id'))
    op.drop_table('search_events')
