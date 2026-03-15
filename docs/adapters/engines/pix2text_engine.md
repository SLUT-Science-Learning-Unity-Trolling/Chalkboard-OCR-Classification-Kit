## Класс Pix2TextEngine

**Обёртка над Pix2Text, реализует FormulaOCREngine.**

```python
class Pix2TextEngine(FormulaOCREngine):
    """Обёртка над Pix2Text, реализует FormulaOCREngine."""
```

---
## def init:

```python
    def __init__(self, p2t: Pix2Text):
        self.p2t = p2t
        tfo = getattr(self.p2t, "text_formula_ocr", None)
        if tfo is None or getattr(tfo, "mfd", None) is None or getattr(tfo, "latex_ocr", None) is None:
            raise RuntimeError("Pix2Text: text_formula_ocr/mfd/latex_ocr not available")
```
---
## def from_config:

```python
    @classmethod
    def from_config(cls, device: str = "cpu") -> "Pix2TextEngine":
        total_configs = {"text_formula": {"languages": ("ru", "en")}}
        p2t = Pix2Text.from_config(
            total_configs=total_configs,
            enable_formula=True,
            enable_table=False,
            device=device,
        )
        return cls(p2t)
```
---
## def detect_formulas:

```python
    def detect_formulas(self, pil_img: Image.Image, resized_shape: int = 2048, batch_size: int = 1) -> List[OcrBox]:
        tfo = self.p2t.text_formula_ocr
        analyzer_outs = tfo.mfd(pil_img.copy(), resized_shape=resized_shape)

        patches = []
        meta = []
        w, h = pil_img.size
        for mf in analyzer_outs:
            box = np.array(mf["box"], dtype=np.float32)
            x_min, y_min = int(max(0, box[:,0].min())), int(max(0, box[:,1].min()))
            x_max, y_max = int(min(w, box[:,0].max())), int(min(h, box[:,1].max()))
            if x_max - x_min < 2 or y_max - y_min < 2:
                continue
            patches.append(pil_img.crop((x_min, y_min, x_max, y_max)))
            meta.append({"type": mf.get("type", "isolated"), "box": box})

        if not patches:
            return []

        recs = tfo.latex_ocr.recognize(patches, batch_size=batch_size)

        outs = []
        for m, r in zip(meta, recs, strict=False):
            txt = (r.get("text") or "").strip()
            if not txt:
                continue
            outs.append(
                OcrBox(
                    type=("embedding" if m["type"] == "embedding" else "isolated"),
                    text=txt,
                    score=float(r.get("score", 0.0) or 0.0),
                    box=m["box"],
                )
            )
        return outs
```
---