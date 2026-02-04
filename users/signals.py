from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .tasks import send_welcome_email_task
from .models import User

@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created and instance.email:
        # Отправляем задачу в Celery только после успешного коммита транзакции
        transaction.on_commit(lambda: send_welcome_email_task.delay(instance.email, instance.username))
