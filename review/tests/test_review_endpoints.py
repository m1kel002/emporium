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
        self.shop = create_shop(self.user)
        self.product = create_product(user=self.user, shop=self.shop)

    def test_get_review(self):
        """should list reviews of a product"""
        create_review(self.user, self.product, message='foo', created_by=self.user)
        create_review(self.user, self.product, message='bar', created_by=self.user)
        res = self.client.get(REVIEWS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['results']), 2)

    def test_unauthorized_create_review(self):
        """
        GIVEN an unauthenticated user
        WHEN the user tries to create review
        THEN an Unauthorized error should return
        """
        payload = dict(message='foo', rating='4.5')
        res = self.client.post(REVIEWS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

@pytest.mark.django_db
class TestReviewPrivateEndpoints(TestCase):

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.shop = create_shop(user=self.user)
        self.product = create_product(user=self.user, shop=self.shop)
        self.client.force_authenticate(user=self.user)

    def test_create_review(self):
        payload = dict(message='hello world', rating='4.5', product=self.product.id)
        res = self.client.post(REVIEWS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_review_blank_message(self):
        """
        GIVEN a review payload with no message
        WHEN a user creates a review
        THEN a review should be created with blank message
        """
        payload = dict(rating='4.5', product=self.product.id)
        res = self.client.post(REVIEWS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        review = res.data
        self.assertEqual(review['message'], '')

    def test_create_review_with_invalid_rating(self):
        """
        GIVEN a review payload with a rating greater than 5
        WHEN a user creates the review
        THEN a validation error should return
        """
        payload = dict(rating=6, product=self.product.id)

        res = self.client.post(REVIEWS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('rating', res.data)

    def test_create_review_with_invalid_rating1(self):
        """
        GIVEN a review payload with a rating less than 0
        WHEN a user creates the review
        THEN a validation error should return
        """
        payload = dict(rating=-1, product=self.product.id)
        res = self.client.post(REVIEWS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('rating', res.data)