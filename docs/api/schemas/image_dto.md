# Модуль image_dto

Модуль содержит DTO для работы с изображениями.

## Класс UploadImageDTO

**Модель данных для загрузки изображения.**

**Args:**
- `url_to_upload (str)`: Путь к изображению.
## Класс ImageDTO

**Модель данных для изображения.**

**Args:**
- `user_id (str)`: Уникальный идентификатор пользователя.
- `url (str)`: Путь к изображению.

---
## def fromrow:
#### Создает экземпляр класса из словаря.

#### Аргументы
| Аргумент | Тип | Описание |
|----------|-----|----------|
| `row` | `dict[str, Any]` | Словарь с данными пользователя |

#### Возвращает
| Тип | Описание |
|-----|----------|
| `ImageDTO` | Экземпляр класса ImageDTO |

```python
    @classmethod
    def fromrow(cls, row: dict[str, Any]) -> ImageDTO:
        """Создает экземпляр класса из словаря.

        Args:
            row (dict[str, Any]): Словарь с данными пользователя

        Returns:
            ImageDTO: Экземпляр класса ImageDTO
        """
        return cls(
            id=str(row.get("_id") or row.get("id")),
            user_id=str(row.get("_user_id") or row.get("user_id")),
            url=row["url"],
        )
```
---