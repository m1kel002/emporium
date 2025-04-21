from unittest import TestCase
from django.urls import reverse
from core.models import Product, Shop
import pytest
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from urllib.parse import urlencode
from product.serializers import ProductSerializer

PRODUCTS_URL = reverse('product:product-list-create')

def products_url_with_query_param(**query_param):
    return f'{PRODUCTS_URL}?{urlencode(query_param)}'

def get_product_detail_url(id):
    return reverse('product:product-detail', args=[id])

def create_user(**params):
    return get_user_model().objects.create_user(**params)

def create_shop(user, **params):
    defaults = dict(
        name='Shop1',
    )
    defaults.update(params)
    return Shop.objects.create(user=user, created_by=user, **defaults)

def create_product(user, **params):
    defaults = dict(
        name='Product1',
        price=1.2,
        quantity=5
    )
    defaults.update(params)
    return Product.objects.create(created_by=user, **defaults)

@pytest.mark.django_db
class TestProductEndpoints(TestCase):

    def setUp(self):
        self.user = create_user(email='user@example.com', password='test123', name='Test User')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_products_by_shop(self):
        """should list products under a shop"""
        shop = create_shop(user=self.user)
        other_shop = create_shop(user=self.user)
        create_product(user=self.user, shop=shop)
        create_product(user=self.user, name='Product2', shop=shop)
        other_product = create_product(user=self.user, name='Product3', shop=other_shop)
        res = self.client.get(products_url_with_query_param(shop=shop.id))
        products = res.data['results']
        product_ids = [product['id'] for product in products]
        self.assertNotIn(other_product.id, product_ids)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


    def test_list_products_by_search(self):
        """should list products based on keywords set in search"""
        search_keywords = 'earch'
        shop = create_shop(user=self.user)
        create_product(user=self.user, shop=shop, quantity=1)
        product_to_find = create_product(user=self.user, name='Search Me', shop=shop, quantity=1)
        res = self.client.get(products_url_with_query_param(search=search_keywords))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        product_ids = [product['id'] for product in res.data['results']]
        self.assertIn(product_to_find.id, product_ids)

    def test_list_products_with_stocks(self):
        """should only list products with quantity greater than 0"""
        shop = create_shop(user=self.user)
        create_product(user=self.user, shop=shop, quantity=1)
        invalid_product = create_product(user=self.user, name='0 Product', shop=shop, quantity=0)
        res = self.client.get(products_url_with_query_param(shop=shop.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        product_ids = [product['id'] for product in res.data['results']]
        self.assertNotIn(invalid_product.id, product_ids)

    def test_get_product_detail(self):
        shop = create_shop(user=self.user)
        product = create_product(user=self.user, shop=shop)
        res = self.client.get(get_product_detail_url(product.id))
        serializer = ProductSerializer(product)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)