#!/usr/bin/env bash
# Публикует плагины в публичный репозиторий BSM-plugins, откуда их
# подтягивает bsm_updater.py внутри BSM (ветка main = релизный канал).
#
#   ./publish_plugins.sh "сообщение коммита"
set -euo pipefail

repo=${BSM_PLUGINS_REPO:-https://github.com/ir00nman/BSM-plugins.git}
here=$(cd "$(dirname "$0")" && pwd)
msg=${1:-"Update BSM plugins"}

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

if ! git clone -q "$repo" "$work/repo" 2>/dev/null; then
  git init -q -b main "$work/repo"
  git -C "$work/repo" remote add origin "$repo"
fi
cp "$here/absorb_shield.py" "$here/boosters.py" "$work/repo/"
cat > "$work/repo/README.md" <<'EOF'
# BSM plugins

Плагины для BombSquad 1.8.5 (API 9): `absorb_shield.py` и `boosters.py`.
Сборка BSM подтягивает их отсюда автоматически (ветка `main`).
Для обычного BombSquad положи файлы в папку модов и включи плагины.
EOF
git -C "$work/repo" add -A
if git -C "$work/repo" diff --cached --quiet; then
  echo "Нечего публиковать: на GitHub уже эти версии."
  exit 0
fi
git -C "$work/repo" commit -q -m "$msg"
git -C "$work/repo" push -q -u origin main
echo "Опубликовано: $repo"
