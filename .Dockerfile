FROM python:3.11-slim-bullseye

WORKDIR /app

RUN curl -sSL https://install.python-poetry.org | python3 -

COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

COPY src ./src
COPY data ./data

ENTRYPOINT ["python -m", "src.main"]
