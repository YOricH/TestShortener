# project/shortener/api/viewsets.py
# Endpoints for REST API.

from .serializers import DirectionSerializer, UserDirectionSerializer
from shortener.models import Direction, UserDirection
from rest_framework import viewsets
from rest_framework import mixins
import logging
import uuid


logger = logging.getLogger(__name__)


class DirectionViewSet(mixins.UpdateModelMixin, mixins.CreateModelMixin, mixins.ListModelMixin,
                       mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    API endpoint that allows directions to be viewed or edited.
    """
    queryset = Direction.objects.all()
    serializer_class = DirectionSerializer


class UserDirectionViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    API endpoint that allows user directions to be viewed or edited.
    """
    queryset = UserDirection.objects.all()
    serializer_class = UserDirectionSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned user directions to a given user UUID,
        by filtering against a `user_uuid` query parameter in the URL.
        """
        queryset = UserDirection.objects.all()
        user_uuid = self.request.query_params.get('user_uuid', None)

        if user_uuid is not None:

            try:
                uuid.UUID(user_uuid)
            except Exception as e:
                logger.exception(f'Invalid user_uuid: {type(e)} - {str(e)}')
                return ''

            queryset = queryset.filter(user_uuid=user_uuid)

        return queryset
