#!/usr/bin/env bash
set -euo pipefail

required=(
  Hyprland waybar hyprlock nwg-dock-hyprland nwg-displays
  swaybg swaync-client kitty thunar firefox nmcli nm-connection-editor bluetoothctl blueman-manager
  wpctl pactl wl-copy wl-paste cliphist grim slurp brightnessctl
  notify-send jq curl magick python3
)
optional=(wayvnc tlp)

missing_required=0

printf '%s\n' 'Required commands:'
for command_name in "${required[@]}"; do
  if command -v "$command_name" >/dev/null 2>&1; then
    printf '  OK       %s\n' "$command_name"
  else
    printf '  MISSING  %s\n' "$command_name"
    missing_required=1
  fi
done

printf '%s\n' 'Optional commands:'
for command_name in "${optional[@]}"; do
  if command -v "$command_name" >/dev/null 2>&1; then
    printf '  OK       %s\n' "$command_name"
  else
    printf '  SKIP     %s\n' "$command_name"
  fi
done

if ! python3 - <<'PY'
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("GtkLayerShell", "0.1")
from gi.repository import Gtk, GtkLayerShell  # noqa: F401
PY
then
  printf '%s\n' '  MISSING  Python GTK 3 / GtkLayerShell bindings'
  missing_required=1
else
  printf '%s\n' '  OK       Python GTK 3 / GtkLayerShell bindings'
fi

exit "$missing_required"
