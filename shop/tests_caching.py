import pytest
from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APIClient
from shop.factories import ProductFactory, CategoryFactory
from unittest.mock import patch

@pytest.mark.django_db(transaction=True)
class TestRedisCaching:
    def setup_method(self):
        self.client = APIClient()
        cache.clear()

    def test_product_list_caching(self):
        ProductFactory.create_batch(3)
        url = reverse('product-list')
        
        # First request (populate cache)
        with patch('shop.views.catalog.ProductViewSet.get_queryset') as mock_qs:
            # We need to return an actual queryset for the super().list() to work
            from shop.models import Product
            mock_qs.return_value = Product.objects.all()
            
            response1 = self.client.get(url)
            assert response1.status_code == 200
            assert mock_qs.called

        # Second request (should come from cache)
        with patch('shop.views.catalog.ProductViewSet.get_queryset') as mock_qs:
            response2 = self.client.get(url)
            assert response2.status_code == 200
            # If cached, get_queryset should NOT be called
            assert not mock_qs.called

    def test_cache_invalidation_on_product_save(self):
        product = ProductFactory(name="Old Name")
        url = reverse('product-list')
        
        # Populate cache
        self.client.get(url)
        
        # Modify product (triggers signal)
        product.name = "New Name"
        product.save()
        
        # Request again (should hit DB because cache was cleared)
        with patch('shop.views.catalog.ProductViewSet.get_queryset') as mock_qs:
            from shop.models import Product
            mock_qs.return_value = Product.objects.all()
            self.client.get(url)
            assert mock_qs.called
