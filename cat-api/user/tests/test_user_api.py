"""
Tests for the user API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**args):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**args)


class PublicUserApiTest(TestCase):
    """Test the public features of the user API."""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_ok(self):
        """Test creating a user is ok."""
        data = {
            'email': 'test@example.com',
            'password': 'pass123',
            'name': 'Test Name',
        }
        res = self.client.post(CREATE_USER_URL, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=data['email'])

        self.assertTrue(user.check_password(data['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_error(self):
        """Test error returned if user with email exists."""
        data = {
            'email': 'test@example.com',
            'password': 'pass123',
            'name': 'Test Name',
        }
        create_user(**data)
        res = self.client.post(CREATE_USER_URL, data)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Tests an error is returned if password is less than 5 chars."""
        data = {
            'email': 'test@example.com',
            'password': 'qw',
            'name': 'Test Name'
        }
        res = self.client.post(CREATE_USER_URL, data)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user = get_user_model().objects.filter(
            email=data['email']
        ).exists()
        self.assertFalse(user)

    def test_create_token_for_user(self):
        """Test generated token for register user."""
        user = {
            'email': 'test@example.com',
            'password': 'pass123',
            'name': 'Test Name',
        }
        create_user(**user)

        data = {
            'email': user['email'],
            'password': user['password'],
            'name': user['name'],
        }
        res = self.client.post(TOKEN_URL, data)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test returns error when credentials invalid."""
        create_user(email='test@example.com', password='test123')

        data = {'email': 'tset@example.com', 'password': 'tset321'}
        res = self.client.post(TOKEN_URL, data)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_with_blank_password(self):
        """Test returns error when password is blank."""
        data = {'email': 'test@example.com', 'password': ''}
        res = self.client.post(TOKEN_URL, data)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test authentication is required for users."""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API requests authentication."""

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='pass123',
            name='Test Name'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_ok(self):
        """Test retrieving profile for logged user."""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'email': self.user.email,
            'name': self.user.name,
        })

    def test_post_me_not_allowed(self):
        """Test POST is not allowed for the 'me' endpoint"""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user."""
        data = {'name': 'New Name', 'password': 'newpass123'}

        res = self.client.patch(ME_URL, data, format='json')

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, data['name'])
        self.assertTrue(self.user.check_password(data['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
