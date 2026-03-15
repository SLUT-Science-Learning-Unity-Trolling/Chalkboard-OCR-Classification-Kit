# app/adapters/engines/rapidocr_engine.py
from __future__ import annotations

from typing import List, Optional
import numpy as np

from app.adapters.interfaces.ocr_engine import TextOCREngine, OcrBox
from rapidocr_onnxruntime import RapidOCR

class RapidOCREngine(TextOCREngine):
    """
    Обёртка над RapidOCR (rapidocr_onnxruntime).
    Ожидает входное изображение в формате BGR (как результат cv2.imread),
    т.к. RapidOCR обычно работает с OpenCV-представлением.

    Пример создания:
        eng = RapidOCREngine.from_config(det_model_path=None, rec_model_path=None)
    """
    def __init__(self, rapid_ocr: RapidOCR):
        if RapidOCR is None:
            raise RuntimeError("rapidocr_onnxruntime is not installed or failed to import.")
        self.rapid_ocr = rapid_ocr

    @classmethod
    def from_config(
        cls,
        det_model_path: Optional[str] = None,
        rec_model_path: Optional[str] = None,
        rec_img_shape: Optional[list] = None,
        **kwargs,
    ) -> "RapidOCREngine":
        """
        Создаёт экземпляр RapidOCREngine.
        Параметры det_model_path/rec_model_path/rec_img_shape можно передать,
        если вы используете кастомные onnx-модели. В простом случае rapidocr можно
        создать без аргументов: RapidOCR().
        Любые дополнительные kwargs будут переданы в конструктор RapidOCR.
        """
        if RapidOCR is None:
            raise RuntimeError("rapidocr_onnxruntime is not installed. "
                               "Install it with `pip install rapidocr-onnxruntime`.")
        params = {}
        if det_model_path is not None:
            params["det_model_path"] = det_model_path
        if rec_model_path is not None:
            params["rec_model_path"] = rec_model_path
        if rec_img_shape is not None:
            params["rec_img_shape"] = rec_img_shape
        params.update(kwargs)
        rapid = RapidOCR(**params) if params else RapidOCR()
        return cls(rapid)

    def detect_text_boxes(self, img_bgr: np.ndarray) -> List[OcrBox]:
        """
        Запускает RapidOCR и возвращает список OcrBox:
        - type="text"
        - text: распознанная строка
        - score: confidence (0.0..1.0)
        - box: np.ndarray dtype=float32 (обычно полигон 4x2 или похожая структура)
        """
        outs: List[OcrBox] = []
        if img_bgr is None:
            return outs
        try:
            res = self.rapid_ocr(img_bgr)
            try:
                res = self.rapid_ocr(img_bgr, )
            except Exception:
                return outs
        except Exception:
            return outs

        if isinstance(res, tuple) and len(res) >= 1:
            ocr_result = res[0]
        else:
            ocr_result = res
        if not ocr_result:
            return outs
        for item in ocr_result:
            if not item:
                continue
            try:
                dt_box, rec_res, score = item[:3]
            except Exception:
                continue
            txt = (rec_res or "").strip()
            if not txt:
                continue
            try:
                box = np.array(dt_box, dtype=np.float32)
            except Exception:
                continue
            try:
                score_f = float(score) if score is not None else 0.0
            except Exception:
                score_f = 0.0
            outs.append(OcrBox(type="text", text=txt, score=score_f, box=box))

        return outs
