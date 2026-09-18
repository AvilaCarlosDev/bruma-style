#!/usr/bin/env bash
# Demo reproducible: corre install.sh contra un $HOME aislado y temporal
# para mostrar, con una ejecucion real, que el instalador hace backup de
# configs existentes antes de sobreescribirlas. No toca tu $HOME real.
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
demo_home="$(mktemp -d /tmp/hyprglass-demo-home.XXXXXX)"
trap 'rm -rf "$demo_home"' EXIT

echo "Demo: instalador aislado en HOME temporal"
echo "HOME temporal: /tmp/hyprglass-demo-home"
echo

mkdir -p "$demo_home/.config/hypr" "$demo_home/.config/waybar"
echo "# config previa del usuario (simulada)" > "$demo_home/.config/hypr/hyprland.conf"
echo "// config previa de waybar (simulada)" > "$demo_home/.config/waybar/config"

echo "Antes de instalar:"
ls "$demo_home/.config/hypr" "$demo_home/.config/waybar"
echo

HOME="$demo_home" "$repo_dir/install.sh"
echo

echo "Verificacion:"
backup_dir=$(find "$demo_home" -maxdepth 1 -name ".hyprglass-backup-*" | head -1)
if cmp -s "$backup_dir/.config/hypr/hyprland.conf" <(printf '%s\n' '# config previa del usuario (simulada)') &&
   cmp -s "$backup_dir/.config/waybar/config" <(printf '%s\n' '// config previa de waybar (simulada)') &&
   [ -d "$demo_home/.config/hypr/scripts" ]; then
  echo "  Backup de la config previa: OK ($(basename "$backup_dir"))"
  echo "  Config nueva instalada: OK"
else
  echo "  FALLO: backup o instalacion incompleta"
  exit 1
fi
