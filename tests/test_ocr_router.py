import sys
import types
import importlib.util
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from punq import Container

pytestmark = pytest.mark.asyncio


def _install_fake_ocr_service_module() -> None:
    """
    Подкладываем фейковый модуль app.core.services.ocr_service,
    чтобы импорт app/api/routers/ocr.py НЕ тянул cv2.
    """
    fake = types.ModuleType("app.core.services.ocr_service")

    def images_bytes_to_pdf_bytes(images: list[bytes]) -> bytes:
        return b"%PDF-FAKE-DEFAULT%"

    fake.images_bytes_to_pdf_bytes = images_bytes_to_pdf_bytes
    sys.modules["app.core.services.ocr_service"] = fake


def _load_ocr_module():
    _install_fake_ocr_service_module()

    project_root = Path(__file__).resolve().parents[1]
    ocr_path = project_root / "app" / "api" / "routers" / "ocr.py"

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


class FakeUpload:
    """
    Нам нужен объект, у которого есть async read().
    Больше твой handler от UploadFile ничего не требует.
    """

    def __init__(self, content: bytes):
        self._content = content

    async def read(self) -> bytes:
        return self._content


async def test_ocr_to_pdf_returns_pdf_and_sets_headers(monkeypatch):
    captured: dict[str, list[bytes]] = {}

    def fake_images_bytes_to_pdf_bytes(images: list[bytes]) -> bytes:
        captured["images"] = images
        return b"%PDF-FAKE%\n..."

    monkeypatch.setattr(
        ocr_module,
        "images_bytes_to_pdf_bytes",
        fake_images_bytes_to_pdf_bytes,
        raising=True,
    )

    handler = _get_handler_fn()

    files = [
        FakeUpload(b"IMG1_BYTES"),
        FakeUpload(b"IMG2_BYTES"),
    ]

    resp = await handler(
        container=Container(),
        current_user=MagicMock(),
        data=files,
    )

    assert resp.media_type == "application/pdf"
    assert resp.headers.get("Content-Disposition") == 'attachment; filename="document.pdf"'
    assert resp.content.startswith(b"%PDF-FAKE%")
    assert captured["images"] == [b"IMG1_BYTES", b"IMG2_BYTES"]


async def test_ocr_to_pdf_works_with_single_file(monkeypatch):
    def fake_images_bytes_to_pdf_bytes(images: list[bytes]) -> bytes:
        assert images == [b"ONLY_ONE"]
        return b"%PDF-SINGLE%"

    monkeypatch.setattr(
        ocr_module,
        "images_bytes_to_pdf_bytes",
        fake_images_bytes_to_pdf_bytes,
        raising=True,
    )

    handler = _get_handler_fn()

    resp = await handler(
        container=Container(),
        current_user=MagicMock(),
        data=[FakeUpload(b"ONLY_ONE")],
    )

    assert resp.media_type == "application/pdf"
    assert resp.content == b"%PDF-SINGLE%"


async def test_ocr_to_pdf_empty_list_still_returns_pdf(monkeypatch):
    """
    По текущей реализации handler спокойно переживает пустой список:
    он отдаст PDF из images_bytes_to_pdf_bytes([]).
    """
    def fake_images_bytes_to_pdf_bytes(images: list[bytes]) -> bytes:
        assert images == []
        return b"%PDF-EMPTY%"

    monkeypatch.setattr(
        ocr_module,
        "images_bytes_to_pdf_bytes",
        fake_images_bytes_to_pdf_bytes,
        raising=True,
    )

    handler = _get_handler_fn()

    resp = await handler(
        container=Container(),
        current_user=MagicMock(),
        data=[],
    )

    assert resp.media_type == "application/pdf"
    assert resp.content == b"%PDF-EMPTY%"