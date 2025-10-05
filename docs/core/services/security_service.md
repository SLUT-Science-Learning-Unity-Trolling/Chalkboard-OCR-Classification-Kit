## Класс SecurityService

**Секьюрити сервис для работы с сессиями и т.п.**

---
### hash_password
**Функция хэширования пароля.**

**Args:**
- `password`: Пароль

**Returns:**
- `tuple[str, str]: salt, hash`

```python
    def hash_password(self, password: str) -> tuple[str, str]:
        """Функция хэширования пароля.
            Args:
                password: Пароль
                
            Returns:
                tuple[str, str]: salt, hash
        """
        return utils.hash_password(password, salt_size=36)
```
---
### serialize_hash
**Функция сериализации хэша пароля.**

**Args:**
- `salt`: Соль
- `hash_`: Хэш

**Returns:**
- `str: сериализованный хэш`

```python
    def serialize_hash(self, salt: str, hash_: str) -> str:
        """Функция сериализации хэша пароля.
            Args:
                salt: Соль
                hash_: Хэш

            Returns:
                str: сериализованный хэш
        """
        return utils.serialize_hash(salt, hash_)
```
---
### deserialize_hash
**Функция десериализации хэша пароля.**

**Args:**
- `data`: Сериализованный хэш

**Returns:**
- `tuple[str, str]: salt, hash`

```python
    def deserialize_hash(self, data: str) -> tuple[str, str]:
        """Функция десериализации хэша пароля.
            Args:
                data: Сериализованный хэш

            Returns:
                tuple[str, str]: salt, hash
        """
        return utils.deserialize_hash(data)
```
---
### verify_hash
**Функция проверки хэша пароля.**

**Args:**
- `password`: Пароль
- `salt`: Соль
- `hash_`: Хэш

**Returns:**
- `bool: True, если пароль верен`

```python
    def verify_hash(self, password: str, salt: str, hash_: str) -> bool:
        """Функция проверки хэша пароля.
            Args:
                password: Пароль
                salt: Соль
                hash_: Хэш

            Returns:
                bool: True, если пароль верен
        """
        return utils.check_password(password, hash_, salt)
```
---