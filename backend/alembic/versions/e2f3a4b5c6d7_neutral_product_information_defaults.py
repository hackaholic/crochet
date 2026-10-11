"""Remove unconfirmed promises from untouched product information defaults."""
from alembic import op
import sqlalchemy as sa
revision = 'e2f3a4b5c6d7'
down_revision = 'd1e2f3a4b5c6'
branch_labels = None
depends_on = None

def upgrade():
    defaults_table = sa.table(
        'product_information_defaults',
        sa.column('processing_time', sa.Text),
        sa.column('shipping_delivery', sa.Text),
    )
    connection = op.get_bind()
    connection.execute(
        sa.update(defaults_table)
        .where(defaults_table.c.processing_time == 'Standard handcrafted orders ship within 3–5 business days. Custom pieces may require additional preparation time.')
        .values(processing_time='Processing time is confirmed for each order.')
    )
    connection.execute(
        sa.update(defaults_table)
        .where(defaults_table.c.shipping_delivery == 'Delivered across India via standard courier partners. Tracking details are shared upon dispatch.')
        .values(shipping_delivery='Shipping availability and delivery details are confirmed for each order.')
    )

def downgrade():
    # Do not restore unconfirmed claims or overwrite admin edits on downgrade.
    pass
