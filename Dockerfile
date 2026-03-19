FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    g++ \
    python3-dev \
    libffi-dev \
    libsodium-dev \
    libgl1 \
    libglx0 \
    libglib2.0-0 \
    libpng-dev \
    libjpeg-dev \
    libgomp1 \
    tesseract-ocr \
    libtesseract-dev \
    pandoc \
    lmodern \
    fonts-liberation \
    texlive-xetex \
    texlive-latex-base \
    texlive-fonts-recommended \
    texlive-latex-extra \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir "poetry>=1.5.1" \
    && poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock* ./

RUN poetry install --no-interaction --no-ansi --no-root

COPY . .

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
