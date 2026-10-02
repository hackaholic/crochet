"""task_018_default_occasions_and_images

Revision ID: 9c3d4e5f6a7b
Revises: 8b2c3d4e5f6a
Create Date: 2026-10-03 03:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9c3d4e5f6a7b'
down_revision: Union[str, Sequence[str], None] = '8b2c3d4e5f6a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Update occasions default visibility, display order, and distinct Sulocraft assets
    # Exactly 5 enabled defaults: birthday (1), justbecause (2), anniversary (3), babyshower (4), wedding (5)
    # Remaining 8 disabled by default: valentine (6), decor (7), diwali (8), mother (9), father (10), rakhi (11), housewarming (12), christmas (13)
    occasions_updates = [
        ("birthday", True, 1, "occasions/birthday-gifting-v2.png"),
        ("justbecause", True, 2, "occasions/just-because-gifting.png"),
        ("anniversary", True, 3, "occasions/anniversary-gifting-v2.png"),
        ("babyshower", True, 4, "occasions/baby-shower-hamper.png"),
        ("wedding", True, 5, "occasions/wedding-gifting-v2.png"),
        ("valentine", False, 6, "occasions/valentine-couple-bunnies.png"),
        ("decor", False, 7, "occasions/decor-hanging-planter.png"),
        ("diwali", False, 8, "occasions/diwali-marigold-garland.png"),
        ("mother", False, 9, "occasions/mothers-day-rose-bouquet.png"),
        ("father", False, 10, "occasions/fathers-day-coaster-set.png"),
        ("rakhi", False, 11, "occasions/rakhi-gift-potli.png"),
        ("housewarming", False, 12, "occasions/housewarming-wall-hanging.png"),
        ("christmas", False, 13, "occasions/christmas-toran.png"),
    ]

    conn = op.get_bind()
    for occ_id, is_enabled, display_order, img_key in occasions_updates:
        conn.execute(
            sa.text(
                """
                UPDATE occasions
                SET is_enabled = :is_enabled,
                    display_order = :display_order,
                    image_key = :image_key,
                    image_url = :image_key
                WHERE id = :id
                """
            ),
            {
                "is_enabled": is_enabled,
                "display_order": display_order,
                "image_key": img_key,
                "id": occ_id,
            },
        )

    # 2. Add product associations for justbecause if missing
    justbecause_products = [12, 15, 5, 3]
    for idx, pid in enumerate(justbecause_products):
        conn.execute(
            sa.text(
                """
                INSERT INTO product_occasions (product_id, occasion_id, display_order)
                SELECT :pid, 'justbecause', :display_order
                WHERE EXISTS (SELECT 1 FROM products WHERE id = :pid)
                  AND NOT EXISTS (
                      SELECT 1 FROM product_occasions WHERE product_id = :pid AND occasion_id = 'justbecause'
                  )
                """
            ),
            {"pid": pid, "display_order": idx},
        )


def downgrade() -> None:
    pass
