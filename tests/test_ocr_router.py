import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from punq import Container
from app.core.services.validation_service import ImageValidator

pytestmark = pytest.mark.asyncio


# Фейковый OCRService

def _install_fake_ocr_service_module() -> None:
    """
    Подкладываем фейковый модуль app.core.services.ocr_service,
    чтобы импорт app/api/routers/ocr.py НЕ тянул cv2 и реальные зависимости.
    """
    fake = types.ModuleType("app.core.services.ocr_service")

    class FakeOCRService:
        def __init__(self, *args, **kwargs):
            pass

        def images_bytes_to_pdf_bytes(self, images: list[bytes]) -> bytes:
            return b"%PDF-FAKE-DEFAULT%"

    fake.OCRService = FakeOCRService
    sys.modules["app.core.services.ocr_service"] = fake


# Загружаем router модуль

def _load_ocr_module():
    _install_fake_ocr_service_module()

    project_root = Path(__file__).resolve().parents[1]
    ocr_path = project_root / "app" / "api" / "routers" / "ocr.py"

    import importlib.util
    module_name = "test_loaded_ocr_router_module"
    spec = importlib.util.spec_from_file_location(module_name, ocr_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module spec from {ocr_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


ocr_module = _load_ocr_module()


def _get_handler_fn():
    """
    В Litestar декоратор @post возвращает HTTPRouteHandler,
    у него обычно есть .fn (оригинальная функция).
    """
    return getattr(ocr_module.ocr_to_pdf, "fn", ocr_module.ocr_to_pdf)


# Фейковый UploadFile

class FakeUpload:
    """
    Объект, у которого есть async read().
    """

    def __init__(self, content: bytes):
        self._content = content

    async def read(self) -> bytes:
        return self._content


# Тесты

async def test_ocr_to_pdf_returns_pdf_and_sets_headers():
    fake_service = ocr_module.OCRService()
    fake_service.images_bytes_to_pdf_bytes = lambda images: b"%PDF-FAKE%\n..."

    container = Container()
    container.register(ocr_module.OCRService, instance=fake_service)
    container.register(ImageValidator, instance=MagicMock())

    handler = _get_handler_fn()
    files = [FakeUpload(b"IMG1_BYTES"), FakeUpload(b"IMG2_BYTES")]

    resp = await handler(
        container=container,
        current_user=MagicMock(),
        data=files,
    )

    assert resp.media_type == "application/pdf"
    assert resp.headers.get("Content-Disposition") == 'attachment; filename="document.pdf"'
    assert resp.content.startswith(b"%PDF-FAKE%")


async def test_ocr_to_pdf_works_with_single_file():
    fake_service = ocr_module.OCRService()
    fake_service.images_bytes_to_pdf_bytes = lambda images: b"%PDF-SINGLE%" if images == [b"ONLY_ONE"] else b"%PDF-OTHER%"

    container = Container()
    container.register(ocr_module.OCRService, instance=fake_service)
    container.register(ImageValidator, instance=MagicMock())

    handler = _get_handler_fn()

    resp = await handler(
        container=container,
        current_user=MagicMock(),
        data=[FakeUpload(b"ONLY_ONE")],
    )

    assert resp.media_type == "application/pdf"
    assert resp.content == b"%PDF-SINGLE%"


async def test_ocr_to_pdf_empty_list_raises_value_error():
    fake_service = ocr_module.OCRService()
    fake_service.images_bytes_to_pdf_bytes = lambda images: b"%PDF-EMPTY%"

    container = Container()
    container.register(ocr_module.OCRService, instance=fake_service)
    container.register(ImageValidator, instance=MagicMock())

    handler = _get_handler_fn()

    with pytest.raises(ValueError, match="No images provided"):
        await handler(container=container, current_user=MagicMock(), data=[])