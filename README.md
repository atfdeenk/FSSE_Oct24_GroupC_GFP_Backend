### 1. Initialize Project

```bash
uv init
```

### 2. Add Dependencies

```bash
uv add flask                # web framework
uv add flask-sqlalchemy     # ORM
uv add flask-migrate        # DB migrations
uv add psycopg2-binary      # DB driver
uv add pytest               # for testing
uv add flask-jwt-extended   # for authentication
uv add pydantic             # for data validation
uv add python-dotenv        # for environment variables
uv add taskipy              # for task automation

uv add flask-cors           # for frontend-backend integration
uv add marshmallow-sqlalchemy # for data validation

```

```toml
    [tool.taskipy.tasks]
    fr = "flask --app app run --port 8000 --reload --debug"
```

### Run server:

```bash
uv run task fr
```

### 3. Run Tests (Optional)

```bash
uv run pytest -s -v
```

### 4. Set Up Database Migrations

```bash
uv run flask db init
uv run flask db migrate -m "Initial migration"
uv run flask db upgrade
```

### 5. Flask App Directory Structure

```bash
.
├── instance/                # Environment-specific configs (e.g., secrets, DB URIs)
├── middlewares/            # Custom middleware (auth decorators, error handling, etc.)
├── models/                 # SQLAlchemy database models (User, Product, Order, etc.)
├── repo/                   # Repository layer for DB queries (separates logic from routes)
├── route/                  # Flask Blueprints (auth, product, cart, order endpoints)
├── shared/                 # Utility functions, constants, reusable services
├── tests/                  # Pytest-based unit/integration tests
├── config/                 # App configuration (dev, prod, default settings)
│
├── app.py                  # Main app entrypoint and app factory
├── conftest.py             # Global test fixtures for pytest
├── pyproject.toml          # Project metadata and dependencies (used by `uv`)
├── README.md               # Project documentation and setup instructions
└── uv.lock                 # Locked dependencies for reproducibility
```

---

### Step 2: Deploy to Koyeb

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
