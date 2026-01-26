import pytest
from users.factories import UserFactory
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from shop.factories import ProductFactory, CategoryFactory 
from shop.models import Product 

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def admin_user(db):
    # Создаем пользователя с правами персонала (is_staff)
    return UserFactory(is_staff=True)

@pytest.mark.django_db
def test_product_list_status_code(api_client):
    # Создаем 3 товара с помощью нашей фабрики
    ProductFactory.create_batch(3)
    
    # URL для списка товаров (проверьте, что в urls.py имя 'product-list')
    url = reverse('product-list')
    
    # Делаем GET запрос
    response = api_client.get(url)
    
    # Проверяем, что статус 200 OK
    assert response.status_code == status.HTTP_200_OK
    
    # Проверяем, что в списке действительно 3 товара
    # (Если у вас есть пагинация, данные будут в response.data['results'])
    if 'results' in response.data:
        assert len(response.data['results']) == 3
    else:
        assert len(response.data) == 3



@pytest.fixture
def user(db):
    return UserFactory()

@pytest.mark.django_db
def test_order_checkout_process(api_client, user):
    # 1. Подготовка данных
    product = ProductFactory(stock=10, price=1000)
    api_client.force_authenticate(user=user)
    
    # Добавляем в корзину (по экшену 'add' и полю 'product_id')
    add_to_cart_url = reverse('cart-add')
    api_client.post(add_to_cart_url, {'product_id': product.id, 'quantity': 2})
    
    # 2. Оформление заказа через ваш экшен 'checkout'
    checkout_url = reverse('orders-checkout') 
    order_data = {
        'address': 'Karakalpakstan, Nukus'
    }
    
    response = api_client.post(checkout_url, order_data)
    
    # 3. Проверки
    # Так как ваш API возвращает 201 Created при успешном checkout
    assert response.status_code == status.HTTP_201_CREATED
    assert "message" in response.data
    
    # Проверяем, что stock уменьшился (10 - 2 = 8)
    product.refresh_from_db()
    assert product.stock == 8
    
    # Проверяем, что корзина очистилась (GET /api/shop/cart/)
    cart_url = reverse('cart-list')
    cart_response = api_client.get(cart_url)
    assert len(cart_response.data['items']) == 0

@pytest.mark.django_db
def test_add_to_cart_out_of_stock(api_client, user):
    # Создаем товар с нулевым запасом
    product = ProductFactory(stock=0)
    api_client.force_authenticate(user=user)
    
    url = reverse('cart-add')
    response = api_client.post(url, {'product_id': product.id, 'quantity': 1})
    
    # Ожидаем ошибку 400 Bad Request
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['error'] == "Stockda jetkilikli onim joq"

@pytest.mark.django_db
def test_create_review(api_client, user):
    product = ProductFactory()
    api_client.force_authenticate(user=user)
    
    url = reverse('reviews-list')
    review_data = {
        'product': product.id,
        'rating': 5,
        'comment': 'Sipatli Onim!'
    }
    
    response = api_client.post(url, review_data)
    
    # Проверяем успешное создание
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['comment'] == 'Sipatli Onim!'
    assert response.data['user_name'] == user.username

@pytest.mark.django_db
class TestProductAdminAPI:
    def test_create_product_as_admin(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        category = CategoryFactory()
        
        url = reverse('product-list')
        data = {
            'category': category.id,
            'name': 'Admin Phone',
            'slug': 'admin-phone',
            'description': 'Super Admin Phone',
            'price': 5000,
            'stock': 5
        }
        
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'Admin Phone'

    def test_create_product_as_regular_user_denied(self, api_client, user):
        api_client.force_authenticate(user=user)
        url = reverse('product-list')
        data = {'name': 'normal Phone'}
        
        response = api_client.post(url, data)
        
        # Обычный пользователь не должен иметь доступа (403 Forbidden)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_product_as_admin(self, api_client, admin_user):
        product = ProductFactory()
        api_client.force_authenticate(user=admin_user)
        
        url = reverse('product-detail', kwargs={'pk': product.pk})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Product.objects.filter(id=product.id).exists()