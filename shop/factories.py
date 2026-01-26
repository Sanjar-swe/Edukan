import factory
from shop.models import Category, Product

class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category
        django_get_or_create = ('slug',)

    name = factory.Faker('word')
    slug = factory.Faker('slug')

class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    category = factory.SubFactory(CategoryFactory)
    name = factory.Faker('word')
    slug = factory.Faker('slug')
    description = factory.Faker('sentence')
    price = 1000.00
    stock = 10
    is_active = True

from .models import Review
from users.factories import UserFactory

class ReviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Review

    product = factory.SubFactory(ProductFactory)
    user = factory.SubFactory(UserFactory)
    rating = factory.Faker('random_int', min=1, max=5)
    comment = factory.Faker('paragraph')