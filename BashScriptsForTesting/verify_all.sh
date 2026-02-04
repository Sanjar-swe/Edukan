#!/bin/bash

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}--- Глобальная проверка проекта OnlineDukan ---${NC}"

# 1. Запуск Юнит-тестов Сервисов (Domain Logic)
echo -e "\n${GREEN}[1/3] Запуск юнит-тестов сервиса (shop/tests_services.py)...${NC}"
../venv/bin/pytest ../shop/tests_services.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Сервисы проверены!${NC}"
else
    echo -e "${RED}❌ Ошибка в сервисах!${NC}"
    exit 1
fi

# 2. Запуск Юнит-тестов Celery Tasks (Async Logic)
echo -e "\n${GREEN}[2/3] Запуск юнит-тестов задач (shop/tests_tasks.py)...${NC}"
../venv/bin/pytest ../shop/tests_tasks.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Фоновые задачи проверены!${NC}"
else
    echo -e "${RED}❌ Ошибка в задачах!${NC}"
    exit 1
fi

# 3. Запуск Интеграционных тестов API (Robustness)
echo -e "\n${GREEN}[3/3] Запуск интеграционных тестов API (shop/tests_robustness.py)...${NC}"
../venv/bin/pytest ../shop/tests_robustness.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ API проверено!${NC}"
else
    echo -e "${RED}❌ Ошибка в API!${NC}"
    exit 1
fi

echo -e "\n${GREEN}--- Все проверки успешно завершены! Система готова к продакшену. ---${NC}"
