"""Admin media URLs are read-only representations; database keys remain intact."""
import unittest
from unittest.mock import patch
from app.schemas.admin import AdminProductOut

class AdminProductMediaTests(unittest.TestCase):
    def test_urls_resolve_without_changing_storage_keys(self):
        item = AdminProductOut(id=1, name='Test', slug='test', status='ACTIVE', brand='Sulocraft', primaryImage='products/test.webp', galleryImages=['products/detail.webp'], customizable=False, rating=0, reviewsCount=0)
        with patch('app.schemas.admin.build_image_url', side_effect=lambda key: f'https://cdn.example/{key}'):
            payload = item.model_dump(by_alias=True)
        self.assertEqual(payload['primaryImageUrl'], 'https://cdn.example/products/test.webp')
        self.assertEqual(payload['galleryImageUrls'], ['https://cdn.example/products/detail.webp'])
        self.assertEqual(payload['primaryImage'], 'products/test.webp')
        self.assertEqual(payload['galleryImages'], ['products/detail.webp'])

    def test_external_url_is_preserved_by_shared_resolver(self):
        item = AdminProductOut(id=1, name='Test', slug='test', status='ACTIVE', brand='Sulocraft', primaryImage='https://cdn.example/photo.webp', customizable=False, rating=0, reviewsCount=0)
        self.assertEqual(item.primary_image_url, 'https://cdn.example/photo.webp')
        self.assertEqual(item.gallery_image_urls, [])
