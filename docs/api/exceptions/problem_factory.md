# Модуль problem_factory

Фабрика для создания DTO с описанием ошибок.

## Класс ErrorCodes

**Коды ошибок.**

---
## def init:
#### Конструктор.

```python
    def __init__(self, code: str, title: str, status: int) -> None:
        """Конструктор."""
        self.code = code
        self.title = title
        self.status = status
```
---
## def example:
#### Генерирует словарь с описанием ошибки в формате Problem Details.

```python
    def example(self, detail: str) -> dict[str, str | int]:
        """Генерирует словарь с описанием ошибки в формате Problem Details."""
        return {
            "type": f"https://example.com/probs/{self.code}",
            "title": self.title,
            "status": self.status,
            "detail": detail,
        }
```
---