import pytest
from rest_framework.test import APIClient
from shop.factories import OrderFactory, UserFactory

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
def test_pay_order_success(api_client):
    user = UserFactory()
    order = OrderFactory(user=user, status='pending')
    api_client.force_authenticate(user=user)
    
    response = api_client.post(f'/api/shop/orders/{order.id}/pay/')
    
    assert response.status_code == 200
    order.refresh_from_db()
    assert order.status == 'paid'

@pytest.mark.django_db
def test_pay_order_already_paid(api_client):
    user = UserFactory()
    order = OrderFactory(user=user, status='paid')
    api_client.force_authenticate(user=user)
    
    response = api_client.post(f'/api/shop/orders/{order.id}/pay/')
    
    assert response.status_code == 400
    assert "Buyırtpa ushın aldın tólem qılgansız" in str(response.data)

@pytest.mark.django_db
def test_pay_order_cancelled(api_client):
    user = UserFactory()
    order = OrderFactory(user=user, status='cancelled')
    api_client.force_authenticate(user=user)
    
    response = api_client.post(f'/api/shop/orders/{order.id}/pay/')
    
    assert response.status_code == 400
    assert "Biykar qılıngan buyırtpanı tólep bolmaydı" in str(response.data)

@pytest.mark.django_db
def test_pay_order_not_owner(api_client):
    owner = UserFactory()
    other_user = UserFactory()
    order = OrderFactory(user=owner, status='pending')
    api_client.force_authenticate(user=other_user)
    
    response = api_client.post(f'/api/shop/orders/{order.id}/pay/')
    
    # Depends on how permissions are handled. 
    # If get_queryset filters by user, it return 404.
    assert response.status_code == 404
