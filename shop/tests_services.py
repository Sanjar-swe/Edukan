import pytest
from unittest.mock import patch
from django.core.exceptions import ValidationError
from shop.models import Cart, CartItem, Order, Product
from shop.factories import ProductFactory, CategoryFactory
from users.factories import UserFactory
from shop.dto import OrderCheckoutDTO
from shop.services import create_order

@pytest.mark.django_db(transaction=True)
class TestOrderService:
    @patch('shop.tasks.send_order_notification_task.delay')
    def test_create_order_success(self, mock_task_delay):
        # 1. Setup data
        user = UserFactory()
        product = ProductFactory(price=100, stock=10)
        cart = Cart.objects.create(user=user)
        item = CartItem.objects.create(cart=cart, product=product, quantity=2)
        
        # 2. Create DTO
        dto = OrderCheckoutDTO(
            user_id=user.id,
            cart_item_ids=[item.id],
            address="Service Test Address"
        )
        
        # 3. Call service directly
        order = create_order(dto)
        
        # 4. Assertions
        assert isinstance(order, Order)
        assert order.total_price == 200
        
        # 5. Check task dispatch
        assert mock_task_delay.called
        mock_task_delay.assert_called_once_with(order.id)

    def test_create_order_missing_cart(self):
        user = UserFactory()
        dto = OrderCheckoutDTO(user_id=user.id, cart_item_ids=[1], address="Addr")
        
        with pytest.raises(ValidationError) as exc:
            create_order(dto)
        assert "Sebet tabilmadi" in str(exc.value)

    def test_create_order_insufficient_stock(self):
        user = UserFactory()
        product = ProductFactory(price=100, stock=1)
        cart = Cart.objects.create(user=user)
        item = CartItem.objects.create(cart=cart, product=product, quantity=2)
        
        dto = OrderCheckoutDTO(
            user_id=user.id,
            cart_item_ids=[item.id],
            address="Service Test Address"
        )
        
        with pytest.raises(ValidationError) as exc:
            create_order(dto)
        
        assert "jetkiliksiz" in str(exc.value)

    def test_create_order_empty_selection(self):
        user = UserFactory()
        Cart.objects.create(user=user) # Create empty cart
        dto = OrderCheckoutDTO(user_id=user.id, cart_item_ids=[], address="Addr")
        
        with pytest.raises(ValidationError) as exc:
            create_order(dto)
        assert "Saylang'an onimler tabilmadi" in str(exc.value)
