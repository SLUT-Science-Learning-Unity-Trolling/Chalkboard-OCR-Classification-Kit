## Класс OCRService


```python
class OCRService:
```

---
## def init:

```python
    def __init__(self, formula_engine: FormulaOCREngine, text_engine: TextOCREngine, *,
                 detect_width: int = 2400, upscale: int = 3):
        self.formula_engine = formula_engine
        self.text_engine = text_engine
        self.detect_width = detect_width
        self.upscale = upscale
```
---
## def _prepare_image:

```python
    def _prepare_image(self, image_bytes: bytes, skip_warp: bool = False) -> Image.Image:
        img0 = Image.open(io.BytesIO(image_bytes))
        img = preprocess_screen_photo(
            img0,
            detect_width=self.detect_width,
            upscale=self.upscale,
            fallback_crop=True,
            skip_warp=skip_warp,
        )
        return img
```
---
## def _detect_formula_boxes:

```python
    def _detect_formula_boxes(self, pil_img: Image.Image, resized_shape: int = 2048, batch_size: int = 1):
        try:
            return self.formula_engine.detect_formulas(pil_img, resized_shape=resized_shape, batch_size=batch_size)
        except Exception as e:
            logger.warning(f"Formula engine failed: {e}")
            return []
```
---
## def _detect_text_boxes:

```python
    def _detect_text_boxes(self, bgr_masked: np.ndarray):
        try:
            return self.text_engine.detect_text_boxes(bgr_masked)
        except Exception as e:
            logger.warning(f"Text engine failed: {e}")
            return []
```
---
## def _assemble_markdown:

```python
    def _assemble_markdown(self, text_boxes: List[OcrBox], formula_boxes: List[OcrBox], math_delims: MathDelims = "dollars"):
        md = _boxes_to_markdown(text_boxes + formula_boxes, math_delims=math_delims)
        md = replace_lat_to_cyr_outside_math(md)
        md = unwrap_plain_text_math(md)
        return md.strip() or "(OCR вернул пустой результат)"
```
---
## def image_bytes_to_markdown:

```python
    def image_bytes_to_markdown(self, image_bytes: bytes, *, contain_formula: bool = True, resized_shape: int = 2048, math_delims: MathDelims = "dollars", skip_warp: bool = False) -> str:
        img = self._prepare_image(image_bytes, skip_warp=skip_warp)
        formula_boxes = []
        if contain_formula:
            formula_boxes = self._detect_formula_boxes(img, resized_shape=resized_shape, batch_size=1)
        bgr = _pil_to_bgr(img)
        bgr_masked = _mask_polys_white(bgr, [fb.box for fb in formula_boxes])
        text_boxes = self._detect_text_boxes(bgr_masked)
        md = self._assemble_markdown(text_boxes, formula_boxes, math_delims=math_delims)
        logger.info(f"OCR result length: {len(md.strip())}")
        return md
```
---
## def _ensure_nonempty_markdown:

```python
    def _ensure_nonempty_markdown(self, md: str) -> str:
        md2 = (md or "").strip()
        return md2 if md2 else "(OCR вернул пустой результат)"
```
---
## def _sanitize_latex_outside_math:
#### Экранирует спецсимволы LaTeX вне математических блоков.

```python
    def _sanitize_latex_outside_math(self, md: str) -> str:
        """Экранирует спецсимволы LaTeX вне математических блоков."""
        def escape_latex(s: str) -> str:
            return (
                s.replace("\\", "\\textbackslash{}")
                .replace("&", "\\&")
                .replace("%", "\\%")
                .replace("$", "\\$")
                .replace("#", "\\#")
                .replace("_", "\\_")
                .replace("{", "\\{")
                .replace("}", "\\}")
                .replace("~", "\\textasciitilde{}")
                .replace("^", "\\textasciicircum{}")
                .replace("|", "\\textbar{}")
            )

        parts = _MATH_BLOCK_RE.split(md)
        out: list[str] = []
        for part in parts:
            if not part:
                continue
            if _MATH_BLOCK_RE.fullmatch(part):
                out.append(part)
            else:
                out.append(escape_latex(part))
        return "".join(out)
```
---
## def markdown_to_pdf_bytes:

```python
    def markdown_to_pdf_bytes(self, markdown_text: str, out_font: str = "Liberation Serif", out_sans: str = "Liberation Sans", out_mono: str = "Liberation Mono", pdf_engine: str = "xelatex", math_delims: MathDelims = "dollars", debug: bool = False) -> bytes:
        markdown_text = self._ensure_nonempty_markdown(markdown_text)
        markdown_text = self._sanitize_latex_outside_math(markdown_text)
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
                tex_preview = (out_tex.read_text(encoding="utf-8", errors="replace")[:2000] if out_tex.exists() else "")
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
## def images_bytes_to_markdown:

```python
    def images_bytes_to_markdown(self, images: List[bytes], math_delims: MathDelims = "dollars", contain_formula: bool = True) -> str:
        results: List[str] = []
        for idx, image_bytes in enumerate(images, start=1):
            logger.info(f"Processing image #{idx}")
            md = self.image_bytes_to_markdown(image_bytes, math_delims=math_delims, contain_formula=contain_formula)
            md = restore_paragraphs(md)
            block = f"Фото {idx}\n\n{md.strip()}"
            results.append(block)
        return "\n\n".join(results)
```
---
## def images_bytes_to_pdf_bytes:

```python
    def images_bytes_to_pdf_bytes(self, images: List[bytes], summarize: bool = True) -> bytes:
        md = self.images_bytes_to_markdown(images)
        if summarize:
            try:
                md_summary = summarize_markdown_openrouter_requests(md)
                md = md_summary
            except Exception as e:
                logger.warning(f"Не удалось сделать саммари: {e}")
        return self.markdown_to_pdf_bytes(md)
```
---
## def image_bytes_to_pdf_bytes:

```python
    @monitor_ocr_func
    def image_bytes_to_pdf_bytes(self, image_bytes: bytes, summarize: bool = True) -> bytes:
        img_test = Image.open(io.BytesIO(image_bytes))
        w, h = img_test.size
        aspect = w / h if h > 0 else 1.0
        skip_warp = False
        logger.info(f"image_bytes_to_pdf_bytes: image={w}x{h}, aspect={aspect:.2f}, skip_warp={skip_warp}")
        md = self.image_bytes_to_markdown(image_bytes, math_delims="dollars", skip_warp=skip_warp, contain_formula=True)
        md = restore_paragraphs(md)
        if summarize:
            try:
                md_summary = summarize_markdown_openrouter_requests(md)
                md = md_summary
            except Exception as e:
                logger.warning(f"Не удалось сделать саммари: {e}")
        return self.markdown_to_pdf_bytes(md, math_delims="dollars", debug=False)
```
---
## def monitor_ocr_func:
#### Декоратор для мониторинга OCR: считает ошибки, успешные обработки и latency.

```python
def monitor_ocr_func(func):
    """Декоратор для мониторинга OCR: считает ошибки, успешные обработки и latency."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
        except Exception:
            OCR_ERRORS.inc()
            raise
        else:
            OCR_PROCESSED.inc()
            return result
        finally:
            duration = time.perf_counter() - start
            OCR_LATENCY.observe(duration)
    return wrapper
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

    width_a = np.linalg.norm(br - bl)
    width_b = np.linalg.norm(tr - tl)
    max_w = int(max(width_a, width_b))

    height_a = np.linalg.norm(tr - br)
    height_b = np.linalg.norm(tl - bl)
    max_h = int(max(height_a, height_b))

    max_w = max(max_w, 2)
    max_h = max(max_h, 2)

    dst = np.array(
        [[0, 0], [max_w - 1, 0], [max_w - 1, max_h - 1], [0, max_h - 1]],
        dtype="float32",
    )
    matrix = cv2.getPerspectiveTransform(rect, dst)
    return cv2.warpPerspective(image_bgr, matrix, (max_w, max_h))
```
---
## def _find_largest_quad:

```python
def _find_largest_quad(image_bgr: np.ndarray, detect_width: int = 2400) -> np.ndarray | None:
    h, w = image_bgr.shape[:2]
    if w > detect_width:
        r = detect_width / float(w)
        small = cv2.resize(image_bgr, (detect_width, int(h * r)), interpolation=cv2.INTER_AREA)
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
def _enhance_for_ocr(warped_bgr: np.ndarray, upscale: int = 3, force_binary: bool = False) -> Image.Image:
    h_before, w_before = warped_bgr.shape[:2]
    logger.info(f"_enhance_for_ocr input: {w_before}x{h_before}")

    den = cv2.bilateralFilter(warped_bgr, d=9, sigmaColor=75, sigmaSpace=75)
    lab = cv2.cvtColor(den, cv2.COLOR_BGR2LAB)
    l_channel, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l2 = clahe.apply(l_channel)
    merged = cv2.cvtColor(cv2.merge([l2, a, b]), cv2.COLOR_LAB2BGR)
    out = merged

    if upscale and upscale > 1:
        out = cv2.resize(out, (out.shape[1] * upscale, out.shape[0] * upscale), interpolation=cv2.INTER_CUBIC)
        logger.info(f"After upscale {upscale}x: {out.shape[1]}x{out.shape[0]}")

    if force_binary:
        gray = cv2.cvtColor(out, cv2.COLOR_BGR2GRAY)
        gray = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)
        bin_img = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10)
        out = cv2.cvtColor(bin_img, cv2.COLOR_GRAY2BGR)

    pil = _bgr_to_pil(out)
    pil = ImageEnhance.Contrast(pil).enhance(1.15)
    pil = ImageEnhance.Brightness(pil).enhance(1.02)

    logger.info(f"Final PIL size: {pil.size}")
    return pil
```
---
## def preprocess_screen_photo:

```python
def preprocess_screen_photo(img_pil: Image.Image, detect_width: int = 2400, upscale: int = 3, fallback_crop: bool = True, skip_warp: bool = False) -> Image.Image:
    logger.info(f"preprocess_screen_photo input: {img_pil.size}")
    img_pil = ImageOps.exif_transpose(img_pil).convert("RGB")
    logger.info(f"After exif_transpose: {img_pil.size}")
    bgr = _pil_to_bgr(img_pil)
    w, h = img_pil.size
    if skip_warp:
        logger.info("Skipping warp by flag")
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
    result: list[str] = []
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
## def unwrap_plain_text_math:

```python
def unwrap_plain_text_math(md: str) -> str:
    lines = md.splitlines()
    out: list[str] = []
    for line in lines:
        s = line.strip()
        if s.startswith("$$") and s.endswith("$$"):
            body = s[2:-2].strip()
            m = _SIMPLE_TEXT_IN_MATH_RE.match(body)
            if m:
                txt = m.group(1).replace("~", " ")
                out.append(txt)
                continue
        out.append(line)
    return "\n".join(out)
```
---
## def replace_lat_to_cyr_outside_math:

```python
def replace_lat_to_cyr_outside_math(text: str) -> str:
    parts = _MATH_BLOCK_RE.split(text)
    out: list[str] = []
    for part in parts:
        if not part:
            continue
        if _MATH_BLOCK_RE.fullmatch(part):
            out.append(part)
        else:
            out.append(part.translate(_LAT2CYR))
    return "".join(out)
```
---
## def _box_stats:

```python
def _box_stats(box: np.ndarray):
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
    items_sorted = sorted(items, key=lambda it: (_box_stats(it.box)[5], _box_stats(it.box)[4]))
    lines: List[List[OcrBox]] = []
    cur: List[OcrBox] = []
    cur_y: float | None = None
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
## def summarize_markdown_openrouter_requests:

```python
def summarize_markdown_openrouter_requests(md: str, api_key: str | None = None, *, api_base: str = "https://openrouter.ai/api/v1", model: str = "arcee-ai/trinity-large-preview:free", temperature: float = 0.0, max_retries: int = 3) -> str:
    api_key = api_key or getattr(config, "API_KEY", None)
    if not api_key:
        raise RuntimeError("Не найден OpenRouter API key.")

    url = api_base.rstrip("/") + "/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    messages = [{"role":"user","content":f"Сделай краткий конспект этого текста, сохрани форматы Markdown и формулы LaTeX:\n\n{md}"}]

    for attempt in range(1, max_retries+1):
        try:
            response = requests.post(
                url=url, headers=headers, data=json.dumps({"model": model, "messages": messages, "temperature": temperature, "reasoning": {"enabled": True}}), timeout=30
            )
            response.raise_for_status()
            data = response.json()
            assistant_msg = data["choices"][0]["message"]
            messages.append({"role":"assistant","content":assistant_msg.get("content"), "reasoning_details": assistant_msg.get("reasoning_details")})
            return assistant_msg.get("content", "").strip()
        except requests.RequestException as e:
            logger.warning(f"Попытка {attempt} не удалась: {e}")
            if attempt == max_retries:
                raise RuntimeError(f"Не удалось получить ответ после {max_retries} попыток: {e}") from None
        except (KeyError, ValueError) as e:
            raise RuntimeError(f"Непредвиденный формат ответа OpenRouter: {e}") from None
```
---