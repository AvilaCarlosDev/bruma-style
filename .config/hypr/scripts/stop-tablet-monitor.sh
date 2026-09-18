#!/usr/bin/env bash
set -euo pipefail

runtime_dir="${XDG_RUNTIME_DIR:?hyprglass: XDG_RUNTIME_DIR no está definido; el PID y el registro de WayVNC no van en /tmp compartido}"
pid_file="$runtime_dir/hyprglass-wayvnc.pid"

if [[ -f "$pid_file" ]]; then
  pid="$(cat "$pid_file")"
  if [[ "$pid" =~ ^[0-9]+$ ]] && kill -0 "$pid" 2>/dev/null; then
    kill "$pid"
  fi
  rm -f -- "$pid_file"
fi

tablet_monitor="$(hyprctl monitors -j | python3 -c 'import json,sys; monitors=json.load(sys.stdin); print(next((m["name"] for m in monitors if m["name"].startswith("HEADLESS-")), ""))')"
if [[ -n "$tablet_monitor" ]]; then
  if [[ ! "$tablet_monitor" =~ ^[A-Za-z0-9._:-]+$ ]]; then
    printf '%s\n' 'hyprglass: invalid headless monitor name' >&2
    exit 1
  fi
  hyprctl output remove "$tablet_monitor"
fi
