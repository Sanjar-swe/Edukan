import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from users.factories import UserFactory

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user(db):
    return UserFactory()

@pytest.mark.django_db
class TestCartAccess:
    def test_cart_access_unauthorized(self, api_client):
        # Исправлено имя на 'cart-list'
        url = reverse('cart-list') 
        response = api_client.get(url)
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    def test_cart_access_authorized(self, api_client, user):
        api_client.force_authenticate(user=user)
        # Исправлено имя на 'cart-list'
        url = reverse('cart-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

@pytest.mark.django_db
class TestUserProfile:
    def test_profile_update_patch_allowed(self, api_client, user):
        api_client.force_authenticate(user=user)
        url = reverse('profile')
        response = api_client.patch(url, {'address': 'New Address'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['address'] == 'New Address'

    def test_profile_update_put_disallowed(self, api_client, user):
        api_client.force_authenticate(user=user)
        url = reverse('profile')
        # PUT requires all fields, but it should be 405 regardless
        response = api_client.put(url, {'username': user.username, 'address': 'New Address'})
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED