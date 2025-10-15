# Модуль user_repo

Модуль содержит класс UserRepo для работы с базой данных MongoDB.

## Класс UserRepo

**Репозиторий для работы с пользователями.**

---
## def init:
#### Инициализация репозитория.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `gateway` | `DBGatewayInterface` | гейтвей для работы с базой данных. |

```python
    def __init__(self, gateway: DBGatewayInterface) -> None:
        """Инициализация репозитория.

        Args:
            gateway (DBGatewayInterface): гейтвей для работы с базой данных.
        """
        super().__init__(gateway, collection_name="users")
```
---