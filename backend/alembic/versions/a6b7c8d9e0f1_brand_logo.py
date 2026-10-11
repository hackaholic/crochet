"""Nullable database-controlled official brand logo."""
from alembic import op
import sqlalchemy as sa
revision = 'a6b7c8d9e0f1'
down_revision = 'f3a4b5c6d7e8'
branch_labels = None
depends_on = None
def upgrade():
    op.add_column('brand_settings', sa.Column('logo_url', sa.String(500), nullable=True))
    brand = sa.table('brand_settings', sa.column('logo_url', sa.String(500)))
    op.execute(brand.update().where(brand.c.logo_url.is_(None)).values(logo_url='brand/sulocraft-logo.png'))
def downgrade():
    op.drop_column('brand_settings', 'logo_url')
