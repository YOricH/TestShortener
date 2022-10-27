# project/shortener/api/viewsets.py
# Endpoints for REST API.

from .serializers import DirectionSerializer, UserDirectionSerializer
from project.shortener.models import Direction, UserDirection, get_set_user_uuid
from rest_framework import viewsets
from rest_framework import mixins
from uuid import UUID
from logging import getLogger


logger = getLogger(__name__)


class DirectionViewSet(
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    API endpoint that allows directions to be viewed or edited.
    """

    queryset = Direction.objects.all()
    serializer_class = DirectionSerializer

    def get_queryset(self):
        get_set_user_uuid(self.request)
        return self.queryset


class UserDirectionViewSet(
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    API endpoint that allows user directions to be viewed or edited.
    Only the records of the current user are displayed (according to the session).
    """

    queryset = UserDirection.objects.all()
    serializer_class = UserDirectionSerializer

    def get_queryset(self):
        """
        Restricts the returned user directions to a given user UUID (in the session)
        """
        user_uuid = get_set_user_uuid(self.request)

        if user_uuid is None:
            return UserDirection.objects.none()

        try:
            uuid_field = UUID(user_uuid)
        except Exception as e:
            logger.exception(f'Invalid user_uuid {user_uuid}: {type(e)} - {str(e)}')
            return UserDirection.objects.none()

        return UserDirection.objects.filter(user_uuid=uuid_field)
