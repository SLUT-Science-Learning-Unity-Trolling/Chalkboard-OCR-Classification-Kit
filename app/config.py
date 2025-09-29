import os

from dotenv import load_dotenv


load_dotenv()


class Config:
    DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
    DATABASE_PORT = os.getenv("DATABASE_PORT", "27017")
    DATABASE_USER = os.getenv("DATABASE_USER")
    DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "mongodb")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        f"mongodb://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}",
    )
