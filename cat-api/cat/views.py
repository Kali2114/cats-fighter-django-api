"""
Views for cat APIs.
"""
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes
)
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Ability, Cat, FightingStyles
from cat import serializers


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'abilities',
                OpenApiTypes.STR,
                description='Comma separated list of IDs to filter',
            ),
            OpenApiParameter(
                'fighting_styles',
                OpenApiTypes.STR,
                description='Comma separated list of fighting styles to filter'
            )
        ]
    )
)
class CatViewSet(viewsets.ModelViewSet):
    """View for cat APIs."""
    serializer_class = serializers.CatDetailSerializer
    queryset = Cat.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _params_to_ints(self, qs):
        """Convert a list of strings to integers."""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieve cats for authenticated user."""
        abilities = self.request.query_params.get('abilities')
        fighting_styles = self.request.query_params.get('fighting_styles')
        queryset = self.queryset
        if abilities:
            abilities_ids = self._params_to_ints(abilities)
            queryset = queryset.filter(abilities__id__in=abilities_ids)
        if fighting_styles:
            fighting_styles_ids = self._params_to_ints(fighting_styles)
            queryset = queryset.filter(fighting_styles__id__in=fighting_styles_ids)

        return queryset.filter(
            user=self.request.user
        ).order_by('-id').distinct()

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


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                OpenApiTypes.INT, enum=[0, 1],
                description='Filter by items assigned to cats.'
            )
        ]
    )
)
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
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(cat__isnull=False)

        return queryset.filter(
            user=self.request.user
        ).order_by('-name').distinct()


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                OpenApiTypes.INT, enum=[0, 1],
                description='Filter by items assigned to cats.'
            )
        ]
    )
)
class FightingStylesViewSet(mixins.UpdateModelMixin,
                            mixins.ListModelMixin,
                            mixins.DestroyModelMixin,
                            viewsets.GenericViewSet):
    """Manage fighting styles in the database."""
    serializer_class = serializers.FightingStylesSerializer
    queryset = FightingStyles.objects.all()

    def get_queryset(self):
        """Filter queryset to authenticated user."""
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(cat__isnull=False)

        return (queryset
                .order_by('-name').distinct())

