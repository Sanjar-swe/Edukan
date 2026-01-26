import pytest
from django.db import IntegrityError
from rest_framework.test import APIClient
from shop.models import CartItem, OrderItem, Product
from shop.factories import ProductFactory, CategoryFactory
from users.factories import UserFactory
from shop.models import Cart, Order
from django.db.models.deletion import ProtectedError

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
class TestRobustnessImprovements:
    def test_product_get_price_with_discount(self):
        product = ProductFactory(price=1000, discount_price=800)
        assert product.get_price() == 800

    def test_product_get_price_without_discount(self):
        product = ProductFactory(price=1000, discount_price=None)
        assert product.get_price() == 1000

    def test_cart_item_unique_constraint(self):
        user = UserFactory()
        cart = Cart.objects.create(user=user)
        product = ProductFactory()
        
        CartItem.objects.create(cart=cart, product=product, quantity=1)
        
        with pytest.raises(IntegrityError):
            CartItem.objects.create(cart=cart, product=product, quantity=2)

    def test_order_history_protection(self):
        user = UserFactory()
        product = ProductFactory()
        order = Order.objects.create(user=user, total_price=1000, address="Test Address")
        OrderItem.objects.create(order=order, product=product, quantity=1, price=1000)
        
        # Should not be able to delete product because it's protected in OrderItem
        with pytest.raises(ProtectedError):
            product.delete()

    def test_checkout_uses_discount_price(self, api_client):
        user = UserFactory()
        api_client.force_authenticate(user=user)
        product = ProductFactory(price=1000, discount_price=800, stock=10)
        
        # Add to cart
        res = api_client.post('/api/shop/cart/add/', {'product_id': product.id, 'quantity': 2})
        cart = Cart.objects.get(user=user)
        item = cart.items.first()
        
        # Checkout with specific cart_item_ids
        response = api_client.post('/api/shop/orders/checkout/', {
            'cart_item_ids': [item.id],
            'address': 'Test Address'
        })
        assert response.status_code == 201
        
        order_id = response.data['order_id']
        order = Order.objects.get(id=order_id)
        
        # Total price should be 800 * 2 = 1600
        assert order.total_price == 1600
        
        order_item = order.items.first()
        assert order_item.price == 800

    def test_partial_checkout(self, api_client):
        user = UserFactory()
        api_client.force_authenticate(user=user)
        
        p1 = ProductFactory(price=100, stock=10)
        p2 = ProductFactory(price=200, stock=10)
        
        # Add both to cart
        api_client.post('/api/shop/cart/add/', {'product_id': p1.id, 'quantity': 1})
        api_client.post('/api/shop/cart/add/', {'product_id': p2.id, 'quantity': 1})
        
        cart = Cart.objects.get(user=user)
        item1 = cart.items.get(product=p1)
        item2 = cart.items.get(product=p2)
        
        # Checkout only p1
        response = api_client.post('/api/shop/orders/checkout/', {
            'cart_item_ids': [item1.id],
            'address': 'Test Address'
        })
        assert response.status_code == 201
        
        # Check order
        order = Order.objects.get(id=response.data['order_id'])
        assert order.items.count() == 1
        assert order.items.first().product == p1
        
        # Check cart - item2 should still be there
        assert cart.items.count() == 1
        assert cart.items.filter(product=p2).exists()
        assert not cart.items.filter(product=p1).exists()

    def test_checkout_fails_without_address(self, api_client):
        user = UserFactory(address="Profile Address")
        api_client.force_authenticate(user=user)
        product = ProductFactory(stock=10)
        api_client.post('/api/shop/cart/add/', {'product_id': product.id, 'quantity': 1})
        cart = Cart.objects.get(user=user)
        item = cart.items.first()
        
        # Checkout without address in payload - should fail despite profile address
        response = api_client.post('/api/shop/orders/checkout/', {
            'cart_item_ids': [item.id]
        })
        assert response.status_code == 400
        assert "address" in response.data['error'].lower()
