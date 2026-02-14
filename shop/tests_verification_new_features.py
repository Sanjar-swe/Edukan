import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from users.factories import UserFactory
from shop.factories import ProductFactory
from shop.models import Cart, CartItem
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
import os

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return UserFactory()

@pytest.fixture
def admin_user():
    return UserFactory(is_staff=True, is_superuser=True)

@pytest.mark.django_db
def test_health_check(api_client):
    """Проверка Healthcheck endpoint"""
    url = reverse('health-check')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"status": "ok"}

@pytest.mark.django_db
class TestCheckoutAddressLogic:
    def test_checkout_with_explicit_address(self, api_client, user):
        """Оформление заказа с указанным адресом"""
        api_client.force_authenticate(user=user)
        product = ProductFactory(stock=10, price=100)
        cart = Cart.objects.create(user=user)
        CartItem.objects.create(cart=cart, product=product, quantity=1)
        
        url = reverse('orders-checkout')
        data = {
            'address': 'Explicit Address',
            'cart_item_ids': [] # All cart
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['message'] == "Buyırtpa rásmiylestirildi"

    def test_checkout_with_profile_address_fallback(self, api_client, user):
        """Оформление заказа БЕЗ адреса в запросе, но С адресом в профиле"""
        user.address = "Profile Update Address"
        user.save()
        api_client.force_authenticate(user=user)
        
        product = ProductFactory(stock=10, price=100)
        cart = Cart.objects.create(user=user)
        CartItem.objects.create(cart=cart, product=product, quantity=1)
        
        url = reverse('orders-checkout')
        data = {
            'cart_item_ids': [] 
            # address НЕ передаем
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        
    def test_checkout_no_address_anywhere(self, api_client, user):
        """Оформление заказа БЕЗ адреса везде -> Ошибка"""
        user.address = "" # Пустой адрес в профиле
        user.save()
        api_client.force_authenticate(user=user)
        
        product = ProductFactory(stock=10, price=100)
        cart = Cart.objects.create(user=user)
        CartItem.objects.create(cart=cart, product=product, quantity=1)
        
        url = reverse('orders-checkout')
        data = {'cart_item_ids': []}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "address" in str(response.data)

@pytest.mark.django_db
class TestMediaUpload:
    def test_product_creation_with_image(self, api_client, admin_user):
        """Загрузка изображения товара через API (Multipart)"""
        api_client.force_authenticate(user=admin_user)
        category = ProductFactory().category # Reuse category
        
        # Создаем dummy image
        image_content = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x05\x04\x04\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
        uploaded_image = SimpleUploadedFile(name='test_image.gif', content=image_content, content_type='image/gif')
        
        url = reverse('product-list')
        data = {
            'category': category.id,
            'name': 'Image Product',
            'slug': 'img-prod',
            'description': 'Desc',
            'price': 100,
            'stock': 10,
            'image': uploaded_image # Передаем файл
        }
        
        # Важно: format='multipart'
        response = api_client.post(url, data, format='multipart')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'test_image' in response.data['image']
        
        # Проверяем что файл реально создался (если MEDIA_ROOT настроен)
        # В тестах обычно используется temp media root, но проверим путь в ответе
        assert utils_media_url_check(response.data['image'])

def utils_media_url_check(url):
    return '/media/products/' in url or 'http' in url
