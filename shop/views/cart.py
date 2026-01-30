from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from ..models import Cart, CartItem, Product
from ..serializers import CartSerializer, CartAddSerializer

@extend_schema(tags=['2. Sebet (Cart)'])
class CartViewSet(viewsets.ViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @extend_schema(request=CartAddSerializer, responses={201: None})
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
        if product.stock < quantity:
            return Response({"error": "Stockda jetkilikli onim joq"}, status=status.HTTP_400_BAD_REQUEST)
        
        cart, _ = Cart.objects.get_or_create(user=request.user)
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            item.quantity += quantity
        else: 
            item.quantity = quantity
        item.save()
        return Response({"message": "Onim sebetke qosildi"}, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        cart = get_object_or_404(Cart, user=request.user)
        item = get_object_or_404(CartItem, cart=cart, product_id=pk)
        item.delete()
        return Response({"message": "Onim sebetten o'shirildi"}, status=status.HTTP_204_NO_CONTENT)
