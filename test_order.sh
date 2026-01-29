#!/bin/bash

BASE_URL="http://127.0.0.1:8000/api"
USERNAME="NewUser"
PASSWORD="testpassword123"
CONTAINER_NAME="onlinedukan-web-1"

# 1. Логин и получение токена
echo "🔑 Авторизация..."
RESPONSE=$(curl -s -X POST "$BASE_URL/users/login/" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"$USERNAME\", \"password\": \"$PASSWORD\"}")

TOKEN=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access', ''))")

if [ -z "$TOKEN" ]; then
  echo "❌ Ошибка авторизации"
  exit 1
fi

echo "✅ Токен получен"

# 2. Очистка корзины (для чистоты теста, опционально, но полезно)
# (Пропускаем для простоты, просто добавляем новый)

# 3. Добавление товара в корзину (ID товара 1)
echo "🛒 Добавление товара (ID: 1) в корзину..."
ADD_CART_RESPONSE=$(curl -s -X POST "$BASE_URL/shop/cart/add/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 1}')

echo "Ответ добавления: $ADD_CART_RESPONSE"

# 4. Получение корзины, чтобы узнать ID добавленного айтема
echo "� Получение корзины..."
CART_RESPONSE=$(curl -s -X GET "$BASE_URL/shop/cart/" \
  -H "Authorization: Bearer $TOKEN")

# Извлекаем ID первого айтема (предполагаем, что есть items[])
# JSON структура: { "items": [ { "id": 123, ... } ] }
ITEM_ID=$(echo "$CART_RESPONSE" | python3 -c "import sys, json; print((json.load(sys.stdin).get('items', [{}])[0].get('id', '')))")

if [ -z "$ITEM_ID" ] || [ "$ITEM_ID" == "None" ]; then
  echo "❌ Не удалось получить ID товара из корзины. Ответ корзины:"
  echo "$CART_RESPONSE"
  exit 1
fi

echo "✅ ID товара в корзине: $ITEM_ID"

# 5. Создание заказа (Checkout)
echo "📦 Оформление заказа..."
ORDER_RESPONSE=$(curl -s -X POST "$BASE_URL/shop/orders/checkout/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"address\": \"г. Нукус, Тестовая улица, д. 1\", \"cart_item_ids\": [$ITEM_ID]}")

echo "Ответ заказа: $ORDER_RESPONSE"
