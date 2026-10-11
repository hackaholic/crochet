"""add_product_information_and_defaults

Revision ID: d1e2f3a4b5c6
Revises: c1d2e3f4a5b6
Create Date: 2026-10-11 11:30:00.000000

"""
from datetime import datetime, timezone
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1e2f3a4b5c6'
down_revision: Union[str, Sequence[str], None] = 'c1d2e3f4a5b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add six product information columns to products table
    with op.batch_alter_table("products", schema=None) as batch_op:
        batch_op.add_column(sa.Column("handmade_details", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("materials_used", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("size_dimensions", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("processing_time", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("care_instructions", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("shipping_delivery", sa.Text(), nullable=True))

    # 2. Create product_information_defaults table
    op.create_table(
        "product_information_defaults",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("handmade_details", sa.Text(), nullable=True),
        sa.Column("materials_used", sa.Text(), nullable=True),
        sa.Column("size_dimensions", sa.Text(), nullable=True),
        sa.Column("processing_time", sa.Text(), nullable=True),
        sa.Column("care_instructions", sa.Text(), nullable=True),
        sa.Column("shipping_delivery", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )

    # 3. Seed initial factual default copy (DEC019-3: honest templates without unverified blanket claims)
    defaults_table = sa.table(
        "product_information_defaults",
        sa.column("id", sa.Integer),
        sa.column("handmade_details", sa.Text),
        sa.column("materials_used", sa.Text),
        sa.column("size_dimensions", sa.Text),
        sa.column("processing_time", sa.Text),
        sa.column("care_instructions", sa.Text),
        sa.column("shipping_delivery", sa.Text),
        sa.column("updated_at", sa.DateTime),
    )

    now_utc = datetime.now(timezone.utc)
    op.bulk_insert(
        defaults_table,
        [
            {
                "id": 1,
                "handmade_details": "Handcrafted with traditional crochet techniques. Each piece is made by hand with attention to detail; subtle variations are natural and make each item unique.",
                "materials_used": "Quality yarn and secure stitching tailored for crochet heirlooms.",
                "size_dimensions": "Dimensions vary by design; please refer to the product specifications.",
                "processing_time": "Standard handcrafted orders ship within 3–5 business days. Custom pieces may require additional preparation time.",
                "care_instructions": "Gently spot clean or dust with a dry soft cloth. Keep away from excessive moisture and direct prolonged sunlight.",
                "shipping_delivery": "Delivered across India via standard courier partners. Tracking details are shared upon dispatch.",
                "updated_at": now_utc,
            }
        ],
    )


def downgrade() -> None:
    op.drop_table("product_information_defaults")
    with op.batch_alter_table("products", schema=None) as batch_op:
        batch_op.drop_column("shipping_delivery")
        batch_op.drop_column("care_instructions")
        batch_op.drop_column("processing_time")
        batch_op.drop_column("size_dimensions")
        batch_op.drop_column("materials_used")
        batch_op.drop_column("handmade_details")
