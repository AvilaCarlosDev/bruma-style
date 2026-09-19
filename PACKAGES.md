# Dependencias

[English](PACKAGES.en.md) · **Español**

Vaho se desarrolla y prueba en Arch Linux. Los grupos de paquetes de abajo
describen lo que el repositorio realmente invoca; no es un instalador
independiente de la distribución.

## Escritorio base

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

Los atajos por defecto abren Kitty, Thunar y Firefox. Edita las variables
`terminal`, `fileManager` y `browser` al inicio de `.config/hypr/hyprland.lua`
si usas otras aplicaciones.

GTK 3, PyGObject y GtkLayerShell son necesarios para los menús de vidrio. Esos
menús no requieren GTK 4; `.config/gtk-4.0` solo aplica preferencias
equivalentes a las aplicaciones GTK 4.

## Funciones opcionales

```sh
# monitor virtual para tableta
sudo pacman -S --needed wayvnc

# umbrales de carga de batería (solo en hardware compatible)
sudo pacman -S --needed tlp
```

El selector de fondos lee imágenes de `~/wallpaper` y crea miniaturas en
`~/.cache/wallpaper-selector`.

Ejecuta `./scripts/check-dependencies.sh` tras instalar los paquetes. Informa
por separado de los comandos obligatorios que faltan y de las funciones
opcionales.

## Para desarrollo

```sh
pip install -r requirements-dev.txt   # pytest y ruff
sudo pacman -S --needed shellcheck ripgrep
sudo pacman -S --needed xorg-server-xvfb   # pruebas de interfaz con GTK real (tests/gtk)
```
