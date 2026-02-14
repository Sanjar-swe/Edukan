from rest_framework import serializers
from .models import Category, Product, Cart, CartItem, Order, OrderItem, Review
from django.db.models import Sum, F

# 1. Категории
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent']

# 2. Товары
class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    discount_percent = serializers.IntegerField(source='calc_discount_percent', read_only=True)
    is_on_sale = serializers.BooleanField(read_only=True)
    set_discount_percent = serializers.IntegerField(write_only=True, required=False, min_value=0, max_value=99)
    
    class Meta:
        model = Product
        fields = [
            'id', 'category', 'category_name', 'name', 'slug', 
            'description', 'price', 'discount_price', 'image', 
            'stock', 'is_active', 'discount_percent', 'is_on_sale',
            'set_discount_percent'
        ]

    def validate(self, attrs):
        price = attrs.get('price')
        # If we are updating, we might not have price in attrs, so get from instance
        if not price and self.instance:
            price = self.instance.price
            
        discount_percent = attrs.pop('set_discount_percent', None)
        
        if discount_percent is not None and price:
            from decimal import Decimal
            discount_multiplier = Decimal(1) - (Decimal(discount_percent) / Decimal(100))
            attrs['discount_price'] = (price * discount_multiplier).quantize(Decimal('0.01'))
            
        return attrs

# 3. Корзина
# одна позиция в корзине (товар + количество)
class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product', 'product_name', 'product_price', 'quantity']

    def get_product_price(self, obj):
        return obj.product.get_price()

# корзина целиком (список позиций + итог)
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_price', 'created_at']

    def get_total_price(self, obj):
        total = sum(item.product.get_price() * item.quantity for item in obj.items.all())
        return total

class CartAddSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1, min_value=1)

class OrderCheckoutSerializer(serializers.Serializer):
    address = serializers.CharField(
        max_length=500,
        required=False,
        help_text="Адрес доставки. Если не указан — используется адрес из профиля"
    )
    cart_item_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="ID элементов корзины, которые нужно оформить (если пусто - оформится вся корзина)"
    )

# 4. Заказы
class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'product_name', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    # total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'total_price', 'status', 'address', 'items', 'created_at']
        read_only_fields = ['user', 'total_price', 'status', 'created_at']


# 5. Отзывы 
class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'user_name', 'rating', 'comment', 'created_at']
        read_only_fields = ['user', 'created_at']
    