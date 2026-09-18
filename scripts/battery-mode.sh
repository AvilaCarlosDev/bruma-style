#!/usr/bin/env bash
# Optional TLP charge-threshold helper.
set -euo pipefail

MODE="${1:-}"
battery_path="${HYPRGLASS_BATTERY_PATH:-}"

if [[ -z "$battery_path" ]]; then
  for candidate in /sys/class/power_supply/*; do
    if [[ -r "$candidate/type" ]] && [[ "$(<"$candidate/type")" == "Battery" ]]; then
      battery_path="$candidate"
      break
    fi
  done
fi

if [[ -z "$battery_path" || ! -d "$battery_path" ]]; then
  printf '%s\n' 'hyprglass: no battery device detected' >&2
  exit 1
fi

battery_name="${battery_path##*/}"
if [[ ! "$battery_name" =~ ^[A-Za-z0-9_]+$ ]]; then
  printf 'hyprglass: unsupported battery device name: %s\n' "$battery_name" >&2
  exit 1
fi

write_thresholds() {
  local start=$1 stop=$2
  printf 'START_CHARGE_THRESH_%s=%s\nSTOP_CHARGE_THRESH_%s=%s\n' \
    "$battery_name" "$start" "$battery_name" "$stop" | \
    sudo tee /etc/tlp.d/99-hyprglass-battery.conf >/dev/null
}

case $MODE in
  full)
    # Carga completa (0-100%)
    write_thresholds 0 100
    notify-send "🔋 Batería" "Modo: CARGA COMPLETA (0-100%)" -t 3000
    ;;
  preserve)
    # Preservación (40-80%)
    write_thresholds 40 80
    notify-send "🔋 Batería" "Modo: PRESERVACIÓN (40-80%)" -t 3000
    ;;
  balanced)
    # Equilibrado (50-90%)
    write_thresholds 50 90
    notify-send "🔋 Batería" "Modo: EQUILIBRADO (50-90%)" -t 3000
    ;;
  reset)
    # Eliminar configuración personalizada
    sudo rm -f /etc/tlp.d/99-hyprglass-battery.conf
    notify-send "🔋 Batería" "Modo: DEFAULT TLP" -t 3000
    ;;
  *)
    printf 'Uso: %s {full|preserve|balanced|reset}\n' "$0" >&2
    exit 2
    ;;
esac

# Aplicar cambios
sudo tlp start 2>/dev/null

# Notificar nivel actual
sleep "${HYPRGLASS_SLEEP_SECONDS:-2}"
LEVEL=$(cat "$battery_path/capacity" 2>/dev/null || printf '?')
STATUS=$(cat "$battery_path/status" 2>/dev/null || printf '?')
notify-send "🔋 Estado Actual" "Nivel: ${LEVEL}%\nEstado: ${STATUS}" -t 5000
