"""
Serializers for cat APIs.
"""
from rest_framework import serializers

from core.models import Ability, Cat, FightingStyles


class FightingStylesSerializer(serializers.ModelSerializer):
    """Serializer for cat objects fighting styles."""
    class Meta:
        model = FightingStyles
        fields = ['id', 'name', 'ground_allowed']
        read_only_fields = ['id']


class AbilitySerializer(serializers.ModelSerializer):
    """Serializer for cat objects abilities."""
    class Meta:
        model = Ability
        fields = ['id', 'name']
        read_only_fields = ['id']


class CatSerializer(serializers.ModelSerializer):
    """Serializer for cat objects."""
    abilities = AbilitySerializer(many=True, required=False)
    fighting_styles = FightingStylesSerializer(many=True, required=False)

    class Meta:
        model = Cat
        fields = ['id', 'name', 'dangerous', 'abilities', 'fighting_styles']
        read_only_fields = ['id']

    def _get_or_create_abilities(self, abilities, cat):
        """Handle getting or creating abilities."""
        auth_user = self.context['request'].user
        for ability in abilities:
            ability_obj, created = Ability.objects.get_or_create(
                user=auth_user,
                **ability
            )
            cat.abilities.add(ability_obj)

    def _get_or_create_fighting_styles(self, fighting_styles, cat):
        """Handle getting or creating fighting styles."""
        for style in fighting_styles:
            style_obj, created = FightingStyles.objects.get_or_create(
                **style
            )
            cat.fighting_styles.add(style_obj)

    def create(self, validated_data):
        """Create and return a cat object."""
        abilities = validated_data.pop('abilities', [])
        fighting_styles = validated_data.pop('fighting_styles', [])
        cat = Cat.objects.create(**validated_data)
        self._get_or_create_abilities(abilities, cat)
        self._get_or_create_fighting_styles(fighting_styles, cat)

        return cat

    def update(self, instance, validated_data):
        """Update and return a cat object."""
        abilities = validated_data.pop('abilities', None)
        fighting_styles = validated_data.pop('fighting_styles', None)
        if abilities is not None:
            instance.abilities.clear()
            self._get_or_create_abilities(abilities, instance)

        if fighting_styles is not None:
            instance.fighting_styles.clear()
            self._get_or_create_fighting_styles(fighting_styles, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class CatDetailSerializer(CatSerializer):
    """Serializer for cat detail."""

    class Meta(CatSerializer.Meta):
        fields = CatSerializer.Meta.fields + ['description', 'weight', 'color']
