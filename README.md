# bruma-style

[English](README.en.md) · **Español**

[![CI](https://github.com/AvilaCarlosDev/bruma-style/actions/workflows/ci.yml/badge.svg)](https://github.com/AvilaCarlosDev/bruma-style/actions/workflows/ci.yml)
[![Licencia: MIT](https://img.shields.io/badge/licencia-MIT-blue.svg)](LICENSE)
![Arch Linux](https://img.shields.io/badge/Arch_Linux-1793D1?logo=archlinux&logoColor=white)
![Hyprland](https://img.shields.io/badge/Hyprland-0.56.2-00a8a8)

Bruma-style es el subconjunto público y portable de mi escritorio Arch Linux +
Hyprland. Su lenguaje visual usa superficies translúcidas, geometría redondeada
y menús GTK propios. No es un clon de macOS ni pretende reproducir otro entorno
de escritorio.

> **Alcance actual:** probado en Arch Linux con Hyprland 0.56.2 y una ThinkPad
> E14. Las teclas de hardware, los umbrales de carga de batería y los nombres de
> monitor cambian entre equipos; las limitaciones relevantes están documentadas
> más abajo.

## Qué incluye

- Configuración nativa de Hyprland en Lua con márgenes, desenfoque, esquinas
  redondeadas, animaciones y atajos de teclado y ratón.
- Una Waybar flotante con módulos de distribución de teclado, multimedia, clima,
  red, Bluetooth, audio, CPU, memoria, batería, notificaciones y energía.
- Menús GTK 3 + GtkLayerShell hechos a mano para aplicaciones, energía, red,
  audio, batería, portapapeles, Bluetooth y fondos de pantalla.
- Una salida virtual opcional, bajo demanda, con WayVNC para usar una tableta
  como segunda pantalla.
- Un instalador que respalda antes de escribir y comprobaciones automáticas de
  la configuración pública.

El repositorio público excluye a propósito PWAs propias de cada equipo, perfiles
de red privados, procesos Shimeji, rutas absolutas del home, cachés y copias
de seguridad locales.

## Capturas

Waybar:

![Waybar](docs/assets/bruma-style-waybar.png)

Uno de los menús de vidrio:

![Menú de energía](docs/assets/bruma-style-glass-menu.png)

Demostración del instalador real `install.sh` en un entorno aislado:

![Demostración del instalador](docs/assets/bruma-style-install-demo.png)

## Requisitos

Bruma-style apunta a Arch Linux. La lista completa de paquetes, función por
función, está en [PACKAGES.md](PACKAGES.md). Los menús propios requieren
**GTK 3, PyGObject y GtkLayerShell**.

Tras instalar las dependencias, comprueba el equipo actual con:

```sh
./scripts/check-dependencies.sh
```

## Instalación

Revisa el repositorio antes de instalar y luego ejecuta:

```sh
./install.sh
```

El instalador:

1. crea una copia de seguridad con fecha en `~/.bruma-style-backup-*`;
2. copia las preferencias elegidas de Hyprland, Waybar y GTK;
3. instala el ayudante opcional de batería en `~/scripts`.

Reemplaza los directorios de configuración correspondientes después de guardar
la copia. **No** instala paquetes del sistema, no activa servicios y no toca TLP
hasta que invoques el ayudante de batería de forma explícita.

## Configuración

### Aplicaciones predeterminadas

Edita estas variables al inicio de `.config/hypr/hyprland.lua`:

```lua
local terminal = "kitty"
local fileManager = "thunar"
local browser = "firefox"
```

### Distribuciones de teclado y teclas de hardware

Las distribuciones por defecto son US y español latinoamericano, con cambio
mediante `SUPER + Space`. Los atajos de teclas multimedia se probaron en una
ThinkPad E14. Las teclas que el sistema reporta como `XF86Display`,
`XF86NotificationCenter` o `XF86Favorites` pueden ser distintas o no existir en
otro hardware.

La tecla `XF86Favorites` de la fila Fn activa o desactiva Bluetooth. Es
independiente de `SUPER + F12`, que controla la salida opcional de la tableta.

### Monitor de tableta

Instala WayVNC y pulsa `SUPER + F12` para crear o quitar la salida virtual. El
espacio de trabajo 10 queda asignado a ella; usa `SUPER + 0` y
`SUPER + SHIFT + 0` para enfocarlo o mover una ventana allí.

Los valores por defecto se pueden cambiar en la sesión de Hyprland:

```sh
export BRUMA_PRIMARY_MONITOR=eDP-1
export BRUMA_TABLET_MODE=1280x800@60
export BRUMA_TABLET_POSITION=1920x0
```

WayVNC solo se inicia cuando la salida de la tableta está activa, y Bruma-style le
pasa de forma explícita la salida virtual detectada. WayVNC escucha en localhost
por defecto, así que el acceso remoto requiere tu propia configuración
autenticada de WayVNC y reglas de cortafuegos o de red privada adecuadas.
Bruma-style no incluye usuarios, contraseñas ni certificados, ni un modo de
escucha pública por defecto.

### Clima

El script de Waybar usa wttr.in y toma Caracas como ejemplo público:

```sh
export WEATHER_LOCATION='Caracas,Venezuela'
export WEATHER_LOCATION_PRETTY='Caracas, VE'
```

### Umbrales de batería

El menú de batería llama a TLP mediante `~/scripts/battery-mode.sh`. Es opcional
y solo funciona si el firmware del portátil y TLP admiten umbrales de carga. El
ayudante detecta el primer dispositivo de energía de tipo `Battery`; define
`BRUMA_BATTERY_PATH` para forzar otro.

El ayudante usa `sudo` y escribe únicamente
`/etc/tlp.d/99-bruma-style-battery.conf`. Revísalo antes de elegir un modo.

## Validación

```sh
./tests/run.sh
```

Las comprobaciones analizan cada archivo de shell y Python, validan el JSON de
Waybar, rechazan rutas personales y componentes obsoletos, ejercitan el
instalador en un home aislado y verifican que las copias conserven el contenido
previo.

Los menús en Python tienen dos capas de pruebas. La lógica se prueba sin GTK ni
pantalla (GTK y los comandos del sistema se simulan):

```sh
pip install -r requirements-dev.txt
ruff check .
pytest
```

La interfaz se prueba con GTK real, construyendo cada menú y accionando sus
filas sin mostrar ninguna ventana. Requiere PyGObject y Xvfb (o un display):

```sh
xvfb-run -a python3 -m pytest tests/gtk
```

El CI ejecuta todo lo anterior (las pruebas de interfaz bajo Xvfb), además de ShellCheck, un escaneo de secretos
(gitleaks) y una comprobación que rechaza marcas de agua de IA en archivos y
mensajes de commit.

## Seguridad y privacidad

No subas credenciales, perfiles Wi-Fi/VPN, PWAs del navegador, registros,
historial de shell ni copias completas del directorio personal. El repositorio
solo incluye configuración pública. Las contraseñas de red las gestiona el agente
de secretos de NetworkManager, no se pasan como argumentos de línea de comandos.

Los reportes de seguridad siguen [SECURITY.md](SECURITY.md). Las contribuciones
se describen en [CONTRIBUTING.md](CONTRIBUTING.md).

## Créditos

Creado y mantenido por [Carlos Avila](https://github.com/AvilaCarlosDev).
Desarrollado con el apoyo de Claude (Anthropic) como asistente de revisión de
arquitectura y redacción de pruebas; las decisiones de diseño y la revisión
final son del autor. El historial del proyecto está en [CHANGELOG.md](CHANGELOG.md).

## Licencia

MIT — ver [LICENSE](LICENSE).
