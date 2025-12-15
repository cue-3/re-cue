#!/usr/bin/env bash
set -e

echo "=== Local Smoketest Debug ==="
echo ""

# Ensure Python package is installed
echo "📦 Installing Python package..."
cd reverse-engineer-python
pip install -e . > /dev/null 2>&1
cd ..

# Test from workspace root
echo ""
echo "=== Test 1: Running from workspace root with --path ==="
pwd
recue --spec --plan --use-cases --data-model \
  --description "Spring Boot demo application for task and user management" \
  --path sample-apps/spring-boot-demo \
  --verbose

echo ""
echo "=== Checking for output directories ==="
find . -type d -name "re-*" | head -20

echo ""
echo "=== Test 2: Check what directory was created ==="
ls -la sample-apps/spring-boot-demo/ | grep "^d"

echo ""
echo "=== Test 3: If re-bookstore-api exists in spring-boot-demo ==="
if [ -d "sample-apps/spring-boot-demo/re-bookstore-api" ]; then
  echo "✅ Found re-bookstore-api in spring-boot-demo"
  ls -la sample-apps/spring-boot-demo/re-bookstore-api/
else
  echo "❌ re-bookstore-api NOT in spring-boot-demo"
  echo "Searching entire workspace..."
  find . -type d -name "re-bookstore-api" 2>/dev/null
fi

echo ""
echo "=== Test 4: Alternative - cd into directory and use --path . ==="
cd sample-apps/spring-boot-demo
pwd
recue --spec --plan \
  --description "Spring Boot demo application" \
  --path . \
  --verbose

echo ""
echo "=== Final check ==="
ls -la | grep "^d"
