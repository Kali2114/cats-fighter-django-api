"""
Tests for models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

from .. import models


def create_user(email='user@example.com', password='pass123'):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email, password)


class ModelTest(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating user with email."""
        email = 'test@example.com'
        password = 'test123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_normalized_email(self):
        """Test normalized email for new users."""
        sample_emails = [
            ['test1@ExAmPle.cOm', 'test1@example.com'],
            ['Test2@exaMPLe.cOM', 'Test2@example.com'],
            ['TEST3@EXAMpLE.COM', 'TEST3@example.com']
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'pass123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email(self):
        """Test creating user without an email raises error."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'pass123')

    def test_create_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'pass123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_cat(self):
        """Test creating a cat is successful."""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'test123',
        )
        cat = models.Cat.objects.create(
            user=user,
            name='sample cats name',
            description='sample description',
            weight=5,
            color='black',
            dangerous=True,
        )

        self.assertEqual(str(cat), cat.name)

    def test_create_ability(self):
        """Test creating ability successful."""
        user = create_user()
        ability = models.Ability.objects.create(
            user=user,
            name='Invisible'
        )
        self.assertEqual(str(ability), ability.name)
