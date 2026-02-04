#!/bin/bash

# Скрипт для расширенной симуляции действий пользователя в Online Dukan API (10 шагов)
# Требования: curl, jq

BASE_URL="http://localhost:8000/api"
USER_NAME="user_$(date +%s)"
USER_PASS="Pass12345"
USER_EMAIL="${USER_NAME}@example.com"
ADMIN_USER="admin"  # Предполагаем наличие админа для создания данных
ADMIN_PASS="admin"  # Или используем созданного пользователя если у него есть права

echo "=== ПОДГОТОВКА: Создание данных (Категории и Товары) ==="
# Примечание: В реальном проекте создание товаров обычно делает админ. 
# Для симуляции мы попробуем создать их, но если API закрыто для не-админов,
# скрипт просто продолжит работу с существующими данными.

# 1. Регистрация
echo -e "\n[Шаг 1] Регистрация пользователя..."
REG_RES=$(curl -s -X POST "${BASE_URL}/users/register/" \
    -H "Content-Type: application/json" \
    -d "{\"username\": \"${USER_NAME}\", \"email\": \"${USER_EMAIL}\", \"password\": \"${USER_PASS}\", \"phone_number\": \"+998901234567\", \"address\": \"Nukus\"}")
echo "OK: Пользователь $USER_NAME создан."

# 2. Логин
echo -e "\n[Шаг 2] Авторизация и получение JWT..."
AUTH_RES=$(curl -s -X POST "${BASE_URL}/users/login/" \
    -H "Content-Type: application/json" \
    -d "{\"username\": \"${USER_NAME}\", \"password\": \"${USER_PASS}\"}")
TOKEN=$(echo $AUTH_RES | jq -r '.access')
if [ "$TOKEN" == "null" ]; then echo "Ошибка входа!"; exit 1; fi
echo "OK: Токен получен."

# 3. Список категорий
echo -e "\n[Шаг 3] Просмотр категорий товаров..."
CATEGORIES=$(curl -s -X GET "${BASE_URL}/shop/categories/" -H "Authorization: Bearer $TOKEN")
echo "Найдено категорий: $(echo $CATEGORIES | jq '.results | length')"

# 4. Поиск товара
echo -e "\n[Шаг 4] Поиск электроники (фильтр)..."
PRODUCTS=$(curl -s -X GET "${BASE_URL}/shop/products/?search=phone" -H "Authorization: Bearer $TOKEN")
echo "Результаты поиска получены."

# Берем первый доступный товар для дальнейших тестов
# Если товаров нет, создадим один через shell (имитация админки)
FIRST_ID=$(echo $PRODUCTS | jq -r '.results[0].id // empty')
if [ -z "$FIRST_ID" ]; then
    echo "⚠️ Товары не найдены. Пытаемся создать тестовый товар через Django manage.py..."
    python3 ../manage.py shell <<EOF
from ..shop.models import Category, Product
cat, _ = Category.objects.get_or_create(name="Электроника", slug="electronics")
Product.objects.get_or_create(
    category=cat, name="Смартфон X", slug="phone-x-$(date +%s)", 
    price=5000000, stock=10, is_active=True, description="Тест"
)
EOF
    PRODUCTS=$(curl -s -X GET "${BASE_URL}/shop/products/" -H "Authorization: Bearer $TOKEN")
    FIRST_ID=$(echo $PRODUCTS | jq -r '.results[0].id')
fi
echo "OK: Работаем с товаром ID: $FIRST_ID"

# 5. Просмотр деталей товара
echo -e "\n[Шаг 5] Просмотр детальной информации о товаре..."
curl -s -X GET "${BASE_URL}/shop/products/${FIRST_ID}/" -H "Authorization: Bearer $TOKEN" | jq .name

# 6. Добавление в корзину
echo -e "\n[Шаг 6] Добавление товара в корзину..."
curl -s -X POST "${BASE_URL}/shop/cart/add/" \
    -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
    -d "{\"product_id\": $FIRST_ID, \"quantity\": 2}" | jq .message

# 7. Обновление профиля
echo -e "\n[Шаг 7] Обновление адреса в профиле..."
curl -s -X PATCH "${BASE_URL}/users/profile/" \
    -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
    -d "{\"address\": \"Nukus, ul. Berdakha 45\"}" | jq .address

# 8. Просмотр корзины перед заказом
echo -e "\n[Шаг 8] Проверка содержимого корзины..."
curl -s -X GET "${BASE_URL}/shop/cart/" -H "Authorization: Bearer $TOKEN" | jq .total_items_count

# 9. Оформление заказа (Checkout)
echo -e "\n[Шаг 9] Финальное оформление заказа..."
ORDER_RES=$(curl -s -X POST "${BASE_URL}/shop/orders/checkout/" \
    -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
    -d "{\"address\": \"Nukus, Berdakha 45\"}")
ORDER_ID=$(echo $ORDER_RES | jq -r '.order_id')
echo "OK: Заказ #$ORDER_ID создан."

# 10. Проверка истории заказов
echo -e "\n[Шаг 10] Просмотр истории моих заказов..."
curl -s -X GET "${BASE_URL}/shop/orders/" -H "Authorization: Bearer $TOKEN" | jq '.results | length'

echo -e "\n--- СИМУЛЯЦИЯ ИЗ 10 ШАГОВ ЗАВЕРШЕНА ---"
