FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=apps/chat/pyproject.toml,target=apps/chat/pyproject.toml \
    --mount=type=bind,source=apps/common/pyproject.toml,target=apps/common/pyproject.toml \
    uv sync --frozen --no-install-workspace --no-dev

ADD apps/chat/ ./apps/chat/
ADD apps/common/ ./apps/common/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --all-packages

FROM python:3.13-slim-bookworm

RUN groupadd -r app && useradd -r -g app app

WORKDIR /app

COPY --from=builder --chown=app:app /app/.venv /app/.venv
COPY --from=builder --chown=app:app /app/apps/chat /app/apps/chat
COPY --from=builder --chown=app:app /app/apps/common /app/apps/common/

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/apps/chat"

USER app

CMD ["uvicorn", "apps.chat.app.bootstrap:create_app", "--factory", "--host", "0.0.0.0", "--port", "8080"]
