"""
Serializers for cat APIs.
"""
from rest_framework import serializers

from core.models import Cat


class CatSerializer(serializers.ModelSerializer):
    """Serializer for cat objects."""

    class Meta:
        model = Cat
        fields = ['id', 'name', 'description',
                  'weight', 'color', 'dangerous']
        read_only_fields = ['id']