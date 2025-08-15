# ---- BASE STAGE ----
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app/src

WORKDIR /app

RUN pip install --no-cache-dir poetry==2.1.4

COPY . .

COPY poetry.lock pyproject.toml ./

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-root



# ---- API SERVER STAGE ----
FROM base AS api_server

EXPOSE 8000

CMD ["gunicorn", "src.api_server.app:app", "--workers", "4", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]



# ---- LOG WORKER STAGE ----
FROM base AS log_worker
CMD ["poetry", "run", "python","-m", "log_worker.worker"]