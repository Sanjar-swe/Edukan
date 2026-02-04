from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Product, Category
import logging

logger = logging.getLogger(__name__)

def clear_catalog_cache():
    """Очищает кеш каталога (продукты и категории)."""
    # В идеале здесь нужно использовать конкретные ключи, 
    # но для простоты и надежности при изменении в админке сносим весь префикс или частотные ключи
    try:
        # django-redis поддерживает .delete_pattern, но стандартный cache нет.
        # Для начала просто удалим основные ключи, если мы знаем их паттерны, 
        # или используем cache.clear() если проект небольшой.
        cache.clear() 
        logger.info("Catalog cache cleared successfully.")
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")

@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def product_changed_handler(sender, instance, **kwargs):
    clear_catalog_cache()

@receiver(post_save, sender=Category)
@receiver(post_delete, sender=Category)
def category_changed_handler(sender, instance, **kwargs):
    clear_catalog_cache()
