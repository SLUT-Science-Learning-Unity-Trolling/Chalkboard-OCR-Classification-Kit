## Класс TesseractOCREngine

**Простой обёрток над pytesseract (TextOCREngine).**

```python
class TesseractOCREngine(TextOCREngine):
    """Простой обёрток над pytesseract (TextOCREngine)."""
```

---
## def init:

```python
    def __init__(self, lang: str = "rus", config: str = ""):
        self.lang = lang
        if not config:
            config = "--oem 3 --psm 6"
        self.config = config
```
---
## def from_config:
#### Создаёт экземпляр TesseractOCREngine с конфигурацией по умолчанию.

```python
    @classmethod
    def from_config(cls, lang: str = "rus", config: str = "") -> "TesseractOCREngine":
        """Создаёт экземпляр TesseractOCREngine с конфигурацией по умолчанию."""
        return cls(lang=lang, config=config)
```
---
## def detect_text_boxes:

```python
    def detect_text_boxes(self, img_bgr: np.ndarray) -> List[OcrBox]:
        import cv2
        pil = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
        data = pytesseract.image_to_data(
            pil, lang=self.lang, config=self.config, output_type=pytesseract.Output.DICT
        )
        outs = []
        n_boxes = len(data.get("level", []))
        for i in range(n_boxes):
            txt = (data.get("text", [""])[i] or "").strip()
            if not txt:
                continue
            x = int(data.get("left", [0])[i])
            y = int(data.get("top", [0])[i])
            w = int(data.get("width", [0])[i])
            h = int(data.get("height", [0])[i])
            box = np.array([[x, y], [x + w, y], [x + w, y + h], [x, y + h]], dtype=np.float32)
            conf = float(data.get("conf", [-1])[i] or -1.0)
            score = max(0.0, conf) / 100.0 if conf >= 0 else 0.0
            outs.append(OcrBox(type="text", text=txt, score=score, box=box))
        return outs
```
---