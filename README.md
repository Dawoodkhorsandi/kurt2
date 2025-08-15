# Kurt2: A High-Performance URL Shortener

A little history: "Kurt" means "short" in Kurdish. This project is the second version of a URL shortener originally written 5 years ago. You can see the first version [here](https://github.com/Dawoodkhorsandi/kurt).

Kurt2 is a robust and scalable URL shortener system built with a modern, production-grade technology stack. It is designed for high performance and reliability, featuring a clean, decoupled architecture that is easy to maintain and extend.

## Key Features

*   **Scalable Architecture**: The system is designed to handle a high volume of traffic, with a load-balanced API server and a decoupled background worker for processing tasks.
*   **High-Performance Stack**: Utilizes a powerful combination of technologies, including FastAPI, PostgreSQL, Redis, and NGINX, to deliver a fast and responsive user experience.
*   **Asynchronous Task Processing**: A background worker processes non-critical tasks, such as logging URL visits, asynchronously. This ensures that the API server can respond to user requests as quickly as possible.
*   **Database Connection Pooling**: Uses PgBouncer to efficiently manage database connections, which is crucial for handling a large number of concurrent users.
*   **Clean, Decoupled Codebase**: The project follows the principles of clean architecture, with a clear separation of concerns between the API, business logic, and data layers. This makes the codebase easy to understand, test, and maintain.

## Architecture Overview

The system is composed of several services that work together to provide a seamless user experience.

```
      +-------------------+
      |       User        |
      +-------------------+
              |
              v
      +-------------------+
      |  NGINX Load Balancer |
      +-------------------+
              |
              v
+---------------------------+      +---------------------------+
|   FastAPI API Server (x5)   |      |   Log Worker (x3)         |
+---------------------------+      +---------------------------+
       |           ^                      |
       v           |                      v
+-------------------+      +-------------------+
|   Redis Cache     |      |   Message Queue   |
+-------------------+      +-------------------+
       |           |                      |
       v           +----------------------+
+-------------------+
|    PgBouncer      |
+-------------------+
       |
       v
+-------------------+
|    PostgreSQL     |
+-------------------+
```

## Technologies Used

*   **Backend**: FastAPI, Python 3.10
*   **Database**: PostgreSQL, PgBouncer
*   **Cache**: Redis
*   **Message Queue**: Redis
*   **Web Server**: NGINX, Uvicorn, Gunicorn
*   **ORM**: SQLAlchemy, SQLModel
*   **Dependency Injection**: `dependency-injector`
*   **Migrations**: Alembic
*   **Testing**: Pytest, `pytest-asyncio`
*   **Linting/Formatting**: Ruff, pre-commit

## Getting Started

This project is fully containerized and can be run with a single command.

### Prerequisites

*   Docker
*   Docker Compose

### Installation

1.  **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd kurt2
    ```

2.  **Create an environment file:**

    Copy the example environment file and update it with your desired settings.

    ```bash
    cp .env.example .env
    ```

3.  **Build and run the services:**

    ```bash
    docker-compose up --build
    ```

This will start all the services, including the API server, the background worker, the database, and the cache. The API will be accessible at `http://localhost:80`.

## Application Entrypoints
The system is designed with two distinct entrypoints, allowing for a clear separation of concerns between handling user requests and processing background tasks.

#### 1. API Server (`api_server`)
*   **Purpose**: This is the main web application that handles all incoming HTTP requests from users. It's responsible for creating new short URLs and redirecting users from a short URL to the original long URL.
*   **How it Works**: It's a FastAPI application run by Gunicorn and Uvicorn workers. The `docker-compose.yml` is configured to run multiple instances of the API server, and NGINX acts as a load balancer to distribute traffic among them.

#### 2. Log Worker (`log_worker`)
*   **Purpose**: This is a background worker that processes tasks asynchronously. Its primary job is to log URL visit information (like IP address and user agent) to the database.
*   **How it Works**: When a user visits a short URL, the API server doesn't wait to write the visit data to the database. Instead, it publishes a message to a Redis message queue and immediately redirects the user. The `log_worker` listens for new messages on this queue, consumes them, and writes the data to the PostgreSQL database. This decoupling ensures the API remains fast and responsive.

## Developer Guide

### Running Tests
The project uses `pytest` for testing. To run the test suite, execute the following command from the root of the project:
```bash
pytest
```
**Note**: For the tests to run correctly, you must create a `.env.test` file in the project root. This file should contain the configuration for a separate test database to ensure that the tests do not affect your development database. You can copy `.env.example` to `.env.test` and modify the database connection variables.

### Linting and Formatting
We use `Ruff` for linting and formatting and `pre-commit` to ensure code quality before committing.

1.  **Install pre-commit hooks:**
    ```bash
    pre-commit install
    ```

2.  **Run checks manually:**
    To run all pre-commit hooks on all files:
    ```bash
    pre-commit run --all-files
    ```
    To run Ruff specifically:
    ```bash
    ruff check . --fix
    ```

### Database Migrations
We use `Alembic` to manage database schema migrations.

*   **Note**: If you are setting up the project for the first time, you may need to initialize Alembic.

1.  **Create a new migration:**
    When you make changes to your SQLAlchemy models, you'll need to generate a new migration script:
    ```bash
    alembic revision --autogenerate -m "A descriptive message for your migration"
    ```

2.  **Apply migrations:**
    To apply all pending migrations to your database:
    ```bash
    alembic upgrade head
    ```

## Configuration
The application is configured using environment variables. Create a `.env` file in the project root (you can copy `.env.example`) and fill in the following values:

| Variable                  | Description                                                              | Example                               |
| ------------------------- | ------------------------------------------------------------------------ | ------------------------------------- |
| `LOG_LEVEL`               | The logging level for the application.                                   | `INFO`                                |
| `POSTGRES_HOST`           | The hostname of the PostgreSQL database or PgBouncer.                    | `pgbouncer`                           |
| `POSTGRES_PORT`           | The port of the PostgreSQL database or PgBouncer.                        | `6432`                                |
| `POSTGRES_USER`           | The username for the PostgreSQL database.                                | `user`                                |
| `POSTGRES_PASSWORD`       | The password for the PostgreSQL database.                                | `password`                            |
| `POSTGRES_DB`             | The name of the PostgreSQL database.                                     | `kurt`                                |
| `REDIS_HOST`              | The hostname of the Redis server.                                        | `redis`                               |
| `REDIS_PORT`              | The port of the Redis server.                                            | `6379`                                |
| `REDIS_DB`                | The Redis database number to use for the cache.                          | `0`                                   |
| `REDIS_MESSAGE_QUEUE_DB`  | The Redis database number to use for the message queue.                  | `1`                                   |
| `API_REPLICAS`            | The number of API server instances to run.                               | `5`                                   |
| `WORKER_REPLICAS`         | The number of log worker instances to run.                               | `3`                                   |

## Docker Compose Explained
The `docker-compose.yml` file orchestrates the different services of the application:

*   **`nginx`**: The reverse proxy and load balancer. It distributes incoming traffic across the `api_server` replicas.
*   **`api_server`**: The FastAPI application that handles user requests. It is configured to scale to multiple replicas.
*   **`log_worker`**: The background worker that processes asynchronous tasks from the message queue.
*   **`postgres`**: The PostgreSQL database service.
*   **`pgbouncer`**: A connection pooler for PostgreSQL. The `api_server` and `log_worker` connect to the database through PgBouncer to improve performance.
*   **`redis`**: The Redis server, used for both caching and as a message broker.

## Local Manual Setup
If you prefer to run the application locally without Docker, follow these steps:

1.  **Install Dependencies**:
    *   Install PostgreSQL and Redis on your local machine.
    *   Create a Python virtual environment and install the project dependencies:
        ```bash
        python -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
        ```

2.  **Configure Environment**:
    *   Create a `.env` file and update the `POSTGRES_HOST`, `POSTGRES_PORT`, `REDIS_HOST`, and `REDIS_PORT` variables to point to your local instances (e.g., `localhost`).

3.  **Run Migrations**:
    *   Apply the database migrations to your local PostgreSQL database:
        ```bash
        alembic upgrade head
        ```

4.  **Run the Applications**:
    *   You will need to run the API server and the log worker in separate terminal windows.
    *   **Run the API Server**:
        ```bash
        uvicorn src.api_server.app:app --host 0.0.0.0 --port 8000
        ```
    *   **Run the Log Worker**:
        ```bash
        python -m src.log_worker.worker
        ```

## Project Structure

The project is organized into the following main directories:

*   `src/`: Contains the core application code.
    *   `api_server/`: The FastAPI web application.
    *   `log_worker/`: The asynchronous background worker.
    *   `core/`: The core business logic, services, and repositories.
*   `tests/`: Contains the test suite.
*   `nginx/`: NGINX configuration files.
*   `pgbouncer/`: PgBouncer configuration files.
*   `alembic/`: Alembic database migration scripts.
