FROM python:3.12-bookworm

ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100

WORKDIR /app

RUN pip install --no-cache-dir "poetry"

COPY pyproject.toml poetry.lock .
RUN poetry config --no-cache virtualenvs.create false && poetry install --no-cache --no-root --no-interaction --no-ansi --only main

COPY . .
RUN poetry install --no-cache --no-interaction --no-ansi --only main

# CMD ["poetry", "run", "faststream", "run", "app.main2:app"]
CMD ["poetry", "run", "python", "app/main.py"]

