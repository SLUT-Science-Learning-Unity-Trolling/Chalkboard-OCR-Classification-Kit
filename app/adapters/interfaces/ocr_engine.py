# app/adapters/interfaces/ocr_engine.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, List, Tuple
import PIL
import numpy as np

@dataclass
class OcrBox:
    """Результат распознавания одного блока текста/формулы."""
    type: str 
    text: str
    score: float
    box: np.ndarray 

class TextOCREngine(Protocol):
    """Интерфейс для движка, возвращающего текстовые боксы."""
    def detect_text_boxes(self, img_bgr: np.ndarray) -> List[OcrBox]:
        """Возвращает список OcrBox с type='text'"""
        ...

class FormulaOCREngine(Protocol):
    """Интерфейс для движка, детектирующего и распознающего формулы (pix2text)."""
    def detect_formulas(self, pil_img: PIL.Image.Image, resized_shape: int = 2048, batch_size: int = 1) -> List[OcrBox]:
        """Возвращает список OcrBox с type 'embedding' или 'isolated'"""
        ...