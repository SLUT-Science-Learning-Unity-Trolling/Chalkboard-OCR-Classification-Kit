from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True, slots=True)
class TokenClaims:
    """Базовые claims для токена."""
    sub: str
    type: Literal["access", "refresh"]
    jti: str
    username: str | None = None
    email: str | None = None