# ba_meta require api 9
"""BSM Updater — подтягивает свежие плагины BSM с GitHub.

При каждом запуске игры в фоне сверяет absorb_shield.py и boosters.py с
публичным репозиторием и, если там новая версия, скачивает её в папку модов
игры. Новая версия включается при следующем запуске (игра загружает плагины
только на старте). Копии, встроенные в APK, остаются запасными: без
интернета играешь на последней скачанной версии.
"""

from __future__ import annotations

import os
import re
import ssl
import sys
import threading
import urllib.request

import babase

# Public repo with just the plugin files (its main branch is the release
# channel).
RAW_URL = 'https://raw.githubusercontent.com/ir00nman/BSM-plugins/main/'
FILES = {
    # Downloaded file -> module names that may already be running it.
    'absorb_shield.py': ('absorb_shield', 'bsm_absorb_shield'),
    'boosters.py': ('boosters', 'bsm_boosters'),
}
_VERSION_RE = re.compile(r"^BSM_VERSION = '([^']+)'", re.MULTILINE)


def _version_key(version: str) -> tuple:
    return tuple(int(part) for part in re.findall(r'\d+', version))


def _running_version(modules: tuple) -> str:
    """Highest version among the copies loaded right now."""
    best = '0'
    for name in modules:
        version = getattr(sys.modules.get(name), 'BSM_VERSION', None)
        if version and _version_key(version) > _version_key(best):
            best = version
    return best


def _ssl_context() -> ssl.SSLContext:
    try:
        import certifi  # Bundled with the game.

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def _fetch(name: str, context: ssl.SSLContext) -> str | None:
    request = urllib.request.Request(
        RAW_URL + name,
        headers={'User-Agent': 'BSM-updater', 'Cache-Control': 'no-cache'},
    )
    with urllib.request.urlopen(request, timeout=15, context=context) as resp:
        if resp.status != 200:
            return None
        return resp.read().decode('utf-8')


def _looks_valid(text: str, name: str) -> bool:
    """A real plugin file, not an error page or a half download."""
    if '# ba_meta require api 9' not in text:
        return False
    if '# ba_meta export babase.Plugin' not in text:
        return False
    try:
        compile(text, name, 'exec')
    except SyntaxError:
        return False
    return True


def _check_for_updates() -> None:
    moddir = babase.app.env.python_directory_user
    if not moddir:
        return
    try:
        os.makedirs(moddir, exist_ok=True)
        context = _ssl_context()
    except Exception:
        return
    updated = []
    for name, modules in FILES.items():
        try:
            text = _fetch(name, context)
        except Exception:
            continue  # Offline or GitHub hiccup: keep what we have.
        if not text or not _looks_valid(text, name):
            continue
        match = _VERSION_RE.search(text)
        if match is None:
            continue
        remote = match.group(1)
        if _version_key(remote) <= _version_key(_running_version(modules)):
            continue
        path = os.path.join(moddir, name)
        try:
            with open(path + '.tmp', 'w', encoding='utf-8') as outfile:
                outfile.write(text)
            os.replace(path + '.tmp', path)
        except Exception:
            continue
        updated.append(remote)
    if updated:
        babase.pushcall(
            babase.CallStrict(_announce, max(updated, key=_version_key)),
            from_other_thread=True,
        )


def _announce(version: str) -> None:
    babase.screenmessage(
        f'BSM: загружено обновление {version} — перезапусти игру',
        color=(0.4, 1.0, 0.4),
    )
    try:
        from babase import _commonassets

        _commonassets.audio.ding.get().play()
    except Exception:
        pass


# ba_meta export babase.Plugin
class BSMUpdaterPlugin(babase.Plugin):
    """Downloads newer BSM plugins from GitHub in the background."""

    def on_app_running(self) -> None:
        threading.Thread(target=_check_for_updates, daemon=True).start()
