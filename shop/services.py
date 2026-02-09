from django.db import transaction
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from .models import Cart, Order, OrderItem, Product
from .dto import OrderCheckoutDTO
from .tasks import send_order_notification_task

def create_order(dto: OrderCheckoutDTO) -> Order:
    """
    Бизнес-логика оформления заказа. 
    Независима от HTTP/DRF. 
    Принимает DTO и возвращает объект Order.
    """
    with transaction.atomic():
        # 1. Получаем корзину пользователя
        cart = Cart.objects.filter(user_id=dto.user_id).first()
        if not cart:
            raise ValidationError("Sebet tabilmadi")
        
        # 2. Выбираем элементы корзины, которые пользователь хочет купить
        if dto.cart_item_ids:
            selected_items = cart.items.filter(id__in=dto.cart_item_ids).select_related('product')
        else:
            selected_items = cart.items.all().select_related('product')
        
        if not selected_items.exists():
            raise ValidationError("Saylang'an onimler tabilmadi yamasa sebet bos")

        # 3. Блокируем продукты (select_for_update) для предотвращения race conditions (остатки)
        product_ids = [item.product_id for item in selected_items]
        locked_products = {p.id: p for p in Product.objects.select_for_update().filter(id__in=product_ids)}
        
        total_price = 0
        order_items_to_create = []
        products_to_update = []

        # 4. Проверяем остатки и считаем сумму
        for item in selected_items:
            product = locked_products.get(item.product_id)
            if not product:
                raise ValidationError(f"Onim tabilmadi: ID {item.product_id}")

            if product.stock < item.quantity:
                raise ValidationError(f"Stockda {product.name} jetkiliksiz")

            price_at_checkout = product.get_price()
            total_price += price_at_checkout * item.quantity
            
            order_items_to_create.append(OrderItem(
                product=product,
                quantity=item.quantity,
                price=price_at_checkout
            ))
            
            # Уменьшаем остаток
            product.stock -= item.quantity
            products_to_update.append(product)

        # 5. Создаем заказ
        order = Order.objects.create(
            user_id=dto.user_id,
            total_price=total_price,
            address=dto.address,
            status='pending'
        )

        # 6. Массовое создание элементов заказа и обновление остатков
        for order_item in order_items_to_create:
            order_item.order = order
        
        OrderItem.objects.bulk_create(order_items_to_create)
        Product.objects.bulk_update(products_to_update, ['stock'])

        # 7. Очищаем купленные позиции из корзины
        selected_items.delete()

        # 8. Отправляем уведомление асинхронно после коммита транзакции
        transaction.on_commit(lambda: send_order_notification_task.delay(order.id))

        return order
