import os
import django
import sys
from decimal import Decimal

# Set up Django
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.append(PROJECT_ROOT)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from shop.models import Category, Product
from shop.serializers import ProductSerializer

def test_discount_logic():
    print("--- Testing Discount Logic ---")
    
    # 1. Test Model Logic
    cat = Category.objects.create(name="Test", slug="test")
    p = Product(
        category=cat,
        name="Test",
        slug="test-prod",
        price=Decimal("1000.00"),
        discount_price=Decimal("800.00")
    )
    
    print(f"Price: {p.price}, Discount: {p.discount_price}")
    print(f"Is on sale: {p.is_on_sale}")
    print(f"Calc Percentage: {p.calc_discount_percent}%")
    
    assert p.is_on_sale is True
    assert p.calc_discount_percent == 20
    
    # 2. Test Validation
    p.discount_price = Decimal("1200.00")
    try:
        p.full_clean()
        print("FAIL: Validation did not catch high discount price")
    except Exception as e:
        print(f"SUCCESS: Validation caught error: {e}")
        
    # 3. Test Serializer Auto-Calculation
    data = {
        "category": cat.id,
        "name": "Auto Calc Prod",
        "slug": "auto-calc",
        "description": "test",
        "price": "1000.00",
        "set_discount_percent": 25,
        "stock": 10
    }
    
    serializer = ProductSerializer(data=data)
    if serializer.is_valid():
        print(f"Serializer valid. Calculated discount_price: {serializer.validated_data['discount_price']}")
        assert serializer.validated_data['discount_price'] == Decimal("750.00")
    else:
        print(f"Serializer errors: {serializer.errors}")

    # Cleanup
    cat.delete()
    print("--- Test Completed ---")

if __name__ == "__main__":
    test_discount_logic()
