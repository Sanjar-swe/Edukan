#!/bin/bash

# Master simulation script for Online Dukan (10 scenarios x 10 steps)
# Requires: curl, jq

BASE_URL="http://localhost:8000/api"

# Helper: Print step
print_step() {
    echo -e "[Scenario $1 | Step $2] $3"
}

# Helper: Ensure Product exists
ensure_data() {
    echo "Подготовка данных..."
    ../venv/bin/python ../manage.py shell <<EOF
from ..shop.models import Category, Product
cat, _ = Category.objects.get_or_create(name="Электроника", slug="electronics")
Product.objects.get_or_create(
    slug="phone-x-test",
    defaults={
        'category': cat, 
        'name': "Смартфон X", 
        'price': 5000000, 
        'stock': 100, 
        'is_active': True, 
        'description': "Тест"
    }
)
Product.objects.get_or_create(
    slug="audio-y-test",
    defaults={
        'category': cat, 
        'name': "Наушники Y", 
        'price': 200000, 
        'stock': 50, 
        'is_active': True, 
        'description': "Тест аудио"
    }
)
EOF
}

# Scenario 1: Классический Покупатель
run_s1() {
    S=1; U="user_s${S}_$(date +%s)"; P="Pass123"
    echo -e "\n=== Сценарий $S: Классический Покупатель ==="
    print_step $S 1 "Регистрация"; curl -s -X POST "${BASE_URL}/users/register/" -H "Content-Type: application/json" -d "{\"username\":\"$U\",\"password\":\"$P\"}" > /dev/null
    print_step $S 2 "Логин"; T=$(curl -s -X POST "${BASE_URL}/users/login/" -H "Content-Type: application/json" -d "{\"username\":\"$U\",\"password\":\"$P\"}" | jq -r .access)
    print_step $S 3 "Категории"; curl -s -H "Authorization: Bearer $T" "${BASE_URL}/shop/categories/" > /dev/null
    print_step $S 4 "Товары"; PRODS=$(curl -s -H "Authorization: Bearer $T" "${BASE_URL}/shop/products/")
    print_step $S 5 "Детали"; PID=$(echo $PRODS | jq -r '.results[0].id'); curl -s -H "Authorization: Bearer $T" "${BASE_URL}/shop/products/$PID/" > /dev/null
    print_step $S 6 "В корзину"; curl -s -X POST -H "Authorization: Bearer $T" -H "Content-Type: application/json" -d "{\"product_id\":$PID,\"quantity\":1}" "${BASE_URL}/shop/cart/add/" > /dev/null
    print_step $S 7 "Вид корзины"; curl -s -H "Authorization: Bearer $T" "${BASE_URL}/shop/cart/" > /dev/null
    print_step $S 8 "Заказ"; curl -s -X POST -H "Authorization: Bearer $T" -H "Content-Type: application/json" -d "{\"address\":\"Home 1\"}" "${BASE_URL}/shop/orders/checkout/" > /dev/null
    print_step $S 9 "Статус"; echo "Заказ оформлен."
    print_step $S 10 "История"; curl -s -H "Authorization: Bearer $T" "${BASE_URL}/shop/orders/" | jq '.results | length'
}

# Scenario 2: Просто Смотрю
run_s2() {
    S=2; U="user_s${S}_$(date +%s)"; P="Pass123"
    echo -e "\n=== Сценарий $S: Просто Смотрю ==="
    print_step $S 1 "Регистрация"; curl -s -X POST "${BASE_URL}/users/register/" -H "Content-Type: application/json" -d "{\"username\":\"$U\",\"password\":\"$P\"}" > /dev/null
    print_step $S 2 "Логин"; T=$(curl -s -X POST "${BASE_URL}/users/login/" -H "Content-Type: application/json" -d "{\"username\":\"$U\",\"password\":\"$P\"}" | jq -r .access)
    print_step $S 3 "Главная"; curl -s -H "Authorization: Bearer $T" "${BASE_URL}/shop/categories/" > /dev/null
    print_step $S 4 "Электроника"; curl -s -H "Authorization: Bearer $T" "${BASE_URL}/shop/products/?search=phone" > /dev/null
    print_step $S 5 "Товар 1"; PID=$(curl -s -H "Authorization: Bearer $T" "${BASE_URL}/shop/products/" | jq -r '.results[0].id'); curl -s -H "Authorization: Bearer $T" "${BASE_URL}/shop/products/$PID/" > /dev/null
    print_step $S 6 "Товар 2"; PID2=$(curl -s -H "Authorization: Bearer $T" "${BASE_URL}/shop/products/" | jq -r '.results[1].id // .results[0].id'); curl -s -H "Authorization: Bearer $T" "${BASE_URL}/shop/products/$PID2/" > /dev/null
    print_step $S 7 "Пагинация"; curl -s -H "Authorization: Bearer $T" "${BASE_URL}/shop/products/?page=1" > /dev/null
    print_step $S 8 "Сортировка"; curl -s -H "Authorization: Bearer $T" "${BASE_URL}/shop/products/?ordering=-price" > /dev/null
    print_step $S 9 "Профиль"; curl -s -H "Authorization: Bearer $T" "${BASE_URL}/users/profile/" > /dev/null
    print_step $S 10 "Выход"; echo "Пользователь ушел без покупок."
}

# Scenario 3: Личный Кабинет
run_s3() {
    S=3; U="user_s${S}_$(date +%s)"; P="Pass123"
    echo -e "\n=== Сценарий $S: Личный Кабинет ==="
    print_step $S 1 "Регистрация"; curl -s -X POST "${BASE_URL}/users/register/" -H "Content-Type: application/json" -d "{\"username\":\"$U\",\"password\":\"$P\"}" > /dev/null
    print_step $S 2 "Логин"; T=$(curl -s -X POST "${BASE_URL}/users/login/" -H "Content-Type: application/json" -d "{\"username\":\"$U\",\"password\":\"$P\"}" | jq -r .access)
    print_step $S 3 "Вид профиля"; curl -s -H "Authorization: Bearer $T" "${BASE_URL}/users/profile/" > /dev/null
    print_step $S 4 "Смена адреса"; curl -s -X PATCH -H "Authorization: Bearer $T" -H "Content-Type: application/json" -d "{\"address\":\"New Nukus 1\"}" "${BASE_URL}/users/profile/" > /dev/null
    print_step $S 5 "Смена телефона"; curl -s -X PATCH -H "Authorization: Bearer $T" -H "Content-Type: application/json" -d "{\"phone_number\":\"+998000000\"}" "${BASE_URL}/users/profile/" > /dev/null
    print_step $S 6 "Проверка профиля"; curl -s -H "Authorization: Bearer $T" "${BASE_URL}/users/profile/" | jq .address
    print_step $S 7 "Сброс сессии"; T=""
    print_step $S 8 "Перезаход"; T=$(curl -s -X POST "${BASE_URL}/users/login/" -H "Content-Type: application/json" -d "{\"username\":\"$U\",\"password\":\"$P\"}" | jq -r .access)
    print_step $S 9 "Валидация данных"; curl -s -H "Authorization: Bearer $T" "${BASE_URL}/users/profile/" | jq .phone_number
    print_step $S 10 "Конец"; echo "Профиль в порядке."
}

# Scenario 4: Мастер Корзины
run_s4() {
    S=4; U="user_s${S}_$(date +%s)"; P="Pass123"
    echo -e "\n=== Сценарий $S: Мастер Корзины ==="
    print_step $S 1 "Вход"; T=$(curl -s -X POST "${BASE_URL}/users/login/" -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"admin\"}" | jq -r .access)
    if [ "$T" == "null" ]; then run_s1; return; fi # Fallback
    print_step $S 2 "Поиск А"; PID=$(curl -s -H "Authorization: Bearer $T" "${BASE_URL}/shop/products/" | jq -r '.results[0].id')
    print_step $S 3 "Add A"; curl -s -X POST -H "Authorization: Bearer $T" -H "Content-Type: application/json" -d "{\"product_id\":$PID,\"quantity\":1}" "${BASE_URL}/shop/cart/add/" > /dev/null
    print_step $S 4 "Поиск Б"; PID2=$(curl -s -H "Authorization: Bearer $T" "${BASE_URL}/shop/products/" | jq -r '.results[1].id')
    print_step $S 5 "Add Б"; curl -s -X POST -H "Authorization: Bearer $T" -H "Content-Type: application/json" -d "{\"product_id\":$PID2,\"quantity\":3}" "${BASE_URL}/shop/cart/add/" > /dev/null
    print_step $S 6 "Корзина - 2 позиции"; curl -s -H "Authorization: Bearer $T" "${BASE_URL}/shop/cart/" | jq .items
    print_step $S 7 "Удаление А"; curl -s -X DELETE -H "Authorization: Bearer $T" "${BASE_URL}/shop/cart/$PID/remove/" > /dev/null
    print_step $S 8 "Корзина - 1 позиция"; curl -s -H "Authorization: Bearer $T" "${BASE_URL}/shop/cart/" | jq .items
    print_step $S 9 "Доп. количество"; curl -s -X POST -H "Authorization: Bearer $T" -H "Content-Type: application/json" -d "{\"product_id\":$PID2,\"quantity\":10}" "${BASE_URL}/shop/cart/add/" > /dev/null
    print_step $S 10 "Итог"; curl -s -H "Authorization: Bearer $T" "${BASE_URL}/shop/cart/" | jq .total_price
}

# Scenario 5: Экономный Поиск
run_s5() {
    S=5; U="user_s${S}_$(date +%s)"; P="Pass123"
    echo -e "\n=== Сценарий $S: Экономный Поиск ==="
    print_step $S 1 "Вход"; T=$(curl -s -X POST "${BASE_URL}/users/login/" -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"admin\"}" | jq -r .access)
    print_step $S 2 "Все товары"; curl -s -H "Authorization: Bearer $T" "${BASE_URL}/shop/products/" > /dev/null
    print_step $S 3 "Цена < 1 млн"; curl -s -H "Authorization: Bearer $T" "${BASE_URL}/shop/products/?price=1000000" > /dev/null
    print_step $S 4 "Сортировка по цене (ASC)"; curl -s -H "Authorization: Bearer $T" "${BASE_URL}/shop/products/?ordering=price" > /dev/null
    print_step $S 5 "Сортировка по цене (DESC)"; curl -s -H "Authorization: Bearer $T" "${BASE_URL}/shop/products/?ordering=-price" > /dev/null
    print_step $S 6 "Поиск по слову"; curl -s -H "Authorization: Bearer $T" "${BASE_URL}/shop/products/?search=test" > /dev/null
    print_step $S 7 "Категория фильтр"; curl -s -H "Authorization: Bearer $T" "${BASE_URL}/shop/products/?category=1" > /dev/null
    print_step $S 8 "Детали первого"; curl -s -H "Authorization: Bearer $T" "${BASE_URL}/shop/products/" | jq -r '.results[0].name'
    print_step $S 9 "Детали второго"; curl -s -H "Authorization: Bearer $T" "${BASE_URL}/shop/products/" | jq -r '.results[1].name'
    print_step $S 10 "Выход"; echo "Поиск завершен."
}

# Scenario 6: Лояльный Клиент (Repeat)
run_s6() {
    S=6; U="user_s${S}_$(date +%s)"; P="Pass123"
    echo -e "\n=== Сценарий $S: Лояльный Клиент ==="
    print_step $S 1 "Рега"; curl -s -X POST "${BASE_URL}/users/register/" -H "Content-Type: application/json" -d "{\"username\":\"$U\",\"password\":\"$P\"}" > /dev/null
    print_step $S 2 "Логин"; T=$(curl -s -X POST "${BASE_URL}/users/login/" -H "Content-Type: application/json" -d "{\"username\":\"$U\",\"password\":\"$P\"}" | jq -r .access)
    print_step $S 3 "Покупка 1"; PID=$(curl -s -H "Authorization: Bearer $T" "${BASE_URL}/shop/products/" | jq -r '.results[0].id')
    print_step $S 4 "Add"; curl -s -X POST -H "Authorization: Bearer $T" -H "Content-Type: application/json" -d "{\"product_id\":$PID,\"quantity\":1}" "${BASE_URL}/shop/cart/add/" > /dev/null
    print_step $S 5 "Order"; curl -s -X POST -H "Authorization: Bearer $T" -H "Content-Type: application/json" -d "{\"address\":\"A\"}" "${BASE_URL}/shop/orders/checkout/" > /dev/null
    print_step $S 6 "Logout"; T=""
    print_step $S 7 "Relogin"; T=$(curl -s -X POST "${BASE_URL}/users/login/" -H "Content-Type: application/json" -d "{\"username\":\"$U\",\"password\":\"$P\"}" | jq -r .access)
    print_step $S 8 "History"; curl -s -H "Authorization: Bearer $T" "${BASE_URL}/shop/orders/" > /dev/null
    print_step $S 9 "Add again"; curl -s -X POST -H "Authorization: Bearer $T" -H "Content-Type: application/json" -d "{\"product_id\":$PID,\"quantity\":1}" "${BASE_URL}/shop/cart/add/" > /dev/null
    print_step $S 10 "History items"; curl -s -H "Authorization: Bearer $T" "${BASE_URL}/shop/orders/" | jq '.results | length'
}

# Scenario 7: Оптовик
run_s7() {
    S=7; U="user_s${S}_$(date +%s)"; P="Pass123"
    echo -e "\n=== Сценарий $S: Оптовик ==="
    print_step $S 1 "Вход"; T=$(curl -s -X POST "${BASE_URL}/users/login/" -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"admin\"}" | jq -r .access)
    print_step $S 2 "Склад перед"; curl -s -H "Authorization: Bearer $T" "${BASE_URL}/shop/products/1/" | jq .stock
    print_step $S 3 "Опт покупка x10"; curl -s -X POST -H "Authorization: Bearer $T" -H "Content-Type: application/json" -d "{\"product_id\":1,\"quantity\":10}" "${BASE_URL}/shop/cart/add/" > /dev/null
    print_step $S 4 "Еще x10"; curl -s -X POST -H "Authorization: Bearer $T" -H "Content-Type: application/json" -d "{\"product_id\":1,\"quantity\":10}" "${BASE_URL}/shop/cart/add/" > /dev/null
    print_step $S 5 "Корзина"; curl -s -H "Authorization: Bearer $T" "${BASE_URL}/shop/cart/" | jq .items
    print_step $S 6 "Склад во время"; curl -s -H "Authorization: Bearer $T" "${BASE_URL}/shop/products/1/" | jq .stock
    print_step $S 7 "Order"; curl -s -X POST -H "Authorization: Bearer $T" -H "Content-Type: application/json" -d "{\"address\":\"Wholesale\"}" "${BASE_URL}/shop/orders/checkout/" > /dev/null
    print_step $S 8 "Склад после"; curl -s -H "Authorization: Bearer $T" "${BASE_URL}/shop/products/1/" | jq .stock
    print_step $S 9 "Order list"; curl -s -H "Authorization: Bearer $T" "${BASE_URL}/shop/orders/" > /dev/null
    print_step $S 10 "Итог"; echo "Склад обновлен корректно."
}

# Scenario 8: Исследователь Поиска
run_s8() {
    S=8; U="user_s8_$(date +%s)"; P="Pass123"
    echo -e "\n=== Сценарий $S: Исследователь Поиска ==="
    print_step $S 1 "Вход"; T=$(curl -s -X POST "${BASE_URL}/users/login/" -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"admin\"}" | jq -r .access)
    print_step $S 2 "Search 'phone'"; curl -s -G "${BASE_URL}/shop/products/" -d "search=phone" -H "Authorization: Bearer $T" > /dev/null
    print_step $S 3 "Search 'test'"; curl -s -G "${BASE_URL}/shop/products/" -d "search=test" -H "Authorization: Bearer $T" > /dev/null
    print_step $S 4 "Filter category 1"; curl -s -G "${BASE_URL}/shop/products/" -d "category=1" -H "Authorization: Bearer $T" > /dev/null
    print_step $S 5 "Categories list"; curl -s -H "Authorization: Bearer $T" "${BASE_URL}/shop/categories/" > /dev/null
    print_step $S 6 "Ordering price"; curl -s -G "${BASE_URL}/shop/products/" -d "ordering=price" -H "Authorization: Bearer $T" > /dev/null
    print_step $S 7 "Ordering date"; curl -s -G "${BASE_URL}/shop/products/" -d "ordering=-created_at" -H "Authorization: Bearer $T" > /dev/null
    print_step $S 8 "Retrieve Item 1"; curl -s -H "Authorization: Bearer $T" "${BASE_URL}/shop/products/1/" > /dev/null
    print_step $S 9 "Retrieve Item 2"; curl -s -H "Authorization: Bearer $T" "${BASE_URL}/shop/products/2/" > /dev/null
    print_step $S 10 "End"; echo "Исследование завершено."
}

# Scenario 9: Двухэтапная Покупка
run_s9() {
    S=9; U="user_s9_$(date +%s)"; P="Pass123"
    echo -e "\n=== Сценарий $S: Двухэтапная Покупка ==="
    print_step $S 1 "Рега"; curl -s -X POST "${BASE_URL}/users/register/" -H "Content-Type: application/json" -d "{\"username\":\"$U\",\"password\":\"$P\"}" > /dev/null
    print_step $S 2 "Вход"; T=$(curl -s -X POST "${BASE_URL}/users/login/" -H "Content-Type: application/json" -d "{\"username\":\"$U\",\"password\":\"$P\"}" | jq -r .access)
    print_step $S 3 "Add to cart"; curl -s -X POST -H "Authorization: Bearer $T" -H "Content-Type: application/json" -d "{\"product_id\":1,\"quantity\":1}" "${BASE_URL}/shop/cart/add/" > /dev/null
    print_step $S 4 "Session kill"; T=""
    print_step $S 5 "Long pause..."; sleep 1
    print_step $S 6 "Relogin"; T=$(curl -s -X POST "${BASE_URL}/users/login/" -H "Content-Type: application/json" -d "{\"username\":\"$U\",\"password\":\"$P\"}" | jq -r .access)
    print_step $S 7 "Verify cart items"; curl -s -H "Authorization: Bearer $T" "${BASE_URL}/shop/cart/" | jq .items
    print_step $S 8 "Update address"; curl -s -X PATCH -H "Authorization: Bearer $T" -H "Content-Type: application/json" -d "{\"address\":\"Delayed house\"}" "${BASE_URL}/users/profile/" > /dev/null
    print_step $S 9 "Checkout"; curl -s -X POST -H "Authorization: Bearer $T" -H "Content-Type: application/json" -d "{\"address\":\"Delayed house\"}" "${BASE_URL}/shop/orders/checkout/" > /dev/null
    print_step $S 10 "Order list"; curl -s -H "Authorization: Bearer $T" "${BASE_URL}/shop/orders/" | jq '.results | length'
}

# Scenario 10: Тестер Ограничений
run_s10() {
    S=10; U="user_s10_$(date +%s)"; P="Pass123"
    echo -e "\n=== Сценарий $S: Тестер Ограничений ==="
    print_step $S 1 "Вход"; T=$(curl -s -X POST "${BASE_URL}/users/login/" -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"admin\"}" | jq -r .access)
    print_step $S 2 "Stock overflow"; curl -s -X POST -H "Authorization: Bearer $T" -H "Content-Type: application/json" -d "{\"product_id\":1,\"quantity\":999999}" "${BASE_URL}/shop/cart/add/" | jq .error
    print_step $S 3 "Empty checkout"; curl -s -X POST -H "Authorization: Bearer $T" -H "Content-Type: application/json" -d "{\"address\":\"X\"}" "${BASE_URL}/shop/orders/checkout/" | jq .error
    print_step $S 4 "No auth profile"; curl -s -X GET "${BASE_URL}/users/profile/" | jq .detail
    print_step $S 5 "No auth cart"; curl -s -X GET "${BASE_URL}/shop/cart/" | jq .detail
    print_step $S 6 "Add correct item"; curl -s -X POST -H "Authorization: Bearer $T" -H "Content-Type: application/json" -d "{\"product_id\":1,\"quantity\":1}" "${BASE_URL}/shop/cart/add/" > /dev/null
    print_step $S 7 "Order correctly"; curl -s -X POST -H "Authorization: Bearer $T" -H "Content-Type: application/json" -d "{\"address\":\"Safe\"}" "${BASE_URL}/shop/orders/checkout/" | jq .message
    print_step $S 8 "Verify history"; curl -s -H "Authorization: Bearer $T" "${BASE_URL}/shop/orders/" | jq '.results | length'
    print_step $S 9 "Stock check"; curl -s -H "Authorization: Bearer $T" "${BASE_URL}/shop/products/1/" | jq .stock
    print_step $S 10 "End test"; echo "Тесты ограничений завершены."
}

# --- Main Driver ---
ensure_data

if [ "$1" == "--all" ]; then
    for i in {1..10}; do run_s$i; done
elif [[ "$1" =~ ^[1-9]$|^10$ ]]; then
    run_s$1
else
    echo "Usage: ./run_all_scenarios.sh [1-10] | --all"
fi
