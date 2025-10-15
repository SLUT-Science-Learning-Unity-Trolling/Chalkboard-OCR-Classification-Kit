# Модуль image_repo

Модуль содержит класс ImageRepo для работы с базой данных MongoDB.

## Класс ImageRepo

**Класс для работы с базой данных MongoDB.**

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
        super().__init__(gateway, collection_name="images")
```
---