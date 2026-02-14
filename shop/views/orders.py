from django.core.exceptions import ValidationError
from rest_framework import viewsets, permissions, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from ..models import Order
from ..serializers import OrderSerializer, OrderCheckoutSerializer
from ..dto import OrderCheckoutDTO
from ..services import create_order

@extend_schema(tags=['3. Buyırtpa (Checkout)'])
class OrderViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']  # Exclude PUT

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
        if self.request.user.is_staff:
            return Order.objects.all().select_related('user').prefetch_related('items__product')
        return Order.objects.filter(user=self.request.user).select_related('user').prefetch_related('items__product')

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'checkout']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

    @extend_schema(
        summary="Buyırtpalar tariyxı",
        description="Paydalanıwshınıń barlıq buyırtpaların kóriw. \n\n[Info For Backender]: Standard API Operation"
    )

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Buyırtpa detallerı",
        description="Buyırtpa haqqında tolıq maǵlıwmat. \n\n[Info For Backender]: Standard API Operation"
    )

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Buyırtpa rásmiylestiriw", 
        description="Buyırtpa beriw ushın mánzildi jiberiń. \n\n[Info For Backender]: Background task Celery (Telegram notification)",
        request=OrderCheckoutSerializer, 
        responses={201: OrderSerializer}
    )


    @action(detail=False, methods=['post'])
    def checkout(self, request):
        serializer = OrderCheckoutSerializer(data=request.data)
        if not serializer.is_valid():
            error_msg = next(iter(serializer.errors.values()))[0]
            field_name = next(iter(serializer.errors.keys()))
            return Response({"error": f"{field_name}: {error_msg}"}, status=status.HTTP_400_BAD_REQUEST)

        # Fallback на адрес из профиля, если не передан в запросе
        address = serializer.validated_data.get('address') or getattr(request.user, 'address', None)
        if not address:
            return Response(
                {"error": "Jetkerip beriw mánzili (address) kiritiliwi shárt"},
                status=status.HTTP_400_BAD_REQUEST
            )

        dto = OrderCheckoutDTO(
            user_id=request.user.id,
            cart_item_ids=serializer.validated_data.get('cart_item_ids', []),
            address=address
        )

        try:
            order = create_order(dto)
            return Response(
                {"message": "Buyırtpa rásmiylestirildi", "order_id": order.id}, 
                status=status.HTTP_201_CREATED
            )
        except ValidationError as e:
            return Response({"error": e.message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "Ishki сервер qatesi"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    @extend_schema(
        tags=['3.1 Buyırtpa (Admin)'], 
        summary="Buyırtpa statusın ózgertiw (Admin)",
        description="Buyırtpa statusın jańalaw. \n\n[Info For Backender]: Admin access only"
    )

    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        tags=['3.1 Buyırtpa (Admin)'], 
        summary="Buyırtpanı óshiriw (Admin)",
        description="Buyırtpanı bazadan óshiriw. \n\n[Info For Backender]: Admin access only"
    )

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
