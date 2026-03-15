# Использование:
#   ./clean_project.sh        # удалить мусор
#   ./clean_project.sh -n     # показать, что будет удалено (dry-run)

set -euo pipefail

ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"

DRYRUN=0
if [[ "${1:-}" == "-n" || "${1:-}" == "--dry-run" ]]; then
  DRYRUN=1
fi

TARGETS=(
  "__pycache__"
  ".mypy_cache"
  ".pytest_cache"
  ".ruff_cache"
  ".cache"
  "build"
  "dist"
  "*.egg-info"
  "pip-wheel-metadata"
  ".ipynb_checkpoints"
  ".DS_Store"
  ".coverage"
  "htmlcov"
  ".tox"
  ".eggs"
  "*.pyc"
  ".benchmarks"
  "site"
  ".wiki_tmp"
)

echo ">>> Очистка мусора в Python-проекте"
[[ $DRYRUN -eq 1 ]] && echo "(режим dry-run: только показываю, что будет удалено)"

remove_item() {
  local path="$1"
  local relpath="${path#$ROOT_DIR/}"  # путь относительно корня проекта
  if [[ $DRYRUN -eq 1 ]]; then
    echo "$relpath"
  else
    rm -rf "$path"
    echo "Удалено: $relpath"
  fi
}

for pattern in "${TARGETS[@]}"; do
  while IFS= read -r -d '' item; do
    [[ "$(basename "$item")" == ".env" ]] && continue
    remove_item "$item"
  done < <(find "$ROOT_DIR" -name "$pattern" -print0 2>/dev/null)
done

echo ">>> Готово!"
