#!/bin/bash

# Configuration
BASE_URL="http://localhost:8000/api"
SWAGGER_UI_URL="http://localhost:8000/api/schema/swagger-ui/"
SCHEMA_URL="http://localhost:8000/api/schema/"
REDOC_URL="http://localhost:8000/api/schema/redoc/"

echo "============================================"
echo "   Verifying drf-spectacular Migration"
echo "============================================"

# 1. Check Swagger UI
echo -n "Checking Swagger UI ($SWAGGER_UI_URL)... "
HTTP_CODE=$(curl -o /dev/null -s -w "%{http_code}\n" "$SWAGGER_UI_URL")
if [ "$HTTP_CODE" == "200" ]; then
    echo "OK"
else
    echo "FAIL (HTTP $HTTP_CODE)"
    exit 1
fi

# 2. Check Redoc UI
echo -n "Checking Redoc UI ($REDOC_URL)... "
HTTP_CODE=$(curl -o /dev/null -s -w "%{http_code}\n" "$REDOC_URL")
if [ "$HTTP_CODE" == "200" ]; then
    echo "OK"
else
    echo "FAIL (HTTP $HTTP_CODE)"
    exit 1
fi

# 3. Check Schema (YAML)
echo -n "Checking API Schema Download ($SCHEMA_URL)... "
HTTP_CODE=$(curl -o /dev/null -s -w "%{http_code}\n" "$SCHEMA_URL")
if [ "$HTTP_CODE" == "200" ]; then
    echo "OK"
else
    echo "FAIL (HTTP $HTTP_CODE)"
    exit 1
fi

# 4. Check Authentication (Login) to ensure API is functional
echo -n "Checking API Authentication (Login)... "
# Assuming default user from simulate_user.sh or creating a new temporary one might be needed.
# Since we don't know credentials, we can try to access a public endpoint.
HTTP_CODE=$(curl -o /dev/null -s -w "%{http_code}\n" "${BASE_URL}/shop/products/")
if [ "$HTTP_CODE" == "200" ]; then
    echo "OK (Public endpoint accessible)"
else
    echo "FAIL (HTTP $HTTP_CODE on public endpoint)"
    exit 1
fi

echo -e "\nAll checks passed! drf-spectacular is correctly configured."
