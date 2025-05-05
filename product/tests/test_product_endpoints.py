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

    def test_get_product_by_category(self):
        shop = create_shop(user=self.user)
        create_product(user=self.user, shop=shop, category='test')
        create_product(user=self.user, shop=shop, category='test')
        res = self.client.get(products_url_with_query_param(category='test'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 2)


@pytest.mark.django_db
class TestProductSecuredEndpoints(TestCase):

    def setUp(self):
        self.user = create_user(email='user@example.com', password='test123')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.shop = create_shop(self.user)

    def test_create_product(self):
        """GIVEN a product data with VALID data
        WHEN a user tries to create the product
        THEN the product should be created"""
        payload = dict(name='Test Product',
                       quantity=1,
                       price=20,
                       shop=self.shop.id,
                       variations=['var1', 'var2']
                       )
        res = self.client.post(PRODUCTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        product = Product.objects.get(id=res.data['id'])
        self.assertIsNotNone(product)
        self.assertTrue(hasattr(product, 'id'))
        self.assertEqual(res.data['id'], product.id)

    def test_create_product_with_invalid_price(self):
        """"
        GIVEN a product data with invalid price
        WHEN user tries to create the product
        THEN the product should NOT be created and return an error
        """
        payload = dict(name='Test Product', price=-1, quantity=20, shop=self.shop.id)
        res = self.client.post(PRODUCTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('price', res.data)

    def test_create_product_invalid_quantity(self):
        """
        GIVEN a product data with invalid quantity
        WHEN a user tries to create the product
        THEN the product should NOT be created and return an error
        """
        payload = dict(name='Test Product', price=20, quantity=-1, shop=self.shop.id)
        res = self.client.post(PRODUCTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('quantity', res.data)

    def test_create_product_invalid_name(self):
        """
        GIVEN a product data with invalid name
        WHEN a user tries to create the product
        THEN the product should NOT be created and return an error
        """
        payload = dict(name=' ', price=1, quantity=20, shop=self.shop.id)
        res = self.client.post(PRODUCTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', res.data)

    def test_create_product_duplicate_variations(self):
        """
        GIVEN a product data with duplicate variations
        WHEN a user tries to create the product
        THEN the product should NOT be created and return an error
        """
        payload = dict(name='Test Product', price=20, quantity=20, shop=self.shop.id,
                       variations=['var1', 'var1'])
        res = self.client.post(PRODUCTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('variations', res.data)

    def test_create_product_with_invalid_rating(self):
        """
        GiVEN a product data with invalid rating
        WHEN user tries to create the product
        THEN the product should not be created and return an error
        """
        payload = dict(name='Test Product', price=10, rating=-1, quantity=1, shop=self.shop.id)
        res = self.client.post(PRODUCTS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('rating', res.data)