#!/bin/bash

BASE_URL="http://127.0.0.1:8000/api"
USERNAME="NewUser"
PASSWORD="testpassword123"

# 1. Логин
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

# 2. Получение корзины
echo "📥 Запрос содержимого корзины..."
CART_RESPONSE=$(curl -s -X GET "$BASE_URL/shop/cart/" \
  -H "Authorization: Bearer $TOKEN")

# Красивый вывод JSON
echo "Ответ сервера:"
echo "$CART_RESPONSE" | python3 -m json.tool
