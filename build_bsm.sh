#!/usr/bin/env bash
# Собирает BSM.apk из оригинального BombSquad APK со встроенным модом.
#
#   BSM_KEYSTORE_PASS=... ./build_bsm.sh BombSquad_Android_Generic_1.8.5.apk [BSM.apk]
#
# Нужны apktool, Java и Android build-tools (zipalign, apksigner).
# Ключ берётся из bsm.keystore (или из пути в BSM_KEYSTORE); если файла
# нет, создаётся новый — но тогда BSM не встанет поверх версии,
# подписанной старым ключом.
set -euo pipefail

orig=${1:?использование: build_bsm.sh <BombSquad.apk> [выходной.apk]}
out=${2:-BSM.apk}
here=$(cd "$(dirname "$0")" && pwd)
keystore=${BSM_KEYSTORE:-$here/bsm.keystore}
: "${BSM_KEYSTORE_PASS:?задай пароль ключа в BSM_KEYSTORE_PASS}"

if [[ -z ${JAVA_HOME:-} ]] && command -v brew >/dev/null; then
  export JAVA_HOME="$(brew --prefix openjdk)/libexec/openjdk.jdk/Contents/Home"
fi
[[ -n ${JAVA_HOME:-} ]] && export PATH="$JAVA_HOME/bin:$PATH"
sdk=${ANDROID_HOME:-$HOME/Library/Android/sdk}
buildtools=$(ls -d "$sdk"/build-tools/* 2>/dev/null | sort -V | tail -1)
[[ -n $buildtools ]] && export PATH="$buildtools:$PATH"

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT

apktool d -f -o "$work/dec" "$orig"

# Свой пакет, чтобы ставиться рядом с оригинальной игрой.
perl -pi -e 's/net\.froemling\.bombsquad(?=["\.])(?!\.(App|MainActivity)")/net.froemling.bsm/g' \
  "$work/dec/AndroidManifest.xml"
grep -rl '<string name="app_name_bombsquad">' "$work/dec/res" | xargs perl -pi -e \
  's#<string name="app_name_bombsquad">[^<]*</string>#<string name="app_name_bombsquad">BSM</string>#'

# Мод встроен в игру: копировать в папку mods ничего не нужно.
cp "$here/absorb_shield.py" \
  "$work/dec/assets/ballistica_files/ba_data/python/bsm_absorb_shield.py"

apktool b -o "$work/unsigned.apk" "$work/dec"
zipalign -f -P 16 4 "$work/unsigned.apk" "$work/aligned.apk"

if [[ ! -f $keystore ]]; then
  keytool -genkeypair -keystore "$keystore" -alias bsm -keyalg RSA \
    -keysize 2048 -validity 10000 -dname "CN=BSM" \
    -storepass "$BSM_KEYSTORE_PASS" -keypass "$BSM_KEYSTORE_PASS"
fi
apksigner sign --ks "$keystore" --ks-key-alias bsm \
  --ks-pass "pass:$BSM_KEYSTORE_PASS" --key-pass "pass:$BSM_KEYSTORE_PASS" \
  --out "$out" "$work/aligned.apk"
rm -f "$out.idsig"
apksigner verify "$out"
echo "Готово: $out"
