"""Remove unconfirmed promises from untouched product information defaults."""
from alembic import op
import sqlalchemy as sa
revision = 'e2f3a4b5c6d7'
down_revision = 'd1e2f3a4b5c6'
branch_labels = None
depends_on = None

def upgrade():
    connection = op.get_bind()
    replacements = {
        'processing_time': ('Standard handcrafted orders ship within 3–5 business days. Custom pieces may require additional preparation time.', 'Processing time is confirmed for each order.'),
        'shipping_delivery': ('Delivered across India via standard courier partners. Tracking details are shared upon dispatch.', 'Shipping availability and delivery details are confirmed for each order.'),
    }
    for column, (old, new) in replacements.items():
        connection.execute(sa.text(f'UPDATE product_information_defaults SET {column} = :new WHERE {column} = :old'), {'new': new, 'old': old})

def downgrade():
    # Do not restore unconfirmed claims or overwrite admin edits on downgrade.
    pass
