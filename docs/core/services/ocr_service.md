## Класс OcrBox

## def build_p2t_formula:

```python
def build_p2t_formula(device: str = "cpu") -> Pix2Text:
    total_configs = {"text_formula": {"languages": ("ru", "en")}}
    return Pix2Text.from_config(
        total_configs=total_configs,
        enable_formula=True,
        enable_table=False,
        device=device,
    )
```
---
## def build_paddle_ru:

```python
def build_paddle_ru(device: str = "cpu") -> PaddleOCR:
    return PaddleOCR(
        lang="ru",
        device=device,
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
    )
```
---
## def _pil_to_bgr:

```python
def _pil_to_bgr(img: Image.Image) -> np.ndarray:
    rgb = np.array(img.convert("RGB"))
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
```
---
## def _bgr_to_pil:

```python
def _bgr_to_pil(bgr: np.ndarray) -> Image.Image:
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)
```
---
## def _order_points:

```python
def _order_points(pts: np.ndarray) -> np.ndarray:
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect
```
---
## def _four_point_transform:

```python
def _four_point_transform(image_bgr: np.ndarray, pts: np.ndarray) -> np.ndarray:
    rect = _order_points(pts.astype("float32"))
    (tl, tr, br, bl) = rect

    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxW = int(max(widthA, widthB))

    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxH = int(max(heightA, heightB))

    maxW = max(maxW, 2)
    maxH = max(maxH, 2)

    dst = np.array(
        [[0, 0], [maxW - 1, 0], [maxW - 1, maxH - 1], [0, maxH - 1]], dtype="float32"
    )
    M = cv2.getPerspectiveTransform(rect, dst)
    return cv2.warpPerspective(image_bgr, M, (maxW, maxH))
```
---
## def _find_largest_quad:

```python
def _find_largest_quad(
    image_bgr: np.ndarray, detect_width: int = 1200
) -> Optional[np.ndarray]:
    h, w = image_bgr.shape[:2]
    if w > detect_width:
        r = detect_width / float(w)
        small = cv2.resize(
            image_bgr, (detect_width, int(h * r)), interpolation=cv2.INTER_AREA
        )
        ratio = 1.0 / r
    else:
        small = image_bgr.copy()
        ratio = 1.0

    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    edges = cv2.Canny(gray, 50, 150)
    edges = cv2.dilate(edges, None, iterations=2)
    edges = cv2.erode(edges, None, iterations=1)

    cnts, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        logger.info("No contours found in edge detection")
        return None

    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:10]
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            quad = approx.reshape(4, 2).astype("float32") * ratio
            logger.info(f"Found quad: {quad}")
            return quad

    logger.info("No 4-point quad found")
    return None
```
---
## def _enhance_for_ocr:

```python
def _enhance_for_ocr(warped_bgr: np.ndarray, upscale: int = 2) -> Image.Image:
    h_before, w_before = warped_bgr.shape[:2]
    logger.info(f"_enhance_for_ocr input: {w_before}x{h_before}")

    den = cv2.bilateralFilter(warped_bgr, d=9, sigmaColor=75, sigmaSpace=75)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    den = cv2.morphologyEx(den, cv2.MORPH_CLOSE, kernel, iterations=1)

    lab = cv2.cvtColor(den, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.5, tileGridSize=(10, 10))
    l2 = clahe.apply(l)
    out = cv2.cvtColor(cv2.merge([l2, a, b]), cv2.COLOR_LAB2BGR)

    if upscale and upscale > 1:
        out = cv2.resize(
            out,
            (out.shape[1] * upscale, out.shape[0] * upscale),
            interpolation=cv2.INTER_CUBIC,
        )
        logger.info(f"After upscale {upscale}x: {out.shape[1]}x{out.shape[0]}")

    pil = _bgr_to_pil(out)
    pil = ImageEnhance.Contrast(pil).enhance(1.5)
    pil = pil.filter(ImageFilter.UnsharpMask(radius=3, percent=200, threshold=2))
    pil = ImageEnhance.Brightness(pil).enhance(1.05)

    logger.info(f"Final PIL size: {pil.size}")
    return pil
```
---
## def preprocess_screen_photo:

```python
def preprocess_screen_photo(
    img_pil: Image.Image,
    detect_width: int = 1200,
    upscale: int = 2,
    fallback_crop: bool = True,
    skip_warp: bool = False,
) -> Image.Image:
    logger.info(f"preprocess_screen_photo input: {img_pil.size}")

    img_pil = ImageOps.exif_transpose(img_pil).convert("RGB")
    logger.info(f"After exif_transpose: {img_pil.size}")

    bgr = _pil_to_bgr(img_pil)

    w, h = img_pil.size
    aspect = w / h if h > 0 else 1.0
    if skip_warp or (0.8 < aspect < 1.25):
        logger.info(f"Skipping warp: aspect ratio {aspect:.2f}")
        if fallback_crop:
            m = int(min(w, h) * 0.05)
            img_pil = img_pil.crop((m, m, w - m, h - m))
            logger.info(f"After fallback_crop: {img_pil.size}")
        return _enhance_for_ocr(_pil_to_bgr(img_pil), upscale=upscale)

    quad = _find_largest_quad(bgr, detect_width=detect_width)
    if quad is not None:
        logger.info("Applying perspective transform")
        warped = _four_point_transform(bgr, quad)
        logger.info(f"After warp: {warped.shape[1]}x{warped.shape[0]}")
        return _enhance_for_ocr(warped, upscale=upscale)

    logger.info("Fallback: no quad found, using simple crop")
    if fallback_crop:
        m = int(min(w, h) * 0.05)
        img_pil = img_pil.crop((m, m, w - m, h - m))
        logger.info(f"After fallback_crop: {img_pil.size}")

    return _enhance_for_ocr(_pil_to_bgr(img_pil), upscale=upscale)
```
---
## def restore_paragraphs:

```python
def restore_paragraphs(text: str) -> str:
    lines = text.split("\n")
    result: List[str] = []

    for i, line in enumerate(lines):
        result.append(line)

        if i < len(lines) - 1:
            next_line = lines[i + 1]

            if line.strip().endswith(".") and next_line and next_line[0].isupper():
                result.append("")
            elif next_line.startswith(("Определение", "Замечание", "Теорема", "Лемма")):
                result.append("")

    return "\n".join(result)
```
---
## def _box_stats:

```python
def _box_stats(box: np.ndarray) -> Tuple[float, float, float, float, float, float]:
    xs = box[:, 0]
    ys = box[:, 1]
    x_min, x_max = float(xs.min()), float(xs.max())
    y_min, y_max = float(ys.min()), float(ys.max())
    x_c = (x_min + x_max) / 2.0
    y_c = (y_min + y_max) / 2.0
    return x_min, y_min, x_max, y_max, x_c, y_c
```
---
## def _estimate_line_height:

```python
def _estimate_line_height(items: List[OcrBox]) -> float:
    hs = []
    for it in items:
        _, y_min, _, y_max, _, _ = _box_stats(it.box)
        hs.append(max(2.0, y_max - y_min))
    return float(np.median(np.array(hs, dtype=np.float32))) if hs else 20.0
```
---
## def _group_into_lines:

```python
def _group_into_lines(items: List[OcrBox], line_height: float) -> List[List[OcrBox]]:
    items_sorted = sorted(
        items, key=lambda it: (_box_stats(it.box)[5], _box_stats(it.box)[4])
    )
    lines: List[List[OcrBox]] = []
    cur: List[OcrBox] = []
    cur_y: Optional[float] = None

    thresh = max(8.0, 0.6 * line_height)

    for it in items_sorted:
        y_c = _box_stats(it.box)[5]
        if cur_y is None:
            cur_y = y_c
            cur = [it]
            continue

        if abs(y_c - cur_y) <= thresh:
            cur.append(it)
            cur_y = (cur_y * 0.7) + (y_c * 0.3)
        else:
            lines.append(cur)
            cur = [it]
            cur_y = y_c

    if cur:
        lines.append(cur)

    for ln in lines:
        ln.sort(key=lambda it: _box_stats(it.box)[4])
    return lines
```
---
## def _boxes_to_markdown:

```python
def _boxes_to_markdown(items: List[OcrBox], math_delims: MathDelims = "dollars") -> str:
    if math_delims == "dollars":
        isolated_sep = ("$$\n", "\n$$")
        embed_sep = (" $", "$ ")
    else:
        isolated_sep = ("\\[\n", "\n\\]")
        embed_sep = ("\\(", "\\)")

    line_h = _estimate_line_height(items)
    lines = _group_into_lines(items, line_height=line_h)

    out_lines: List[str] = []

    for ln in lines:
        buf: List[str] = []
        for it in ln:
            txt = (it.text or "").strip()
            if not txt:
                continue

            if it.type == "text":
                buf.append(txt)
            elif it.type == "embedding":
                buf.append(f"{embed_sep[0]}{txt}{embed_sep[1]}")
            else:
                if buf:
                    out_lines.append(" ".join(buf).strip())
                    buf = []
                out_lines.append(f"{isolated_sep[0]}{txt}{isolated_sep[1]}")

        if buf:
            out_lines.append(" ".join(buf).strip())

    return "\n".join([x for x in out_lines if x.strip()]).strip()
```
---
## def _pix2text_detect_and_recognize_formulas:

```python
def _pix2text_detect_and_recognize_formulas(
    p2t: Pix2Text,
    img_pil: Image.Image,
    resized_shape: int = 2048,
    mfr_batch_size: int = 1,
) -> List[OcrBox]:
    tfo = p2t.text_formula_ocr
    if tfo is None or tfo.mfd is None or tfo.latex_ocr is None:
        raise RuntimeError("Pix2Text text_formula_ocr/mfd/latex_ocr is not available")

    img0 = img_pil.convert("RGB")
    w, h = img0.size

    ratio = resized_shape / float(max(1, w))
    resized_hw = (max(1, int(h * ratio)), resized_shape)

    analyzer_outs = tfo.mfd(img0.copy(), resized_shape=resized_hw)

    patches: List[Image.Image] = []
    meta: List[dict] = []
    for mf in analyzer_outs:
        box = np.array(mf["box"], dtype=np.float32)
        x_min, y_min, x_max, y_max, *_ = _box_stats(box)
        x0 = max(0, int(x_min))
        y0 = max(0, int(y_min))
        x1 = min(w, int(x_max))
        y1 = min(h, int(y_max))
        if x1 - x0 < 2 or y1 - y0 < 2:
            continue
        patches.append(img0.crop((x0, y0, x1, y1)))
        meta.append({"type": mf.get("type", "isolated"), "box": box})

    if not patches:
        return []

    recs = tfo.latex_ocr.recognize(patches, batch_size=mfr_batch_size)

    outs: List[OcrBox] = []
    for m, r in zip(meta, recs):
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
## def _mask_polys_white:

```python
def _mask_polys_white(bgr: np.ndarray, polys: List[np.ndarray]) -> np.ndarray:
    if not polys:
        return bgr

    out = bgr.copy()
    h, w = out.shape[:2]

    for poly in polys:
        p = np.array(poly, dtype=np.int32).reshape(-1, 1, 2)
        p[:, 0, 0] = np.clip(p[:, 0, 0], 0, w - 1)
        p[:, 0, 1] = np.clip(p[:, 0, 1], 0, h - 1)
        cv2.fillPoly(out, [p], (255, 255, 255))

    return out
```
---
## def _paddle_text_boxes:

```python
def _paddle_text_boxes(paddle: PaddleOCR, img_bgr: np.ndarray) -> List[OcrBox]:
    outs: List[OcrBox] = []

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
                box = np.array(rec_polys[i], dtype=np.float32)  # (4,2) [page:5]
                outs.append(
                    OcrBox(
                        type="text",
                        text=txt,
                        score=float(rec_scores[i] or 0.0),
                        box=box,
                    )
                )
        return outs

    res = paddle.ocr(img_bgr, cls=True)
    lines = (
        res[0]
        if (
            isinstance(res, list)
            and res
            and isinstance(res[0], list)
            and (len(res) == 1)
        )
        else res
    )
    if not lines:
        return outs

    for line in lines:
        if not line or len(line) < 2:
            continue
        box = np.array(line[0], dtype=np.float32)
        payload = line[1]
        txt = (
            payload[0] if isinstance(payload, (list, tuple)) and payload else ""
        ).strip()
        score = (
            float(payload[1])
            if isinstance(payload, (list, tuple)) and len(payload) > 1
            else 0.0
        )
        if txt:
            outs.append(OcrBox(type="text", text=txt, score=score, box=box))
    return outs
```
---
## def image_bytes_to_markdown:

```python
def image_bytes_to_markdown(
    image_bytes: bytes,
    p2t: Optional[Pix2Text] = None,
    paddle: Optional[PaddleOCR] = None,
    resized_shape: int = 2048,
    contain_formula: bool = True,
    math_delims: MathDelims = "dollars",
    skip_warp: bool = False,
) -> str:
    p2t = p2t or build_p2t_formula(device="cpu")
    paddle = paddle or build_paddle_ru(device="cpu")

    img0 = Image.open(io.BytesIO(image_bytes))
    logger.info(f"Loaded image: {img0.size}")

    img = preprocess_screen_photo(
        img0,
        detect_width=1200,
        upscale=2,
        fallback_crop=True,
        skip_warp=skip_warp,
    )
    logger.info(f"After preprocess: {img.size}")

    # 1) Формулы (Pix2Text)
    formula_boxes: List[OcrBox] = []
    if contain_formula:
        formula_boxes = _pix2text_detect_and_recognize_formulas(
            p2t=p2t,
            img_pil=img,
            resized_shape=resized_shape,
            mfr_batch_size=1,
        )

    # 2) Текст (PaddleOCR) на изображении с замаскированными формулами
    bgr = _pil_to_bgr(img)
    bgr_masked = _mask_polys_white(bgr, [fb.box for fb in formula_boxes])
    text_boxes = _paddle_text_boxes(paddle, bgr_masked)

    # 3) Merge -> Markdown
    md = _boxes_to_markdown(text_boxes + formula_boxes, math_delims=math_delims)
    logger.info(f"OCR result length: {len(md.strip())}")
    return md.strip() or "(OCR вернул пустой результат)"
```
---
## def _ensure_nonempty_markdown:

```python
def _ensure_nonempty_markdown(md: str) -> str:
    md2 = (md or "").strip()
    return md2 if md2 else "(OCR вернул пустой результат)"
```
---
## def markdown_to_pdf_bytes:

```python
def markdown_to_pdf_bytes(
    markdown_text: str,
    out_font: str = "Liberation Serif",
    out_sans: str = "Liberation Sans",
    out_mono: str = "Liberation Mono",
    pdf_engine: str = "xelatex",
    math_delims: MathDelims = "dollars",
    debug: bool = False,
) -> bytes:
    markdown_text = _ensure_nonempty_markdown(markdown_text)

    input_format = "markdown"
    if math_delims == "dollars":
        input_format = "markdown+tex_math_dollars"
    else:
        input_format = "markdown+tex_math_single_backslash"

    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        md_file = td_path / "doc.md"
        out_pdf = td_path / "doc.pdf"
        out_tex = td_path / "doc.tex"

        md_file.write_text(markdown_text, encoding="utf-8")

        cmd = [
            "pandoc",
            str(md_file),
            "-f",
            input_format,
            "-s",
            f"--pdf-engine={pdf_engine}",
            "-V",
            "lang=ru-RU",
            "-V",
            "babel-lang=russian",
            "-V",
            f"mainfont={out_font}",
            "-V",
            f"sansfont={out_sans}",
            "-V",
            f"monofont={out_mono}",
            "-o",
            str(out_pdf),
        ]
        if debug:
            cmd.append("--verbose")

        logger.info(f"Pandoc command: {' '.join(cmd)}")
        proc = subprocess.run(cmd, capture_output=True, text=True)

        if proc.returncode != 0:
            tex_cmd = [
                "pandoc",
                str(md_file),
                "-f",
                input_format,
                "-s",
                "-o",
                str(out_tex),
            ]
            subprocess.run(tex_cmd, capture_output=True, text=True)

            tex_preview = (
                out_tex.read_text(encoding="utf-8", errors="replace")[:2000]
                if out_tex.exists()
                else ""
            )
            raise RuntimeError(
                "pandoc failed.\n"
                f"returncode: {proc.returncode}\n"
                f"stderr:\n{proc.stderr}\n"
                f"---- TEX (first 2000 chars) ----\n{tex_preview}\n"
                f"---- MD stats ----\nlen={len(markdown_text)} head={markdown_text[:200]!r}\n"
            )

        return out_pdf.read_bytes()
```
---
## def image_bytes_to_pdf_bytes:
#### Главная функция OCR→Markdown→PDF.
Для фото экрана (квадратных) автоматически включает skip_warp=True.

```python
def image_bytes_to_pdf_bytes(image_bytes: bytes) -> bytes:
    """
    Главная функция OCR→Markdown→PDF.
    Для фото экрана (квадратных) автоматически включает skip_warp=True.
    """
    img_test = Image.open(io.BytesIO(image_bytes))
    w, h = img_test.size
    aspect = w / h if h > 0 else 1.0
    skip_warp = 0.8 < aspect < 1.25

    logger.info(
        f"image_bytes_to_pdf_bytes: image={w}x{h}, aspect={aspect:.2f}, skip_warp={skip_warp}"
    )

    md = image_bytes_to_markdown(
        image_bytes,
        math_delims="dollars",
        skip_warp=skip_warp,
        contain_formula=True,
    )
    md = restore_paragraphs(md)
    return markdown_to_pdf_bytes(md, math_delims="dollars", debug=False)
```
---