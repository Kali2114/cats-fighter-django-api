"""
Tests for cat API.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Cat

from cat.serializers import CatSerializer, CatDetailSerializer


CAT_URL = reverse('cat:cat-list')


def detail_url(cat_id):
    """Create and return a cat detail url."""
    return reverse('cat:cat-detail', args=[cat_id])

def create_cat(user, **args):
    """Create and return simple cat object."""
    defaults = {
        'name': 'Blodly Cat',
        'description': 'He will get you in five seconds!',
        'weight': 5.5,
        'color': 'Blue',
        'dangerous': True,
    }
    defaults.update(**args)

    cat = Cat.objects.create(user=user, **defaults)
    return cat

def create_user(**kwargs):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**kwargs)


class PublicCatApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_authorisation_required(self):
        """Test auth is required to call API."""
        res = self.client.get(CAT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCatApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com', password='pass123')
        self.client.force_authenticate(self.user)

    def test_retrieve_cats(self):
        create_cat(user=self.user)
        create_cat(user=self.user)

        res = self.client.get(CAT_URL)

        cats = Cat.objects.all().order_by('-id')
        serializer = CatSerializer(cats, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_cat_list_limted_to_user(self):
        """Test list of cats is limited to authentication user."""
        other_user = create_user(email='other@example.com', password='pass123')
        create_cat(user=self.user)
        create_cat(user=other_user)

        res = self.client.get(CAT_URL)

        cats = Cat.objects.filter(user=self.user)
        serializer = CatSerializer(cats, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_cat_detail(self):
        """Test get cat detail."""
        cat = create_cat(user=self.user)

        url = detail_url(cat.id)
        res = self.client.get(url)

        serializer = CatDetailSerializer(cat)
        self.assertEqual(res.data, serializer.data)

    def test_create_cat(self):
        """Test creating a cat object."""
        data = {
        'name': 'Water Cat',
        'description': 'He will get you in five seconds!',
        'weight': 6,
        'color': 'Red',
        'dangerous': True,
        }
        res = self.client.post(CAT_URL, data)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        cat = Cat.objects.get(id=res.data['id'])
        for k, v in data.items():
            self.assertEqual(getattr(cat, k), v)
        self.assertEqual(cat.user, self.user)

    def test_partial_update(self):
        """Test partial update of a cat object."""
        cat = create_cat(
        user=self.user,
        name='Hello Boy',
        description='Grrr!',
        weight=7,
        color='Blue',
        dangerous=False,
        )

        data = {'weight': 8}
        url = detail_url(cat.id)
        res = self.client.patch(url, data)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        cat.refresh_from_db()
        self.assertEqual(cat.weight, data['weight'])
        self.assertEqual(cat.user, self.user)

    def test_full_update(self):
        """Test full update of cat object."""
        cat = create_cat(
        user=self.user,
        name='Hello Boy',
        description='Grrr!',
        weight=7,
        color='Blue',
        dangerous=False,
        )

        data = {
            'name': 'Hephaistos',
            'description': 'Amigo',
            'weight': 11,
            'color': 'Red',
            'dangerous': True
        }
        url = detail_url(cat.id)
        res = self.client.put(url, data)

        self.assertEqual(res.status_code, status.HTTP_200_OK),
        cat.refresh_from_db()
        for k, v in data.items():
            self.assertEqual(getattr(cat, k), v)
        self.assertEqual(cat.user, self.user)

    def test_update_user_error(self):
        """Test changing the cat user error."""
        other_user = create_user(email='user2@example.com', password='ssap321')
        cat = create_cat(user=self.user)
        data = {'user': other_user.id}
        url = detail_url(cat.id)
        self.client.patch(url, data)

        cat.refresh_from_db()
        self.assertEqual(cat.user, self.user)

    def test_delete_cat(self):
        """Test deleting cat object successful."""
        cat = create_cat(user=self.user)
        url = detail_url(cat.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Cat.objects.filter(id=cat.id).exists())

    def test_cat_other_users_error(self):
        """Test trying to delete another user cat gives error."""
        another_user = create_user(email='user2@example.com', password='ssap321')
        cat = create_cat(user=another_user)

        url = detail_url(cat.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(cat.user, another_user)
        self.assertTrue(Cat.objects.filter(id=cat.id).exists())

