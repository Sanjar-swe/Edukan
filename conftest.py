import pytest
from django.conf import settings

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    Автоматически дает доступ к БД для всех тестов,
    чтобы не писать @pytest.mark.django_db каждый раз.
    """
    pass

@pytest.fixture(autouse=True)
def override_settings(settings):
    """
    Переопределяет настройки для тестов:
    - Использует LocMemCache вместо Redis
    - Использует in-memory брокер для Celery
    """
    settings.CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }
    settings.CELERY_BROKER_URL = 'memory://'
    settings.CELERY_RESULT_BACKEND = 'db+sqlite:///results.sqlite'
    settings.MEDIA_ROOT = '/tmp/media_test/' # Чтобы не мусорить в реальной папке
