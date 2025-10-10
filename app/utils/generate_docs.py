"""Модуль для генерации Markdown-документации."""
# GenerateDocs_Plugin

import argparse
import ast
import os
import re
import shutil
import subprocess

from pathlib import Path
from typing import Any

from app.config import config


PROJECT_DIRS = config.PROJECT_DIRS
DOCS_DIR = config.DOCS_DIR
SUPPORTED_EXT = config.SUPPORTED_EXT
WIKI_REPO = config.WIKI_REPO
LOCAL_WIKI_DIR = config.LOCAL_WIKI_DIR


def parse_google_docstring(docstring: str) -> dict[str, Any]:
    """Парсит Google-style докстринг в структуру словаря.

    Args:
        docstring (str): Исходный докстринг функции, метода или класса.

    Returns:
        dict: Словарь с ключами:
            - first_line (str): Первая строка описания.
            - rest_description (str): Основное описание.
            - args (str): Раздел аргументов.
            - returns (str): Раздел возвращаемых значений.
            - raises (str): Раздел исключений.
    """
    if not docstring:
        return {
            "first_line": "",
            "rest_description": "",
            "args": "",
            "returns": "",
            "raises": "",
        }

    sections: dict[str, Any] = {
        "first_line": "",
        "rest_description": [],
        "args": [],
        "returns": [],
        "raises": [],
    }
    current_section = "description"
    is_first_line = True

    for line in docstring.splitlines():
        line_strip = line.strip()
        if re.match(r"^(Args|Attributes):", line_strip):
            current_section = "args"
        elif re.match(r"^Returns:", line_strip):
            current_section = "returns"
        elif re.match(r"^(Raises|Exceptions):", line_strip):
            current_section = "raises"
        else:
            if current_section == "description":
                if is_first_line and line_strip:
                    sections["first_line"] = line_strip
                    is_first_line = False
                else:
                    if isinstance(sections["rest_description"], list):
                        sections["rest_description"].append(line)
            else:
                if isinstance(sections[current_section], list):
                    sections[current_section].append(line)

    for key in sections:
        if key == "first_line":
            continue
        sections[key] = "\n".join(sections[key]).strip()
    return sections


def extract_docstrings(file_path: Path) -> dict[Any, Any]:
    """Извлекает докстринги и тела функций/методов из Python-файла.

    Args:
        file_path (Path): Путь к Python-файлу.

    Returns:
        dict: Структура с докстрингами и кодом:
            - module (str): Докстринг модуля.
            - classes (dict): Классы и их методы.
            - functions (dict): Глобальные функции.
    """
    with open(file_path, encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=str(file_path))

    docstrings: dict[str, Any] = {
        "module": ast.get_docstring(tree),
        "classes": {},
    }

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            class_doc: dict[str, Any] = parse_google_docstring(
                ast.get_docstring(node) or ""
            )
            class_doc["methods"] = {}
            for cnode in node.body:
                if isinstance(cnode, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    method_doc = parse_google_docstring(ast.get_docstring(cnode) or "")
                    method_doc["body"] = get_function_body(file_path, cnode)
                    class_doc["methods"][cnode.name] = method_doc
            docstrings["classes"][node.name] = class_doc
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func_doc = parse_google_docstring(ast.get_docstring(node) or "")
            func_doc["body"] = get_function_body(file_path, node)
            docstrings.setdefault("functions", {})[node.name] = func_doc

    return docstrings


def get_function_body(
    file_path: Path, node: ast.FunctionDef | ast.AsyncFunctionDef
) -> str:
    """Извлекает полный исходный код функции или метода, включая сигнатуру и декораторы.

    Args:
        file_path (Path): Путь к файлу с исходным кодом.
        node (ast.AST): AST-узел функции или метода.

    Returns:
        str: Текст исходного кода функции.
    """
    with open(file_path, encoding="utf-8") as f:
        lines = f.readlines()

    start_line = node.lineno - 1
    if hasattr(node, "decorator_list") and node.decorator_list:
        decorator_start = min(decorator.lineno - 1 for decorator in node.decorator_list)
        start_line = decorator_start
        while start_line > 0 and lines[start_line - 1].strip().startswith("@"):
            start_line -= 1

    end_line: int = node.end_lineno or start_line + 1

    while end_line < len(lines):
        line = lines[end_line].strip()
        if line and line.startswith("@"):
            break
        if line and not line.startswith(" "):
            break
        end_line += 1

    body = "".join(lines[start_line:end_line]).rstrip()
    return body


def format_function_md(name: str, doc: dict[str, Any], is_method: bool = False) -> str:
    """Форматирует функцию или метод в Markdown с таблицами аргументов, возвращаемых значений и исключений.

    Args:
        name (str): Имя функции или метода.
        doc (dict): Докстринг функции, разобранный через parse_google_docstring.
        is_method (bool): Флаг, указывающий, что это метод класса.

    Returns:
        str: Сформатированный Markdown.
    """
    display_name = name.replace("__init__", "init")
    is_async = doc["body"].strip().startswith("async def")
    prefix = "async def" if is_async else "def"
    md = [f"## {prefix} {display_name}:"]

    if doc["first_line"]:
        md.append(f"#### {doc['first_line']}")

    if doc["rest_description"]:
        md.append(doc["rest_description"])

    # HTTP route
    if "@" in doc["body"]:
        route_lines: list[str] = []
        current_route: list[str] = []
        for line in doc["body"].splitlines():
            line_strip = line.strip()
            if line_strip.startswith(("@get", "@post", "@put", "@delete")) or (
                current_route and line_strip
            ):
                current_route.append(line_strip)
                if line_strip.endswith(")"):
                    route_lines.append(" ".join(current_route))
                    current_route = []
        if route_lines:
            md.append("#### Маршруты:")
            for route in route_lines:
                md.append(f"- `{route}`")

    # Аргументы
    if doc["args"]:
        md.append("\n#### Аргументы")
        md.append("| Аргумент | Тип | Описание |")
        md.append("|----------|-----|----------|")
        for arg in doc["args"].split("\n"):
            if arg.strip():
                parts = arg.strip().split(":", 1)
                if len(parts) == 2:
                    name_type = parts[0].strip()
                    desc = parts[1].strip()
                    if "(" in name_type and ")" in name_type:
                        arg_name = name_type.split("(")[0].strip()
                        arg_type = name_type.split("(")[1].replace(")", "").strip()
                    else:
                        arg_name = name_type
                        arg_type = ""
                    md.append(f"| `{arg_name}` | `{arg_type}` | {desc} |")
                else:
                    md.append(f"| `{arg.strip()}` | | |")

    # Возвращаемое значение
    if doc["returns"] and doc["returns"].strip().lower() != "none":
        md.append("\n#### Возвращает")
        md.append("| Тип | Описание |")
        md.append("|-----|----------|")
        for ret in doc["returns"].split("\n"):
            if ret.strip():
                parts = ret.strip().split(":", 1)
                if len(parts) == 2:
                    ret_type = parts[0].strip()
                    ret_desc = parts[1].strip()
                    md.append(f"| `{ret_type}` | {ret_desc} |")
                else:
                    md.append(f"| `{ret.strip()}` | |")

    # Исключения
    if doc["raises"]:
        md.append("\n#### Исключения")
        md.append("| Исключение | Описание |")
        md.append("|------------|----------|")
        for exc in doc["raises"].split("\n"):
            if exc.strip():
                parts = exc.strip().split(":", 1)
                if len(parts) == 2:
                    exc_type = parts[0].strip()
                    exc_desc = parts[1].strip()
                    md.append(f"| `{exc_type}` | {exc_desc} |")
                else:
                    md.append(f"| `{exc.strip()}` | |")

    md.append("\n```python")
    md.append(doc["body"])
    md.append("```")

    return "\n".join(md)


def write_md(file_path: Path, docstrings: dict[str, Any]) -> str:
    """Генерирует Markdown-файл для модуля или класса.

    Args:
        file_path (Path): Путь к Python-файлу.
        docstrings (dict): Словарь с докстрингами, полученный через extract_docstrings.

    Returns:
        str: Полный Markdown контент для файла.
    """
    md_content = []

    if docstrings.get("module"):
        md_content.append(f"# Модуль {file_path.stem}\n\n{docstrings['module']}\n")

    for cls_name, cls_doc in docstrings.get("classes", {}).items():
        md_content.append(f"## Класс {cls_name}\n")
        if cls_doc.get("first_line"):
            md_content.append(f"**{cls_doc['first_line']}**")
        if cls_doc.get("rest_description"):
            md_content.append(cls_doc["rest_description"])
        if cls_doc.get("args"):
            md_content.append("\n**Args:**")
            for arg in cls_doc["args"].split("\n"):
                if arg.strip():
                    parts = arg.strip().split(":", 1)
                    if len(parts) == 2:
                        arg_name_type = parts[0].strip()
                        arg_desc = parts[1].strip()
                        md_content.append(f"- `{arg_name_type}`: {arg_desc}")
                    else:
                        md_content.append(f"- `{arg.strip()}`")
        if cls_doc.get("methods"):
            md_content.append("\n---")
        for method_name, method_doc in cls_doc.get("methods", {}).items():
            md_content.append(
                format_function_md(method_name, method_doc, is_method=True)
            )
            md_content.append("---")

    for func_name, func_doc in docstrings.get("functions", {}).items():
        md_content.append(format_function_md(func_name, func_doc))
        md_content.append("---")

    return "\n".join(md_content)


def create_docs(src_dirs: list[Path], dst_dir: Path) -> None:
    """Создает Markdown-документацию для всех Python-файлов из списка директорий.

    Args:
        src_dirs (list[Path]): Список исходных директорий.
        dst_dir (Path): Папка, куда будут сохранены сгенерированные Markdown-файлы.
    """
    for src_dir in src_dirs:
        for root, _dirs, files in os.walk(src_dir):
            rel_path = Path(root).relative_to(src_dir)
            target_dir = dst_dir / rel_path
            target_dir.mkdir(parents=True, exist_ok=True)

            for file in files:
                file_path = Path(root) / file
                if (
                    file_path.suffix in SUPPORTED_EXT
                    and file_path.name != "__init__.py"
                ):
                    docstrings = extract_docstrings(file_path)
                    md_content = write_md(file_path, docstrings)
                    md_file = target_dir / f"{file_path.stem}.md"
                    with open(md_file, "w", encoding="utf-8") as f:
                        f.write(md_content)


def rename_wiki_files_by_header(local_wiki_dir: Path, docs_dir: Path) -> None:
    """Переименовывает .md файлы в .wiki_tmp на основании второй строки исходных .py файлов.

    Если вторая строка файла начинается с # , используется её содержимое (без решётки и пробелов) как новое имя Markdown-файла.
    Если такого заголовка нет, имя остаётся прежним.

    Args:
        local_wiki_dir (Path): Локальная директория Wiki (.wiki_tmp)
        docs_dir (Path): Папка с документацией (docs/)
    """
    for root, _, files in os.walk(local_wiki_dir):
        for file in files:
            if not file.endswith(".md"):
                continue

            md_path = Path(root) / file
            rel_path = md_path.relative_to(local_wiki_dir)
            py_source = docs_dir / rel_path
            py_source = py_source.with_suffix(".py")

            if not py_source.exists():
                for src_dir in PROJECT_DIRS:
                    possible_py = src_dir / rel_path
                    possible_py = possible_py.with_suffix(".py")
                    if possible_py.exists():
                        py_source = possible_py
                        break

            if not py_source.exists():
                continue

            try:
                with open(py_source, encoding="utf-8") as f:
                    lines = f.readlines()
                if len(lines) < 2:
                    continue
                second_line = lines[1].strip()
                if second_line.startswith("# "):
                    new_name = second_line[2:].strip()
                    if not new_name:
                        continue
                    new_md_name = f"{new_name}.md"
                    new_md_path = md_path.with_name(new_md_name)
                    if new_md_path != md_path:
                        os.rename(md_path, new_md_path)
                        print(f"[Wiki] Переименован: {md_path.name} → {new_md_name}")
            except Exception as e:
                print(f"[Wiki] Ошибка при обработке {md_path}: {e}")


def push_to_wiki(docs_dir: Path) -> None:
    """Копирует Markdown-документы в локальный клон Wiki и пушит изменения в удаленный репозиторий.

    Args:
        docs_dir (Path): Папка с сгенерированной документацией.
    """
    if not LOCAL_WIKI_DIR.exists():
        subprocess.run(["git", "clone", WIKI_REPO, str(LOCAL_WIKI_DIR)], check=True)

    for root, _, files in os.walk(docs_dir):
        rel_path = Path(root).relative_to(docs_dir)
        target_dir = LOCAL_WIKI_DIR / rel_path
        target_dir.mkdir(parents=True, exist_ok=True)
        for file in files:
            if file.endswith(".md"):
                src_file = Path(root) / file
                dst_file = target_dir / file
                shutil.copy2(src_file, dst_file)

    rename_wiki_files_by_header(LOCAL_WIKI_DIR, docs_dir)

    subprocess.run(["git", "-C", str(LOCAL_WIKI_DIR), "add", "."], check=True)
    status = subprocess.run(
        ["git", "-C", str(LOCAL_WIKI_DIR), "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=True,
    )
    if status.stdout.strip():
        subprocess.run(
            [
                "git",
                "-C",
                str(LOCAL_WIKI_DIR),
                "commit",
                "-m",
                "[Wiki] Обновление документации",
            ],
            check=True,
        )
        subprocess.run(["git", "-C", str(LOCAL_WIKI_DIR), "push"], check=True)
        print("[Wiki] Документация успешно обновлена и отправлена в Wiki.")
    else:
        print("[Wiki] Нет изменений для коммита.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Генерация документации проекта")
    parser.add_argument(
        "--push",
        action="store_true",
        help="Если указан, пушить документацию в GitHub Wiki",
    )
    args = parser.parse_args()

    create_docs(PROJECT_DIRS, DOCS_DIR)
    print(f"Документация сгенерирована в {DOCS_DIR}")

    if args.push:
        push_to_wiki(DOCS_DIR)
