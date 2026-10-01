"""Rebuild product taxonomy and add collections for launch.

Revision ID: d71c89f5a432
Revises: e9a1f7c3d280
Create Date: 2026-10-01

Conforms to docs/product-taxonomy.md:
- Creates `collections` and `product_collections` tables.
- Adds `image_key`, `show_when_empty`, `seo_title`, `seo_description`, `created_at`, `updated_at` to `categories`.
- Adds `is_primary` and `display_order` to `product_categories`.
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "d71c89f5a432"
down_revision = "e9a1f7c3d280"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Create collections table
    op.create_table(
        "collections",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False, unique=True, index=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("image_key", sa.String(length=500), nullable=True),
        sa.Column("collection_type", sa.String(length=50), nullable=False, server_default="MERCHANDISING"),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("starts_at", sa.DateTime(), nullable=True),
        sa.Column("ends_at", sa.DateTime(), nullable=True),
        sa.Column("seo_title", sa.String(length=255), nullable=True),
        sa.Column("seo_description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_collections_collection_type", "collections", ["collection_type"])
    op.create_index("ix_collections_is_active", "collections", ["is_active"])

    # 2. Create product_collections table
    op.create_table(
        "product_collections",
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("collection_id", sa.Integer(), sa.ForeignKey("collections.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
    )

    # 3. Add columns to categories
    with op.batch_alter_table("categories") as batch_op:
        batch_op.add_column(sa.Column("image_key", sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column("show_when_empty", sa.Boolean(), nullable=False, server_default="false"))
        batch_op.add_column(sa.Column("seo_title", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("seo_description", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("created_at", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("updated_at", sa.DateTime(), nullable=True))

    # 4. Add columns to product_categories
    with op.batch_alter_table("product_categories") as batch_op:
        batch_op.add_column(sa.Column("is_primary", sa.Boolean(), nullable=False, server_default="false"))
        batch_op.add_column(sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"))
        batch_op.create_index("ix_product_categories_is_primary", ["is_primary"])


def downgrade() -> None:
    with op.batch_alter_table("product_categories") as batch_op:
        batch_op.drop_index("ix_product_categories_is_primary")
        batch_op.drop_column("display_order")
        batch_op.drop_column("is_primary")

    with op.batch_alter_table("categories") as batch_op:
        batch_op.drop_column("updated_at")
        batch_op.drop_column("created_at")
        batch_op.drop_column("seo_description")
        batch_op.drop_column("seo_title")
        batch_op.drop_column("show_when_empty")
        batch_op.drop_column("image_key")

    op.drop_table("product_collections")
    op.drop_index("ix_collections_is_active", table_name="collections")
    op.drop_index("ix_collections_collection_type", table_name="collections")
    op.drop_table("collections")
