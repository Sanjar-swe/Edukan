# Реализованные дизайн-паттерны в проекте Online Dukan

В проекте реализовано несколько классических архитектурных и проектных паттернов, которые делают кодовую базу более структурированной, гибкой и расширяемой. Эти паттерны превратили проект из простого CRUD-приложения в профессиональный инструмент, соответствующий стандартам Enterprise-разработки.

---

## 1. Архитектурные паттерны (Architectural Patterns)

### Service Layer (Слой сервисов)
*   **Где используется:** [shop/services.py:L8-80](file:///home/swe/Desktop/OnlineDukan/shop/services.py#L8-80)
*   **Суть:** Бизнес-логика вынесена из контроллеров (Views) в отдельные функции. Это позволяет использовать одну и ту же логику (например, создание заказа) в разных частях приложения (API, чат-бот, админка) и упрощает её тестирование.

### DTO (Data Transfer Object)
*   **Где используется:** [shop/dto.py:L1-9](file:///home/swe/Desktop/OnlineDukan/shop/dto.py#L1-9)
*   **Суть:** Использование простых структур данных (`dataclasses`) для передачи информации между слоями (из Serializers в Services). Это снижает зависимость бизнес-логики от конкретного фреймворка (Django REST Framework).

### Thin Views, Fat Models/Services
*   **Где используется:** Везде в [shop/views/](file:///home/swe/Desktop/OnlineDukan/shop/views/) (например, [catalog.py:L1-152](file:///home/swe/Desktop/OnlineDukan/shop/views/catalog.py))
*   **Суть:** Вьюсеты отвечают только за HTTP-протокол, валидацию входных данных и возвращение ответов. Вся "тяжелая" логика находится в слое сервисов.

---

## 2. Структурные паттерны (Structural Patterns)

### Adapter / Wrapper (Адаптер)
*   **Где используется:** [api/exceptions.py:L1-55](file:///home/swe/Desktop/OnlineDukan/api/exceptions.py#L1-55)
*   **Суть:** Кастомный обработчик исключений DRF оборачивает стандартные ошибки фреймворка в унифицированный формат, понятный фронтенду, дополняя их полями `possible_reason` и `suggested_fix`.

### Proxy (Заместитель)
*   **Где используется:** [shop/views/catalog.py](file:///home/swe/Desktop/OnlineDukan/shop/views/catalog.py) (линии [42](file:///home/swe/Desktop/OnlineDukan/shop/views/catalog.py#L42), [104](file:///home/swe/Desktop/OnlineDukan/shop/views/catalog.py#L104), [113](file:///home/swe/Desktop/OnlineDukan/shop/views/catalog.py#L113) через `@method_decorator(cache_page)`)
*   **Суть:** Кэширование на уровне эндпоинтов выступает в роли прокси: если данные есть в кэше Redis, они возвращаются мгновенно без обращения к базе данных и выполнения логики вьюсета.

---

## 3. Поведенческие паттерны (Behavioral Patterns)

### Observer (Наблюдатель)
*   **Где используется:** [shop/signals.py:L1-31](file:///home/swe/Desktop/OnlineDukan/shop/signals.py#L1-31)
*   **Суть:** Django Signals (`post_save`, `post_delete`) позволяют одним частям системы (кэшу) реагировать на изменения в других (модели товаров), не связывая их напрямую. Когда товар сохраняется, кэш автоматически сбрасывается.

### Strategy (Стратегия)
*   **Где используется:** [shop/models.py:L42-46](file:///home/swe/Desktop/OnlineDukan/shop/models.py#L42-46) (метод `get_price`)
*   **Суть:** Выбор алгоритма расчета цены (обычная цена или цена со скидкой) инкапсулирован внутри метода. Остальной код просто вызывает `get_price()`, не заботясь о том, какая логика там используется.

### Command (Команда)
*   **Где используется:** [shop/tasks.py:L1-72](file:///home/swe/Desktop/OnlineDukan/shop/tasks.py#L1-72) (Celery задачи)
*   **Суть:** Задачи Celery инкапсулируют действия (отправка уведомления, очистка корзины) как объекты, которые можно ставить в очередь и выполнять асинхронно или по расписанию.

---

## 4. Порождающие паттерны (Creational Patterns)

### Factory (Фабрика)
*   **Где используется:** [shop/factories.py:L1-52](file:///home/swe/Desktop/OnlineDukan/shop/factories.py#L1-52)
*   **Суть:** Использование `factory_boy` для создания тестовых данных. Это позволяет абстрагировать процесс создания сложных объектов моделей со связями.

### Singleton (Одиночка)
*   **Где используется:** Внутренние механизмы Django (например, объект `settings` или пул соединений с БД).
