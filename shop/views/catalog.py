from rest_framework import viewsets, permissions, filters, status, mixins
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django_filters import rest_framework as django_filters
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.conf import settings
from drf_spectacular.utils import extend_schema
from ..models import Category, Product
from ..serializers import CategorySerializer, ProductSerializer

class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr='lte')

    class Meta:
        model = Product
        fields = ['category']

@extend_schema(tags=['1. Ónimler (Catalog)'])
class CategoryViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = None  # Disable pagination for categories
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['parent']

    def get_permissions(self):
        if self.action == 'list':
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    @extend_schema(
        summary="Kategoriyalar dizimi",
        description="Kategoriyalar dizimin alıw. \n\n[Info For Backender]: Redis Cache enabled (15 min)"
    )

    @method_decorator(cache_page(60 * 15, key_prefix='category_list'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)



    @extend_schema(
        tags=['1.1 Ónimler (Catalog Admin)'], 
        summary="Kategoriya jaratıw (Admin)",
        description="Jańa kategoriya qosıw. \n\n[Info For Backender]: Admin access only"
    )

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        tags=['1.1 Ónimler (Catalog Admin)'], 
        summary="Kategoriyanı tolıq ózgertiw (Admin)",
        description="Kategoriyanı tolıq jańalaw. \n\n[Info For Backender]: Admin access only"
    )

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        tags=['1.1 Ónimler (Catalog Admin)'], 
        summary="Kategoriyanı bólek ózgertiw (Admin)",
        description="Kategoriya maydanların bólek jańalaw. \n\n[Info For Backender]: Admin access only"
    )

    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        tags=['1.1 Ónimler (Catalog Admin)'], 
        summary="Kategoriyanı óshiriw (Admin)",
        description="Kategoriyanı bazadan óshiriw. \n\n[Info For Backender]: Admin access only"
    )

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


@extend_schema(tags=['1. Ónimler (Catalog)'])
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True).select_related('category')
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    @extend_schema(
        summary="Ónimler dizimi",
        description="Ónimler dizimin alıw. \n\n[Info For Backender]: Redis Cache enabled (15 min)"
    )

    @method_decorator(cache_page(60 * 15, key_prefix='product_list'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Ónim detallerı",
        description="Ónim haqqında tolıq maǵlıwmat. \n\n[Info For Backender]: Redis Cache enabled (15 min)"
    )

    @method_decorator(cache_page(60 * 15, key_prefix='product_detail'))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=['1.1 Ónimler (Catalog Admin)'], 
        summary="Ónim jaratıw (Admin)",
        description="Sistemaga jańa ónim qosıw. \n\n[Info For Backender]: Admin access only"
    )

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        tags=['1.1 Ónimler (Catalog Admin)'], 
        summary="Ónimdi tolıq ózgertiw (Admin)",
        description="Ónim maǵlıwmatların tolıq jańalaw. \n\n[Info For Backender]: Admin access only"
    )

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        tags=['1.1 Ónimler (Catalog Admin)'], 
        summary="Ónimdi bólek ózgertiw (Admin)",
        description="Ónim maydanların bólek jańalaw. \n\n[Info For Backender]: Admin access only"
    )

    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        tags=['1.1 Ónimler (Catalog Admin)'], 
        summary="Ónimdi óshiriw (Admin)",
        description="Ónimni bazadan óshiriw. \n\n[Info For Backender]: Admin access only"
    )

    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
