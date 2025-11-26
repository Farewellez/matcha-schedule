#!/bin/bash

mkdir -p src/api
mkdir -p src/models
mkdir -p src/controllers
mkdir -p src/views
mkdir -p src/utils
mkdir -p tests

touch src/main.py
touch src/config.py

# API
touch src/api/__init__.py
touch src/api/client.py
touch src/api/endpoints.py

# Models
touch src/models/__init__.py
touch src/models/product.py
touch src/models/material.py
touch src/models/order.py
touch src/models/production.py

# Controllers
touch src/controllers/__init__.py
touch src/controllers/priority_queue.py
touch src/controllers/scheduler.py
touch src/controllers/stock_controller.py
touch src/controllers/auth_controller.py

# Views
touch src/views/__init__.py
touch src/views/auth_view.py
touch src/views/admin_view.py
touch src/views/customer_view.py
touch src/views/production_view.py

# Utils
touch src/utils/__init__.py
touch src/utils/validators.py
touch src/utils/helpers.py

# Tests
touch tests/test_auth.py
touch tests/test_products.py
touch tests/test_orders.py
touch tests/test_scheduler.py

# Root files
touch requirements.txt
touch README.md
touch .gitignore
