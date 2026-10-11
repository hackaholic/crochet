"""add_order_item_cost_and_admin_expenses

Revision ID: f3a4b5c6d7e8
Revises: e2f3a4b5c6d7
Create Date: 2026-10-11 18:30:00.000000

"""
from datetime import datetime, timezone
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f3a4b5c6d7e8'
down_revision: Union[str, Sequence[str], None] = 'e2f3a4b5c6d7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add unit_cost and total_cost columns to order_items table
    with op.batch_alter_table("order_items", schema=None) as batch_op:
        batch_op.add_column(sa.Column("unit_cost", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("total_cost", sa.Integer(), nullable=True))

    # 2. Create admin_expenses table
    op.create_table(
        "admin_expenses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("amount_paise", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False, server_default="INR"),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id", ondelete="SET NULL"), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("expense_date", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    with op.batch_alter_table("admin_expenses", schema=None) as batch_op:
        batch_op.create_index("ix_admin_expenses_category", ["category"], unique=False)
        batch_op.create_index("ix_admin_expenses_expense_date", ["expense_date"], unique=False)
        batch_op.create_index("ix_admin_expenses_order_id", ["order_id"], unique=False)


def downgrade() -> None:
    op.drop_table("admin_expenses")
    with op.batch_alter_table("order_items", schema=None) as batch_op:
        batch_op.drop_column("total_cost")
        batch_op.drop_column("unit_cost")
