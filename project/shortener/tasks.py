# project/shortener/tasks.py
# tasks for Celery

from project.celery import app
from .models import Direction
from django.db import DatabaseError
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


@app.task
def clear_old_directions():
    """Deletes all outdated redirects from DB and from cache."""

    logger.info('Start clearing old directions.')

    threshold_date = Direction.get_threshold_date()
    old_directions = Direction.objects.filter(updated__lte=threshold_date)

    if not old_directions:
        logger.info('haven`t old directions.')
        logger.info('End clearing old directions.')
        return

    old_keys = old_directions.values_list('subpart', flat=True)
    keys = list(old_keys)
    logger.debug(f'Subparts to delete: {keys}')

    try:
        old_directions.delete()
        logger.info('All old directions deleted.')

    except DatabaseError as db_e:
        logger.error(f'error when delete from DB: {db_e}')
        logger.info('End clearing old directions.')
        return

    try:
        cache.delete_many(keys)
        logger.info('All old directions deleted from cache.')

    except Exception as e:
        logger.error(f'error when delete from cache: {e}')

    logger.info('End clearing old directions.')
