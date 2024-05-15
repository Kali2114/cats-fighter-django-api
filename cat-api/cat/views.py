"""
Views for cat APIs.
"""
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
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
        elif self.action == 'upload_image':
            return serializers.CatImageSerializer

        return serializers.CatDetailSerializer

    def perform_create(self, serializer):
        """Create a new cat object."""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        cat = self.get_object()
        serializer = self.get_serializer(cat, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
