# Packages

Minimal Arch package list used by this setup:

```sh
sudo pacman -S --needed \
  hyprland \
  waybar \
  nwg-dock-hyprland \
  nwg-displays \
  swaybg \
  swaync \
  hyprlock \
  wl-clipboard \
  cliphist \
  jq \
  curl \
  brightnessctl \
  networkmanager \
  polkit-gnome \
  desktop-file-utils \
  gtk4 \
  kitty \
  nautilus \
  papirus-icon-theme \
  ttf-jetbrains-mono-nerd

# opcional, solo si usás el monitor virtual/tablet-como-segundo-monitor
sudo pacman -S --needed wayvnc
```
