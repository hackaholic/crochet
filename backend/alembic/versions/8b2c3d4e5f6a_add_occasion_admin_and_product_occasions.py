"""add_occasion_admin_and_product_occasions

Revision ID: 8b2c3d4e5f6a
Revises: 7a1e2f3d4c5b
Create Date: 2026-10-02 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8b2c3d4e5f6a'
down_revision: Union[str, Sequence[str], None] = '7a1e2f3d4c5b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add new columns to occasions table
    with op.batch_alter_table('occasions', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image_key', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('description', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default=sa.true()))
        batch_op.add_column(sa.Column('starts_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('ends_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('updated_at', sa.DateTime(), nullable=True))
        batch_op.create_index(batch_op.f('ix_occasions_is_enabled'), ['is_enabled'], unique=False)
        batch_op.create_index(batch_op.f('ix_occasions_display_order'), ['display_order'], unique=False)

    # 2. Create product_occasions association table
    op.create_table(
        'product_occasions',
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('occasion_id', sa.String(length=50), nullable=False),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['occasion_id'], ['occasions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('product_id', 'occasion_id')
    )
    with op.batch_alter_table('product_occasions', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_product_occasions_product_id'), ['product_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_product_occasions_occasion_id'), ['occasion_id'], unique=False)


def downgrade() -> None:
    with op.batch_alter_table('product_occasions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_product_occasions_occasion_id'))
        batch_op.drop_index(batch_op.f('ix_product_occasions_product_id'))
    op.drop_table('product_occasions')

    with op.batch_alter_table('occasions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_occasions_display_order'))
        batch_op.drop_index(batch_op.f('ix_occasions_is_enabled'))
        batch_op.drop_column('updated_at')
        batch_op.drop_column('created_at')
        batch_op.drop_column('ends_at')
        batch_op.drop_column('starts_at')
        batch_op.drop_column('is_enabled')
        batch_op.drop_column('display_order')
        batch_op.drop_column('description')
        batch_op.drop_column('image_key')
