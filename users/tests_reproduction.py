
import pytest
from rest_framework.test import APIClient
from users.factories import UserFactory
from users.models import User

@pytest.mark.django_db
def test_profile_patch_address_only():
    # 1. Create a user with specific data
    user = UserFactory(
        username="OriginalUser",
        email="original@example.com",
        address="Old Address"
    )
    
    client = APIClient()
    client.force_authenticate(user=user)
    
    # 2. PATCH only the address
    payload = {"address": "New Address"}
    response = client.patch('/api/users/profile/', data=payload)
    
    assert response.status_code == 200
    
    # 3. Verify response data
    data = response.json()
    assert data['address'] == "New Address"
    assert data['username'] == "OriginalUser"  # Should NOT change
    assert data['email'] == "original@example.com" # Should NOT change
    
    # 4. Verify database state
    user.refresh_from_db()
    assert user.address == "New Address"
    assert user.username == "OriginalUser"
    assert user.email == "original@example.com"
