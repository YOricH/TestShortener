# project/shortener/api/serializers.py
# Serializers for REST API.

from shortener.models import Direction, UserDirection
from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from uuid import UUID
import logging


logger = logging.getLogger(__name__)


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

        user_uuid = self.context['request'].data.get('user_uuid', None)
        subpart = validated_data.get('subpart', None)
        target = validated_data.get('target', None)

        direction, err_str = Direction.get_or_create_direction(subpart, target)

        if err_str is not None:
            raise ValidationError(detail={'subpart': err_str})

        if user_uuid:
            user_uuid = UUID(user_uuid)
            user_direction = UserDirection()
            user_direction.direction = direction
            user_direction.user_uuid = user_uuid

            user_direction.save()
            logger.debug(f'Save new UserDirection: {user_direction}')

        return direction


class UserDirectionSerializer(serializers.HyperlinkedModelSerializer):
    """Serializer for UserDirection model."""

    class Meta:
        model = UserDirection
        fields = ('direction', 'user_uuid', 'timestamp')
