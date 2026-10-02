"""add_return_requests

Revision ID: 7a1e2f3d4c5b
Revises: d71c89f5a432
Create Date: 2026-10-02 17:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '7a1e2f3d4c5b'
down_revision: Union[str, Sequence[str], None] = 'd71c89f5a432'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'return_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('return_number', sa.String(length=50), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('reason', sa.String(length=100), nullable=False),
        sa.Column('reason_details', sa.Text(), nullable=True),
        sa.Column('items_json', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
        sa.Column('refund_amount', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('refund_amount_paise', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('refund_status', sa.String(length=50), nullable=False, server_default='PENDING'),
        sa.Column('admin_notes', sa.Text(), nullable=True),
        sa.Column('history_json', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('return_requests', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_return_requests_id'), ['id'], unique=False)
        batch_op.create_index(batch_op.f('ix_return_requests_return_number'), ['return_number'], unique=True)
        batch_op.create_index(batch_op.f('ix_return_requests_order_id'), ['order_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_return_requests_user_id'), ['user_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_return_requests_status'), ['status'], unique=False)
        batch_op.create_index(batch_op.f('ix_return_requests_refund_status'), ['refund_status'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('return_requests', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_return_requests_refund_status'))
        batch_op.drop_index(batch_op.f('ix_return_requests_status'))
        batch_op.drop_index(batch_op.f('ix_return_requests_user_id'))
        batch_op.drop_index(batch_op.f('ix_return_requests_order_id'))
        batch_op.drop_index(batch_op.f('ix_return_requests_return_number'))
        batch_op.drop_index(batch_op.f('ix_return_requests_id'))
    op.drop_table('return_requests')
