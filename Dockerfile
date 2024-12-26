FROM python:3.9.6

WORKDIR /app

RUN curl -sSL https://install.python-poetry.org | python3 -

COPY pyproject.toml poetry.lock ./
RUN ~/.local/share/pypoetry/venv/bin/poetry config virtualenvs.create false && \
    ~/.local/share/pypoetry/venv/bin/poetry install --no-root

COPY src ./src
COPY data ./data

ENTRYPOINT ["python", "-m", "src.main"]
