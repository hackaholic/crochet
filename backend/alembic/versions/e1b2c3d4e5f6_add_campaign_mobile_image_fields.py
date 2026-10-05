"""add_campaign_mobile_image_fields

Revision ID: e1b2c3d4e5f6
Revises: 9c3d4e5f6a7b
Create Date: 2026-10-06 01:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'e1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '9c3d4e5f6a7b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: add mobile_image_url and mobile_image_position to homepage_campaigns."""
    with op.batch_alter_table('homepage_campaigns', schema=None) as batch_op:
        batch_op.add_column(sa.Column('mobile_image_url', sa.String(length=500), nullable=True))
        batch_op.add_column(
            sa.Column(
                'mobile_image_position',
                sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'),
                nullable=True,
            )
        )


def downgrade() -> None:
    """Downgrade schema: remove mobile_image_position and mobile_image_url from homepage_campaigns."""
    with op.batch_alter_table('homepage_campaigns', schema=None) as batch_op:
        batch_op.drop_column('mobile_image_position')
        batch_op.drop_column('mobile_image_url')
