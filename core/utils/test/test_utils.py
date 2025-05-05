from core.models import Shop, Product, Review
from django.contrib.auth import get_user_model

def create_user(**params):
    defaults = dict(email='user@example.com', password='test123', name='Test User')
    defaults.update(params)
    return get_user_model().objects.create_user(**defaults)

def create_shop(user, **params):
    defaults = dict(name='Test Shop', description='Hello world')
    defaults.update(params)
    return Shop.objects.create( user=user, created_by=user, **defaults)

def create_product(user, shop, **params):
    defaults = dict(name='Test Product', price='20.50', quantity=10)
    defaults.update(params)
    return Product.objects.create(created_by=user, shop=shop, **defaults)

def create_review(user, product, **params):
    defaults = dict(rating='2.5', message='Hello World')
    defaults.update(params)
    return Review.objects.create(user=user, product=product, **defaults)