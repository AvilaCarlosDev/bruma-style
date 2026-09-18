#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
failures=0

pass() { printf 'PASS  %s\n' "$1"; }
fail() { printf 'FAIL  %s\n' "$1" >&2; failures=$((failures + 1)); }

expect() {
  local description=$1
  shift
  if "$@"; then pass "$description"; else fail "$description"; fi
}

expect_no_match() {
  local description=$1 pattern=$2
  shift 2
  if rg -n --hidden -g '!.git/**' "$pattern" "$@" >/dev/null 2>&1; then
    fail "$description"
  else
    pass "$description"
  fi
}

cd "$repo_dir"

mapfile -t shell_files < <(find . -path './.git' -prune -o -type f -name '*.sh' -print | sort)
expect "all shell scripts parse" bash -n "${shell_files[@]}"

expect "Python files parse without writing bytecode" python3 - <<'PY'
from pathlib import Path
import ast

for path in Path('.').rglob('*.py'):
    if '.git' in path.parts:
        continue
    ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
PY

expect "Waybar config is valid JSON" python3 -c \
  'import json,sys; json.load(open(sys.argv[1], encoding="utf-8"))' \
  .config/waybar/config

expect_no_match "no personal absolute home paths" '/home/carlosdev' -g '!tests/run.sh' .
expect_no_match "no tracked Python caches" '__pycache__|\.pyc$' < <(git ls-files)
expect_no_match "active config has no rofi/wofi executable dependency" 'rofi\s+-|wofi\s+--' \
  .config/hypr/hyprland.lua .config/waybar/config .config/waybar/scripts scripts/battery-mode.sh
expect_no_match "legacy always-on tablet setup removed" 'setup-headless-monitor\.sh' \
  .config/hypr/hyprland.lua .config/hypr/scripts
expect_no_match "no personal Brave PWA identifier" 'brave-[a-z]{32}-Default' .config/hypr/hyprland.lua
expect_no_match "Waybar has no personal web-app rewrites" 'chrome-[A-Za-z0-9_.-]+-Default' \
  .config/waybar/config
expect_no_match "no private WhiteSur or McMojave theme dependency" 'WhiteSur|McMojave' \
  .config/hypr/hyprland.lua .config/gtk-3.0/settings.ini .config/gtk-4.0/settings.ini
expect_no_match "no legacy macOS branding or wallpaper path" '(?i)macos' .config
expect_no_match "Wi-Fi password is not passed in argv" '"password",\s*pw' \
  .config/waybar/scripts/glass/network_menu.py
expect_no_match "battery integration does not assume BAT0" 'BAT0' \
  .config/waybar/scripts/glass/battery_menu.py scripts/battery-mode.sh

for required in \
  .config/hypr/scripts/setup-workspace-rules.sh \
  .config/hypr/scripts/toggle-tablet-monitor.sh \
  .config/hypr/scripts/start-tablet-monitor.sh \
  .config/hypr/scripts/stop-tablet-monitor.sh \
  .config/waybar/scripts/glass/bluetooth_menu.py; do
  if [[ -f "$required" ]]; then pass "$required exists"; else fail "$required exists"; fi
done

if rg -n 'WEATHER_LOCATION:-' .config/waybar/scripts/weather.sh >/dev/null &&
   rg -n 'WEATHER_LOCATION_PRETTY:-' .config/waybar/scripts/weather.sh >/dev/null; then
  pass "weather location is configurable"
else
  fail "weather location is configurable"
fi

if rg -n 'expanduser\("~/scripts/battery-mode\.sh"\)' \
  .config/waybar/scripts/glass/battery_menu.py >/dev/null; then
  pass "battery helper path is portable"
else
  fail "battery helper path is portable"
fi

tmp_root="$(mktemp -d /tmp/hyprglass-tests.XXXXXX)"
trap 'rm -rf -- "$tmp_root"' EXIT
demo_home="$tmp_root/home"
mkdir -p "$demo_home/.config/hypr" "$demo_home/.config/waybar"
printf '%s\n' 'previous-hypr-config' > "$demo_home/.config/hypr/hyprland.lua"
printf '%s\n' 'previous-waybar-config' > "$demo_home/.config/waybar/config"
printf '%s\n' 'stale-script' > "$demo_home/.config/hypr/stale-file"

if HOME="$demo_home" ./install.sh >"$tmp_root/install.log" 2>&1; then
  pass "installer completes in an isolated HOME"
else
  fail "installer completes in an isolated HOME"
fi

backup_dir="$(find "$demo_home" -maxdepth 1 -type d -name '.hyprglass-backup-*' -print -quit)"
if [[ -n "$backup_dir" ]] &&
   grep -qx 'previous-hypr-config' "$backup_dir/.config/hypr/hyprland.lua" &&
   grep -qx 'previous-waybar-config' "$backup_dir/.config/waybar/config"; then
  pass "installer preserves previous file contents in its backup"
else
  fail "installer preserves previous file contents in its backup"
fi

if [[ ! -e "$demo_home/.config/hypr/stale-file" ]] &&
   grep -qx 'stale-script' "$backup_dir/.config/hypr/stale-file"; then
  pass "installer removes stale files only after backing them up"
else
  fail "installer removes stale files only after backing them up"
fi

for installed in \
  "$demo_home/.config/hypr/hyprland.lua" \
  "$demo_home/.config/waybar/config" \
  "$demo_home/.config/gtk-3.0/settings.ini" \
  "$demo_home/.config/gtk-4.0/settings.ini" \
  "$demo_home/scripts/battery-mode.sh"; do
  if [[ -f "$installed" ]]; then pass "installer copies ${installed#"$demo_home/"}"; else fail "installer copies ${installed#"$demo_home/"}"; fi
done

expect "README relative links resolve" python3 - <<'PY'
from pathlib import Path
import re

root = Path('.')
for name in ('README.md', 'README.en.md', 'PACKAGES.md', 'PACKAGES.en.md', 'CONTRIBUTING.md',
             'SECURITY.md', 'CODE_OF_CONDUCT.md', 'CHANGELOG.md'):
    document = root / name
    text = document.read_text(encoding='utf-8')
    for target in re.findall(r'!?\[[^]]*\]\(([^)]+)\)', text):
        if target.startswith(('http://', 'https://', '#')):
            continue
        path = (document.parent / target.split('#', 1)[0]).resolve()
        if not path.exists():
            raise SystemExit(f'{document}: missing link target {target}')
PY

fake_bin="$tmp_root/bin"
fake_state="$tmp_root/hyprctl.log"
mkdir -p "$fake_bin"
cat > "$fake_bin/hyprctl" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
if [[ "${1:-}" == "monitors" && "${2:-}" == "-j" ]]; then
  printf '%s\n' '[{"name":"eDP-1","activeWorkspace":{"id":1}}]'
  exit 0
fi
printf '%s\n' "$*" >> "${HYPRGLASS_TEST_LOG:?}"
SH
chmod +x "$fake_bin/hyprctl"

if PATH="$fake_bin:$PATH" HYPRGLASS_TEST_LOG="$fake_state" \
  .config/hypr/scripts/setup-workspace-rules.sh &&
   [[ "$(wc -l < "$fake_state")" -eq 9 ]] &&
   rg 'workspace = "1", monitor = "eDP-1"' "$fake_state" >/dev/null &&
   rg 'workspace = "9", monitor = "eDP-1"' "$fake_state" >/dev/null; then
  pass "workspace rules detect the physical monitor without hardcoding it"
else
  fail "workspace rules detect the physical monitor without hardcoding it"
fi

fake_battery="$tmp_root/BAT1"
fake_tlp_config="$tmp_root/tlp.conf"
mkdir -p "$fake_battery"
printf '%s\n' Battery > "$fake_battery/type"
printf '%s\n' 73 > "$fake_battery/capacity"
printf '%s\n' Discharging > "$fake_battery/status"
cat > "$fake_bin/sudo" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
if [[ "${1:-}" == "tee" ]]; then
  cat > "${HYPRGLASS_TEST_TLP_CONFIG:?}"
  exit 0
fi
if [[ "${1:-}" == "tlp" ]]; then
  exit 0
fi
printf 'unexpected sudo command: %s\n' "$*" >&2
exit 1
SH
cat > "$fake_bin/notify-send" <<'SH'
#!/usr/bin/env bash
exit 0
SH
chmod +x "$fake_bin/sudo" "$fake_bin/notify-send"

if PATH="$fake_bin:$PATH" \
   HYPRGLASS_BATTERY_PATH="$fake_battery" \
   HYPRGLASS_TEST_TLP_CONFIG="$fake_tlp_config" \
   HYPRGLASS_SLEEP_SECONDS=0 \
   scripts/battery-mode.sh preserve &&
   grep -qx 'START_CHARGE_THRESH_BAT1=40' "$fake_tlp_config" &&
   grep -qx 'STOP_CHARGE_THRESH_BAT1=80' "$fake_tlp_config"; then
  pass "battery helper detects and configures a non-BAT0 device"
else
  fail "battery helper detects and configures a non-BAT0 device"
fi

tablet_state="$tmp_root/headless-created"
tablet_log="$tmp_root/tablet-hyprctl.log"
tablet_runtime="$tmp_root/runtime"
mkdir -p "$tablet_runtime"
cat > "$fake_bin/hyprctl" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
state="${HYPRGLASS_TEST_TABLET_STATE:?}"
log="${HYPRGLASS_TEST_TABLET_LOG:?}"

if [[ "${1:-}" == "monitors" && "${2:-}" == "-j" ]]; then
  if [[ -e "$state" ]]; then
    printf '%s\n' '[{"name":"eDP-1","activeWorkspace":{"id":1}},{"name":"HEADLESS-1","activeWorkspace":{"id":10}}]'
  else
    printf '%s\n' '[{"name":"eDP-1","activeWorkspace":{"id":1}}]'
  fi
  exit 0
fi
if [[ "${1:-}" == "activeworkspace" && "${2:-}" == "-j" ]]; then
  printf '%s\n' '{"id":1}'
  exit 0
fi
if [[ "${1:-}" == "output" && "${2:-}" == "create" ]]; then
  : > "$state"
elif [[ "${1:-}" == "output" && "${2:-}" == "remove" ]]; then
  rm -f -- "$state"
fi
printf '%s\n' "$*" >> "$log"
SH
cat > "$fake_bin/wayvnc" <<'SH'
#!/usr/bin/env bash
printf 'wayvnc %s\n' "$*" >> "${HYPRGLASS_TEST_TABLET_LOG:?}"
sleep 30
SH
chmod +x "$fake_bin/hyprctl" "$fake_bin/wayvnc"

if PATH="$fake_bin:$PATH" \
   XDG_RUNTIME_DIR="$tablet_runtime" \
   HYPRGLASS_TEST_TABLET_STATE="$tablet_state" \
   HYPRGLASS_TEST_TABLET_LOG="$tablet_log" \
   .config/hypr/scripts/start-tablet-monitor.sh &&
   [[ -e "$tablet_state" && -s "$tablet_runtime/hyprglass-wayvnc.pid" ]] &&
   rg 'output create headless' "$tablet_log" >/dev/null &&
   rg 'workspace = "10", monitor = "HEADLESS-1"' "$tablet_log" >/dev/null &&
   rg 'wayvnc --output HEADLESS-1' "$tablet_log" >/dev/null; then
  pass "tablet start creates and configures an on-demand headless output"
else
  fail "tablet start creates and configures an on-demand headless output"
fi

if PATH="$fake_bin:$PATH" \
   XDG_RUNTIME_DIR="$tablet_runtime" \
   HYPRGLASS_TEST_TABLET_STATE="$tablet_state" \
   HYPRGLASS_TEST_TABLET_LOG="$tablet_log" \
   .config/hypr/scripts/stop-tablet-monitor.sh &&
   [[ ! -e "$tablet_state" && ! -e "$tablet_runtime/hyprglass-wayvnc.pid" ]] &&
   rg 'output remove HEADLESS-1' "$tablet_log" >/dev/null; then
  pass "tablet stop terminates its WayVNC process and removes the output"
else
  fail "tablet stop terminates its WayVNC process and removes the output"
fi

# --- weather.sh: la ubicación es dato del usuario y debe ir codificada en la URL ---
weather_bin="$tmp_root/weather-bin"
weather_log="$tmp_root/weather-curl.log"
mkdir -p "$weather_bin" "$tmp_root/weather-home"
cat > "$weather_bin/curl" <<'SH'
#!/usr/bin/env bash
printf '%s\n' "${@: -1}" >> "${HYPRGLASS_TEST_CURL_LOG:?}"
SH
chmod +x "$weather_bin/curl"

: > "$weather_log"
PATH="$weather_bin:$PATH" \
  XDG_RUNTIME_DIR="$tmp_root/weather-home" \
  HYPRGLASS_TEST_CURL_LOG="$weather_log" \
  WEATHER_LOCATION='Ciudad de Panamá/../x?y=1#z' \
  .config/waybar/scripts/weather.sh >/dev/null 2>&1 || true
expect "weather location is percent-encoded in the request URL" \
  grep -qxF 'https://wttr.in/Ciudad%20de%20Panam%C3%A1%2F..%2Fx%3Fy%3D1%23z?format=j1' "$weather_log"

: > "$weather_log"
PATH="$weather_bin:$PATH" \
  XDG_RUNTIME_DIR="$tmp_root/weather-home" \
  HYPRGLASS_TEST_CURL_LOG="$weather_log" \
  .config/waybar/scripts/weather.sh >/dev/null 2>&1 || true
expect "weather default location still resolves to Caracas" \
  grep -qxF 'https://wttr.in/Caracas%2CVenezuela?format=j1' "$weather_log"

no_runtime_home="$tmp_root/no-runtime-home"
mkdir -p "$no_runtime_home"
env -u XDG_RUNTIME_DIR -u XDG_CACHE_HOME HOME="$no_runtime_home" PATH="$weather_bin:$PATH" \
  HYPRGLASS_TEST_CURL_LOG="$weather_log" \
  .config/waybar/scripts/weather.sh >/dev/null 2>&1 || true
expect "weather cache falls back to a user-owned directory, never a shared /tmp path" \
  test -d "$no_runtime_home/.cache/waybar-weather"

# --- scripts de la tableta: sin XDG_RUNTIME_DIR no deben usar /tmp compartido ---
for script in start-tablet-monitor stop-tablet-monitor; do
  if env -u XDG_RUNTIME_DIR PATH="$fake_bin:$PATH" \
       .config/hypr/scripts/$script.sh 2>"$tmp_root/$script.err"; then
    fail "$script refuses to run without XDG_RUNTIME_DIR"
  elif rg 'XDG_RUNTIME_DIR' "$tmp_root/$script.err" >/dev/null; then
    pass "$script refuses to run without XDG_RUNTIME_DIR"
  else
    fail "$script refuses to run without XDG_RUNTIME_DIR"
  fi
done

if (( failures > 0 )); then
  printf '\n%d check(s) failed.\n' "$failures" >&2
  exit 1
fi

printf '\nAll hyprglass checks passed.\n'
