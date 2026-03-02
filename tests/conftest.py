import sys
import types


def _install_fake_config():
    """
    Глобально подменяем app.config до импорта любых модулей приложения.
    Это убирает падения на внешних зависимостях и даёт тестовые значения config/token_key.
    """
    fake_config = types.ModuleType("app.config")

    class Config:
        # --- Mongo ---
        DATABASE_URL = "mongodb://user:pass@localhost:27017"
        DATABASE_NAME = "test_db"
        # ВАЖНО: в твоём MongoGateway ожидаются DATABASE_USER/DATABASE_PASSWORD,
        # а у тебя местами используется DATABASE_USERNAME. Дадим оба.
        DATABASE_USER = "user"
        DATABASE_USERNAME = "user"
        DATABASE_PASSWORD = "pass"

        # --- MinIO/S3 ---
        MINIO_ENDPOINT = "http://minio.local"
        MINIO_ACCESS_KEY = "access"
        MINIO_SECRET_KEY = "secret"
        MINIO_BUCKET = "bucket-test"

        # --- Tokens ---
        ACCESS_TOKEN_EXPIRE_TIME = 60 * 15
        REFRESH_TOKEN_EXPIRE_TIME = 60 * 60 * 24 * 7

        # --- Redis ---
        REDIS_HOST = "localhost"
        REDIS_PORT = 6379
        REDIS_PASSWORD = ""
        REDIS_URL = "redis://localhost:6379"

        DEBUG = True

    # В проекте у тебя используется: from app.config import config, token_key
    fake_config.Config = Config
    fake_config.config = Config()  # instance, чтобы работало config.ACCESS_TOKEN_EXPIRE_TIME
    fake_config.token_key = "test-token-key"

    sys.modules["app.config"] = fake_config


def _install_fake_boto3_and_botocore():
    """
    Чтобы импорт app.adapters.gateways.s3 не требовал реальных boto3/botocore.
    """
    botocore = types.ModuleType("botocore")
    botocore_exceptions = types.ModuleType("botocore.exceptions")

    class ClientError(Exception):
        def __init__(self, response=None, operation_name="Unknown"):
            self.response = response or {"Error": {"Code": "Mocked", "Message": "Mocked"}}
            self.operation_name = operation_name
            super().__init__(self.response["Error"]["Message"])

    botocore_exceptions.ClientError = ClientError
    botocore.exceptions = botocore_exceptions

    sys.modules["botocore"] = botocore
    sys.modules["botocore.exceptions"] = botocore_exceptions

    boto3 = types.ModuleType("boto3")

    def client(*args, **kwargs):
        raise RuntimeError("boto3.client should be mocked in tests")

    boto3.client = client
    sys.modules["boto3"] = boto3


def _install_fake_paseto():
    """
    Подменяем paseto, чтобы pytest не падал на импорте из-за pysodium/libsodium.
    Роутер auth.py импортирует paseto на верхнем уровне, даже если в тестах он не используется.
    """
    fake_paseto = types.ModuleType("paseto")
    fake_paseto.__dict__.update({"__version__": "0.0-test"})
    sys.modules["paseto"] = fake_paseto

def _install_fake_jam():
    """
    Подменяем пакет jam, который импортируется в SecurityService:
        from jam import utils
    В тестах роутеров нам этот пакет не нужен, но он ломает collection.
    """
    jam = types.ModuleType("jam")
    jam_utils = types.ModuleType("jam.utils")

    # Если где-то в коде вызываются функции из jam.utils — лучше дать заглушки,
    # чтобы не было AttributeError в рантайме.
    def _not_implemented(*args, **kwargs):
        raise RuntimeError("jam.utils is mocked in tests and should not be used")

    # Часто такие пакеты содержат хелперы для IP/RateLimit/Hash/etc.
    # Дадим универсальную заглушку.
    jam_utils.__dict__.update(
        {
            "__all__": [],
            "not_implemented": _not_implemented,
        }
    )

    jam.utils = jam_utils
    sys.modules["jam"] = jam
    sys.modules["jam.utils"] = jam_utils


_install_fake_jam()
_install_fake_config()
_install_fake_boto3_and_botocore()
_install_fake_paseto()