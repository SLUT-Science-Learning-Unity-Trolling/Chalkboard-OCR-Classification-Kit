import re
import pandas as pd
import Levenshtein
from difflib import SequenceMatcher
from sklearn.metrics import precision_score, recall_score, f1_score
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


def normalize_text(text: str) -> str:
    """Нормализация текста для OCR: убираем переносы строк, лишние пробелы, спецсимволы."""
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    text = text.replace("￿", "")
    text = text.strip()
    return text

def cer(ref: str, hyp: str) -> float:
    """Character Error Rate"""
    ref = normalize_text(ref)
    hyp = normalize_text(hyp)
    return Levenshtein.distance(ref, hyp) / max(1, len(ref))

def wer(ref: str, hyp: str) -> float:
    """Word Error Rate"""
    ref_words = normalize_text(ref).split()
    hyp_words = normalize_text(hyp).split()
    return Levenshtein.distance(" ".join(ref_words), " ".join(hyp_words)) / max(1, len(ref_words))

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

def lcs_length(ref: str, hyp: str):
    """Longest Common Subsequence длина и нормализованная"""
    ref = normalize_text(ref)
    hyp = normalize_text(hyp)
    matcher = SequenceMatcher(None, ref, hyp)
    lcs_len = sum(triple.size for triple in matcher.get_matching_blocks())
    return lcs_len, lcs_len / max(len(ref), 1)

def formula_accuracy(ref: str, hyp: str):
    """Простая точность формул ($...$ или \(...\))"""
    ref_formulas = re.findall(r"\$.*?\$|\\\(.*?\\\)", ref)
    hyp_formulas = re.findall(r"\$.*?\$|\\\(.*?\\\)", hyp)
    if not ref_formulas:
        return 1.0
    matched = sum(1 for r, h in zip(ref_formulas, hyp_formulas) if r == h)
    return matched / len(ref_formulas)

def key_terms_accuracy(ref: str, hyp: str, key_terms: list):
    """Точность распознавания ключевых терминов"""
    hyp_norm = normalize_text(hyp).lower()
    hits = sum(1 for term in key_terms if term.lower() in hyp_norm)
    return hits / max(1, len(key_terms))

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


ground_truths = {
    "photo1": "Внешняя и внутренняя сортировки Внутренняя сортировка — данные последовательности целиком вмещаются в оперативную память. Доступ возможен к произвольному элементу последовательности. Элементы последовательности упорядочиваются в памяти без дополнительных затрат. Внешняя сортировка — данные не помещаются в оперативную память. Последовательный доступ к элементу последовательности. Затраты по свободную навигацию по элементам неоправданно высоки.",
}

ocr_results = {
    "Paddle+Pix2Tex": {
        "photo1": """Внешняя и внутренняя сортировки Внутренняя сортировка — данные последова-
тельности целиком вмещаются в оперативную память.
Доступ возможен к произвольному элементу последовательности.
Элементы последовательности упорядочиваются в памяти без дополнительных
затрат.
Внешняясортировка данные не помещаются в оперативную память.
Последовательный доступ ￿ элементу последовательности. Т.е. можно прочесть
только текущий элемент, за НИМ следующий и т. д.
Затраты nо свободную навигацию по элементам неоправданно высоки"""
    },

    "Tesseract+Pix2Tex": {
        "photo1": """Внешняя и внутренняя сортировки Внутренняя сортировка — данные последо-
вательности целиком вмещаются в оперативную память. * Доступ возможен к
произвольному элементу последовательности . * Элементы последовательности
упорядочиваются в памяти без дополнительных затрат.
Внешняя сортировка — данные не помещаются в оперативную память. * Последо-
вательный доступ ￿ — элементу последовательности. Т.е. можно прочесть только
текущий элемент, за ним следующий и т. Д. * Затраты по свободную навигацию
по элементам неоправданно высоки.""",
    },

    "EasyOCR+Pix2Tex": {
        "photo1": """Внешняя и внутренняя сортирОвКИ Внутренняя сортировка данные последо-
вательности целиком вмещаются 8 операТивНуЮ Панять Доступ возможен к
пронзвольнОМУ элементу последователЬнОсТи Элененты последовательности
упорядочиваются 8 паМЯТи без ДОПОЛНИТеЛЬНЫХ затрат: Внешняя сор-
тировка данные не помещаются 8 оперативную ПаМЯТЬ Последовательный
доступ ￿ элементу последовательности: Те: можно прочесть ТОЛЬКО текущий
элемент 3а НИМ СЛедуЮщий Ит.д Затрагы по свободную наВнгаЦиЮ ПО
элементам неоПравданнО ВЫСОКИ:"""
    },

    "RapidOCR+Pix2Tex": {
        "photo1": """ВНеWНАА N ВНуТРеННАА СОРТNРОВКN nаМАТb. оСТуn ВО3МОХеНКnрОW3ВОnbНОМу
3nеМеНТуnОСnеАОВаТеnbНОСТН. 3nеМеНТ6InОСnеАОВаТеnbНОСТW уnО-
РААОуМВаIОТСА В nаМАТW6е3 АОNОnНNТеnbНbIХ 3аТРаТ.
ВНеWНАА сОрТНрОВКа -АаННbIе Не nОМеWаIОТСА В ОnераТНВНуIО
nаМАТb. nоСnеАоВаТеnbНbIМ АосТуn ￿ 3nеМеНТу nОСnеАОВаТеnbНОСТМ.
Т.е. МОХНО nрОуеСТb ТОnbКО ТеКуLN3nеМеНТ,3а НММСnеАуIОWТ.А.
ВаТраТbInОСВО6ОАНуIО НаВМrаLМIО nО 3nеМеНТаМ НеОnраВАаННО ВbI-
СОКН."""
    },

    "Doctr+Pix2Tex": {
        "photo1": """ВНеWНАА М ВНУТDеННАА сорТnрОВКW ВНуТреННАА сортuроsка - АаН-
Нblе nосhероsаrеnbНОСТW уеnКом ВМЕLLаIОТСА В оnерат/ВНуfо nамАТb. .
Аосrуn ВО3МОКЕН К nроn380/bНОМу 3nеМеНту nосhероВатеnbНОСТМ. . 3nе-
меНТbl nосhероsаrеnbНОСТW уnорRА04МВаIОТСА В nамАТW 6е3 LОnОnНА-
Те/bНblХ 3атраr.
ВНеWНАА сортuроека = АаННblе Не nоМеLаFОТСА В оnератhВНуlо nамАТb.
. NосnеnоsатеnbНblк АосТуn ￿ аnеМеНту nосhероВатеnbНОСТМ. Те. МОХНО
nроуесТb ТОNВКО Текуuмi 3nеМеНТ, 33 НММ сhеауiоuww WТА . 3аrраrbl nо
СВО60АНУIО Наbмrаuмiо nо аnемеnтам НеоnраВАаННО ВВIСОКМ"""
    },
}

key_terms = ["Внутренняя сортировка", "Внешняя сортировка", "оперативную память", "произвольному элементу", " последовательный доступ", "упорядочиваются", "неоправданно высоки"]

df_results = evaluate_ocr(ground_truths, ocr_results, key_terms=key_terms)
print(df_results)


sns.set(style="whitegrid")

metrics_to_plot = ["CER", "WER", "WordF1", "LCS_norm", "KeyTermsAcc"]
n_metrics = len(metrics_to_plot)

fig, axes = plt.subplots(2, 3, figsize=(18, 10))
axes = axes.flatten()

for i, metric in enumerate(metrics_to_plot):
    sns.barplot(
        data=df_results,
        x="Photo",
        y=metric,
        hue="Engine",
        palette="Set2",
        ax=axes[i]
    )
    axes[i].set_title(metric)
    if metric not in ["CER", "WER"]:
        axes[i].set_ylim(0, 1)
    axes[i].set_xlabel("")
    axes[i].set_ylabel(metric)
    axes[i].legend_.remove() 

axes[-1].axis("off")

handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, title="OCR Engine", loc="lower center", ncol=len(df_results['Engine'].unique()))
fig.tight_layout(rect=[0, 0.05, 1, 0.95])
plt.show()