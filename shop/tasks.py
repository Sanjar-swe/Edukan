from celery import shared_task
from django.conf import settings
import requests
import logging
from .models import Order

logger = logging.getLogger(__name__)

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=5)
def send_order_notification_task(self, order_id):
    """
    Фоновая задача для отправки уведомления в Telegram.
    Принимает order_id вместо объекта Order (чтобы избежать проблем с сериализацией).
    """
    try:
        order = Order.objects.select_related('user').get(id=order_id)
        if not order.user.telegram_id:
            logger.warning(f"Order {order_id}: User {order.user.username} has no telegram_id")
            return

        token = settings.TELEGRAM_BOT_TOKEN
        if not token:
            logger.error("TELEGRAM_BOT_TOKEN is not configured")
            return

        text = (
            f"🆕 <b>Jańa buyırtpa! / Новый заказ!</b>\n\n"
            f"🆔 ID: {order.id}\n"
            f"👤 Paydalanıwshı: {order.user.username}\n"
            f"💰 Summa: {order.total_price} som\n"
            f"📍 Mánzil: {order.address}\n"
            f"📅 Waqtı: {order.created_at.strftime('%Y-%m-%d %H:%M')}"
        )
        
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        response = requests.post(url, json={
            "chat_id": order.user.telegram_id, 
            "text": text,
            "parse_mode": "HTML"
        }, timeout=10)
        
        response.raise_for_status()
        logger.info(f"Notification sent for order {order_id} to telegram_id {order.user.telegram_id}")
        
    except Order.DoesNotExist:
        logger.error(f"Order {order_id} does not exist")
    except Exception as e:
        logger.error(f"Error sending notification for order {order_id}: {e}")
        # Задача автоматически повторится благодаря autoretry_for
        raise e
