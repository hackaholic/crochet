"""case_insensitive_tag_uniqueness

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-10-09 23:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Safe data deduplication: handle existing data if duplicate tags with different casing exist
    conn = op.get_bind()

    # Query all tags to find any case duplicates
    tags_res = conn.execute(text("SELECT id, name FROM tags ORDER BY id ASC")).fetchall()
    canonical_map: dict[str, int] = {}  # lower_name -> canonical_id
    duplicate_ids: list[tuple[int, int]] = []  # [(duplicate_id, canonical_id)]

    for tag_id, name in tags_res:
        lower_name = name.lower()
        if lower_name not in canonical_map:
            canonical_map[lower_name] = tag_id
        else:
            duplicate_ids.append((tag_id, canonical_map[lower_name]))

    # For each duplicate tag, repoint product_tags references or delete conflicts
    for dup_id, canon_id in duplicate_ids:
        # Check product_tags pointing to dup_id
        # If product already has canon_id, delete the dup_id row to prevent composite PK conflict
        conn.execute(
            text("""
                DELETE FROM product_tags
                WHERE tag_id = :dup_id
                AND product_id IN (
                    SELECT product_id FROM product_tags WHERE tag_id = :canon_id
                )
            """),
            {"dup_id": dup_id, "canon_id": canon_id},
        )
        # For remaining rows pointing to dup_id, update them to canon_id
        conn.execute(
            text("UPDATE product_tags SET tag_id = :canon_id WHERE tag_id = :dup_id"),
            {"dup_id": dup_id, "canon_id": canon_id},
        )
        # Delete duplicate tag
        conn.execute(
            text("DELETE FROM tags WHERE id = :dup_id"),
            {"dup_id": dup_id},
        )

    # 2. Create functional unique index on lower(name)
    op.create_index(
        'uq_tags_name_lower',
        'tags',
        [sa.text('lower(name)')],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index('uq_tags_name_lower', table_name='tags')
