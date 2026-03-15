## def normalize_text:
#### Нормализация текста для OCR: убираем переносы строк, лишние пробелы, спецсимволы.

```python
def normalize_text(text: str) -> str:
    """Нормализация текста для OCR: убираем переносы строк, лишние пробелы, спецсимволы."""
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    text = text.replace("￿", "")
    text = text.strip()
    return text
```
---
## def cer:
#### Character Error Rate

```python
def cer(ref: str, hyp: str) -> float:
    """Character Error Rate"""
    ref = normalize_text(ref)
    hyp = normalize_text(hyp)
    return Levenshtein.distance(ref, hyp) / max(1, len(ref))
```
---
## def wer:
#### Word Error Rate

```python
def wer(ref: str, hyp: str) -> float:
    """Word Error Rate"""
    ref_words = normalize_text(ref).split()
    hyp_words = normalize_text(hyp).split()
    return Levenshtein.distance(" ".join(ref_words), " ".join(hyp_words)) / max(1, len(ref_words))
```
---
## def word_f1_metrics:
#### Precision, Recall, F1 для слов

```python
def word_f1_metrics(ref: str, hyp: str):
    """Precision, Recall, F1 для слов"""
    ref_words = normalize_text(ref).split()
    hyp_words = normalize_text(hyp).split()

    y_true = [1 if w in hyp_words else 0 for w in ref_words]
    y_pred = [1]*len(y_true)
    precision = precision_score(y_true, y_pred, zero_division=1)
    recall = recall_score(y_true, y_pred, zero_division=1)
    f1 = f1_score(y_true, y_pred, zero_division=1)
    return precision, recall, f1
```
---
## def lcs_length:
#### Longest Common Subsequence длина и нормализованная

```python
def lcs_length(ref: str, hyp: str):
    """Longest Common Subsequence длина и нормализованная"""
    ref = normalize_text(ref)
    hyp = normalize_text(hyp)
    matcher = SequenceMatcher(None, ref, hyp)
    lcs_len = sum(triple.size for triple in matcher.get_matching_blocks())
    return lcs_len, lcs_len / max(len(ref), 1)
```
---
## def formula_accuracy:
#### Простая точность формул ($...$ или \(...\))

```python
def formula_accuracy(ref: str, hyp: str):
    """Простая точность формул ($...$ или \(...\))"""
    ref_formulas = re.findall(r"\$.*?\$|\\\(.*?\\\)", ref)
    hyp_formulas = re.findall(r"\$.*?\$|\\\(.*?\\\)", hyp)
    if not ref_formulas:
        return 1.0
    matched = sum(1 for r, h in zip(ref_formulas, hyp_formulas) if r == h)
    return matched / len(ref_formulas)
```
---
## def key_terms_accuracy:
#### Точность распознавания ключевых терминов

```python
def key_terms_accuracy(ref: str, hyp: str, key_terms: list):
    """Точность распознавания ключевых терминов"""
    hyp_norm = normalize_text(hyp).lower()
    hits = sum(1 for term in key_terms if term.lower() in hyp_norm)
    return hits / max(1, len(key_terms))
```
---
## def evaluate_ocr:
#### ground_truths: {photo_id: text}

ocr_results: {engine_name: {photo_id: text}}
key_terms: список ключевых слов для дополнительной проверки

```python
def evaluate_ocr(ground_truths: dict, ocr_results: dict, key_terms: list = []):
    """
    ground_truths: {photo_id: text}
    ocr_results: {engine_name: {photo_id: text}}
    key_terms: список ключевых слов для дополнительной проверки
    """
    rows = []
    for engine, results in ocr_results.items():
        for photo_id, ocr_text in results.items():
            gt_text = ground_truths.get(photo_id, "")
            precision, recall, f1 = word_f1_metrics(gt_text, ocr_text)
            lcs_len, lcs_norm = lcs_length(gt_text, ocr_text)
            formula_acc = formula_accuracy(gt_text, ocr_text)
            term_acc = key_terms_accuracy(gt_text, ocr_text, key_terms) if key_terms else None
            rows.append({
                "Engine": engine,
                "Photo": photo_id,
                "CER": cer(gt_text, ocr_text),
                "WER": wer(gt_text, ocr_text),
                "WordPrecision": precision,
                "WordRecall": recall,
                "WordF1": f1,
                "LCS_len": lcs_len,
                "LCS_norm": lcs_norm,
                "FormulaAcc": formula_acc,
                "KeyTermsAcc": term_acc
            })
    return pd.DataFrame(rows)
```
---