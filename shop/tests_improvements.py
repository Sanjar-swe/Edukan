import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from shop.models import Product, Category, Cart, CartItem
from shop.factories import ProductFactory, CategoryFactory, UserFactory

@pytest.mark.django_db
class TestImprovements:
    def setup_method(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.category = CategoryFactory(name="Tech")
        self.p1 = ProductFactory(name="Cheap Phone", price=100, category=self.category, stock=5)
        self.p2 = ProductFactory(name="Expensive Phone", price=1000, category=self.category, stock=5)
        
    def test_price_range_filtering(self):
        url = reverse('product-list')
        
        # Test min_price
        response = self.client.get(url, {'min_price': 500})
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results'] if 'results' in response.data else response.data
        assert len(results) == 1
        assert results[0]['name'] == "Expensive Phone"
        
        # Test max_price
        response = self.client.get(url, {'max_price': 500})
        results = response.data['results'] if 'results' in response.data else response.data
        assert len(results) == 1
        assert results[0]['name'] == "Cheap Phone"
        
        # Test range
        response = self.client.get(url, {'min_price': 50, 'max_price': 1500})
        results = response.data['results'] if 'results' in response.data else response.data
        assert len(results) == 2

    def test_cart_cumulative_stock_validation(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('cart-add')
        
        # Step 1: Add 3 items (stock is 5)
        response = self.client.post(url, {'product_id': self.p1.id, 'quantity': 3})
        assert response.status_code == status.HTTP_201_CREATED
        
        # Step 2: Try to add 3 more (3+3=6 > 5)
        response = self.client.post(url, {'product_id': self.p1.id, 'quantity': 3})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Stockda jetkilikli onim joq" in response.data['error']
        
        # Step 3: Add only 2 more (3+2=5 <= 5)
        response = self.client.post(url, {'product_id': self.p1.id, 'quantity': 2})
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verify final quantity is 5
        cart = Cart.objects.get(user=self.user)
        assert CartItem.objects.get(cart=cart, product=self.p1).quantity == 5
