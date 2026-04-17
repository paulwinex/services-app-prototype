FROM python:3.14-slim AS builder

ARG INSTALL_DEV=false

ENV PATH="/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_CACHE_DIR=/root/.cache/uv \
    UV_COMPILE_BYTECODE=1 \
    UV_FROZEN=1 \
    UV_LINK_MODE=copy \
    UV_NO_MANAGED_PYTHON=1 \
    UV_PROJECT_ENVIRONMENT=/venv \
    UV_PYTHON_DOWNLOADS=never \
    UV_REQUIRE_HASHES=0 \
    UV_VERIFY_HASHES=1 \
    VIRTUAL_ENV=/venv

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv venv $VIRTUAL_ENV && \
    if [ "$INSTALL_DEV" = "true" ]; then \
        uv sync --no-install-project --no-editable; \
    else \
        uv sync --no-install-project --no-editable --no-group dev; \
    fi

COPY ./src /app/src

FROM python:3.14-slim AS production-image

ENV TZ=Europe/Moscow
RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/venv \
    PYTHONPATH="/app/src"

WORKDIR /app/src
COPY --link --from=builder /venv /venv
COPY --link --from=builder /app/src /app/src

EXPOSE 8000
RUN chmod +x /app/src/entrypoint-app.sh
ENTRYPOINT ["/app/src/entrypoint-app.sh"]

FROM python:3.14-slim AS testing-image

ENV TZ=Europe/Moscow
RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/venv \
    PYTHONPATH="/app/src" \
    TESTING=true

WORKDIR /app/src
COPY --link --from=builder /venv /venv
COPY --link --from=builder /app/src /app/src
COPY tests/ /app/tests
COPY pyproject.toml /app/pyproject.toml

RUN chmod +x /app/src/entrypoint-testing.sh
ENTRYPOINT ["/app/src/entrypoint-testing.sh"]