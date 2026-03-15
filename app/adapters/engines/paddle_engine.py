# app/adapters/engines/paddle_engine.py
from __future__ import annotations

from typing import List
import numpy as np
from paddleocr import PaddleOCR

from app.adapters.interfaces.ocr_engine import TextOCREngine, OcrBox

class PaddleOCREngine(TextOCREngine):
    """Обёртка над PaddleOCR, реализует TextOCREngine."""
    def __init__(self, paddle: PaddleOCR):
        self.paddle = paddle

    @classmethod
    def from_config(cls, device: str = "cpu") -> "PaddleOCREngine":
        paddle = PaddleOCR(
            lang="ru",
            device=device,
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
        )
        return cls(paddle)

    def detect_text_boxes(self, img_bgr: np.ndarray) -> List[OcrBox]:
        outs = []

        paddle = self.paddle
        if hasattr(paddle, "predict"):
            results = paddle.predict(img_bgr)
            for res in results:
                j = getattr(res, "json", None)
                if not isinstance(j, dict):
                    continue
                payload = j.get("res", j)
                rec_texts = payload.get("rec_texts") or []
                rec_scores = payload.get("rec_scores") or []
                rec_polys = payload.get("rec_polys") or []
                if hasattr(rec_scores, "tolist"):
                    rec_scores = rec_scores.tolist()
                if hasattr(rec_polys, "tolist"):
                    rec_polys = rec_polys.tolist()
                n = min(len(rec_texts), len(rec_scores), len(rec_polys))
                for i in range(n):
                    txt = str(rec_texts[i] or "").strip()
                    if not txt:
                        continue
                    box = np.array(rec_polys[i], dtype=np.float32)
                    outs.append(OcrBox(type="text", text=txt, score=float(rec_scores[i] or 0.0), box=box))
            return outs

        res = paddle.ocr(img_bgr, cls=True)
        lines = (res[0] if (isinstance(res, list) and res and isinstance(res[0], list) and (len(res) == 1)) else res)
        if not lines:
            return outs

        for line in lines:
            if not line or len(line) < 2:
                continue
            box = np.array(line[0], dtype=np.float32)
            payload = line[1]
            txt = (payload[0] if isinstance(payload, (list, tuple)) and payload else "").strip()
            score = (float(payload[1]) if isinstance(payload, (list, tuple)) and len(payload) > 1 else 0.0)
            if txt:
                outs.append(OcrBox(type="text", text=txt, score=score, box=box))
        return outs