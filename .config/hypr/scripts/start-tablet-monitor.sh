#!/usr/bin/env bash
set -euo pipefail

runtime_dir="${XDG_RUNTIME_DIR:?hyprglass: XDG_RUNTIME_DIR no está definido; el PID y el registro de WayVNC no van en /tmp compartido}"
pid_file="$runtime_dir/hyprglass-wayvnc.pid"
log_file="$runtime_dir/hyprglass-wayvnc.log"
tablet_mode="${HYPRGLASS_TABLET_MODE:-1280x800@60}"
tablet_position="${HYPRGLASS_TABLET_POSITION:-1920x0}"
primary_monitor="${HYPRGLASS_PRIMARY_MONITOR:-}"

monitor_json="$(hyprctl monitors -j)"
if [[ -z "$primary_monitor" ]]; then
  primary_monitor="$(python3 -c 'import json,sys; monitors=json.load(sys.stdin); print(next((m["name"] for m in monitors if not m["name"].startswith("HEADLESS-")), ""))' <<< "$monitor_json")"
fi

tablet_monitor="$(python3 -c 'import json,sys; monitors=json.load(sys.stdin); print(next((m["name"] for m in monitors if m["name"].startswith("HEADLESS-")), ""))' <<< "$monitor_json")"
if [[ -z "$tablet_monitor" ]]; then
  hyprctl output create headless
  sleep 0.5
  tablet_monitor="$(hyprctl monitors -j | python3 -c 'import json,sys; monitors=json.load(sys.stdin); print(next((m["name"] for m in monitors if m["name"].startswith("HEADLESS-")), ""))')"
fi

if [[ -z "$tablet_monitor" || -z "$primary_monitor" ]] ||
   [[ ! "$tablet_monitor" =~ ^[A-Za-z0-9._:-]+$ ]] ||
   [[ ! "$primary_monitor" =~ ^[A-Za-z0-9._:-]+$ ]]; then
  printf '%s\n' 'hyprglass: failed to detect physical or headless monitor' >&2
  exit 1
fi

if [[ ! "$tablet_mode" =~ ^(preferred|[0-9]+x[0-9]+(@[0-9]+([.][0-9]+)?)?)$ ]] ||
   [[ ! "$tablet_position" =~ ^-?[0-9]+x-?[0-9]+$ ]]; then
  printf '%s\n' 'hyprglass: invalid tablet mode or position' >&2
  exit 1
fi

hyprctl eval "hl.monitor({ output = \"$tablet_monitor\", mode = \"$tablet_mode\", position = \"$tablet_position\", scale = 1 })"
hyprctl eval "hl.workspace_rule({ workspace = \"10\", monitor = \"$tablet_monitor\", default = true })"

original_workspace="$(hyprctl activeworkspace -j | python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])')"
if [[ ! "$original_workspace" =~ ^[0-9]+$ ]]; then
  printf '%s\n' 'hyprglass: invalid active workspace id' >&2
  exit 1
fi
stray_workspace="$(hyprctl monitors -j | TABLET_MONITOR="$tablet_monitor" python3 -c 'import json,os,sys; monitor=next((m for m in json.load(sys.stdin) if m["name"] == os.environ["TABLET_MONITOR"]), None); print(monitor["activeWorkspace"]["id"] if monitor and monitor["activeWorkspace"]["id"] != 10 else "")')"

if [[ -n "$stray_workspace" ]]; then
  hyprctl dispatch "hl.dsp.focus({ workspace = $stray_workspace })"
  hyprctl dispatch "hl.dsp.workspace.move({ monitor = \"$primary_monitor\" })"
fi
hyprctl dispatch 'hl.dsp.focus({ workspace = 10 })'
hyprctl dispatch "hl.dsp.workspace.move({ monitor = \"$tablet_monitor\" })"
hyprctl dispatch "hl.dsp.focus({ workspace = $original_workspace })"

if [[ -f "$pid_file" ]] && kill -0 "$(cat "$pid_file")" 2>/dev/null; then
  exit 0
fi

wayvnc --output "$tablet_monitor" >"$log_file" 2>&1 </dev/null &
wayvnc_pid=$!
printf '%s\n' "$wayvnc_pid" > "$pid_file"
sleep 0.2
if ! kill -0 "$wayvnc_pid" 2>/dev/null; then
  rm -f -- "$pid_file"
  hyprctl output remove "$tablet_monitor" || true
  printf 'hyprglass: WayVNC failed to start; check %s\n' "$log_file" >&2
  exit 1
fi
