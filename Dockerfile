FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./
COPY app ./app

RUN pip install --upgrade pip \
    && pip install "poetry>=1.5.1" \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
