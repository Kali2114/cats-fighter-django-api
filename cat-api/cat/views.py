"""
Views for cat APIs.
"""
from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Ability, Cat, FightingStyles
from cat import serializers


class CatViewSet(viewsets.ModelViewSet):
    """View for cat APIs."""
    serializer_class = serializers.CatDetailSerializer
    queryset = Cat.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve cats for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.CatSerializer
        return serializers.CatDetailSerializer

    def perform_create(self, serializer):
        """Create a new cat object."""
        serializer.save(user=self.request.user)


class AbilityViewSet(mixins.UpdateModelMixin,
                     mixins.ListModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    """Manage abilities in the database."""
    serializer_class = serializers.AbilitySerializer
    queryset = Ability.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-name')

class FightingStylesViewSet(mixins.UpdateModelMixin,
                            mixins.ListModelMixin,
                            mixins.DestroyModelMixin,
                            viewsets.GenericViewSet):
    """Manage fighting styles in the database."""
    serializer_class = serializers.FightingStylesSerializer
    queryset = FightingStyles.objects.all()
