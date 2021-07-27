from celery import Celery
from django.core.management import call_command

app = Celery('proj')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.conf.broker_url = 'redis://broker:6379/0'
app.conf.beat_schedule = {
    'clearsessions': {
        'task': 'physionet.celery.clear_sessions',
        'schedule': 60*60*24,
        'args': (),
    },
    'purgeaccounts': {
        'task': 'physionet.celery.purgeaccounts',
        'schedule': 60*60,
        'args': (),
    }
}
app.autodiscover_tasks()


@app.task
def clear_sessions():
    call_command('clearsessions')


@app.task
def purge_accounts():
    call_command('purgeaccounts')