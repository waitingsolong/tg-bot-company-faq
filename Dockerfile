FROM python:3.11-buster as builder

RUN pip install poetry==1.8.3

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN --mount=type=cache,id=s/dc048e03-703a-4f6d-8aca-3826e891d42a-$POETRY_CACHE_DIR,target=$POETRY_CACHE_DIR poetry install --no-root

FROM python:3.11-slim-buster as runtime

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY src /app/src
RUN ls -la /app/src
WORKDIR /app/src

EXPOSE 8080
ENTRYPOINT ["python", "-u", "main.py"]