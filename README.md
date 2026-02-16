# Chalkboard-OCR-Classification-Kit

## Как поднять сервер с бэком:
### Сначала скачиваем зависимости:
Без дополнительных библиотек:

```bash
poetry install
```
С библиотеками для документации и тестов:

```bash
poetry install --all-extras
```

### Инициализируем venv:
```bash
poetry env use python3.13
```

### Создайте .env в корне (Пример):
```bash
# MongoDB
DATABASE_HOST=localhost
DATABASE_COMPOSE_HOST=mongo
DATABASE_PORT=27017
DATABASE_USER=admin
DATABASE_PASSWORD=secret
DATABASE_NAME=admin

# JWT
JWT_SECRET_KEY=POPA

# MinIO
MINIO_COMPOSE_ENDPOINT=http://minio:9000
MINIO_ENDPOINT=http://localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=bucket

```

### Поднимите Mongo контейнер:
Можно как через docker, так и через podman, различие только в первом слове команды (Ну и некоторых фишках, но на работоспособность не влияет никак)

```bash
podman run -d --name mongodb -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=secret docker.io/library/mongo:7.0
```

### Проверить контейнер можно через:
Для проверки работающих контейнеров (опять же, можно как docker, так и podman):

```bash
podman ps
```

Для проверки всех когда либо запущенных, но остановленных:

```bash
podman ps -a
```

Для более детального анализа контейнера:
id контейнера можно так же найти через **"podman ps -a"**

```bash
podman inspect {id контейнера}
```

### Запускаем сервер:
```bash
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

## Как поднять сервер с mkdocs:
### Команда запуска сервера:
```bash
PYTHONPATH=. poetry run mkdocs serve
```

## Как установить pre-commit
```bash
pre-commit install
```

## Генерация документации через плагин
Для обычной генерации документации по докстрингам:

```bash
poetry run python app/utils/generate_docs.py
```

Для её генерации и пуша в wiki репозиторий проекта:

```bash
poetry run python app/utils/generate_docs.py --push
```
 
 ## ENV.EXAMPLE

 ```bash
 # MongoDB
DATABASE_HOST=localhost
DATABASE_COMPOSE_HOST=mongo
DATABASE_PORT=27017
DATABASE_USER=admin
DATABASE_PASSWORD=secret
DATABASE_NAME=admin

# JWT
TOKEN_SECRET_KEY=POPA

# MinIO
MINIO_COMPOSE_ENDPOINT=http://minio:9000
MINIO_ENDPOINT=http://localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=bucket

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=secret
```