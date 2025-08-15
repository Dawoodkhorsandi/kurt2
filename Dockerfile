FROM python:3.11.9-slim AS base

ENV PYTHONUNBUFFERED 1

WORKDIR /app
ENV PYTHONPATH=/app/src
RUN pip install --no-cache-dir poetry==2.1.4

COPY poetry.lock pyproject.toml ./

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-root


COPY . .


# ---- API SERVER STAGE ----
FROM base AS api_server

EXPOSE 8000

CMD ["poetry", "run", "gunicorn", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "src.api_server.app:app"]


# ---- LOG WORKER STAGE ----
FROM base AS log_worker

CMD ["poetry", "run", "python", "-m", "src.log_worker.worker"]