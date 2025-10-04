from typing import Any
from litestar import get
from litestar.di import Provide
from app.core.services.auth_service import AuthService
from app.schema.user_dto import UserDTO


@get(
    "/me", dependencies={"current_user": Provide(AuthService.get_current_user)}
)
async def get_me(current_user: UserDTO | None) -> dict[str, Any]:
    """Эндпоинт возвращает данные текущего пользователя."""
    if current_user:
        return {"success": True, "user": current_user}

    return {
        "success": False,
        "message": "Пользователь не зарегистрирован или не найден в системе",
    }
