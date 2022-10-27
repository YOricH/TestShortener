# project/shortener/models.py
# All models of the shortener app are here.

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from datetime import datetime, timedelta, timezone
from random import random
from uuid import UUID, uuid4
from logging import getLogger
from hashlib import md5


logger = getLogger(__name__)


def get_set_user_uuid(request_data):
    """
    Gets or sets and returns the ID of the user in the session.

    Keywords arguments:
    request_data -- object with request data

    Return value:
    user_uuid -- str
    """
    if not request_data or not hasattr(request_data, 'session'):
        err_str = (
            f'The value of parameter "{request_data}" is incorrect: {request_data}'
        )
        logger.error(err_str)
        raise ValueError(err_str)

    user_uuid = request_data.session.get('user_uuid', None)
    logger.debug(f'Session.get(user_uuid)={user_uuid}')

    if not user_uuid:
        user_uuid = str(uuid4())
        request_data.session['user_uuid'] = user_uuid
        logger.debug(f'Set new user_uuid={user_uuid}')

    return user_uuid


class Direction(models.Model):
    """This class represents a redirect from 'target' to 'domain/subpart' in DB."""

    subpart = models.CharField(primary_key=True, max_length=30)
    target = models.URLField(max_length=2000)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    @staticmethod
    def generate_subpart(target, random_sub=False, alphabet=settings.BASE_ENCODING):
        """Generates and returns tne new subpart for the target link. It takes a part of md5-hash of the 'target' string
        end encodes it with 'alphabet'.

        Keywords arguments:
        target -- link for shorting. str
        random_sub -- if True, function uses random hash. Boolean
        alphabet -- the string of chars for encoding. str

        Return value:
        subpart -- the short alias for target. str
        """
        if not target:
            err_str = 'The argument "target" is empty!'
            logger.error(err_str)
            raise ValueError(err_str)

        if random_sub:
            hash_str = str(
                md5(str(random()).encode('utf-8')).hexdigest()[
                    : settings.SUBPART_HASH_LEN
                ]
            )
        else:
            encoded_target = target.encode('utf-8')
            hash_md5 = md5(encoded_target)
            hash_str = str(hash_md5.hexdigest()[: settings.SUBPART_HASH_LEN])

        try:
            num = int(hash_str, 16)
        except (ValueError, TypeError) as e:
            logger.exception(f'"hash_str" to int casting error: {type(e)} - {str(e)}')
            raise

        result = ''
        base_len = len(alphabet)

        while num:
            num, rem = divmod(num, base_len)
            result = alphabet[rem] + result

        return result

    def get_rest_of_life(self):
        """Returns tne rest of life in DB of this direction in seconds.

        Return value:
        int -- rest of life.
        """
        delta = timedelta(seconds=settings.DIRECTION_LIFETIME_SEC)
        now = datetime.now(timezone.utc)
        return (self.updated + delta - now).total_seconds()

    def can_update(self, new_target):
        """
        # If Celery is not working or there was an error we can update and use the expired direction.

        Keywords arguments:
        new_target -- link for shorting. str

        Return value:
        bool - True if we can update this direction.
        """
        if self.get_rest_of_life() > 0:
            return False

        logger.warning(f'Edit the existing direction: "{self}"')
        self.target = new_target
        self.save()
        UserDirection.objects.filter(direction__subpart=self.subpart).delete()
        logger.warning(f'The existing direction was updated: "{self}"')
        return True

    @staticmethod
    def get_or_create_direction(subpart, target):
        """Gets and updates or creates direction. If creation failed, raises ValueError.

        Keywords arguments:
        subpart -- the short alias for target. str
        target -- link for shorting. str

        Return value:
        direction, err_str -- Direction instance and error string.
        """
        err_str = None
        user_subpart = False
        log_message = 'created'

        if not subpart:
            subpart = Direction.generate_subpart(target)
        else:
            user_subpart = True

        direction, created = Direction.objects.get_or_create(
            subpart=subpart, defaults={'target': target}
        )

        if direction.target == target:
            if not created:
                direction.save()  # To update the lifetime
                log_message = 'updated'
            logger.debug(f'The direction "{direction}" has {log_message}.')
            return direction, err_str

        # Next, we process the case when direction.target != target
        if direction.can_update(target):
            return direction, err_str

        if user_subpart:
            err_str = f'The subpart "{subpart}" is already used!'
            logger.warning(err_str)
            return direction, err_str

        # The subpart is already used.
        # The chance of getting here is extremely small, but processing is still necessary.
        # Request in a loop. It's a bad solution, but such a situation is almost impossible.
        logger.warning(f'The subpart "{subpart}" is already used!')

        for i in range(settings.LAST_TRY_NUM):
            subpart = Direction.generate_subpart(target, True)

            direction, created = Direction.objects.get_or_create(
                subpart=subpart, defaults={'target': target}
            )

            if direction.target == target:
                if not created:
                    direction.save()  # To update the lifetime
                logger.debug(f'Save the direction: "{direction}"')
                break

            if direction.can_update(target):
                break

        if direction.target != target:  # If nothing helped
            err_str = (
                f'The subpart "{subpart}" is already used! '
                f'Shuffling did not help. {target} was not recorded in the DB.'
            )
            logger.error(err_str)
            raise ValueError(err_str)

        return direction, err_str

    @staticmethod
    def get_threshold_date():
        """Returns the date less than which the field "updated" records in the database should not be.

        Return value:
        datetime -- date to search for obsolete entries.

        """
        delta = timedelta(seconds=settings.DIRECTION_LIFETIME_SEC)
        now = datetime.now(timezone.utc)

        return now - delta

    def __str__(self):
        return f'{self.target} {self.subpart} {self.updated}'

    def get_absolute_url(self):
        return f'/{self.subpart}'


class UserDirection(models.Model):
    """This class represents the user's redirection in the DB."""

    direction = models.ForeignKey(Direction, on_delete=models.CASCADE)
    user_uuid = models.UUIDField(default=uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return f'{self.direction} {self.user_uuid} {self.timestamp}'

    class Meta:
        ordering = ['-timestamp']
        unique_together = [['direction', 'user_uuid']]

    @staticmethod
    def get_or_create_user_direction(user_uuid, direction):
        """Gets and updates or creates UserDirection.

        Keywords arguments:
        user_uuid -- user ID (from sessions or generated). str or UUID
        direction -- Direction object

        Return value:
        user_direction -- UserDirection instance.
        """
        if isinstance(user_uuid, str):
            user_uuid = UUID(user_uuid)
        user_direction, created = UserDirection.objects.get_or_create(
            user_uuid=user_uuid, direction=direction
        )

        if not created:
            user_direction.save()  # To update the timestamp (for ordering)

        logger.debug(f'Save UserDirection: {user_direction}')
        return user_direction


@receiver(post_save, sender=Direction)
def add_to_cache(instance, **kwargs):
    """Saves a redirect in cache after saving in DB.

    Keywords arguments:
    instance -- instance of sender class, Direction
    """
    if settings.USE_CACHE and settings.CACHE_ON_CREATE:
        try:
            cache.set(
                instance.subpart, instance.target, settings.DIRECTION_LIFETIME_SEC
            )
            logger.debug(f'Direction "{instance}" saved in cache.')
        except Exception as e:
            logger.exception(f'Error saving direction in cache: {type(e)} - {str(e)}')
