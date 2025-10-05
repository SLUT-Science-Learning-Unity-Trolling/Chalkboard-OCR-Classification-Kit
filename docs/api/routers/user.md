### create_user
**Эндпоинт создания пользователя.**

```python
)
async def create_user(
    data: UserCreateDTO,
    container: Container,
) -> UserDTO:
    """Эндпоинт создания пользователя."""
    user_service = container.resolve(UserService)
    try:
        user: User = await user_service.create_user(
            username=data.username,
            email=data.email,
            password=data.password,
            repeat_password=data.repeat_password,
        )
        return UserDTO.fromrow(user.__dict__)

    except (
        PasswordDontMatch,
        PasswordValidationError,
        EmailValidationError,
        UsernameValidationError,
        EmailAlreadyTaken,
        UsernameAlreadyTaken,
    ) as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))
```
---