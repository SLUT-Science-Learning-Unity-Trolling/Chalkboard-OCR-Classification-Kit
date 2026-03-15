## Класс EasyOCREngine

**Обёртка над EasyOCR, реализует TextOCREngine.**

```python
class EasyOCREngine(TextOCREngine):
    """Обёртка над EasyOCR, реализует TextOCREngine."""
```

---
## def init:

```python
    def __init__(self, lang: list | str = ["ru"], gpu: bool = False):
        if isinstance(lang, str):
            lang = [lang]
        self.lang = lang
        self.reader = easyocr.Reader(self.lang, gpu=gpu)
```
---
## def from_config:
#### Создаёт экземпляр с дефолтными настройками.

```python
    @classmethod
    def from_config(cls, lang: list | str = ["ru"], gpu: bool = False) -> "EasyOCREngine":
        """Создаёт экземпляр с дефолтными настройками."""
        return cls(lang=lang, gpu=gpu)
```
---
## def detect_text_boxes:
#### Возвращает список OcrBox из изображения.

EasyOCR работает с BGR (OpenCV), автоматически конвертирует в RGB.

```python
    def detect_text_boxes(self, img_bgr: np.ndarray) -> List[OcrBox]:
        """
        Возвращает список OcrBox из изображения.
        EasyOCR работает с BGR (OpenCV), автоматически конвертирует в RGB.
        """
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        results = self.reader.readtext(img_rgb, detail=1)

        outs: List[OcrBox] = []
        for bbox, text, score in results:
            if not text.strip():
                continue
            box = np.array(bbox, dtype=np.float32)
            outs.append(OcrBox(type="text", text=text.strip(), score=float(score or 0.0), box=box))
        return outs
```
---