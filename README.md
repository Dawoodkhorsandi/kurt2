# Kurt - A Simple URL Shortener

Kurt (کوردی: کورت) means "Short" in Kurdish.

This project is a robust and scalable URL shortening service built with Python. It features a clean architecture, asynchronous task handling, and a decoupled design, making it efficient and maintainable.

## Project History

This project, `kurt2`, is the second iteration of a URL shortener by the same author. The original version, **[kurt](https://github.com/Dawoodkhorsandi/kurt)**, was implemented about 5 years ago using Django. This new version is a complete rewrite, leveraging modern Python technologies like FastAPI and `asyncio` to build a more performant and scalable system from the ground up.

---

## Core Features

- **Fast & Asynchronous**: Built with FastAPI and `asyncio` for high performance.
- **Decoupled Logging**: URL visit logging is handled by a separate background worker, ensuring user-facing endpoints are as fast as possible.
- **Pluggable Infrastructure**: Easily switch between Redis and in-memory implementations for caching and message queuing.
- **Database Migrations**: Uses Alembic to manage database schema changes systematically.
- **Structured Logging**: Centralized and configurable logging for easy debugging and monitoring.
- **Modern Dependency Management**: Uses Poetry for clear and reliable dependency management.

---

## Project Structure

- **/api_server**: Contains the FastAPI web application that handles user requests.
- **/log_worker**: A separate application that consumes visit events from the message queue and updates the database.
- **/src/core**: The core business logic, entities, and application services.
    - **/infrastructures**: Contains implementations for external services like databases, caches, and message queues.
    - **/shorten**: The primary domain logic for URL shortening and visit tracking.
- **/alembic**: Houses the database migration scripts.

---

## Getting Started

### 1. Installation & Dependency Management

This project uses **[Poetry](https://python-poetry.org/)** to manage dependencies.

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd kurt2
    ```

2.  **Install Poetry:**
    Follow the official instructions at [python-poetry.org](https://python-poetry.org/docs/#installation) to install Poetry on your system.

3.  **Install dependencies:**
    Once Poetry is installed, run the following command from the project root. This will create a virtual environment and install all the required packages from the `pyproject.toml` and `poetry.lock` files.

    ```bash
    poetry install
    ```

### 2. Configuration

The application is configured using environment variables. You can create a `.env` file in the project root to manage them.

| Variable              | Description                                                                 | Default       | Required |
| --------------------- | --------------------------------------------------------------------------- | ------------- | -------- |
| `DATABASE_URL`        | The SQLAlchemy connection string for your database.                         | `None`        | **Yes**  |
| `CACHE_TYPE`          | The type of cache to use. Can be `in-memory` or `redis`.                    | `in-memory`   | No       |
| `MESSAGE_QUEUE_TYPE`  | The type of message queue to use. Can be `in-memory` or `redis`.            | `in-memory`   | No       |
| `REDIS_DSN`           | The Data Source Name for Redis. Required if using Redis for cache or queue. | `None`        | **If Redis is used** |
| `API_HOST`            | The host on which the API server will run.                                  | `0.0.0.0`     | No       |
| `API_PORT`            | The port for the API server.                                                | `8000`        | No       |

**Example `.env` file:**
```
DATABASE_URL="postgresql+asyncpg://user:password@db_host/kurt"
CACHE_TYPE="redis"
MESSAGE_QUEUE_TYPE="redis"
REDIS_DSN="redis://localhost:6379/0"
```

### 3. Database Migrations

The project uses Alembic to handle database schema migrations. Commands should be run using `poetry run` to execute them within the project's virtual environment.

1.  **Generate a new migration:**
    After making changes to the models in `src/core/shorten/entities/`, run the following command to automatically generate a migration script.

    ```bash
    poetry run alembic revision --autogenerate -m "Describe your model changes here"
    ```

2.  **Apply migrations:**
    To apply all pending migrations and bring the database up to date, run:

    ```bash
    poetry run alembic upgrade head
    ```

---

## Running the Application

### Running with Docker (Recommended)

The easiest way to get the entire application stack running is by using the provided Docker Compose file. This will start the API server, the log worker, a PostgreSQL database, and a Redis instance.

1.  **Create a `.env` file:**
    Make sure you have a `.env` file in the project root with your desired configuration (see the Configuration section above). The `docker-compose.yml` file is set up to pass these environment variables to the application containers.

2.  **Build and run the containers:**

    ```bash
    docker-compose up --build
    ```

    This command will build the Docker images and start all the services. The API server will be available at `http://localhost:8000`.

3.  **Run migrations in Docker:**
    Before the application can function correctly, you need to run the database migrations inside the running container.

    ```bash
    docker-compose exec api-server alembic upgrade head
    ```

### Docker Compose Explained

The `docker-compose.yml` file defines and configures the multi-container Docker application. When you run `docker-compose up`, it orchestrates the creation of the following services:

*   **`db`**:
    *   **What it is**: A PostgreSQL database container.
    *   **Image**: Uses the official `postgres:14-alpine` image.
    *   **Persistence**: It uses a named volume called `postgres_data` to ensure that your database's data persists even if the container is removed and recreated.
    *   **Configuration**: It's configured using environment variables from your `.env` file for the database name, user, and password.

*   **`redis`**:
    *   **What it is**: A Redis in-memory data store.
    *   **Image**: Uses the official `redis:7-alpine` image.
    *   **Purpose**: It serves as the message queue for communication between the API server and the log worker, and can also be used for caching.

*   **`api_server`**:
    *   **What it is**: The main web application that handles incoming API requests.
    *   **Build**: It's built from the local `Dockerfile` using a specific multi-stage build target named `api_server`.
    *   **Dependencies**: It's configured to start only after the `db` and `redis` services are running.
    *   **Scaling**: The `deploy: replicas: 3` key suggests that the system is designed to run three instances of the API server for handling more traffic, which would be orchestrated by the `nginx_load_balancer`.

*   **`log_worker`**:
    *   **What it is**: The background worker that consumes messages from the Redis queue.
    *   **Build**: It's also built from the local `Dockerfile`, but it uses the `log_worker` build target.
    *   **Dependencies**: It also depends on the `db` and `redis` services.
    *   **Scaling**: It's configured to run two instances, allowing for parallel processing of background jobs.

*   **`nginx_load_balancer`**:
    *   **What it is**: An Nginx web server that acts as a reverse proxy and load balancer.
    *   **Function**: It's the public entry point to the application. It listens on port 80 and distributes incoming HTTP requests across the three `api_server` instances.
    *   **Configuration**: Its behavior is defined by the `nginx/nginx.conf` file, which is mounted into the container.

In summary, this `docker-compose` setup creates a complete, isolated environment for your application that mirrors a production setup, with a database, a message queue, a scalable API, scalable background workers, and a load balancer.

### Manual Setup

#### API Server

The API server is the main entry point for user interactions (creating short URLs and redirecting).

To run the server in a development environment:

```bash
poetry run uvicorn api_server.app:app --host 0.0.0.0 --port 8000 --reload
```

#### Log Worker

The log worker is a background process that listens for visit events on the message queue and updates the database. It's crucial for this to be running to see visit counts increase.

To run the worker:

```bash
poetry run python -m log_worker.worker
```

---

## Deployment Example

For a production environment, it's recommended to use a process manager like `systemd` and a production-grade web server like `gunicorn`.

**Example Gunicorn command for the API server:**

```bash
poetry run gunicorn api_server.app:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```
- `-w 4`: Specifies 4 worker processes. Adjust based on your server's CPU cores.
- `-k uvicorn.workers.UvicornWorker`: Uses Uvicorn's worker class to run the ASGI application.

You can create a `systemd` service file to manage both the API server and the log worker, ensuring they restart automatically on failure.

---

## Code Style

This project uses the **[black](https://github.com/psf/black)** code formatter to ensure a consistent code style. `black` is included as a development dependency, so it will be installed when you run `poetry install`.

All contributions should be formatted with `black` before being submitted.

### Usage

To format the entire project, run the following command from the root directory:

```bash
poetry run black .
```
