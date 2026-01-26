from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from django.db.models import Sum, F
# 
from .models import Category, Product, Cart, CartItem, Order, OrderItem, Review
from .serializers import (CategorySerializer, ProductSerializer, CartSerializer, CartItemSerializer, OrderSerializer, ReviewSerializer)

# 1. Продукты и Категории
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        parent_id = self.request.query_params.get('parent')
        if parent_id:
            if parent_id.lower() == 'null':
                return Category.objects.filter(parent__isnull=True)
            return Category.objects.filter(parent_id=parent_id)
        return Category.objects.filter(parent__isnull=True)

# API для товаров: просмотр доступен всем, создание/изменение/удаление — только админ. 
# Поддерживает фильтрацию, поиск и сортировку.
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'category__parent', 'price']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    # 1. Список товаров (GET /products/)
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # 2. Детальный просмотр (GET /products/{id}/)
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    # 3. Создание товара (POST /products/) - Только Админ
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # 4. Обновление товара (PUT/PATCH /products/{id}/) - Только Админ
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    # 5. Удаление товара (DELETE /products/{id}/) - Только Админ
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

# 2. Корзина
class CartViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add(self, request):
        product_id = request.data.get('product_id')
        try:
            quantity = int(request.data.get('quantity', 1))
            if quantity < 1:
                return Response({"error": "Sanı 1 den kem bolıwı múmkin emes"}, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({"error": "Sanı nadurıs formatta"}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, id=product_id)
        #5-ый пункт валидация
        if product.stock < quantity:
            return Response({
                "error": "Stockda jetkilikli onim joq"},
                status=status.HTTP_400_BAD_REQUEST
            )
        cart, _ = Cart.objects.get_or_create(user=request.user)
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            item.quantity += quantity
        else: 
            item.quantity = quantity
        item.save()
        return Response({
            "message": "Onim sebetke qosildi"},
            status=status.HTTP_201_CREATED
        )

    def destroy(self, request, pk=None):
        cart = get_object_or_404(Cart, user=request.user)
        item = get_object_or_404(CartItem, cart=cart, product_id=pk)
        item.delete()
        return Response({
            "message": "Onim sebetten o'shirildi"},
            status=status.HTTP_204_NO_CONTENT
        )


# 3. Заказы
class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
        return Order.objects.filter(user=self.request.user)
    # защищает от ситуации, когда два человека одновременно пытаются купить последний товар.
    @action(detail=False, methods=['post'])
    @transaction.atomic
    def checkout(self, request):
        cart = get_object_or_404(Cart, user=request.user)
        
        # Получаем список ID айтемов корзины, которые нужно оформить
        cart_item_ids = request.data.get('cart_item_ids', [])
        
        if not cart_item_ids:
            return Response({"error": "Oformit qiliw ushun keminde bir onim saylanuwi kerek (cart_item_ids korsetilmegen)"}, 
                            status=status.HTTP_400_BAD_REQUEST)

        # Фильтруем айтемы в корзине пользователя
        # Используем select_for_update() для блокировки строк товаров, чтобы избежать Race Condition
        selected_items = cart.items.filter(id__in=cart_item_ids).select_related('product')
        
        # Получаем ID товаров, чтобы заблокировать их в базе данных
        product_ids = [item.product_id for item in selected_items]
        # Блокируем строки товаров для обновления (другие транзакции будут ждать)
        locked_products = {p.id: p for p in Product.objects.select_for_update().filter(id__in=product_ids)}
        
        if not selected_items.exists():
            return Response({"error": "Saylang'an onimler tabilmadi yamasa sebet bos"}, 
                            status=status.HTTP_400_BAD_REQUEST)

        # Расчет общей стоимости с учетом скидок для выбранных товаров
        total_price = sum(item.product.get_price() * item.quantity for item in selected_items)
        
        address = request.data.get('address')
        if not address:
            return Response({"error": "Jetkerip beriw mánzili (address) kiritiliwi shárt"}, status=status.HTTP_400_BAD_REQUEST)

        # Создание заказа
        order = Order.objects.create(user=request.user, total_price=total_price, address=address, status='pending')

        order_items = []
        products_to_update = []

        for item in selected_items:
            # Берем заблокированный объект товара из словаря
            product = locked_products.get(item.product_id)
            if not product:
                continue

            if product.stock < item.quantity:
                # Если хоть одного товара не хватает, отменяем всю транзакцию
                return Response({"error": f"Stockda {product.name} jetkiliksiz"}, 
                    status=status.HTTP_400_BAD_REQUEST)

            # Подготавливаем айтем заказа с актуальной ценой (учитывая скидки)
            order_items.append(OrderItem(
                order=order,
                product=product,
                quantity=item.quantity,
                price=product.get_price()
            ))
            
            # Уменьшаем остаток в памяти
            product.stock -= item.quantity
            products_to_update.append(product)

        # Массовые операции (всего 3 запроса к БД)
        OrderItem.objects.bulk_create(order_items)
        Product.objects.bulk_update(products_to_update, ['stock'])
        selected_items.delete() # Удаляем только оформленные айтемы

        return Response({
            "message": "Buyırtpa rásmiylestirildi", 
            "order_id": order.id
        }, status=status.HTTP_201_CREATED)


# 4. Отзывы
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # При сохранении отзыва автоматически привязываем его к текущему пользователю
        serializer.save(user=self.request.user)