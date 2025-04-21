from unittest import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import Shop
from rest_framework import status
import pytest

SHOPS_URL = reverse('shop:shop-list')
CREATE_SHOP_URL = reverse('shop:create')

def create_user(**params):
    defaults = dict(email='user@example.com',
                            password='test123',
                            name='Test User')
    defaults.update(params)
    return get_user_model().objects.create_user(**defaults)

def create_shop(user, **params):
    defaults = dict(
        name='Sample Shop',
        description='This is a sample shop'
    )
    defaults.update(params)
    return Shop.objects.create(user=user, created_by=user, **defaults)

@pytest.mark.django_db
class TestShopPublicEndpoints(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_list_shop(self):
        """Should return list of shops"""
        user_payload = dict(email='user@example.com',
                            password='test123',
                            name='Test User')
        user = create_user(**user_payload)
        create_shop(user=user,
                    name='Shop1')
        res = self.client.get(SHOPS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

    def test_list_shop_with_filters(self):
        """should return filtered shops"""
        user = create_user()
        create_shop(user=user,
                    name='Shop1')
        create_shop(user=user,
                    name='Shoptest')
        query_params = dict(name='test')
        res = self.client.get(SHOPS_URL, query_params)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)

@pytest.mark.django_db
class TestShopPrivateEndpoints(TestCase):

    def setUp(self):
        self.user = create_user(email='user@example.com',
                                password='test123',
                                name='Test User')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_shop(self):
        payload = dict(name='Shop1', user=self.user)
        res = self.client.post(CREATE_SHOP_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        shop = Shop.objects.get(id=res.data['id'])
        for k, v in payload.items():
                self.assertEqual(getattr(shop, k), v)
        self.assertEqual(shop.user, self.user)

    def test_create_shop_with_duplicate_name(self):
        payload = dict(name='Shop1', user=self.user)
        create_shop(user=self.user, name='Shop1')
        res = self.client.post(CREATE_SHOP_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        error_fields = res.data
        self.assertIn('name', error_fields)

    def test_create_shop_with_empty_name(self):
        payload = dict(name='', user=self.user)
        res = self.client.post(CREATE_SHOP_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        error_fields = res.data
        self.assertIn('name', error_fields)
