from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import User

@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        subject = 'Online Dúkan-ǵa xosh keldińiz!'
        message = f'Assalawma áleykum, {instance.username}!\n\nBizdiń platformada dizimnen ótkenińiz ushın raxmet. Siz endi ónimlerdi sebetke salıp, buyırtpa bere alasız.'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [instance.email]
        
        # На реальном проекте здесь будет отправка через SMTP. 
        # В режиме разработки это упадет с ошибкой, если EMAIL_HOST не настроен,
        # поэтому часто добавляют fail_silently=True
        try:
            send_mail(subject, message, email_from, recipient_list, fail_silently=True)
            print(f"Welcome email sent to {instance.email}")
        except Exception as e:
            print(f"Error sending email: {e}")
