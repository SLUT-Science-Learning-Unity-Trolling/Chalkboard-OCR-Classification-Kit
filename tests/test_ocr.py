from __future__ import annotations

import io
import importlib
import sys
import types
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import numpy as np
import pytest
from PIL import Image



def _install_fake_cv2() -> None:
    if "cv2" in sys.modules:
        return

    cv2 = types.ModuleType("cv2")

    # constants used in module
    cv2.COLOR_RGB2BGR = 0
    cv2.COLOR_BGR2RGB = 1
    cv2.COLOR_BGR2GRAY = 2
    cv2.COLOR_GRAY2BGR = 3
    cv2.COLOR_BGR2LAB = 4
    cv2.COLOR_LAB2BGR = 5

    cv2.INTER_AREA = 0
    cv2.INTER_CUBIC = 1

    cv2.NORM_MINMAX = 0

    cv2.ADAPTIVE_THRESH_GAUSSIAN_C = 0
    cv2.THRESH_BINARY = 0

    cv2.RETR_LIST = 0
    cv2.CHAIN_APPROX_SIMPLE = 0

    def _noop(*args, **kwargs):
        return args[0] if args else None

    cv2.cvtColor = _noop
    cv2.resize = _noop
    cv2.GaussianBlur = _noop
    cv2.Canny = _noop
    cv2.dilate = _noop
    cv2.erode = _noop
    cv2.findContours = lambda *a, **k: ([], None)

    cv2.bilateralFilter = _noop
    cv2.split = lambda x: (x, x, x)
    cv2.merge = lambda xs: xs[0] if xs else None
    cv2.createCLAHE = lambda *a, **k: types.SimpleNamespace(apply=lambda x: x)
    cv2.normalize = _noop
    cv2.fillPoly = _noop

    def _not_available(*args, **kwargs):
        raise RuntimeError("cv2 is mocked in unit tests (opencv not installed)")

    cv2.arcLength = _not_available
    cv2.approxPolyDP = _not_available
    cv2.getPerspectiveTransform = _not_available
    cv2.warpPerspective = _not_available
    cv2.adaptiveThreshold = _not_available

    sys.modules["cv2"] = cv2


def _install_fake_paddleocr_and_pix2text() -> None:
    if "paddleocr" not in sys.modules:
        paddleocr = types.ModuleType("paddleocr")

        class PaddleOCR:  # noqa: N801
            def __init__(self, *args: Any, **kwargs: Any) -> None:
                pass

            def ocr(self, *args: Any, **kwargs: Any) -> list:
                return []

            def predict(self, *args: Any, **kwargs: Any) -> list:
                return []

        paddleocr.PaddleOCR = PaddleOCR
        sys.modules["paddleocr"] = paddleocr

    if "pix2text" not in sys.modules:
        pix2text = types.ModuleType("pix2text")

        class Pix2Text:  # noqa: N801
            @classmethod
            def from_config(cls, *args: Any, **kwargs: Any) -> "Pix2Text":
                return cls()

            def __init__(self) -> None:
                self.text_formula_ocr = None

        pix2text.Pix2Text = Pix2Text
        sys.modules["pix2text"] = pix2text


_install_fake_cv2()
_install_fake_paddleocr_and_pix2text()


# Import module under test
ocr = importlib.import_module("app.core.services.ocr_service")


# Fixtures

@pytest.fixture
def simple_image_bytes() -> bytes:
    img = Image.new("RGB", (80, 60), (255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture
def ocr_service():
    formula_engine = Mock()
    text_engine = Mock()
    return ocr.OCRService(formula_engine, text_engine)


# Pure text utils

def test_restore_paragraphs_adds_blank_line_after_sentence():
    text = "Это предложение.\nСледующая строка"
    out = ocr.restore_paragraphs(text)
    assert out == "Это предложение.\n\nСледующая строка"


def test_restore_paragraphs_adds_blank_line_before_keywords():
    text = "Текст\nОпределение 1. ..."
    out = ocr.restore_paragraphs(text)
    assert out == "Текст\n\nОпределение 1. ..."


def test_unwrap_plain_text_math_unwraps_simple_math_text():
    md = "$$\\mathrm{Hello~world}$$\nОстальное"
    out = ocr.unwrap_plain_text_math(md)
    assert out == "Hello world\nОстальное"


def test_replace_lat_to_cyr_outside_math_only():
    s = "a c\n$$a+c$$\n\\(a+c\\)\nend"
    out = ocr.replace_lat_to_cyr_outside_math(s)

    assert out.splitlines()[0] == "а с"
    assert out.splitlines()[1] == "$$a+c$$"
    assert out.splitlines()[2] == "\\(a+c\\)"
    assert out.splitlines()[3] == "еnd"


# OCRService private helpers

def test_ensure_nonempty_markdown(ocr_service):
    assert ocr_service._ensure_nonempty_markdown("") == "(OCR вернул пустой результат)"
    assert ocr_service._ensure_nonempty_markdown("   ") == "(OCR вернул пустой результат)"
    assert ocr_service._ensure_nonempty_markdown("x") == "x"


# markdown_to_pdf_bytes: mock pandoc (subprocess.run)

def test_markdown_to_pdf_bytes_success(monkeypatch, ocr_service):
    def fake_run(cmd, capture_output=True, text=True):
        out_idx = cmd.index("-o") + 1
        out_pdf = cmd[out_idx]
        Path(out_pdf).write_bytes(b"%PDF-FAKE%")
        return types.SimpleNamespace(returncode=0, stderr="", stdout="")

    monkeypatch.setattr(ocr.subprocess, "run", fake_run)

    pdf = ocr_service.markdown_to_pdf_bytes("hello", debug=False)
    assert pdf.startswith(b"%PDF-FAKE%")


def test_markdown_to_pdf_bytes_failure_raises(monkeypatch, ocr_service):
    calls = {"n": 0}

    def fake_run(cmd, capture_output=True, text=True):
        calls["n"] += 1
        if calls["n"] == 1:
            return types.SimpleNamespace(returncode=1, stderr="pandoc error", stdout="")
        return types.SimpleNamespace(returncode=0, stderr="", stdout="")

    monkeypatch.setattr(ocr.subprocess, "run", fake_run)

    with pytest.raises(RuntimeError) as exc:
        ocr_service.markdown_to_pdf_bytes("hello", debug=False)

    assert "pandoc failed" in str(exc.value)


# summarize_markdown_openrouter_requests: mock requests.post

def test_summarize_markdown_openrouter_requests_success(monkeypatch):
    monkeypatch.setattr(ocr.config, "API_KEY", "test-key", raising=False)

    fake_resp = Mock()
    fake_resp.raise_for_status = Mock()
    fake_resp.json = Mock(
        return_value={"choices": [{"message": {"content": "SUM", "reasoning_details": [{"x": 1}]}}]}
    )
    monkeypatch.setattr(ocr.requests, "post", lambda *a, **k: fake_resp)

    out = ocr.summarize_markdown_openrouter_requests("hello")
    assert out == "SUM"


def test_summarize_markdown_openrouter_requests_no_key_raises(monkeypatch):
    monkeypatch.setattr(ocr.config, "API_KEY", "", raising=False)
    with pytest.raises(RuntimeError) as exc:
        ocr.summarize_markdown_openrouter_requests("hello")
    assert "OpenRouter API key" in str(exc.value)


def test_summarize_markdown_openrouter_requests_retries_then_fails(monkeypatch):
    monkeypatch.setattr(ocr.config, "API_KEY", "test-key", raising=False)

    def fake_post(*args, **kwargs):
        raise ocr.requests.RequestException("net down")

    monkeypatch.setattr(ocr.requests, "post", fake_post)

    with pytest.raises(RuntimeError) as exc:
        ocr.summarize_markdown_openrouter_requests("hello", max_retries=2)

    assert "Не удалось получить ответ" in str(exc.value)


# image_bytes_to_markdown: mock heavy OCR path

def test_image_bytes_to_markdown_happy_path(monkeypatch, ocr_service, simple_image_bytes):
    monkeypatch.setattr(ocr_service, "_prepare_image", lambda image_bytes, **kw: Image.open(io.BytesIO(image_bytes)).convert("RGB"))
    monkeypatch.setattr(ocr_service, "_detect_formula_boxes", lambda *args, **kwargs: [
        ocr.OcrBox(
            type="embedding",
            text="x^2",
            score=0.9,
            box=np.array([[0, 0], [10, 0], [10, 10], [0, 10]], dtype=np.float32),
        )
    ])
    monkeypatch.setattr(ocr_service, "_detect_text_boxes", lambda *args, **kwargs: [
        ocr.OcrBox(
            type="text",
            text="a c",
            score=0.9,
            box=np.array([[0, 20], [20, 20], [20, 30], [0, 30]], dtype=np.float32),
        )
    ])
    monkeypatch.setattr(
    ocr_service,
    "_assemble_markdown",
    lambda text_boxes, formula_boxes, math_delims="dollars": "а с $x^2$"
)
    monkeypatch.setattr(ocr, "replace_lat_to_cyr_outside_math", lambda s: s.replace("a", "а").replace("c", "с"))
    monkeypatch.setattr(ocr, "unwrap_plain_text_math", lambda s: s)

    md = ocr_service.image_bytes_to_markdown(
        image_bytes=simple_image_bytes,
        contain_formula=True,
        math_delims="dollars",
        skip_warp=True,
    )

    assert "$x^2$" in md
    assert "а" in md and "с" in md


def test_image_bytes_to_markdown_empty_result(monkeypatch, ocr_service, simple_image_bytes):
    monkeypatch.setattr(ocr_service, "_prepare_image", lambda image_bytes, **kw: Image.open(io.BytesIO(image_bytes)).convert("RGB"))
    monkeypatch.setattr(ocr_service, "_detect_formula_boxes", lambda *args, **kwargs: [])
    monkeypatch.setattr(ocr_service, "_detect_text_boxes", lambda *args, **kwargs: [])
    monkeypatch.setattr(ocr_service, "_assemble_markdown", lambda text_boxes, formula_boxes, math_delims="dollars": "(OCR вернул пустой результат)")

    md = ocr_service.image_bytes_to_markdown(
        image_bytes=simple_image_bytes,
        contain_formula=False,
        skip_warp=True,
    )
    assert md == "(OCR вернул пустой результат)"


# images_bytes_to_pdf_bytes / image_bytes_to_pdf_bytes: mock pipeline

def test_images_bytes_to_markdown_combines_images(monkeypatch, ocr_service, simple_image_bytes):
    monkeypatch.setattr(ocr_service, "image_bytes_to_markdown", lambda image_bytes, **kw: "MD")

    out = ocr_service.images_bytes_to_markdown([simple_image_bytes, simple_image_bytes])
    assert "Фото 1" in out
    assert "Фото 2" in out
    assert out.count("MD") == 2


def test_images_bytes_to_pdf_bytes_with_summary(monkeypatch, ocr_service, simple_image_bytes):
    monkeypatch.setattr(ocr_service, "images_bytes_to_markdown", lambda images, **kw: "MD")
    monkeypatch.setattr(ocr, "summarize_markdown_openrouter_requests", lambda md: "SUMMD")
    monkeypatch.setattr(ocr_service, "markdown_to_pdf_bytes", lambda md, **kw: b"%PDF%")

    pdf = ocr_service.images_bytes_to_pdf_bytes([simple_image_bytes], summarize=True)
    assert pdf.startswith(b"%PDF%")


def test_image_bytes_to_pdf_bytes_without_summary(monkeypatch, ocr_service, simple_image_bytes):
    monkeypatch.setattr(ocr_service, "image_bytes_to_markdown", lambda *a, **kw: "MD")
    monkeypatch.setattr(ocr, "restore_paragraphs", lambda s: s)
    monkeypatch.setattr(ocr_service, "markdown_to_pdf_bytes", lambda md, **kw: b"%PDF%")

    pdf = ocr_service.image_bytes_to_pdf_bytes(simple_image_bytes, summarize=False)
    assert pdf.startswith(b"%PDF%")


def test_image_bytes_to_pdf_bytes_with_summary(monkeypatch, ocr_service, simple_image_bytes):
    monkeypatch.setattr(ocr_service, "image_bytes_to_markdown", lambda *a, **kw: "MD")
    monkeypatch.setattr(ocr, "restore_paragraphs", lambda s: s)
    monkeypatch.setattr(ocr, "summarize_markdown_openrouter_requests", lambda md: "SUMMD")
    monkeypatch.setattr(ocr_service, "markdown_to_pdf_bytes", lambda md, **kw: b"%PDF%")

    pdf = ocr_service.image_bytes_to_pdf_bytes(simple_image_bytes, summarize=True)
    assert pdf.startswith(b"%PDF%")