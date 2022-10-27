# project/shortener/tasks.py
# tasks for Celery

from project.celery import app
from .models import Direction
from django.db import Error
from django.core.cache import cache
from logging import getLogger


logger = getLogger(__name__)


@app.task
def clear_old_directions():
    """Deletes all outdated redirects from DB and from cache."""
    final_message = 'Deleting the old directions is complete.'
    logger.info('Start deleting old directions.')
    threshold_date = Direction.get_threshold_date()
    old_directions = Direction.objects.filter(updated__lte=threshold_date)

    if not old_directions:
        logger.info('There are no old directions found in the DB.')
        logger.info(final_message)
        return

    old_keys = list(old_directions.values_list('subpart', flat=True))
    logger.debug(f'Subparts to delete: {old_keys}')

    try:
        old_directions.delete()
        logger.info('All old directions have been successfully deleted from the DB.')
    except Error as db_e:
        logger.exception(f'Error when deleting from the DB: {type(db_e)} - {str(db_e)}')
        logger.info(final_message)
        return

    try:
        cache.delete_many(old_keys)
        logger.info('All old directions have been successfully deleted from the cache.')
    except Exception as e:
        logger.exception(f'Error when deleting from the cache: {type(e)} - {str(e)}')

    logger.info(final_message)
