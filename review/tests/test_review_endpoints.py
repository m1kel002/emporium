from unittest import TestCase
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from core.utils.test.test_utils import create_user, create_shop, create_product, create_review

REVIEWS_URL = reverse('review:review-list-create')

@pytest.mark.django_db
class TestReviewPublicEndpoints(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()

    def test_get_review(self):
        """should list reviews of a product"""
        shop = create_shop(self.user)
        product = create_product(user=self.user, shop=shop)
        create_review(self.user, product, message='foo', created_by=self.user)
        create_review(self.user, product, message='bar', created_by=self.user)
        res = self.client.get(REVIEWS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 2)
