import io
import pytest

from litestar.datastructures import UploadFile

from app.core.services.validation_service import ValidationService
from app import config as app_config


def make_service(override_allowed_ext: set[str] | None = None) -> ValidationService:
    Cfg = app_config.Config
    attrs = {
        "PASSWORD_MIN_LENGTH": getattr(Cfg, "PASSWORD_MIN_LENGTH"),
        "PASSWORD_SPEC_SYMBOLS": getattr(Cfg, "PASSWORD_SPEC_SYMBOLS"),
        "USERNAME_MIN_LENGTH": getattr(Cfg, "USERNAME_MIN_LENGTH"),
        "USERNAME_MAX_LENGTH": getattr(Cfg, "USERNAME_MAX_LENGTH"),
        "ALLOWED_IMAGE_EXTENSIONS": override_allowed_ext
        if override_allowed_ext is not None
        else set(getattr(Cfg, "ALLOWED_IMAGE_EXTENSIONS")),
    }
    DummyCfg = type("DummyCfg", (), attrs)
    return ValidationService(DummyCfg)


def build_valid_password(cfg) -> str:
    spec = cfg.PASSWORD_SPEC_SYMBOLS[0] if cfg.PASSWORD_SPEC_SYMBOLS else "!"
    base = f"Aa1{spec}"
    need = max(cfg.PASSWORD_MIN_LENGTH - len(base), 0)
    return base + ("x" * need)


# ---------- validate_password ----------

@pytest.mark.asyncio
async def test_validate_password_ok():
    svc = make_service()
    pwd = build_valid_password(svc.config)
    assert await svc.validate_password(pwd) is True


@pytest.mark.asyncio
async def test_validate_password_too_short():
    svc = make_service()
    short_len = max(svc.config.PASSWORD_MIN_LENGTH - 1, 0)
    pwd = "A" * short_len
    with pytest.raises(Exception) as e:
        await svc.validate_password(pwd)
    assert "минимум" in str(e.value)


@pytest.mark.asyncio
async def test_validate_password_no_digit():
    svc = make_service()
    spec = svc.config.PASSWORD_SPEC_SYMBOLS[0] if svc.config.PASSWORD_SPEC_SYMBOLS else "!"
    pwd = "Aa" + spec + "x" * max(svc.config.PASSWORD_MIN_LENGTH - 3, 0)
    with pytest.raises(Exception) as e:
        await svc.validate_password(pwd)
    assert "цифр" in str(e.value)


@pytest.mark.asyncio
async def test_validate_password_no_uppercase():
    svc = make_service()
    spec = svc.config.PASSWORD_SPEC_SYMBOLS[0] if svc.config.PASSWORD_SPEC_SYMBOLS else "!"
    pwd = "aa1" + spec + "x" * max(svc.config.PASSWORD_MIN_LENGTH - 4, 0)
    with pytest.raises(Exception) as e:
        await svc.validate_password(pwd)
    assert "заглавн" in str(e.value)


@pytest.mark.asyncio
async def test_validate_password_no_lowercase():
    svc = make_service()
    spec = svc.config.PASSWORD_SPEC_SYMBOLS[0] if svc.config.PASSWORD_SPEC_SYMBOLS else "!"
    pwd = "AA1" + spec + "X" * max(svc.config.PASSWORD_MIN_LENGTH - 4, 0)
    with pytest.raises(Exception) as e:
        await svc.validate_password(pwd)
    assert "строчн" in str(e.value)


@pytest.mark.asyncio
async def test_validate_password_no_special():
    svc = make_service()

    pwd = build_valid_password(svc.config).replace(
        svc.config.PASSWORD_SPEC_SYMBOLS[0], ""
    )

    if len(pwd) < svc.config.PASSWORD_MIN_LENGTH:
        pwd += "x" * (svc.config.PASSWORD_MIN_LENGTH - len(pwd))
    with pytest.raises(Exception) as e:
        await svc.validate_password(pwd)
    assert "спец" in str(e.value)


# ---------- validate_username ----------

@pytest.mark.asyncio
async def test_validate_username_ok_min_and_regular():
    svc = make_service()
    ok_min = "a" * svc.config.USERNAME_MIN_LENGTH
    ok_regular = "User_123-xyz"
    assert await svc.validate_username(ok_min) is True
    assert await svc.validate_username(ok_regular) is True


@pytest.mark.asyncio
async def test_validate_username_too_short():
    svc = make_service()
    too_short = "a" * max(svc.config.USERNAME_MIN_LENGTH - 1, 0)
    with pytest.raises(Exception) as e:
        await svc.validate_username(too_short)
    assert "не короче" in str(e.value)


@pytest.mark.asyncio
async def test_validate_username_too_long():
    svc = make_service()
    too_long = "a" * (svc.config.USERNAME_MAX_LENGTH + 1)
    with pytest.raises(Exception) as e:
        await svc.validate_username(too_long)
    assert "не должно превышать" in str(e.value)


@pytest.mark.asyncio
@pytest.mark.parametrize("bad", ["имя", "bad space", "bad@", "slash/"])
async def test_validate_username_bad_charset(bad):
    svc = make_service()
    with pytest.raises(Exception) as e:
        await svc.validate_username(bad)
    assert "латинские буквы" in str(e.value)


@pytest.mark.asyncio
async def test_validate_image_extension_ok():
    svc = make_service(override_allowed_ext={"jpg", "jpeg", "png", "tif", "tiff"})
    f = UploadFile(filename="photo.JPEG", content_type="image/jpeg")
    assert await svc.validate_image_extension(f) is True


@pytest.mark.asyncio
async def test_validate_image_extension_bad():
    svc = make_service(override_allowed_ext={"jpg", "jpeg", "png"})
    f = UploadFile(filename="scan.bmp", content_type="image/bmp")
    assert await svc.validate_image_extension(f) is False
