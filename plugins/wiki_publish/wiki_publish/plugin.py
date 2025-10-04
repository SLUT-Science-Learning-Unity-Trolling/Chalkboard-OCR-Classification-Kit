import os
import shutil
import subprocess
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options


class WikiPublishPlugin(BasePlugin):
    """Плагин для автоматического обновления wiki в репозитории."""

    config_scheme = (("wiki_repo", config_options.Type(str, default=None)),)

    def on_post_build(self, config: dict[str, str]) -> None:
        """Срабатывает после сборки MkDocs.

        Args:
            config (dict): Конфиг
        """
        src = config["docs_dir"]
        dst = "wiki"
        wiki_repo = self.config.get("wiki_repo")

        if not wiki_repo:
            print(
                "[WikiPublishPlugin] Параметр wiki_repo не указан в mkdocs.yml"
            )
            return

        if not os.path.exists(dst):
            try:
                subprocess.run(["git", "clone", wiki_repo, dst], check=True)
            except subprocess.CalledProcessError as e:
                print(
                    f"[WikiPublishPlugin] Ошибка при клонировании репозитория wiki: {e}"
                )
                return

        for root, dirs, files in os.walk(dst, topdown=False):
            for file in files:
                if file.endswith(".md"):
                    os.remove(os.path.join(root, file))
            for d in dirs:
                dir_path = os.path.join(root, d)
                if d != ".git" and not os.listdir(dir_path):
                    os.rmdir(dir_path)

        for root, _, files in os.walk(src):
            for file in files:
                if file.endswith(".md"):
                    rel_path = os.path.relpath(root, src)
                    dest_dir = os.path.join(dst, rel_path)
                    os.makedirs(dest_dir, exist_ok=True)

                    src_file = os.path.join(root, file)
                    dest_file = os.path.join(dest_dir, file)
                    shutil.copy2(src_file, dest_file)

        try:
            subprocess.run(["git", "-C", dst, "add", "."], check=True)
            status = subprocess.run(
                ["git", "-C", dst, "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=True,
            )
            if status.stdout:
                subprocess.run(
                    [
                        "git",
                        "-C",
                        dst,
                        "commit",
                        "-m",
                        "[Docs] Обновление GitHub wiki через MkDocs",
                    ],
                    check=True,
                )
                subprocess.run(["git", "-C", dst, "push"], check=True)
                print(
                    "[WikiPublishPlugin] Wiki успешно обновлена и синхронизирована с docs/"
                )
            else:
                print("[WikiPublishPlugin] Нет изменений для коммита.")
        except subprocess.CalledProcessError as e:
            print(f"[WikiPublishPlugin] Ошибка при выполнении git-команд: {e}")
        except Exception as e:
            print(f"[WikiPublishPlugin] Произошла непредвиденная ошибка: {e}")
