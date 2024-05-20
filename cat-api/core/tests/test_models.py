"""
Tests for models.
"""
from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

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

    def test_create_fight_style_successful(self):
        """Test creating fighting style successful with valid name."""
        fighting_style = models.FightingStyles.objects.create(
            name='KB',
            ground_allowed=False,
        )
        self.assertEqual(str(fighting_style), fighting_style.name)

    def test_create_fight_style_unsuccessful(self):
        """Test creating fighting style unsuccessful with an invalid name."""
        with self.assertRaises(ValidationError):
            models.FightingStyles.objects.create(
                name='invalide name',
                ground_allowed=True,
            )

    @patch('core.models.uuid.uuid4')
    def test_cat_file_name_uuid(self, mock_uuid):
        """Test generating image path."""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.cat_image_file_path(None, 'example.jpg')

        self.assertEqual(file_path, f'uploads/cat/{uuid}.jpg')
