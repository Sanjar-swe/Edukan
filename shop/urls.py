from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (CategoryViewSet, ProductViewSet, CartViewSet, OrderViewSet, ReviewViewSet)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet)
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='orders')
router.register(r'reviews', ReviewViewSet, basename='reviews')
urlpatterns = [
    path('', include(router.urls)),
]
