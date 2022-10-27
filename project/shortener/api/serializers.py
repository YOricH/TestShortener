# project/shortener/api/serializers.py
# Serializers for REST API.

from project.shortener.models import Direction, UserDirection, get_set_user_uuid
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from rest_framework import serializers
from logging import getLogger


logger = getLogger(__name__)


class DirectionSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for Direction model."""

    class Meta:
        model = Direction
        fields = ('subpart', 'target', 'updated')

        extra_kwargs = {
            'subpart': {'required': False, 'validators': []},
        }

    def create(self, validated_data):
        """Updates or creates direction and user direction."""
        subpart = validated_data.get('subpart', None)
        target = validated_data.get('target', None)

        direction, err_str = Direction.get_or_create_direction(subpart, target)

        if err_str is not None:
            raise ValidationError(detail={'subpart': err_str})

        try:
            user_uuid = get_set_user_uuid(self.context.get('request'))
        except ValueError:
            return direction

        UserDirection.get_or_create_user_direction(user_uuid, direction)
        return direction


class UserDirectionSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for UserDirection model."""

    class Meta:
        model = UserDirection
        fields = ('direction', 'user_uuid', 'timestamp')

    def create(self, validated_data):
        """Updates or creates user direction."""
        direction = validated_data.get('direction', None)
        request = self.context.get('request')

        if not request or not hasattr(request, 'session'):
            user_direction = UserDirection()
            user_direction.direction = direction
            user_direction.save()
            return user_direction

        try:
            user_uuid = get_set_user_uuid(request)
        except ValueError:
            raise AuthenticationFailed(
                detail='Failed to set or get user id through session.'
            )

        user_direction = UserDirection.get_or_create_user_direction(
            user_uuid, direction
        )
        return user_direction
