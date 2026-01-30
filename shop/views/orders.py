from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from drf_spectacular.utils import extend_schema
from ..models import Cart, Order, OrderItem, Product
from ..serializers import OrderSerializer, OrderCheckoutSerializer

@extend_schema(tags=['3. Buyırtpa (Checkout)'])
class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
        return Order.objects.filter(user=self.request.user)

    @extend_schema(request=OrderCheckoutSerializer, responses={201: OrderSerializer})
    @action(detail=False, methods=['post'])
    @transaction.atomic
    def checkout(self, request):
        cart = get_object_or_404(Cart, user=request.user)
        cart_item_ids = request.data.get('cart_item_ids', [])
        
        if not cart_item_ids:
            return Response({"error": "Oformit qiliw ushun keminde bir onim saylanuwi kerek"}, status=status.HTTP_400_BAD_REQUEST)

        selected_items = cart.items.filter(id__in=cart_item_ids).select_related('product')
        product_ids = [item.product_id for item in selected_items]
        locked_products = {p.id: p for p in Product.objects.select_for_update().filter(id__in=product_ids)}
        
        if not selected_items.exists():
            return Response({"error": "Saylang'an onimler tabilmadi yamasa sebet bos"}, status=status.HTTP_400_BAD_REQUEST)

        total_price = sum(item.product.get_price() * item.quantity for item in selected_items)
        address = request.data.get('address')
        if not address:
            return Response({"error": "Jetkerip beriw mánzili (address) kiritiliwi shárt"}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(user=request.user, total_price=total_price, address=address, status='pending')
        order_items = []
        products_to_update = []

        for item in selected_items:
            product = locked_products.get(item.product_id)
            if not product: continue

            if product.stock < item.quantity:
                return Response({"error": f"Stockda {product.name} jetkiliksiz"}, status=status.HTTP_400_BAD_REQUEST)

            order_items.append(OrderItem(order=order, product=product, quantity=item.quantity, price=product.get_price()))
            product.stock -= item.quantity
            products_to_update.append(product)

        OrderItem.objects.bulk_create(order_items)
        Product.objects.bulk_update(products_to_update, ['stock'])
        selected_items.delete()

        return Response({"message": "Buyırtpa rásmiylestirildi", "order_id": order.id}, status=status.HTTP_201_CREATED)
