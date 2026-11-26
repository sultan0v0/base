FROM python:3.14.4-alpine3.23 AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/venv \
    UV_COMPILE_BYTECODE=1 \
    PATH=/venv/bin:$PATH

WORKDIR /application

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY application/ ./
RUN uv sync --frozen --no-dev

FROM python:3.14.4-alpine3.23 AS runner

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/venv/bin:$PATH

WORKDIR /application
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

COPY --from=builder /venv /venv
COPY --from=builder /application /application
RUN chown -R appuser:appgroup /application

USER appuser
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
