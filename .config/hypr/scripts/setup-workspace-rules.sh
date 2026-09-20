#!/usr/bin/env bash
set -euo pipefail

primary_monitor="${BRUMA_PRIMARY_MONITOR:-}"
if [[ -z "$primary_monitor" ]]; then
  primary_monitor="$(hyprctl monitors -j | python3 -c 'import json,sys; monitors=json.load(sys.stdin); print(next((m["name"] for m in monitors if not m["name"].startswith("HEADLESS-")), ""))')"
fi

if [[ -z "$primary_monitor" || ! "$primary_monitor" =~ ^[A-Za-z0-9._:-]+$ ]]; then
  printf '%s\n' 'bruma-style: no physical monitor detected' >&2
  exit 1
fi

for workspace in {1..9}; do
  hyprctl eval "hl.workspace_rule({ workspace = \"$workspace\", monitor = \"$primary_monitor\" })"
done

tablet_monitor="$(hyprctl monitors -j | python3 -c 'import json,sys; monitors=json.load(sys.stdin); print(next((m["name"] for m in monitors if m["name"].startswith("HEADLESS-")), ""))')"
if [[ -n "$tablet_monitor" ]]; then
  if [[ ! "$tablet_monitor" =~ ^[A-Za-z0-9._:-]+$ ]]; then
    printf '%s\n' 'bruma-style: invalid headless monitor name' >&2
    exit 1
  fi
  hyprctl eval "hl.workspace_rule({ workspace = \"10\", monitor = \"$tablet_monitor\", default = true })"
fi
