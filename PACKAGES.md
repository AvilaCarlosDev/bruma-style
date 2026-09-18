# Dependencies

Hyprglass is developed and tested on Arch Linux. The package groups below
describe what the repository actually calls; they are not a distro-agnostic
installer.

## Core desktop

```sh
sudo pacman -S --needed \
  hyprland waybar hyprlock \
  nwg-dock-hyprland nwg-displays \
  swaybg swaync \
  kitty thunar firefox \
  networkmanager network-manager-applet bluez-utils blueman \
  pipewire pipewire-pulse wireplumber pavucontrol \
  wl-clipboard cliphist \
  grim slurp brightnessctl \
  polkit-gnome libnotify \
  jq curl imagemagick \
  gtk3 python-gobject gtk-layer-shell \
  papirus-icon-theme ttf-jetbrains-mono-nerd noto-fonts-emoji \
  desktop-file-utils
```

The default key bindings launch Kitty, Thunar and Firefox. Edit the
`terminal`, `fileManager` and `browser` variables near the top of
`.config/hypr/hyprland.lua` if you use other applications.

GTK 3, PyGObject and GtkLayerShell are required by the custom glass menus.
GTK 4 is not required by those menus; `.config/gtk-4.0` only applies matching
preferences to GTK 4 applications.

## Optional features

```sh
# virtual tablet monitor
sudo pacman -S --needed wayvnc

# battery charge thresholds (only on supported hardware)
sudo pacman -S --needed tlp
```

The wallpaper picker reads images from `~/wallpaper` and creates thumbnails
under `~/.cache/wallpaper-selector`.

Run `./scripts/check-dependencies.sh` after installing packages. It reports
missing required commands separately from optional features.
