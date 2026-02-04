from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def send_welcome_email_task(self, email, username):
    """
    Асинхронная задача отправки приветственного письма.
    """
    try:
        subject = 'Online Dúkan-ǵa xosh keldińiz!'
        message = f'Assalawma áleykum, {username}!\n\nBizdiń platformada dizimnen ótkenińiz ushın raxmet. Siz endi ónimlerdi sebetke salıp, buyırtpa bere alasız.'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email]
        
        send_mail(subject, message, email_from, recipient_list, fail_silently=False)
        logger.info(f"Welcome email sent to {email}")
        return f"Email sent to {email}"
    except Exception as exc:
        logger.error(f"Error sending welcome email to {email}: {exc}")
        # Повторяем попытку через 60 секунд * номер попытки
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))
