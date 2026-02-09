from rest_framework import viewsets, permissions, serializers, mixins, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from ..models import Review, OrderItem
from ..serializers import ReviewSerializer

class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


@extend_schema_view(
    list=extend_schema(
        summary="Pikirler dizimi",
        description="Ónim haqqında pikirlerdi kóriw. ?product={id} parametri SHÁRT. \n\n[Info For Backender]: Product filter REQUIRED"
    ),
    create=extend_schema(
        summary="Pikir qaldırıw",
        description="Ónimge jańa pikir qaldırıw. \n\n[Info For Backender]: Purchase verification (paid/shipped) included"
    ),
    partial_update=extend_schema(
        summary="Pikir ózgertiw",
        description="Pikir mazmunın yamasa reytingin ózgertiw. \n\n[Info For Backender]: Author only (Strict)"
    ),
    destroy=extend_schema(
        summary="Pikir óshiriw",
        description="Pikirni bazadan óshiriw. \n\n[Info For Backender]: Author only (Strict)"
    )

)

@extend_schema(tags=['4. Pikirler (Reviews)'])
class ReviewViewSet(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    queryset = Review.objects.select_related('user').all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    pagination_class = None  # Disable pagination for reviews
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product']

    def list(self, request, *args, **kwargs):
        # Require product parameter
        if not request.query_params.get('product'):
            return Response(
                {"error": "product parametri kiritiliwi shárt"},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        product = serializer.validated_data.get('product')
        # Проверяем, купил ли пользователь этот товар (статус 'paid' или 'shipped')
        has_purchased = OrderItem.objects.filter(
            order__user=self.request.user,
            product=product,
            order__status__in=['paid', 'shipped']
        ).exists()

        if not has_purchased:
            raise serializers.ValidationError(
                {"error": "Siz bul ónimdi satıp almaǵansız. Pikir qaldırıw ushın aldın onı satıp alıń."}
            )
        
        serializer.save(user=self.request.user)
