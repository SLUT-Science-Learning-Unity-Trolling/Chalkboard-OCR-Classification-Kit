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
    DATABASE_HOST=localhost
    DATABASE_PORT=27017
    DATABASE_USER=admin
    DATABASE_PASSWORD=secret
    DATABASE_NAME=mongodb

    DEBUG=True

    JWT_SECRET_KEY=SECRET
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