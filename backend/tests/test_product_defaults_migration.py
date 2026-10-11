"""Owner-approved copy migration must preserve custom defaults and products."""
import importlib.util
from pathlib import Path
from sqlalchemy import create_engine, text

def test_neutral_defaults_migration_changes_only_original_copy(monkeypatch):
    path = Path(__file__).parents[1] / 'alembic/versions/e2f3a4b5c6d7_neutral_product_information_defaults.py'
    spec = importlib.util.spec_from_file_location('neutral_defaults_migration', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    engine = create_engine('sqlite://')
    with engine.begin() as connection:
        connection.execute(text('CREATE TABLE product_information_defaults (id INTEGER, processing_time TEXT, shipping_delivery TEXT)'))
        connection.execute(text('CREATE TABLE products (id INTEGER, processing_time TEXT)'))
        old = 'Standard handcrafted orders ship within 3–5 business days. Custom pieces may require additional preparation time.'
        shipping = 'Delivered across India via standard courier partners. Tracking details are shared upon dispatch.'
        connection.execute(text('INSERT INTO product_information_defaults VALUES (1, :old, :shipping), (2, :custom, :custom)'), {'old':old,'shipping':shipping,'custom':'Owner custom value'})
        connection.execute(text('INSERT INTO products VALUES (1, :old)'), {'old':old})
        monkeypatch.setattr(module.op, 'get_bind', lambda:connection)
        module.upgrade()
        module.upgrade()  # idempotent; safe if reused in a repair.
        rows = connection.execute(text('SELECT processing_time, shipping_delivery FROM product_information_defaults ORDER BY id')).all()
        assert rows[0] == ('Processing time is confirmed for each order.', 'Shipping availability and delivery details are confirmed for each order.')
        assert rows[1] == ('Owner custom value', 'Owner custom value')
        assert connection.execute(text('SELECT processing_time FROM products')).scalar() == old
        module.downgrade()
        assert connection.execute(text('SELECT processing_time FROM product_information_defaults WHERE id=1')).scalar() != old
