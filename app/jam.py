from jam import Jam
from app.config import config

config = {  # type: ignore
    "auth_type": "jwt",
    "secret_key": config.JWT_SECRET_KEY,
    "alg": "HS256",
    "expire": config.JWT_EXPIRE_TIME,
}

jam = Jam(config=config)
