from unittest import TestCase

from rest_framework.test import APIClient
from core.models import Shop, Product, Cart
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
import pytest
from cart.serializers import CartSerializer

CART_URL = reverse('cart:cart')

def get_cart_detail_url(id):
    return reverse('cart:cart-detail', args=[id])

def create_user(**params):
    defaults = dict(
        name='Test User',
        email='user99@example.com',
        password='test123'
    )
    get_user_model().objects.all().delete()

    defaults.update(params)
    return get_user_model().objects.create_user(**defaults)

def create_shop(**params):
    defaults = dict(
        name='Test Shop'
    )
    defaults.update(params)
    return Shop.objects.create(**defaults)

def create_product(**params):
    defaults = dict(
        name='Product1',
        quantity=1,
        price=2.25
    )
    defaults.update(params)
    return Product.objects.create(**defaults)

def create_cart(product, user):
    return Cart.objects.create(product=product, user=user, quantity=1, created_by=user)

def init_data(user, **params):
    shop = create_shop(**params.get('shop', {}), user=user, created_by=user)
    product = create_product(**params.get('product', {}), shop=shop, created_by=user)
    return shop, product

@pytest.mark.django_db
class TestCartPrivateEndpoints(TestCase):

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_add_to_cart(self):
        """
        given user is authenticated
        when user adds product to cart
        then cart record should be created
        """
        _, product = init_data(user=self.user)
        payload = dict(
            quantity=1,
            product=product.id,
            user=self.user
        )

        res = self.client.post(CART_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        expected = dict(
            quantity=1,
            product=dict(id=product.id,
                         name=product.name,
                         price=str(product.price),
                         image=None)
        )
        self.assertEqual(res.data | expected, res.data)

    def test_update_cart(self):
        """
        given user is authenticated
        when user updates existing cart
        then cart record should be updated
        """
        _, product = init_data(user=self.user)
        cart = create_cart(product=product, user=self.user)
        update_payload = dict(quantity=10)
        res = self.client.patch(get_cart_detail_url(cart.id), update_payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['quantity'], 10)

    def test_delete_cart(self):
        """
        given user is authenticated
        when user deletes existing cart record
        then cart record should be deleted
        """
        _, product = init_data(user=self.user)
        cart = create_cart(product=product, user=self.user)
        res = self.client.delete(get_cart_detail_url(cart.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(Cart.objects.filter(id=cart.id).exists())

    def test_get_list_cart(self):
        """
        given user is authenticated
        when there are existing cart records associated to user
        then user should get list of cart records
        """
        _, product = init_data(user=self.user)
        create_cart(product=product, user=self.user)
        res = self.client.get(CART_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 1)

    def test_get_detail_cart(self):
        """
        given user is authenticated
        when there are existing cart record
        then user should be able to get detailed cart record
        """
        _, product = init_data(user=self.user)
        cart = create_cart(product=product, user=self.user)
        res = self.client.get(get_cart_detail_url(cart.id))
        serializer = CartSerializer(cart)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
