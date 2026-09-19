#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${HOME:-}" || "$HOME" == "/" ]]; then
  printf '%s\n' 'vaho: refusing to install with an empty or root HOME' >&2
  exit 1
fi

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
backup_dir="$HOME/.vaho-backup-$(date +%Y%m%d-%H%M%S)-$$"

echo "Creating backup in: $backup_dir"
mkdir -p "$backup_dir/.config"

for dir in hypr waybar gtk-3.0 gtk-4.0; do
  if [ -e "$HOME/.config/$dir" ]; then
    cp -a "$HOME/.config/$dir" "$backup_dir/.config/"
  fi
done

if [ -e "$HOME/scripts/battery-mode.sh" ]; then
  mkdir -p "$backup_dir/scripts"
  cp -a "$HOME/scripts/battery-mode.sh" "$backup_dir/scripts/"
fi

echo "Installing dotfiles..."
mkdir -p "$HOME/.config"
for dir in hypr waybar gtk-3.0 gtk-4.0; do
  target="$HOME/.config/$dir"
  rm -rf -- "$target"
  cp -a "$repo_dir/.config/$dir" "$target"
done

mkdir -p "$HOME/scripts"
cp -a "$repo_dir/scripts/battery-mode.sh" "$HOME/scripts/"

chmod +x "$HOME/.config/waybar/scripts/"*.sh 2>/dev/null || true
chmod +x "$HOME/.config/hypr/scripts/"*.sh 2>/dev/null || true
chmod +x "$HOME/scripts/battery-mode.sh"

echo "Done."
echo "Backup saved in: $backup_dir"
echo "Restart your Hyprland session or run: hyprctl reload"
