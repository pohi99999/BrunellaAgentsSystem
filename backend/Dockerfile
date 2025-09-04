FROM python:3.11-slim

# Alap csomagok
RUN apt-get update && apt-get install -y \
    git curl build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Függőségek telepítése
COPY pyproject.toml /app/
RUN pip install --upgrade pip && pip install poetry \
    && poetry config virtualenvs.create false

# Másold a teljes projektet
COPY . /app

RUN poetry install --no-root --no-interaction --no-ansi

# Indítsd az API-t Uvicorn-nal
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
