# Hyprland macOS-style dotfiles

Configuracion publica para Arch Linux + Hyprland con un estilo tipo macOS:

- Hyprland con gaps, blur, bordes redondeados y animaciones suaves. Config nativa en
  **Lua** (`hyprland.conf` queda solo de referencia historica, Hyprland carga
  `hyprland.lua` directamente).
- Waybar flotante con estilo glass, con indicador de layout de teclado (US/ES) e
  icono de bluetooth con on-click/off-click correctos.
- Menus propios en GTK ("Liquid Glass"): launcher, power, red, audio/volumen,
  bateria, portapapeles, wallpaper (`waybar/scripts/glass/*.py`). Reemplazan a
  wofi/rofi/nwg-drawer, que ya no se usan ni estan instalados.
- Fn-row del teclado (probado en ThinkPad E14) mapeada a funciones reales: mute,
  volumen, brillo, mic-mute, pantalla externa (`nwg-displays`), centro de
  notificaciones (swaync), bluetooth on/off.
- Monitor virtual headless + `wayvnc` para usar una tablet Android como segundo
  monitor (workspace 10 dedicado, `SUPER+0` / `SUPER+SHIFT+0`).
- Selector de wallpaper.
- Modulo de clima para Waybar usando wttr.in.
- Overrides `.desktop` publicos para ocultar gestores de archivos duplicados del launcher.

## Capturas

Agrega aqui tus screenshots cuando quieras publicar el repositorio.

## Dependencias

Paquetes principales en Arch:

```sh
sudo pacman -S --needed hyprland waybar nwg-dock-hyprland nwg-displays swaybg swaync hyprlock wl-clipboard cliphist jq curl brightnessctl wpctl networkmanager polkit-gnome desktop-file-utils gtk4
```

Opcionales:

```sh
sudo pacman -S --needed kitty nautilus papirus-icon-theme ttf-jetbrains-mono-nerd wayvnc
```

`wayvnc` solo hace falta si vas a usar el monitor virtual/tablet-como-segundo-monitor.

Para los limites de carga de bateria se usa TLP. Si no usas TLP, puedes borrar scripts/battery-mode.sh y quitar el click de bateria en Waybar.

## Instalacion

Clona el repo y ejecuta:

```sh
./install.sh
```

El instalador hace backup de tus configs actuales antes de copiar estas.

Tambien instala overrides en `~/.local/share/applications` para dejar Nautilus/Archivos como gestor de archivos visible y ocultar Nemo, Thunar y Dolphin del launcher.

## Clima

El script de clima usa wttr.in. Por defecto usa Caracas como ejemplo publico.

Puedes cambiarlo sin editar el script agregando variables en tu sesion o en Hyprland:

```conf
env = WEATHER_LOCATION,Caracas,Venezuela
env = WEATHER_LOCATION_PRETTY,Caracas, VE
```

Usa el formato que entiende wttr.in, por ejemplo Madrid,Spain o Buenos+Aires,Argentina.

## Seguridad

Este repo esta pensado para ser publico. No debe contener:

- claves SSH
- tokens o API keys
- archivos .env
- configuraciones de WiFi/VPN
- accesos `.desktop` personales de navegadores o web apps
- caches, logs o historiales
- backups completos del home

Antes de publicar, ejecuta:

```sh
rg -n --hidden -i "token|api[_-]?key|secret|password|passwd|bearer|authorization|private[_-]?key|ssh|github|ghp_|sk-|BEGIN .*PRIVATE KEY|webhook|vpn|wifi|ssid" .
```

Si aparece algo sensible, no publiques hasta limpiarlo.
