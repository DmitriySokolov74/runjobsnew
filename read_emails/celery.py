import os
from celery import Celery
from celery.schedules import crontab


# укажем нахождение модуля settings.py, откуда будут читаться настройки для celery (напр. адрес брокера, т.е. redis)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'runjobsnew.settings')

# создаем приложение-целери с указанием имени проекта:
app = Celery('runjobsnew')
# откуда тянуть настройки для целери и по какому кл. слову их оттуда брать (namespace):
app.config_from_object('django.conf:settings', namespace='CELERY')
# подцеплять таски автоматически:
app.autodiscover_tasks()

#для таска по расписанию
app.conf.beat_schedule = {
    'read_mails_every_five_minutes': {
        'task': 'read_emails.tasks.read_mails',
        'schedule': crontab(minute='*/2'),
    },
}
#read_mails_every_five_minutes- имя таска
# 'task': 'read_emails.tasks.read_mails' - регистрация таска
# 'schedule': crontab(minute='*/5') - установка расписания
# https://docs.celeryproject.org/en/stable/userguide/periodic-tasks.html - crontab examples
