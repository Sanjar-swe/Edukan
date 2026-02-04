#!/bin/bash

# Настройки
API_URL="http://localhost:8000/api/shop"
REDIS_URL="redis://localhost:6379/1"

echo "--- Начинаем проверку кеширования ---"

# 1. Сброс кеша
echo "1. Очистка кеша..."
export REDIS_URL=$REDIS_URL
python3 ../manage.py shell -c "from django.core.cache import cache; cache.clear()"

# 2. Первый запрос (медленный)
echo "2. Первый запрос к списку продуктов (в БД)..."
time curl -s "$API_URL/products/" > /dev/null

# 3. Второй запрос (быстрый)
echo "3. Второй запрос (из кеша)..."
time curl -s "$API_URL/products/" > /dev/null

# 4. Проверка инвалидации при обновлении
echo "4. Обновление товара в БД (через shell)..."
python3 ../manage.py shell -c "from ..shop.models import Product; p=Product.objects.first(); p.name='Updated By Script'; p.save()"

# 5. Проверка обновления данных
echo "5. Запрос после обновления (должен быть сброс кеша и новые данные)..."
RESPONSE=$(curl -s "$API_URL/products/")
if [[ $RESPONSE == *"Updated By Script"* ]]; then
    echo "SUCCESS: Инвалидация кеша сработала, данные обновились."
else
    echo "FAILURE: Инвалидация кеша НЕ сработала или данные не обновились."
    exit 1
fi

echo "--- Проверка завершена успешно ---"
