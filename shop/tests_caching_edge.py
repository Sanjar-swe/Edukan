import pytest
from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APIClient
from shop.factories import ProductFactory, CategoryFactory
from shop.models import Product, Category
from unittest.mock import patch

@pytest.mark.django_db(transaction=True)
class TestRedisCachingEdgeCases:
    def setup_method(self):
        self.client = APIClient()
        cache.clear()

    def test_cache_invalidation_on_product_deletion(self):
        """Проверка сброса кеша при удалении товара."""
        product = ProductFactory(name="Delete Me")
        url = reverse('product-list')
        
        # Заполняем кеш
        self.client.get(url)
        
        # Удаляем товар
        product.delete()
        
        # Проверяем, что следующий запрос идет в БД
        with patch('shop.views.catalog.ProductViewSet.get_queryset') as mock_qs:
            mock_qs.return_value = Product.objects.all()
            self.client.get(url)
            assert mock_qs.called

    def test_cache_invalidation_on_category_deletion(self):
        """Проверка сброса кеша при удалении категории."""
        category = CategoryFactory(name="Delete Category")
        url = reverse('category-list')
        
        # Заполняем кеш
        self.client.get(url)
        
        # Удаляем категорию
        category.delete()
        
        # Проверяем, что следующий запрос идет в БД
        with patch('shop.views.catalog.CategoryViewSet.get_queryset') as mock_qs:
            mock_qs.return_value = Category.objects.all()
            self.client.get(url)
            assert mock_qs.called

    def test_parametric_caching_isolation(self):
        """Проверка, что кеш для разных параметров запроса не пересекается."""
        cat1 = CategoryFactory(name="Cat 1")
        cat2 = CategoryFactory(name="Cat 2")
        ProductFactory(category=cat1, name="Prod 1")
        ProductFactory(category=cat2, name="Prod 2")
        
        url = reverse('product-list')
        
        # Запрос с фильтром по cat1
        res1 = self.client.get(url, {'category': cat1.id})
        assert len(res1.data['results']) == 1
        assert res1.data['results'][0]['name'] == "Prod 1"
        
        # Запрос с фильтром по cat2
        # Если кеш не учитывает параметры, мы можем получить Prod 1 вместо Prod 2
        res2 = self.client.get(url, {'category': cat2.id})
        assert len(res2.data['results']) == 1
        assert res2.data['results'][0]['name'] == "Prod 2"

    def test_search_query_caching(self):
        """Проверка изоляции кеша для поисковых запросов."""
        ProductFactory(name="Apple")
        ProductFactory(name="Banana")
        
        url = reverse('product-list')
        
        res1 = self.client.get(url, {'search': 'Apple'})
        assert len(res1.data['results']) == 1
        assert res1.data['results'][0]['name'] == "Apple"
        
        res2 = self.client.get(url, {'search': 'Banana'})
        assert len(res2.data['results']) == 1
        assert res2.data['results'][0]['name'] == "Banana"

    def test_detail_caching_invalidation(self):
        """Проверка сброса кеша конкретного объекта при его обновлении."""
        product = ProductFactory(name="Initial Name")
        url = reverse('product-detail', args=[product.id])
        
        # Заполняем кеш детали
        self.client.get(url)
        
        # Обновляем товар
        product.name = "Updated Name"
        product.save()
        
        # Проверяем, что запрос детали видит изменения (кеш сброшен)
        res = self.client.get(url)
        assert res.data['name'] == "Updated Name"
