"""
Test for the abilities API.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ability, Cat

from cat.serializers import AbilitySerializer


ABILITIES_URL = reverse('cat:ability-list')


def detail_url(ability_id):
    """Create and return a tag detail url."""
    return reverse('cat:ability-detail', args=[ability_id])

def create_user(email='test@example.com', password='test123'):
    """Create and return the user."""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicAbilitiesApiTests(TestCase):
    """Test unauthenticated API request."""

    def setUp(self):
        self.client = APIClient()

    def test_authorization_required(self):
        """Test auth is required for retrieving abilities."""
        res = self.client.get(ABILITIES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateAbilitiesApiTests(TestCase):
    """Test authenticated API request."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_abilities(self):
        """Test retrieving a list of abilieties."""
        Ability.objects.create(user=self.user, name='Invisibility')
        Ability.objects.create(user=self.user, name='Fly')

        res = self.client.get(ABILITIES_URL)

        abilities = Ability.objects.all().order_by('-name')
        serializer = AbilitySerializer(abilities, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_abilities_limited_to_user(self):
        """Test list of abilities is limited to authenticated user."""
        user2 = create_user(email='user2@example.com')
        Ability.objects.create(user=user2, name='Ice Attacks')
        ability = Ability.objects.create(user=self.user, name='Paranormal Strength')

        res = self.client.get(ABILITIES_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ability.name)
        self.assertEqual(res.data[0]['id'], ability.id)

    def test_update_ability(self):
        """Test updating a ability."""
        ability = Ability.objects.create(user=self.user, name='Fireballs')

        data = {'name': 'Water Shield'}
        url = detail_url(ability.id)
        res = self.client.patch(url, data)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ability.refresh_from_db()
        self.assertEqual(ability.name, data['name'])

    def test_delete_ability(self):
        """Test deleting ability successful."""
        ability = Ability.objects.create(user=self.user, name='High Jumping')
        url = detail_url(ability.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ability.objects.filter(user=self.user).exists())

    def test_filter_abilities_assigned_to_cats(self):
        """Test listing abilities by those assigned to cats."""
        a1 = Ability.objects.create(user=self.user, name='Teleportation')
        a2 = Ability.objects.create(user=self.user, name='Illusion')
        cat = Cat.objects.create(
            user=self.user,
            name='Wolverine',
            description='Fast and furious.',
            weight=3.5,
            color='Black',
            dangerous=True,
        )
        cat.abilities.add(a1)

        res = self.client.get(ABILITIES_URL, {'assigned_only': 1})

        s1 = AbilitySerializer(a1)
        s2 = AbilitySerializer(a2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_abilities_unique(self):
        """Test filtered abilities return a unique list."""
        a = Ability.objects.create(user=self.user, name='Fireball')
        Ability.objects.create(user=self.user, name='Water Clones')
        cat1 = Cat.objects.create(
            user=self.user,
            name='Wolverine',
            description='Fast and furious.',
            weight=3.5,
            color='Black',
            dangerous=True,
        )
        cat2 = Cat.objects.create(
            user=self.user,
            name='Shinki',
            description='Gods Powers.',
            weight=3.5,
            color='Black',
            dangerous=True,
        )
        cat1.abilities.add(a)
        cat2.abilities.add(a)

        res = self.client.get(ABILITIES_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)