## Класс DocTROCREngine

**Обёртка над docTR (python-doctr).**

Использует ocr_predictor для детекции + распознавания.

```python
class DocTROCREngine(TextOCREngine):
    """
    Обёртка над docTR (python-doctr).
    Использует ocr_predictor для детекции + распознавания.
    """
```

---
## def init:

```python
    def __init__(self, predictor: Any):
        if not _DOCTR_AVAILABLE or predictor is None:
            raise RuntimeError("python-doctr is not installed or failed to import.")
        self.predictor = predictor
```
---
## def from_config:
#### Создаёт predictor. Параметры:

- det_arch, reco_arch: архитектуры (например 'db_resnet50', 'crnn_vgg16_bn')
- pretrained: загружать веса
- export_as_straight_boxes: если True -> вы получите прямые bbox (полезно для markdown)
- device: 'cpu' или 'cuda'

```python
    @classmethod
    def from_config(
        cls,
        det_arch: Optional[str] = "fast_base",
        reco_arch: Optional[str] = "crnn_vgg16_bn",
        pretrained: bool = True,
        export_as_straight_boxes: bool = True,
        device: Optional[str] = None,
        **kwargs,
    ) -> "DocTROCREngine":
        """
        Создаёт predictor. Параметры:
          - det_arch, reco_arch: архитектуры (например 'db_resnet50', 'crnn_vgg16_bn')
          - pretrained: загружать веса
          - export_as_straight_boxes: если True -> вы получите прямые bbox (полезно для markdown)
          - device: 'cpu' или 'cuda'
        """
        if not _DOCTR_AVAILABLE:
            raise RuntimeError("python-doctr is not installed. Install with `pip install python-doctr`")

        params = {}
        if det_arch:
            params["det_arch"] = det_arch
        if reco_arch:
            params["reco_arch"] = reco_arch
        if device:
            params["device"] = device
        params.update(kwargs)

        predictor = ocr_predictor(pretrained=pretrained, export_as_straight_boxes=export_as_straight_boxes, **params)
        return cls(predictor)
```
---
## def detect_text_boxes:

```python
    def detect_text_boxes(self, img_bgr: np.ndarray) -> List[OcrBox]:
        import cv2
        from PIL import Image

        outs: List[OcrBox] = []
        if img_bgr is None:
            return outs

        try:
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb).convert("RGB")
        except Exception as e:
            logger.warning("DocTR engine: failed to convert image: %s", e)
            return outs

        try:
            pages = [np.array(img_pil)]
            result = self.predictor(pages)
        except Exception as e:
            logger.warning("DocTR predictor failed: %s", e)
            return outs

        try:
            for page in result.pages:
                page_dims = getattr(page, "dimensions", None)
                if not page_dims:
                    h, w = img_bgr.shape[:2]
                    page_dims = (h, w)
                for block in getattr(page, "blocks", []) or []:
                    for line in getattr(block, "lines", []) or []:
                        for word in getattr(line, "words", []) or []:
                            text = (getattr(word, "value", None) or getattr(word, "text", None) or "").strip()
                            if not text:
                                continue
                            geom = getattr(word, "geometry", None)
                            conf = getattr(word, "confidence", None) or getattr(word, "objectness_score", None) or 0.0
                            try:
                                box = _geom_to_quad(geom, page_dims)
                            except Exception:
                                try:
                                    line_geom = getattr(line, "geometry", None)
                                    box = _geom_to_quad(line_geom, page_dims)
                                except Exception:
                                    continue
                            score = _clamp_score(conf)
                            outs.append(OcrBox(type="text", text=text, score=score, box=box))
        except Exception as e:
            logger.warning("DocTR postprocessing error: %s", e)

        return outs
```
---
## def _clamp_score:
#### Преобразует уверенность в float в диапазоне [0,1].

```python
def _clamp_score(s: Any) -> float:
    """Преобразует уверенность в float в диапазоне [0,1]."""
    try:
        f = float(s)
    except Exception:
        return 0.0
    if f > 1.0 and f <= 100.0:
        f = f / 100.0
    if f < 0.0:
        return 0.0
    if f > 1.0:
        return 1.0
    return f
```
---
## def _geom_to_quad:
#### Приводит geometry из doctR к полигону (4,2) в абсолютных пикселях.

Поддерживает:
- tuple((xmin, ymin), (xmax, ymax)) -- относительные координаты [0..1]
- np.ndarray shape (4,2) с относительными координатами
- np.ndarray shape (2,2) тоже будет обработан
Возвращает np.ndarray dtype=np.float32 с порядком [tl, tr, br, bl].

```python
def _geom_to_quad(geom: Any, page_dims: Tuple[int, int]) -> np.ndarray:
    """
    Приводит geometry из doctR к полигону (4,2) в абсолютных пикселях.
    Поддерживает:
      - tuple((xmin, ymin), (xmax, ymax)) -- относительные координаты [0..1]
      - np.ndarray shape (4,2) с относительными координатами
      - np.ndarray shape (2,2) тоже будет обработан
    Возвращает np.ndarray dtype=np.float32 с порядком [tl, tr, br, bl].
    """
    height, width = page_dims  # page.dimensions в doctr: (height, width)
    # helper to scale normalized coords to pixels
    def scale(x: float, y: float) -> Tuple[float, float]:
        return (float(x) * width, float(y) * height)

    # ndarray inputs
    try:
        a = np.asarray(geom)
    except Exception:
        raise ValueError("Invalid geometry")

    if a.ndim == 2 and a.shape == (4, 2):
        # geometry is polygon (relative) -> scale each point: points are (x, y)
        pts = np.array([[p[0] * width, p[1] * height] for p in a], dtype=np.float32)
        # ensure order tl,tr,br,bl via simple ordering function
        return _order_quad(pts)
    if a.ndim == 2 and a.shape == (2, 2):
        # (xmin,ymin),(xmax,ymax)
        (xmin, ymin), (xmax, ymax) = a.tolist()
        tl = scale(xmin, ymin)
        tr = scale(xmax, ymin)
        br = scale(xmax, ymax)
        bl = scale(xmin, ymax)
        return np.array([tl, tr, br, bl], dtype=np.float32)
    # If it's a tuple of tuples like ((xmin,ymin),(xmax,ymax))
    if isinstance(geom, tuple) and len(geom) == 2:
        try:
            (xmin, ymin), (xmax, ymax) = geom
            tl = scale(xmin, ymin)
            tr = scale(xmax, ymin)
            br = scale(xmax, ymax)
            bl = scale(xmin, ymax)
            return np.array([tl, tr, br, bl], dtype=np.float32)
        except Exception:
            pass

    # fallback: try to reshape into Nx2 and resolve bounding box
    try:
        b = a.reshape(-1, 2)
        xs = b[:, 0]
        ys = b[:, 1]
        xmin, ymin = float(xs.min()), float(ys.min())
        xmax, ymax = float(xs.max()), float(ys.max())
        tl = scale(xmin, ymin)
        tr = scale(xmax, ymin)
        br = scale(xmax, ymax)
        bl = scale(xmin, ymax)
        return np.array([tl, tr, br, bl], dtype=np.float32)
    except Exception as e:
        raise ValueError(f"Can't convert geometry to quad: {e}") from e
```
---
## def _order_quad:
#### Упорядочивает 4 точки в порядок tl, tr, br, bl.

Принимает np.ndarray (4,2).

```python
def _order_quad(pts: np.ndarray) -> np.ndarray:
    """
    Упорядочивает 4 точки в порядок tl, tr, br, bl.
    Принимает np.ndarray (4,2).
    """
    if pts.shape != (4, 2):
        # попытаемся привести
        pts = pts.reshape(-1, 2)
        if pts.shape[0] < 4:
            raise ValueError("Not enough points to form quad")
        pts = pts[:4, :]
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect.astype(np.float32)
```
---