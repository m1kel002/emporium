from unittest import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
import pytest

def create_user(**params):
    return get_user_model().objects.create_user(**params)

CREATE_USER_URL = reverse('user:create')
ME_URL = reverse('user:me')

@pytest.mark.django_db
class TestApiEndpoints(TestCase):

    def setUp(self):
        self.client = APIClient()

    def tearDown(self):
        get_user_model().objects.all().delete()

    def test_create_user(self):
        payload = dict(email='user@example.com', name='User1', password='test123')
        res = self.client.post(CREATE_USER_URL, payload)

        user = get_user_model().objects.get(email=payload['email'])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_email_exists_error(self):
        payload = dict(email='user@example.com', name='Test User', password='test123')
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_password_too_short(self):
        payload = dict(email='user@example.com', name='Test User', password='te')
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_retrieve_user_unauthorized(self):
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


@pytest.mark.django_db
class TestUserPrivateEndpoints(TestCase):

    def setUp(self):
        self.user = create_user(name='Test User', email='user@example.com', password='test123')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_user_success(self):
        expected_user_data = dict(name='Test User', email='user@example.com')
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data | expected_user_data, res.data)

    def test_patch_name_success(self):
        payload = dict(name='UpdatedTest User')
        res = self.client.patch(ME_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data | payload, res.data)
