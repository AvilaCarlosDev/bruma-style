#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if hyprctl monitors -j | python3 -c 'import json,sys; sys.exit(0 if any(m["name"].startswith("HEADLESS-") for m in json.load(sys.stdin)) else 1)'; then
  "$script_dir/stop-tablet-monitor.sh"
  notify-send "Tablet monitor" "Apagado" 2>/dev/null || true
else
  "$script_dir/start-tablet-monitor.sh"
  notify-send "Tablet monitor" "Prendido — conecta tu cliente VNC" 2>/dev/null || true
fi
