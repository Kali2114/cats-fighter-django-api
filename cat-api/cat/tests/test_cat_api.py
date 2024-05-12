"""
Tests for cat API.
"""
from django.forms.models import model_to_dict
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Cat,
    Ability,
    FightingStyles,
)

from cat.serializers import (
    CatSerializer,
    CatDetailSerializer,
    FightingStylesSerializer,
)


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

    def test_create_cat_with_new_ability(self):
        """Test creating a cat with new ability."""
        data = {
            'name': 'Char Cat',
            'description': 'Fast and Furious',
            'weight': 7,
            'color': 'Blue',
            'dangerous': False,
            'abilities': [{'name': 'Lighting Style'}, {'name': 'Teleportation'}]
        }
        res = self.client.post(CAT_URL, data, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        cats = Cat.objects.filter(user=self.user)
        self.assertEqual(cats.count(), 1)
        cat = cats[0]
        self.assertEqual(cat.abilities.count(), 2)
        for ability in data['abilities']:
            exists = cat.abilities.filter(
                user=self.user,
                name=ability['name'],
            ).exists()
            self.assertTrue(exists)

    def test_creating_cat_with_existing_abilities(self):
        """Test creating a cat with existing ability."""
        ability_stone_body = Ability.objects.create(user=self.user, name='Stone Body')
        data = {
            'name': 'Dark Cat',
            'description': 'Mysterious cat...',
            'weight': 9,
            'color': 'Dark',
            'dangerous': True,
            'abilities': [{'name': 'Quick Attacks'}, {'name': 'Stone Body'}]
        }
        res = self.client.post(CAT_URL, data, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        cats = Cat.objects.filter(user=self.user)
        self.assertEqual(cats.count(), 1)
        cat = cats[0]
        self.assertEqual(cat.abilities.count(), 2)
        self.assertIn(ability_stone_body, cat.abilities.all())
        for ability in data['abilities']:
            exists = cat.abilities.filter(
                user=self.user,
                name=ability['name']
            )
            self.assertTrue(exists)

    def test_create_ability_on_update(self):
        """Test creating ability when updating a cat."""
        cat = create_cat(user=self.user)

        data = {'abilities': [{'name': 'Earthquake'}]}
        url = detail_url(cat.id)
        res = self.client.patch(url, data, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_ability = Ability.objects.get(user=self.user, name='Earthquake')
        self.assertIn(new_ability, cat.abilities.all())

    def test_update_ability_assign_in(self):
        """Test assigning an existing ability when updating a cat."""
        ability_fire_punch = Ability.objects.create(user=self.user, name='Fire Punch')
        cat = create_cat(user=self.user)
        cat.abilities.add(ability_fire_punch)

        ability_ice_shield = Ability.objects.create(user=self.user, name='Ice Shield')
        data = {'abilities': [{'name': 'Ice Shield'}]}
        url = detail_url(cat.id)
        res = self.client.patch(url, data, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(ability_ice_shield, cat.abilities.all())
        self.assertNotIn(ability_fire_punch, cat.abilities.all())

    def test_clear_cat_abilities(self):
        """Test clearing cat abilities."""
        ability = Ability.objects.create(user=self.user, name='Wood Style')
        cat = create_cat(user=self.user)
        cat.abilities.add(ability)

        data = {'abilities': []}
        url = detail_url(cat.id)
        res = self.client.patch(url, data, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(cat.abilities.count(), 0)

    def test_create_cat_with_new_fighting_style(self):
        """Test creating a cat with new fighting style."""
        data = {
            'name': 'Blody Cat',
            'description': 'He will get you in five seconds!',
            'weight': 5.5,
            'color': 'Blue',
            'dangerous': True,
            'fighting_styles': [{'name': 'KB', 'ground_allowed': False},
                                {'name': 'MT', 'ground_allowed': False},
                                ]
        }
        res = self.client.post(CAT_URL, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        cats = Cat.objects.all()
        self.assertEqual(cats.count(), 1)
        cat = cats[0]
        self.assertEqual(cat.fighting_styles.count(), 2)
        for styles in data['fighting_styles']:
            exists = cat.fighting_styles.filter(
                name=styles['name'],
                ground_allowed=styles['ground_allowed']
            ).exists()
            self.assertTrue(exists)

    def test_create_cat_with_existing_fight_style(self):
        """Test creating a cat with existing fight style."""
        style = FightingStyles.objects.create(name='BJJ', ground_allowed=True)
        style_dict = model_to_dict(style, fields=['name', 'ground_allowed'])
        data = {
            'name': 'Bloody Cat',
            'description': 'He will get you in five seconds!',
            'weight': 5.5,
            'color': 'Blue',
            'dangerous': True,
            'fighting_styles': [style_dict]
        }
        res = self.client.post(CAT_URL, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Cat.objects.count(), 1)
        cat = Cat.objects.get()
        self.assertIn(style, cat.fighting_styles.all())

    def test_create_fighting_style_on_update(self):
        """Test creating a fighting style when updating a cat."""
        cat = create_cat(user=self.user)

        data = {'fighting_styles': [{'name': 'BJJ', 'ground_allowed': True}]}
        url = detail_url(cat.id)
        res = self.client.patch(url, data, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(cat.fighting_styles.count(), 1)
        new_style = FightingStyles.objects.get(name='BJJ')
        self.assertIn(new_style, cat.fighting_styles.all())

    def test_update_cat_assign_fighting_style(self):
        """Test assigning an existing fighting style when update a cat."""
        style1 = FightingStyles.objects.create(name='BX', ground_allowed=False)
        cat = create_cat(user=self.user)
        cat.fighting_styles.add(style1)

        style2 = FightingStyles.objects.create(name='WR', ground_allowed=True)
        data = {'fighting_styles': [{'name': 'WR', 'ground_allowed': True}]}
        url = detail_url(cat.id)
        res = self.client.patch(url, data, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(style2, cat.fighting_styles.all())
        self.assertNotIn(style1, cat.fighting_styles.all())

    def test_clear_cat_fighting_styles(self):
        fighting_style = FightingStyles.objects.create(name='MT', ground_allowed=False)
        cat = create_cat(user=self.user)
        cat.fighting_styles.add(fighting_style)

        data = {'fighting_styles': []}
        url = detail_url(cat.id)
        res = self.client.patch(url, data, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(cat.fighting_styles.count(), 0)
        self.assertFalse(cat.fighting_styles.filter(id=fighting_style.id).exists())
