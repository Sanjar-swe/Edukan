#!/bin/bash

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}--- Запуск тестов Domain-Centric архитектуры ---${NC}"

# 1. Запуск Юнит-тестов Сервисного слоя (без HTTP)
echo -e "\n${GREEN}[1/2] Запуск юнит-тестов сервиса (shop/tests_services.py)...${NC}"
../venv/bin/pytest ../shop/tests_services.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Юнит-тесты сервиса пройдены!${NC}"
else
    echo -e "${RED}❌ Юнит-тесты сервиса провалены!${NC}"
    exit 1
fi

# 2. Запуск Интеграционных тестов (через API)
echo -e "\n${GREEN}[2/2] Запуск интеграционных тестов API (shop/tests_robustness.py)...${NC}"
../venv/bin/pytest ../shop/tests_robustness.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Интеграционные тесты пройдены!${NC}"
else
    echo -e "${RED}❌ Интеграционные тесты провалены!${NC}"
    exit 1
fi

echo -e "\n${GREEN}--- Все проверки успешно завершены! Архитектура подтверждена. ---${NC}"
