from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Product, Category
import logging

logger = logging.getLogger(__name__)

# Ключи-префиксы, используемые в @cache_page (views/catalog.py)
CACHE_KEY_PREFIXES = ['product_list', 'product_detail', 'category_list']


def clear_catalog_cache():
    """Очищает кеш каталога по конкретным ключам вместо полной очистки."""
    try:
        for prefix in CACHE_KEY_PREFIXES:
            # django-redis поддерживает delete_pattern для удаления по wildcard
            cache.delete_pattern(f'*{prefix}*')
        logger.info("Catalog cache invalidated for: %s", ', '.join(CACHE_KEY_PREFIXES))
    except AttributeError:
        # Fallback для не-redis бэкендов, которые не поддерживают delete_pattern
        cache.clear()
        logger.warning("Cache backend does not support delete_pattern, used cache.clear()")
    except Exception as e:
        logger.error("Error clearing cache: %s", e)


@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def product_changed_handler(sender, instance, **kwargs):
    clear_catalog_cache()


@receiver(post_save, sender=Category)
@receiver(post_delete, sender=Category)
def category_changed_handler(sender, instance, **kwargs):
    clear_catalog_cache()
