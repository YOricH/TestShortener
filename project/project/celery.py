# project/celery.py
# Settings for Celery

import os
from django.conf import settings
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

app = Celery('project')
app.config_from_object('django.conf:settings')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'clear-old-directions': {
        'task': 'shortener.tasks.clear_old_directions',
        'schedule': crontab(minute=f'*/{settings.SCHEDULE_CLEAR_DATA_MINUTES}'),
    },
}
