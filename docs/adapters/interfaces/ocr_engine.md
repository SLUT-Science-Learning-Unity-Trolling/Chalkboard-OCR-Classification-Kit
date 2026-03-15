## Класс OcrBox

**Результат распознавания одного блока текста/формулы.**

```python
@dataclass
class OcrBox:
    """Результат распознавания одного блока текста/формулы."""
    type: str 
    text: str
    score: float
    box: np.ndarray
```
## Класс TextOCREngine

**Интерфейс для движка, возвращающего текстовые боксы.**

```python
class TextOCREngine(Protocol):
    """Интерфейс для движка, возвращающего текстовые боксы."""
```

---
## def detect_text_boxes:
#### Возвращает список OcrBox с type='text'

```python
    def detect_text_boxes(self, img_bgr: np.ndarray) -> List[OcrBox]:
        """Возвращает список OcrBox с type='text'"""
        ...
```
---
## Класс FormulaOCREngine

**Интерфейс для движка, детектирующего и распознающего формулы (pix2text).**

```python
class FormulaOCREngine(Protocol):
    """Интерфейс для движка, детектирующего и распознающего формулы (pix2text)."""
```

---
## def detect_formulas:
#### Возвращает список OcrBox с type 'embedding' или 'isolated'

```python
    def detect_formulas(self, pil_img: PIL.Image.Image, resized_shape: int = 2048, batch_size: int = 1) -> List[OcrBox]:
        """Возвращает список OcrBox с type 'embedding' или 'isolated'"""
        ...
```
---