"""
Test for fighting styles API.
"""
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import FightingStyles

from cat.serializers import FightingStylesSerializer


FIGHTING_STYLES_URL = reverse('cat:fightingstyles-list')


def detail_url(fighting_style_id):
    """Create and return a fighting style detail URL."""
    return reverse('cat:fightingstyles-detail', args=[fighting_style_id])

class FightingStylesApiTests(TestCase):
    """Test fighting styles API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_fighting_styles(self):
        """Test retrieving a fighting styles list"""
        FightingStyles.objects.create(name='WR', ground_allowed=True)
        FightingStyles.objects.create(name='MT', ground_allowed=False)

        res = self.client.get(FIGHTING_STYLES_URL)

        styles = FightingStyles.objects.all().order_by('-name')
        serializer = FightingStylesSerializer(styles ,many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_update_fighting_style(self):
        """Test updating a fighting style."""
        style = FightingStyles.objects.create(name='BJJ', ground_allowed=True)

        data = {'name': 'WR', 'ground_allowed': True}
        url = detail_url(style.id)
        res = self.client.patch(url, data)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        style.refresh_from_db()
        self.assertEqual(style.name, data['name'])

    def test_delete_fighting_style(self):
        """Test deleting a fighting style."""
        style = FightingStyles.objects.create(name='BX', ground_allowed=False)

        url = detail_url(style.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        styles = FightingStyles.objects.all()
        self.assertFalse(styles.exists())