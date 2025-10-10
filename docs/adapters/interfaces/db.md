# Модуль db

Модуль содержит интерфейс DBGatewayInterface для работы с базой данных.

## Класс DBGatewayInterface

**Гейтвей для подключения к базе данных.**

---
## def get_connection:
#### Получение или создание коннекшена.

```python
    @abstractmethod
    def get_connection(self, **kwargs: dict[str, Any]) -> Any:
        """Получение или создание коннекшена."""
        raise NotImplementedError
```
---