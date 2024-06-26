FROM python:3.11-bookworm as builder

RUN pip install poetry==1.8.3

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN --mount=type=cache,id=s/e642758f-83db-481a-a44b-0fe14773b2d2-$POETRY_CACHE_DIR,target=$POETRY_CACHE_DIR poetry install --no-root

RUN .venv/bin/pip install pysqlite3-binary==0.5.3

FROM python:3.11-bookworm as runtime

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY src /app/src
RUN ls -la /app/src
WORKDIR /app/src

EXPOSE 8080
ENTRYPOINT ["python", "-u", "main.py"]