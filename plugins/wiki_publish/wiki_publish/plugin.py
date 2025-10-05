# type: ignore

import shutil
import subprocess
from pathlib import Path
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options
import html2text
from bs4 import BeautifulSoup
import re


class WikiPublishPlugin(BasePlugin):
    """Плагин для обновления GitHub wiki с ручными и сгенерированными docs."""

    config_scheme = (("wiki_repo", config_options.Type(str, default=None)),)

    def on_post_build(self, config):
        """Публикация wiki с ручными и сгенерированными docs."""
        wiki_repo = self.config.get("wiki_repo")
        docs_dir = Path(config["docs_dir"])
        site_dir = Path(config["site_dir"])  # Уже сгенерированный сайт
        dst = Path("wiki")

        if not wiki_repo:
            print("[WikiPublishPlugin] Не указан wiki_repo")
            return

        # Клонируем wiki, если нет
        if not dst.exists():
            try:
                subprocess.run(
                    ["git", "clone", wiki_repo, str(dst)], check=True
                )
            except subprocess.CalledProcessError as e:
                print(f"[WikiPublishPlugin] Ошибка клонирования: {e}")
                return

        # Чистим старые Markdown файлы wiki
        for file in dst.rglob("*.md"):
            file.unlink()

        # Конвертируем HTML -> Markdown и копируем в wiki
        for html_file in site_dir.rglob("*.html"):
            # Пропускаем файлы, которые не находятся в папке с index.html
            if html_file.name != "index.html":
                continue
            # Используем имя родительской папки для имени файла Markdown
            parent_dir = html_file.parent
            file_name = (
                parent_dir.name + ".md"
                if parent_dir.name != site_dir.name
                else "index.md"
            )
            rel_path = (
                parent_dir.relative_to(site_dir).parent / file_name
                if parent_dir != site_dir
                else Path(file_name)
            )
            dest_file = dst / rel_path
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            with open(html_file, encoding="utf-8") as f:
                html_content = f.read()

            # Парсим HTML и обрезаем до первого якоря с классом "headerlink"
            soup = BeautifulSoup(html_content, "html.parser")
            anchor = soup.find("a", class_="headerlink")
            if anchor:
                # Получаем родительский h4 и все последующие элементы
                h4 = anchor.find_parent("h4")
                if h4:
                    # Создаем новый soup с минимальной HTML структурой
                    new_soup = BeautifulSoup(
                        "<!DOCTYPE html><html><head><meta charset='utf-8'></head><body></body></html>",
                        "html.parser",
                    )
                    # Добавляем h4 и все последующие элементы
                    current = h4
                    while current:
                        new_soup.body.append(current)
                        current = current.next_sibling
                    html_content = str(new_soup)
                else:
                    print(
                        f"[WikiPublishPlugin] Не найден родительский h4 для якоря в {html_file}"
                    )
            else:
                print(
                    f"[WikiPublishPlugin] Якорь с классом 'headerlink' не найден в {html_file}"
                )

            # Конвертируем в Markdown
            md_content = html2text.html2text(html_content)

            # Обрезаем всё до "Содержание" и включаем "Содержание", сохраняя всё после первого #
            lines = md_content.splitlines()
            start_index = None
            content_index = None
            for i, line in enumerate(lines):
                if line.strip() == "Содержание":
                    content_index = i
                    break
            if content_index is not None:
                # Ищем первый заголовок # после "Содержание"
                for i, line in enumerate(lines[content_index:]):
                    if line.startswith("# "):
                        start_index = content_index + i
                        break
                if start_index is not None:
                    # Удаляем всё до "Содержание", включая саму строку "Содержание"
                    md_content = "\n".join(lines[start_index:])
                else:
                    # Если заголовок # не найден, оставляем всё после "Содержание"
                    md_content = "\n".join(lines[content_index:])
            else:
                print(
                    f"[WikiPublishPlugin] Блок 'Содержание' не найден в {html_file}, сохраняем весь контент"
                )

            # Удаляем все строки, содержащие "---|---"
            lines = md_content.splitlines()
            lines = [line for line in lines if "---|---" not in line]
            md_content = "\n".join(lines)

            # Удаляем блоки "Source code in ..." и последующие строки до "|"
            lines = md_content.splitlines()
            cleaned_lines = []
            skip = False
            source_code_pattern = re.compile(r"^Source code in `.*\.py`$")
            for line in lines:
                if source_code_pattern.match(line):
                    skip = True
                    continue
                if skip and line.strip() == "|":
                    skip = False
                    continue
                if not skip:
                    cleaned_lines.append(line)
            md_content = "\n".join(cleaned_lines)

            # Удаляем строки, связанные с "Made with [ Material for MkDocs ]..." и "material/)"
            lines = md_content.splitlines()
            cleaned_lines = []
            made_with_pattern = re.compile(
                r"^(Made with \[ Material for MkDocs \]\(https://squidfunk\.github\.io/mkdocs-|material/\))$"
            )
            for line in lines:
                if not made_with_pattern.match(line):
                    cleaned_lines.append(line)
            md_content = "\n".join(cleaned_lines)

            # Сохраняем Markdown
            with open(dest_file, "w", encoding="utf-8") as f:
                f.write(md_content)

        # Копируем ручные Markdown файлы из docs/, если они ещё не сконвертированы
        for md_file in docs_dir.rglob("*.md"):
            rel_path = md_file.relative_to(docs_dir)
            dest_file = dst / rel_path
            if not dest_file.exists():
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(md_file, dest_file)

        # Git add/commit/push
        try:
            subprocess.run(["git", "-C", str(dst), "add", "."], check=True)
            status = subprocess.run(
                ["git", "-C", str(dst), "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=True,
            )
            if status.stdout:
                subprocess.run(
                    [
                        "git",
                        "-C",
                        str(dst),
                        "commit",
                        "-m",
                        "[Docs] Обновление wiki",
                    ],
                    check=True,
                )
                subprocess.run(["git", "-C", str(dst), "push"], check=True)
                print("[WikiPublishPlugin] Wiki успешно обновлена.")
            else:
                print("[WikiPublishPlugin] Нет изменений для коммита.")
        except subprocess.CalledProcessError as e:
            print(f"[WikiPublishPlugin] Ошибка git: {e}")
