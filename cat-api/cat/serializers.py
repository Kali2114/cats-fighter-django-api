"""
Serializers for cat APIs.
"""
from rest_framework import serializers

from core.models import Ability, Cat


class CatSerializer(serializers.ModelSerializer):
    """Serializer for cat objects."""

    class Meta:
        model = Cat
        fields = ['id', 'name', 'dangerous']
        read_only_fields = ['id']


class CatDetailSerializer(CatSerializer):
    """Serializer for cat detail."""

    class Meta(CatSerializer.Meta):
        fields = CatSerializer.Meta.fields + ['description', 'weight', 'color']


class AbilitySerializer(serializers.ModelSerializer):
    """Serializer for cat objects abilities."""
    class Meta:
        model = Ability
        fields = ['id', 'name']
        read_only_fields = ['id']
