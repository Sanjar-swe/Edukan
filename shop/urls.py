from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import catalog, cart, orders, reviews

router = DefaultRouter()
router.register(r'categories', catalog.CategoryViewSet, basename='category')
router.register(r'products', catalog.ProductViewSet)
router.register(r'cart', cart.CartViewSet, basename='cart')
router.register(r'orders', orders.OrderViewSet, basename='orders')
router.register(r'reviews', reviews.ReviewViewSet, basename='reviews')

urlpatterns = [
    path('', include(router.urls)),
]
