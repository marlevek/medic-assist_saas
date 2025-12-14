import os 
from celery import Celery 
from celery.schedules import crontab 


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicAI.settings')

app = Celery('medicAI')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Tarefas agendadas
app.conf.beat_schedule = {
    'send-appointment-reminders': {
      'task': 'appointments.tasks.send_appointment_reminders',
        'schedule': crontab(hour=9, minute=0),  # 9h diariamente
    },
    'generate-daily-reports': {
        'task': 'analytics.tasks.generate_daily_reports',
        'schedule': crontab(hour=23, minute=0),  # 23h diariamente
    },
}