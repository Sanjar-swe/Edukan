from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from ..models import Cart, CartItem, Product
from ..serializers import CartSerializer, CartAddSerializer, CartItemSerializer

@extend_schema(tags=['2. Sebet (Cart)'])
class CartViewSet(viewsets.ViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Sebetti kóriw",
        description="Sebettegi ónimler dizimin alıw. \n\n[Info For Backender]: Standard API Operation"
    )

    def list(self, request):
        cart, _ = Cart.objects.prefetch_related('items__product').get_or_create(user=request.user)
        serializer = CartItemSerializer(cart.items.all(), many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Ónim qosıw", 
        description="Sebetke jańa ónim qosıw yamasa sanın ózgertiw. \n\n[Info For Backender]: Stock validation included",
        request=CartAddSerializer, 
        responses={201: None}
    )

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
        cart, _ = Cart.objects.get_or_create(user=request.user)
        
        # Checking cumulative quantity
        existing_item = CartItem.objects.filter(cart=cart, product=product).first()
        current_qty = existing_item.quantity if existing_item else 0
        total_qty = current_qty + quantity
        
        if product.stock < total_qty:
            return Response({
                "error": "Stockda jetkilikli onim joq", 
                "details": f"Qoymada bar: {product.stock}, sebetińizde: {current_qty}, soralıp atır: {quantity}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if existing_item:
            existing_item.quantity = total_qty
            existing_item.save()
        else: 
            CartItem.objects.create(cart=cart, product=product, quantity=quantity)
            
        return Response({"message": "Onim sebetke qosildi"}, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Ónimdi óshiriw",
        description="Ónimdi sebetten tolıq óshiriw. \n\n[Info For Backender]: Standard API Operation"
    )

    def destroy(self, request, pk=None):
        cart = get_object_or_404(Cart, user=request.user)
        item = get_object_or_404(CartItem, cart=cart, product_id=pk)
        item.delete()
        return Response({"message": "Onim sebetten o'shirildi"}, status=status.HTTP_204_NO_CONTENT)
