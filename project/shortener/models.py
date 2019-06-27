# project/shortener/models.py
# All models of the shortener app are here.

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from datetime import datetime, timedelta, timezone
from random import random
import logging
import hashlib
import uuid

logger = logging.getLogger(__name__)


class Direction(models.Model):
    """This class represents a redirect from 'target' to 'domain/subpart' in DB."""

    subpart = models.CharField(primary_key=True, max_length=30)
    target = models.URLField(max_length=2000)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    @classmethod
    def generate_subpart(cls, target, random_sub=False, alphabet=settings.BASE_ENCODING):
        """Generates and returns tne new subpart for target link. It takes a part of md5-hash of the 'target' string
        end encodes it with 'alphabet'.

        Keywords arguments:
        target -- link for shorting, str
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
            hash_str = str(hashlib.md5(str(random()).encode('utf-8')).hexdigest()[:settings.SUBPART_HASH_LEN])
        else:
            encoded_target = target.encode('utf-8')
            hash_md5 = hashlib.md5(encoded_target)
            hash_str = str(hash_md5.hexdigest()[:settings.SUBPART_HASH_LEN])

        num = int(hash_str, 16)

        if not num:
            return alphabet[0]

        if num < 0:
            err_str = 'The variable "target" num < 0!'
            logger.error(err_str)
            raise ValueError(err_str)

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

    @classmethod
    def get_or_create_direction(cls, subpart, target):
        """Gets and updates or creates direction. If creation failed, raises Exception.

        Keywords arguments:
        subpart -- the short alias for target. str
        target -- link for shorting, str

        Return value:
        direction, err_str -- Direction instance and error string.
        """
        err_str = None
        user_subpart = False

        if not subpart:
            subpart = Direction.generate_subpart(target)
        else:
            user_subpart = True

        exist = False

        try:  # Use get() (not get_or_create()) to avoid unnecessary query.
            direction = Direction.objects.get(subpart=subpart)
            exist = True
        except Direction.DoesNotExist:
            direction = Direction()
            direction.subpart = subpart
            direction.target = target
            direction.save()

            logger.debug(f'Created new direction: "{direction}"')

        if direction.target != target:

            # If Celery is not working or there was an error.
            if direction.get_rest_of_life() <= 0:
                logger.warning(f'Edit the existing direction: "{direction}"')

                direction.target = target
                direction.save()

                logger.warning(f'The existing direction updated: "{direction}"')
            else:
                if user_subpart:
                    err_str = f'The subpart "{subpart}" is already used!'
                    logger.warning(err_str)
                else:
                    # The subpart is already used.
                    # The chance of getting here is extremely small, but processing is still needed.
                    # Request in a loop. This is bad, but this situation is almost impossible.
                    logger.warning(f'The subpart "{subpart}" is already used!')

                    for i in range(settings.LAST_TRY_NUM):
                        subpart = Direction.generate_subpart(target, True)

                        try:
                            direction = Direction.objects.get(subpart=subpart)
                        except Direction.DoesNotExist:
                            direction = Direction()
                            direction.subpart = subpart
                            direction.target = target
                            direction.save()

                            logger.debug(f'Created new direction: "{direction}"')
                            break

                        if direction.target != target:

                            if direction.get_rest_of_life() <= 0:
                                logger.warning(f'Edit the existing direction: "{direction}"')

                                direction.target = target
                                direction.save()

                                logger.warning(f'The existing direction updated: "{direction}"')
                                break

        else:
            if exist:
                direction.save()

                logger.debug(f'The direction "{direction}" has updated.')

        if direction.target != target:
            if not user_subpart:
                # If nothing helped:
                err_str = f'The subpart "{subpart}" is already used! ' \
                    f'Shuffling did not help. {target} did not writed to DB.'

                logger.error(err_str)
                raise Exception(err_str)

        return direction, err_str

    @classmethod
    def get_threshold_date(cls):
        """Returns the date, less than which should not be a field 'updated' of records in the database.

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
    """This class represents an user list of redirects in DB."""

    direction = models.ForeignKey(Direction, on_delete=models.CASCADE)
    user_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)

    def __str__(self):
        return f'{self.direction} {self.user_uuid} {self.timestamp}'

    class Meta:
        ordering = ["-timestamp"]


@receiver(post_save, sender=Direction)
def add_to_cache(instance, **kwargs):
    """Saves a redirect in cache after saving in DB.

    Keywords arguments:
    instance -- instance of sender class, Direction (in this case)

    """
    if settings.CACHE_ON_CREATE and settings.USE_CACHE:

        try:
            cache.set(instance.subpart, instance.target, settings.DIRECTION_LIFETIME_SEC)
            logger.debug(f'Direction "{instance}" saved in cache.')
        except Exception as e:
            logger.exception(f'Error saving direction in cache: {type(e)} - {str(e)}')
