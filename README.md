# Bumibrew - Sustainable Market Backend

A backend service for a sustainable market built with Flask. This project provides APIs for managing users, products, orders, and more, with features like authentication, database migrations, and caching.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [1. Initialize Project](#1-initialize-project)
- [2. Add Dependencies](#2-add-dependencies)
- [3. Run Server](#3-run-server)
- [4. Run Tests (Optional)](#4-run-tests-optional)
- [5. Set Up Database Migrations](#5-set-up-database-migrations)
- [6. Project Metadata](#6-project-metadata)
- [7. Flask App Directory Structure](#7-flask-app-directory-structure)
- [8. Sample User Data](#8-sample-user-data)
- [9. Deployment to Koyeb](#9-deployment-to-koyeb)
- [10. Contributing](#10-contributing)
- [11. License](#11-license)

---

## Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/indygreg/uv) - Universal Python environment manager
- Docker (for deployment)
- PostgreSQL or compatible database
- Redis (for caching)

---

## 1. Initialize Project

Initialize the project environment using `uv`:

```bash
uv init
```

---

## 2. Add Dependencies

Add required dependencies using `uv add`:

```bash
uv add flask                # Web framework
uv add flask-sqlalchemy     # ORM
uv add flask-migrate        # Database migrations
uv add psycopg2-binary      # PostgreSQL driver
uv add pytest               # Testing framework
uv add flask-jwt-extended   # Authentication
uv add pydantic             # Data validation
uv add python-dotenv        # Environment variables
uv add taskipy              # Task automation
uv add flask-cors           # Frontend-backend integration
uv add marshmallow          # Data validation
uv add Flask-Limiter        # Rate limiting
uv add redis                # Caching
uv remove marshmallow-sqlalchemy  # Removed due to conflicts or redundancy

uv export > requirements.txt  # Export dependencies to requirements.txt
```

---

## 3. Run Server

Start the Flask development server on port 8000 with reload and debug enabled:

```bash
uv run task fr
```

The `fr` task is defined in `pyproject.toml` as:

```toml
[tool.taskipy.tasks]
fr = "flask --app app run --port 8000 --reload --debug"
```

---

## 4. Run Tests (Optional)

Run tests with verbose output:

```bash
uv run pytest -s -v
```

---

## 5. Set Up Database Migrations

Initialize and apply database migrations:

```bash
uv run flask db init
uv run flask db migrate -m "Initial migration"
uv run flask db upgrade
```

---

## 6. Project Metadata

Project metadata is defined in `pyproject.toml`:

```toml
[project]
name = "bumibrew"
version = "0.1.0"
description = "Sustainable market backend built with Flask"
readme = "README.md"
requires-python = ">=3.11"

dependencies = [
    "flask",
    "flask-sqlalchemy",
    "flask-jwt-extended",
    "flask-migrate",
    "sqlalchemy",
    "psycopg2-binary",
    "pytest",
    "pytest-cov",
    "black",
    "isort",
    "taskipy>=1.14.1",
    "flask-cors>=5.0.1",
    "marshmallow-sqlalchemy>=1.4.2",
    "python-dotenv>=1.1.0",
]
```

---

## 7. Flask App Directory Structure

```
.
├── instance/                # Environment-specific configs (e.g., secrets, DB URIs)
├── middlewares/             # Custom middleware (auth decorators, error handling, etc.)
├── models/                  # SQLAlchemy database models (User, Product, Order, etc.)
├── repo/                    # Repository layer for DB queries (separates logic from routes)
├── route/                   # Flask Blueprints (auth, product, cart, order endpoints)
├── shared/                  # Utility functions, constants, reusable services
├── tests/                   # Pytest-based unit/integration tests
├── config/                  # App configuration (dev, prod, default settings)
│
├── app.py                   # Main app entrypoint and app factory
├── conftest.py              # Global test fixtures for pytest
├── pyproject.toml           # Project metadata and dependencies (used by `uv`)
├── README.md                # Project documentation and setup instructions
└── uv.lock                  # Locked dependencies for reproducibility
```

---

## 8. Sample User Data

Example JSON objects for different user roles:

```json
{
  "username": "vendortest1",
  "first_name": "Vendor1",
  "last_name": "Test",
  "email": "vendortest1@example.com",
  "phone": "08110000001",
  "password": "vendorpass123",
  "date_of_birth": "1987-04-21",
  "address": "Jl. Vendor No.1",
  "city": "Bandung",
  "state": "Jawa Barat",
  "country": "Indonesia",
  "zip_code": "40111",
  "image_url": "http://example.com/vendor1.jpg",
  "role": "vendor",
  "bank_account": "111222333",
  "bank_name": "Bank Mandiri"
}
```

```json
{
  "username": "customertest1",
  "first_name": "Customer",
  "last_name": "Test",
  "email": "customertest1@example.com",
  "phone": "08110000002",
  "password": "customerpass123",
  "date_of_birth": "1992-06-10",
  "address": "Jl. Customer No.2",
  "city": "Jakarta",
  "state": "DKI Jakarta",
  "country": "Indonesia",
  "zip_code": "10110",
  "image_url": "http://example.com/customer1.jpg",
  "role": "customer",
  "bank_account": "444555666",
  "bank_name": "Bank BCA"
}
```

```json
{
  "username": "admintest1",
  "first_name": "Admin",
  "last_name": "Test",
  "email": "admintest1@example.com",
  "phone": "08110000003",
  "password": "adminpass123",
  "date_of_birth": "1980-01-01",
  "address": "Jl. Admin No.3",
  "city": "Surabaya",
  "state": "Jawa Timur",
  "country": "Indonesia",
  "zip_code": "60222",
  "image_url": "http://example.com/admin1.jpg",
  "role": "admin",
  "bank_account": "777888999",
  "bank_name": "Bank BRI"
}
```

---

## 9. Deployment to Koyeb

To deploy the Flask application to Koyeb, follow these steps:

1. Ensure you have connected your Supabase database and set the necessary environment variables in Koyeb.

2. Add a `Procfile` to your project root with the following content to specify the run command for Koyeb:

```
web: gunicorn --bind 0.0.0.0:$PORT --workers 4 app:app
```

3. Build and push your Docker image to a container registry (e.g., Docker Hub):

```bash
docker build -t your-dockerhub-username/your-app-name:latest .
docker push your-dockerhub-username/your-app-name:latest
```

4. Create or update your Koyeb service to use the pushed Docker image.

5. Set the environment variables in your Koyeb service settings, including:

- `DATABASE_URL` or individual DB connection variables
- `JWT_SECRET_KEY`
- Supabase-related environment variables

6. Deploy the service and monitor the logs to ensure the app starts successfully.

For more details, refer to the [Koyeb documentation](https://koyeb.com/docs).

---

## 10. Contributing

Contributions are welcome! Please open issues or submit pull requests for improvements or bug fixes.

---

## 11. License

Specify your project license here (e.g., MIT License).

---

## 12. API Documentation

The detailed API endpoint documentation for BumiBrew is available at:

[API Endpoint Documentation - BumiBrew](https://pointed-perigee-309.notion.site/API-ENDPOINT-DOCUMENTATION-BumiBrew-1e165fc7cbc880fa99c6fba6997f97fd)
