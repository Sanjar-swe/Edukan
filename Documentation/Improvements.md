# Список улучшений проекта Online Dukan

В данном документе перечислены улучшения и функциональные возможности, реализованные в проекте сверх базовых требований, указанных в `TZ.md`. Все пункты снабжены ссылками на соответствующие файлы и диапазоны строк кода.

## 1. Архитектурные улучшения

- **Паттерн Service-Layer (Слой сервисов)**:
    Вся сложная бизнес-логика (например, оформление заказа с проверкой остатков и асинхронными задачами) вынесена из Django Views в отдельные сервисные функции. Это делает код чище и облегчает тестирование.
    - **Реализация**: [shop/services.py:L8-80](file:///home/swe/Desktop/OnlineDukan/shop/services.py#L8-80)

- **Использование DTO (Data Transfer Object)**:
    Для передачи данных между слоями API и сервисов используются объекты DTO (Data Transfer Objects). Это позволяет абстрагировать логику от структуры запросов DRF и избежать прямой зависимости сервисов от объектов запроса.
    - **Реализация**: [shop/dto.py:L1-9](file:///home/swe/Desktop/OnlineDukan/shop/dto.py#L1-9)

## 2. Бизнес-логика и база данных

- **Атомарные транзакции и защита от Race Conditions**:
    Процесс оформления заказа полностью обернут в `transaction.atomic`. Для защиты от конкурентных запросов (когда два пользователя заказывают последний товар одновременно) используется блокировка строк `select_for_update()`.
    - **Реализация**: [shop/services.py:L14-31](file:///home/swe/Desktop/OnlineDukan/shop/services.py#L14-31)

- **Гибкая логика оформления заказа**:
    Пользователь может оформить заказ не только на всю корзину целиком, но и выбрать конкретные позиции по их ID.
    - **Реализация**: [shop/serializers.py:L52-59](file:///home/swe/Desktop/OnlineDukan/shop/serializers.py#L52-59)

## 3. Производительность и масштабируемость

- **Кэширование на базе Redis**:
    Проект настроен на использование Redis в качестве бэкенда для кэширования, что значительно ускоряет работу с часто запрашиваемыми данными.
    - **Конфигурация**: [core/settings.py:L220-228](file:///home/swe/Desktop/OnlineDukan/core/settings.py#L220-228)

- **Автоматическая инвалидация кэша**:
    Реализована система сигналов, которая автоматически очищает кэш каталога при любом изменении товаров или категорий (через админку или API).
    - **Реализация**: [shop/signals.py:L1-31](file:///home/swe/Desktop/OnlineDukan/shop/signals.py#L1-31)

- **Кэширование ключевых эндпоинтов**:
    Для снижения нагрузки на БД реализовано кэширование на уровне представлений (Cache Page):
    - **Список категорий (15 мин)**: [shop/views/catalog.py:L42](file:///home/swe/Desktop/OnlineDukan/shop/views/catalog.py#L42)
    - **Список товаров (15 мин)**: [shop/views/catalog.py:L104](file:///home/swe/Desktop/OnlineDukan/shop/views/catalog.py#L104)
    - **Детали конкретного товара (15 мин)**: [shop/views/catalog.py:L113](file:///home/swe/Desktop/OnlineDukan/shop/views/catalog.py#L113)

## 4. Фоновые задачи (Celery)

- **Асинхронные уведомления**:
    Отправка уведомлений о новых заказах в Telegram вынесена в фоновые задачи, чтобы не задерживать ответ пользователю.
    - **Задача**: [shop/tasks.py:L31-72](file:///home/swe/Desktop/OnlineDukan/shop/tasks.py#L31-72)

- **Периодическая очистка корзин (Celery Beat)**:
    Автоматическое удаление заброшенных корзин (старше 14 дней) для поддержания чистоты базы данных.
    - **Логика задачи**: [shop/tasks.py:L12-27](file:///home/swe/Desktop/OnlineDukan/shop/tasks.py#L12-27)
    - **Расписание (Beat)**: [core/settings.py:L211-216](file:///home/swe/Desktop/OnlineDukan/core/settings.py#L211-216)

## 5. Безопасность и стабильность

- **Ограничение частоты запросов (Throttling)**:
    Настроены лимиты для анонимных и авторизованных пользователей, а также специальный лимит для попыток аутентификации.
    - **Конфигурация**: [core/settings.py:L163-172](file:///home/swe/Desktop/OnlineDukan/core/settings.py#L163-172)

- **Унифицированная обработка ошибок**:
    Реализован кастомный обработчик исключений, который возвращает ошибки в едином формате с полями `possible_reason` и `suggested_fix`, что улучшает опыт фронтенд-разработчиков.
    - **Реализация**: [api/exceptions.py:L1-55](file:///home/swe/Desktop/OnlineDukan/api/exceptions.py#L1-55)

## 6. Тестирование и DevOps

- **Автоматизированные тест-сценарии**:
    Создан набор bash-скриптов для полной проверки API, включая сценарии покупки и проверку работы кэша.
    - **Директория**: [BashScriptsForTesting/](file:///home/swe/Desktop/OnlineDukan/BashScriptsForTesting/)

- **Контейнеризация (Docker & Docker Compose)**:
    Весь проект вместе с БД, Redis и Celery разворачивается одной командой.
    - **Dockerfile**: [Dockerfile:L1-29](file:///home/swe/Desktop/OnlineDukan/Dockerfile#L1-29)
    - **Docker Compose**: [docker-compose.yml:L1-68](file:///home/swe/Desktop/OnlineDukan/docker-compose.yml#L1-68)
